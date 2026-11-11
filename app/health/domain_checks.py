"""Passive domain checks. Public information only.

What this does:  DNS TXT lookups (SPF, DMARC, DKIM on common selectors), one TLS
                 handshake on port 443, one HTTPS GET of the home page.
What it never does: port scanning, path guessing, login attempts, anything
                 against a domain the user has not confirmed they own.
"""
from __future__ import annotations

import ipaddress
import re
import socket
import ssl
from datetime import datetime, timezone
from typing import Callable

DOMAIN_RE = re.compile(r"^(?=.{4,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}$")
BLOCKED_SUFFIXES = (".local", ".localhost", ".internal", ".lan", ".home", ".corp", ".test", ".example", ".invalid")
DKIM_SELECTORS = ("default", "google", "selector1", "selector2", "k1", "s1", "s2", "dkim", "mail")
SECURITY_HEADERS = ("strict-transport-security", "content-security-policy", "x-content-type-options",
                    "x-frame-options", "referrer-policy")
HEADER_NAMES = {"strict-transport-security": "Strict-Transport-Security",
                "content-security-policy": "Content-Security-Policy",
                "x-content-type-options": "X-Content-Type-Options",
                "x-frame-options": "X-Frame-Options", "referrer-policy": "Referrer-Policy"}
USER_AGENT = "WolftechHealthCheck/0.1 (passive header check requested by the domain owner)"
NES4 = "CERTIN-NES.4"
TIMEOUT = 6.0


class DomainCheckRefused(Exception):
    """Raised when a check must not run (no ownership confirmation, or an unsafe target)."""


def normalise_domain(raw: str) -> str:
    """Return a clean hostname or raise ValueError with a plain-English reason."""
    d = (raw or "").strip().lower()
    d = re.sub(r"^[a-z]+://", "", d)
    d = d.split("/")[0].split("?")[0].split("#")[0]
    if "@" in d:
        d = d.rsplit("@", 1)[1]
    d = d.rstrip(".")
    if ":" in d:
        raise ValueError("Enter just the domain, without a port number.")
    if not d:
        raise ValueError("Enter your domain, for example yourfirm.in")
    try:
        ipaddress.ip_address(d)
    except ValueError:
        pass
    else:
        raise ValueError("Enter a domain name, not an IP address.")
    if d == "localhost" or d.endswith(BLOCKED_SUFFIXES):
        raise ValueError("That is a local or reserved name, not a public domain.")
    if not DOMAIN_RE.match(d):
        raise ValueError("That does not look like a domain name. Example: yourfirm.in")
    return d


def finding(check: str, status: str, summary: str, detail: str = "", rule_id: str = "",
            scored: bool = False, fix: str = "") -> dict:
    return {"check": check, "status": status, "summary": summary, "detail": detail[:400],
            "rule_id": rule_id, "scored": scored, "fix": fix}


# ----------------------------------------------------------------------- DNS

def dns_txt(name: str) -> list[str]:
    """TXT strings for a name. Empty list if none. Raises LookupError if DNS itself failed."""
    import dns.exception
    import dns.resolver

    resolver = dns.resolver.Resolver()
    resolver.timeout = 3.0
    resolver.lifetime = TIMEOUT
    try:
        answer = resolver.resolve(name, "TXT")
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return []
    except dns.exception.DNSException as exc:  # timeout, no nameservers, etc.
        raise LookupError(str(exc) or exc.__class__.__name__) from exc
    return [b"".join(rr.strings).decode("utf-8", "replace") for rr in answer]


def check_spf(domain: str, txt: Callable[[str], list[str]]) -> dict:
    try:
        records = [r for r in txt(domain) if r.lower().startswith("v=spf1")]
    except LookupError as exc:
        return finding("SPF", "error", "Could not look up DNS just now. Try again later.", str(exc), NES4)
    fix = f"Publish one TXT record on {domain} starting with v=spf1 and ending with -all or ~all. Your email provider gives the exact text."
    if not records:
        return finding("SPF", "fail", "No SPF record found. Anyone can send email that looks like it is from your domain.", "", NES4, True, fix)
    if len(records) > 1:
        return finding("SPF", "fail", "More than one SPF record found. Only one is allowed, so receivers may ignore both.",
                       " | ".join(records), NES4, True, "Merge the SPF records into a single TXT record.")
    record = records[0]
    low = record.lower()
    if "+all" in low:
        return finding("SPF", "fail", "SPF record allows any server to send as your domain (+all).", record, NES4, True, fix)
    if low.rstrip().endswith(("-all", "~all")):
        return finding("SPF", "pass", "SPF record found and ends with a strict or soft fail rule.", record, NES4, True)
    return finding("SPF", "warn", "SPF record found but it does not end with -all or ~all, so it gives little protection.",
                   record, NES4, True, fix)


def check_dmarc(domain: str, txt: Callable[[str], list[str]]) -> dict:
    try:
        records = [r for r in txt(f"_dmarc.{domain}") if r.lower().startswith("v=dmarc1")]
    except LookupError as exc:
        return finding("DMARC", "error", "Could not look up DNS just now. Try again later.", str(exc), NES4)
    fix = (f"Add a TXT record at _dmarc.{domain} starting with v=DMARC1; p=quarantine; and a reporting address. "
           "Start with p=none for two weeks if you are unsure, then tighten.")
    if not records:
        return finding("DMARC", "fail", "No DMARC record found.", "", NES4, True, fix)
    record = records[0]
    match = re.search(r"\bp\s*=\s*([a-z]+)", record.lower())
    policy = match.group(1) if match else ""
    if policy in ("quarantine", "reject"):
        return finding("DMARC", "pass", f"DMARC record found with policy '{policy}'.", record, NES4, True)
    if policy == "none":
        return finding("DMARC", "warn", "DMARC record found but the policy is 'none' (monitor only). Spoofed email is still delivered.",
                       record, NES4, True, f"Change the policy at _dmarc.{domain} to p=quarantine once reports look clean.")
    return finding("DMARC", "fail", "DMARC record found but it has no valid policy.", record, NES4, True, fix)


def check_dkim(domain: str, txt: Callable[[str], list[str]]) -> dict:
    for selector in DKIM_SELECTORS:
        try:
            records = txt(f"{selector}._domainkey.{domain}")
        except LookupError:
            continue
        for record in records:
            if re.search(r"\bp\s*=\s*[A-Za-z0-9+/]{20,}", record):   # an empty p= means the key is revoked
                return finding("DKIM", "pass", f"DKIM key found (selector '{selector}').", record[:80] + "...", NES4, True)
    return finding("DKIM", "info",
                   "No DKIM key found on common selector names. This is not a failure: the selector name cannot be known from outside.",
                   "Selectors tried: " + ", ".join(DKIM_SELECTORS), NES4, False,
                   "Ask your email provider to confirm DKIM signing is switched on.")


# ----------------------------------------------------------------- TLS + HTTP

def public_addresses(domain: str) -> list[str]:
    """Resolve the domain and refuse anything that is not a public internet address."""
    try:
        infos = socket.getaddrinfo(domain, 443, type=socket.SOCK_STREAM)
    except OSError:
        return []
    addresses = sorted({info[4][0] for info in infos})
    for addr in addresses:
        ip = ipaddress.ip_address(addr.split("%")[0])
        if not ip.is_global:
            raise DomainCheckRefused("The domain points to a private or local address, so website checks were skipped.")
    return addresses


def _handshake(domain: str, context: ssl.SSLContext) -> dict:
    with socket.create_connection((domain, 443), timeout=TIMEOUT) as sock:
        with context.wrap_socket(sock, server_hostname=domain) as tls:
            return tls.getpeercert()


def tls_probe(domain: str) -> dict:
    """One TLS handshake on port 443 (repeated once with the bundled CA list if this
    machine's own certificate store cannot build the chain).
    Returns {'ok': bool, 'days_left': int|None, 'error': str}."""
    contexts = [ssl.create_default_context()]
    try:
        import certifi
        contexts.append(ssl.create_default_context(cafile=certifi.where()))
    except ImportError:  # pragma: no cover
        pass
    cert, error = None, ""
    for context in contexts:
        try:
            cert = _handshake(domain, context)
            break
        except ssl.SSLCertVerificationError as exc:
            error = f"certificate problem: {exc.verify_message or exc}"
            if "local issuer" not in error:      # expired, wrong name, self-signed: the site's own fault
                break
        except (OSError, ssl.SSLError) as exc:
            error = f"unreachable: {exc.__class__.__name__}"
            break
    if cert is None:
        return {"ok": False, "days_left": None, "error": error}
    expires = datetime.fromtimestamp(ssl.cert_time_to_seconds(cert["notAfter"]), tz=timezone.utc)
    return {"ok": True, "days_left": (expires - datetime.now(timezone.utc)).days, "error": ""}


def check_tls(domain: str, probe: Callable[[str], dict]) -> dict:
    name = "TLS certificate"
    result = probe(domain)
    if not result["ok"]:
        if result["error"].startswith("unreachable"):
            return finding(name, "info", "No HTTPS website answered on this domain, so there was nothing to check.", result["error"])
        if "local issuer" in result["error"]:
            return finding(name, "warn", "The certificate chain could not be verified from this machine. The website may be "
                                         "missing an intermediate certificate, or this computer's certificate store is out of date.",
                           result["error"], fix="Ask your website host to check that the full certificate chain is installed.")
        return finding(name, "fail", "The website's security certificate is not valid for this domain.", result["error"],
                       fix="Ask your website host to install a valid certificate for this domain.")
    days = result["days_left"]
    if days < 0:
        return finding(name, "fail", "The website's security certificate has expired.", fix="Renew the certificate now.")
    if days < 21:
        return finding(name, "warn", f"Certificate is valid but expires in {days} days.",
                       fix="Renew the certificate, and switch on automatic renewal.")
    return finding(name, "pass", f"Certificate is valid and matches the domain. {days} days to expiry.")


def http_probe(domain: str) -> dict:
    """One GET of the home page (one extra hop allowed to the same site). Returns {'headers': {...}, 'error': str}."""
    import httpx

    allowed = {domain, f"www.{domain}", domain.removeprefix("www.")}
    url = f"https://{domain}/"
    try:
        with httpx.Client(timeout=TIMEOUT, follow_redirects=False, headers={"User-Agent": USER_AGENT}) as client:
            response = client.get(url)
            if response.is_redirect:
                target = httpx.URL(response.headers.get("location", "")) if response.headers.get("location") else None
                if target is not None and target.is_relative_url:
                    target = response.url.join(target)
                if target is not None and target.scheme == "https" and target.host in allowed:
                    response = client.get(target)
    except httpx.HTTPError as exc:
        return {"headers": {}, "error": exc.__class__.__name__}
    return {"headers": {k.lower(): v for k, v in response.headers.items()}, "error": ""}


def check_headers(domain: str, probe: Callable[[str], dict]) -> dict:
    name = "HTTP security headers"
    result = probe(domain)
    if result["error"]:
        return finding(name, "info", "The website did not answer, so headers could not be read.", result["error"])
    present = [HEADER_NAMES[h] for h in SECURITY_HEADERS if h in result["headers"]]
    missing = [HEADER_NAMES[h] for h in SECURITY_HEADERS if h not in result["headers"]]
    detail = f"Present: {', '.join(present) or 'none'}. Missing: {', '.join(missing) or 'none'}."
    if not missing:
        return finding(name, "pass", "All 5 recommended headers are present.", detail)
    return finding(name, "warn", f"{len(present)} of 5 recommended headers present.", detail,
                   fix="Ask your website developer to add the missing headers.")


# ----------------------------------------------------------------------- run

def run_domain_checks(
    domain: str,
    ownership_confirmed: bool,
    *,
    txt: Callable[[str], list[str]] | None = None,
    addresses: Callable[[str], list[str]] | None = None,
    tls: Callable[[str], dict] | None = None,
    http: Callable[[str], dict] | None = None,
) -> list[dict]:
    """Run all passive checks. The keyword arguments let tests replace the network."""
    if not ownership_confirmed:
        raise DomainCheckRefused("Please confirm that you own or control this domain before running the check.")
    domain = normalise_domain(domain)
    txt = txt or dns_txt
    results = [check_spf(domain, txt), check_dmarc(domain, txt), check_dkim(domain, txt)]
    try:
        found = (addresses or public_addresses)(domain)
    except DomainCheckRefused as exc:
        results.append(finding("Website checks", "info", str(exc)))
        return results
    if not found:
        results.append(finding("Website checks", "info", "No website address found for this domain, so website checks were skipped."))
        return results
    results.append(check_tls(domain, tls or tls_probe))
    results.append(check_headers(domain, http or http_probe))
    return results


def nes4_cap(results: list[dict]) -> tuple[str, str] | None:
    """If the DNS check contradicts the questionnaire, cap rule CERTIN-NES.4 at 'Partly'."""
    failed = [r["check"] for r in results if r.get("scored") and r.get("rule_id") == NES4 and r["status"] in ("fail", "warn")]
    if not failed:
        return None
    return ("partial", f"The domain check found a problem with {' and '.join(failed)}, so this cannot be counted as fully in place.")

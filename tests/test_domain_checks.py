"""Passive domain checks, with the network replaced by fakes. No test touches the internet."""
import pytest

from app.health import domain_checks as dc
from app.rules.certin import CERTIN_RULES
from app.scoring import assess


def fake_txt(records: dict[str, list[str]]):
    return lambda name: records.get(name, [])


GOOD_DNS = {
    "firm.in": ["google-site-verification=abc", "v=spf1 include:_spf.mail.example -all"],
    "_dmarc.firm.in": ["v=DMARC1; p=reject; rua=mailto:dmarc@firm.in"],
    "selector1._domainkey.firm.in": ["v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC"],
}
ALL_HEADERS = {h: "x" for h in dc.SECURITY_HEADERS}


def run(dns=GOOD_DNS, addresses=("93.184.216.34",), tls=None, headers=ALL_HEADERS, confirmed=True, domain="firm.in"):
    return dc.run_domain_checks(
        domain, confirmed, txt=fake_txt(dns), addresses=lambda d: list(addresses),
        tls=lambda d: tls or {"ok": True, "days_left": 80, "error": ""},
        http=lambda d: {"headers": headers, "error": ""},
    )


def by_check(results):
    return {r["check"]: r for r in results}


# ------------------------------------------------------------- consent + safety

def test_refuses_without_ownership_confirmation():
    with pytest.raises(dc.DomainCheckRefused):
        run(confirmed=False)


def test_no_lookup_happens_before_confirmation():
    def boom(name):
        raise AssertionError("network touched")
    with pytest.raises(dc.DomainCheckRefused):
        dc.run_domain_checks("firm.in", False, txt=boom, addresses=boom, tls=boom, http=boom)


@pytest.mark.parametrize("bad", ["", "localhost", "10.0.0.1", "192.168.1.1", "::1", "printer.local", "db.internal",
                                 "firm.in:8080", "not a domain", "nodot", "samplelaw.example", "-bad.in"])
def test_rejects_unsafe_or_invalid_targets(bad):
    with pytest.raises(ValueError):
        dc.normalise_domain(bad)


@pytest.mark.parametrize("raw,clean", [("Firm.IN", "firm.in"), ("https://firm.in/contact?x=1", "firm.in"),
                                       ("info@firm.in", "firm.in"), (" www.firm.co.in. ", "www.firm.co.in")])
def test_normalises_what_people_type(raw, clean):
    assert dc.normalise_domain(raw) == clean


def test_private_address_skips_website_checks():
    def private(domain):
        raise dc.DomainCheckRefused("The domain points to a private or local address, so website checks were skipped.")
    results = dc.run_domain_checks("firm.in", True, txt=fake_txt(GOOD_DNS), addresses=private,
                                   tls=lambda d: pytest.fail("tls probed"), http=lambda d: pytest.fail("http probed"))
    assert [r["check"] for r in results] == ["SPF", "DMARC", "DKIM", "Website checks"]


def test_public_addresses_guard_refuses_loopback(monkeypatch):
    monkeypatch.setattr(dc.socket, "getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("127.0.0.1", 443))])
    with pytest.raises(dc.DomainCheckRefused):
        dc.public_addresses("firm.in")
    monkeypatch.setattr(dc.socket, "getaddrinfo", lambda *a, **k: [(2, 1, 6, "", ("10.1.2.3", 443))])
    with pytest.raises(dc.DomainCheckRefused):
        dc.public_addresses("firm.in")


def test_only_passive_probes_exist():
    """The module opens exactly one kind of socket (port 443) and has no scanning loop over ports."""
    import inspect
    source = inspect.getsource(dc)
    assert source.count("create_connection(") == 1 and "(domain, 443)" in source
    assert "range(" not in source


# -------------------------------------------------------------------- results

def test_all_good():
    r = by_check(run())
    assert [r[c]["status"] for c in ("SPF", "DMARC", "DKIM", "TLS certificate", "HTTP security headers")] == ["pass"] * 5
    assert dc.nes4_cap(list(r.values())) is None


@pytest.mark.parametrize("record,status", [
    (["v=spf1 include:x -all"], "pass"), (["v=spf1 include:x ~all"], "pass"),
    (["v=spf1 include:x ?all"], "warn"), (["v=spf1 +all"], "fail"),
    (["v=spf1 a -all", "v=spf1 mx -all"], "fail"), ([], "fail"), (["unrelated=1"], "fail"),
])
def test_spf_grading(record, status):
    assert dc.check_spf("firm.in", fake_txt({"firm.in": record}))["status"] == status


@pytest.mark.parametrize("record,status", [
    (["v=DMARC1; p=reject"], "pass"), (["v=DMARC1; p=quarantine; pct=100"], "pass"),
    (["v=DMARC1; p=none"], "warn"), (["v=DMARC1;"], "fail"), ([], "fail"),
])
def test_dmarc_grading(record, status):
    assert dc.check_dmarc("firm.in", fake_txt({"_dmarc.firm.in": record}))["status"] == status


def test_revoked_dkim_key_is_not_counted_as_found():
    revoked = {f"{sel}._domainkey.firm.in": ["v=DKIM1; p="] for sel in dc.DKIM_SELECTORS}
    assert dc.check_dkim("firm.in", fake_txt(revoked))["status"] == "info"


def test_unverifiable_chain_is_a_warning_not_a_false_failure():
    probe = {"ok": False, "days_left": None, "error": "certificate problem: unable to get local issuer certificate"}
    assert dc.check_tls("firm.in", lambda d: probe)["status"] == "warn"


def test_dkim_not_found_is_information_not_failure():
    r = dc.check_dkim("firm.in", fake_txt({}))
    assert r["status"] == "info" and r["scored"] is False and "not a failure" in r["summary"]


def test_dns_outage_is_reported_as_could_not_check():
    def down(name):
        raise LookupError("timeout")
    assert dc.check_spf("firm.in", down)["status"] == "error"
    assert dc.check_dmarc("firm.in", down)["status"] == "error"
    assert dc.check_spf("firm.in", down)["scored"] is False


@pytest.mark.parametrize("probe,status", [
    ({"ok": True, "days_left": 80, "error": ""}, "pass"),
    ({"ok": True, "days_left": 10, "error": ""}, "warn"),
    ({"ok": True, "days_left": -1, "error": ""}, "fail"),
    ({"ok": False, "days_left": None, "error": "certificate problem: hostname mismatch"}, "fail"),
    ({"ok": False, "days_left": None, "error": "unreachable: TimeoutError"}, "info"),
])
def test_tls_grading(probe, status):
    assert dc.check_tls("firm.in", lambda d: probe)["status"] == status


def test_header_grading():
    two = {"strict-transport-security": "max-age=1", "x-content-type-options": "nosniff"}
    r = dc.check_headers("firm.in", lambda d: {"headers": two, "error": ""})
    assert r["status"] == "warn" and "2 of 5" in r["summary"] and "Content-Security-Policy" in r["detail"]
    assert dc.check_headers("firm.in", lambda d: {"headers": {}, "error": "ConnectError"})["status"] == "info"


def test_tls_and_headers_are_never_scored_or_tied_to_a_rule():
    r = by_check(run(tls={"ok": True, "days_left": -5, "error": ""}, headers={}))
    for name in ("TLS certificate", "HTTP security headers"):
        assert r[name]["scored"] is False and r[name]["rule_id"] == ""


# ------------------------------------------------------- effect on the score

def test_failed_dns_check_caps_the_email_rule_at_partly():
    results = run(dns={"firm.in": ["v=spf1 -all"]})            # no DMARC
    cap = dc.nes4_cap(results)
    assert cap and cap[0] == "partial" and "DMARC" in cap[1]
    answers = {r.id: "yes" for r in CERTIN_RULES}
    capped = assess(CERTIN_RULES, answers, caps={"CERTIN-NES.4": cap})
    assert capped.score < 100 and [g.rule.id for g in capped.gaps] == ["CERTIN-NES.4"]
    assert capped.gaps[0].status == "Partly in place"


def test_cap_never_raises_an_honest_no():
    cap = dc.nes4_cap(run(dns={}))
    answers = {r.id: "yes" for r in CERTIN_RULES} | {"CERTIN-NES.4": "no"}
    assert assess(CERTIN_RULES, answers, caps={"CERTIN-NES.4": cap}).gaps[0].answer == "no"

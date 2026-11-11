"""Cyber Health Check: assessment, stored domain results and the report."""
from __future__ import annotations

import json

from sqlmodel import Session, select

from ..compliance.documents import Doc
from ..compliance.service import get_answers
from ..models import DomainCheck, Firm
from ..rules.certin import APPLICABILITY_NOTE, CERTIN_RULES, DIR, MSME
from ..scoring import Assessment, assess
from .domain_checks import nes4_cap, run_domain_checks

STATUS_LABELS = {"pass": "Pass", "warn": "Needs work", "fail": "Fail", "info": "Info", "error": "Could not check"}


def latest_domain_check(session: Session, firm_id: int) -> DomainCheck | None:
    return session.exec(
        select(DomainCheck).where(DomainCheck.firm_id == firm_id).order_by(DomainCheck.id.desc())
    ).first()


def domain_results(check: DomainCheck | None) -> list[dict]:
    if check is None:
        return []
    try:
        data = json.loads(check.results_json)
    except ValueError:
        return []
    return data if isinstance(data, list) else []


def health_assessment(session: Session, firm: Firm) -> Assessment:
    caps = {}
    cap = nes4_cap(domain_results(latest_domain_check(session, firm.id)))
    if cap:
        caps["CERTIN-NES.4"] = cap
    return assess(CERTIN_RULES, get_answers(session, firm.id, "health"), firm.flags(), caps=caps, order="effort")


def run_and_store(session: Session, firm: Firm, domain: str, ownership_confirmed: bool, **probes) -> DomainCheck:
    """Runs the passive checks (raises DomainCheckRefused / ValueError) and stores the result."""
    results = run_domain_checks(domain, ownership_confirmed, **probes)
    from .domain_checks import normalise_domain
    check = DomainCheck(firm_id=firm.id, domain=normalise_domain(domain), ownership_confirmed=True,
                        results_json=json.dumps(results))
    session.add(check)
    session.commit()
    session.refresh(check)
    return check


def grade(score: int | None) -> str:
    if score is None:
        return "-"
    for limit, letter in ((90, "A"), (75, "B"), (60, "C"), (40, "D")):
        if score >= limit:
            return letter
    return "E"


def build_report(firm: Firm, result: Assessment, check: DomainCheck | None) -> Doc:
    score = "-" if result.score is None else str(result.score)
    blocks: list[tuple] = [
        ("p", f"Cyber Health Check for {firm.name}. Score: {score} / 100 (grade {grade(result.score)}, {result.band}). "
              f"{result.met} of {result.applicable} checks met."),
        ("note", APPLICABILITY_NOTE + " The score and the effort labels are Wolftech's estimate, not a legal finding."),
        ("h2", "1. Fixes, easiest first"),
    ]
    if result.gaps:
        rows = []
        for n, gap in enumerate(result.gaps, 1):
            kind = "Mandatory direction" if gap.rule.kind == "law" else "CERT-In guidance"
            fix = gap.rule.fix + (f" Note: {gap.note}" if gap.note else "")
            rows.append([str(n), gap.rule.title, gap.status, gap.rule.effort, fix,
                         f"{gap.rule.id} - {gap.rule.citation} ({kind})"])
        blocks.append(("table", ["#", "Item", "Status", "Effort", "What to do", "Rule"], rows))
    else:
        blocks.append(("p", "No fixes needed from your answers. Keep evidence for each item."))

    blocks.append(("h2", "2. Domain check (passive)"))
    results = domain_results(check)
    if check and results:
        blocks.append(("p", f"Domain: {check.domain}. Run on {check.run_at:%d %B %Y}. Ownership confirmed by the user. "
                            "Only public DNS records, one TLS handshake and one page request were used."))
        rows = []
        for r in results:
            rule = r.get("rule_id") or "Good practice (no specific CERT-In rule; not scored)"
            rows.append([r["check"], STATUS_LABELS.get(r["status"], r["status"]),
                         r["summary"] + (f" {r['detail']}" if r.get("detail") else ""), r.get("fix") or "-", rule])
        blocks.append(("table", ["Check", "Result", "What we found", "What to do", "Rule"], rows))
    else:
        blocks.append(("p", "Not run. Enter your own domain on the report page to check SPF, DKIM, DMARC, the TLS "
                            "certificate and HTTP security headers."))

    blocks.append(("h2", "3. If you have a cyber incident"))
    blocks.append(("ul", [
        "Report listed incidents to CERT-In within 6 hours of noticing them: incident@cert-in.org.in, phone 1800-11-4949 "
        "(Directions of 28 April 2022, direction (ii)).",
        "Keep system logs for a rolling 180 days in India and give them to CERT-In when asked (direction (iv)).",
        "If personal data is involved, the DPDP breach steps in the Compliance Kit also apply from 13 May 2027.",
    ]))
    sources = [(r.id, f"{r.citation} - {r.source.title}", r.source.url) for r in (g.rule for g in result.gaps)]
    if not sources:
        sources = [("CERT-In", DIR.title, DIR.url), ("CERT-In", MSME.title, MSME.url)]
    return Doc("health-report", "Cyber Health Check Report", "Scored security check.", [], blocks,
               firm_name=firm.name, extra_sources=sources)

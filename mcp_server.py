"""Wolftech Shield Suite - MCP server (MCP Python SDK v2).

Run:  python mcp_server.py          (stdio transport)

Tools: assess_readiness, list_gaps, generate_document, run_health_check.
Reads and writes the same local SQLite file as the web app. Nothing leaves the
machine except the passive domain check, and only when the caller confirms
ownership of the domain.
"""
from __future__ import annotations

from pathlib import Path

from mcp.server.mcpserver import MCPServer
from sqlmodel import Session, select

from app import db
from app.compliance import service as compliance
from app.compliance.documents import DOC_SLUGS, DOCUMENTS, build_document
from app.health import service as health
from app.health.domain_checks import DomainCheckRefused
from app.models import Firm
from app.pdf import render_pdf
from app.rules.base import DISCLAIMER
from app.rules.certin import APPLICABILITY_NOTE
from app.seed import seed_demo

mcp = MCPServer(
    "wolftech-shield-suite",
    instructions=(
        "DPDP Act readiness and CERT-In cyber health tools for small Indian firms, by Wolftech AI Labs. "
        "Every result is a draft for review by a qualified lawyer and is not legal advice. "
        "Leave firm_id empty to use the fictional demo workspace 'Sample Law Associates'."
    ),
)


def _session() -> Session:
    session = Session(db.get_engine())
    seed_demo(session)
    return session


def _firm(session: Session, firm_id: int | None) -> Firm:
    if firm_id is None:
        firm = session.exec(select(Firm).where(Firm.is_demo == True)).first()  # noqa: E712
    else:
        firm = session.get(Firm, firm_id)
    if firm is None:
        raise ValueError(f"No workspace with id {firm_id}. Call assess_readiness with no firm_id to list workspaces.")
    return firm


def _gap(gap) -> dict:
    rule = gap.rule
    out = {
        "rule_id": rule.id, "title": rule.title, "status": gap.status, "priority": gap.priority,
        "requirement": rule.requirement, "citation": rule.citation,
        "source": rule.source.title, "source_url": rule.source.url,
        "fix": rule.fix, "evidence_to_keep": rule.evidence,
    }
    if rule.effort:
        out["effort"] = rule.effort
        out["kind"] = "Mandatory direction" if rule.kind == "law" else "CERT-In baseline guidance"
    if gap.note:
        out["note"] = gap.note
    return out


def _doc_text(doc) -> str:
    lines = [doc.title.upper(), doc.firm_name, doc.disclaimer, ""]
    for block in doc.blocks:
        kind = block[0]
        if kind == "h2":
            lines += ["", block[1], "-" * len(block[1])]
        elif kind in ("p", "note"):
            lines.append(block[1])
        elif kind in ("ul", "ol"):
            lines += [f"  {n}. {item}" if kind == "ol" else f"  - {item}" for n, item in enumerate(block[1], 1)]
        elif kind == "table":
            lines.append(" | ".join(block[1]))
            lines += [" | ".join(row) for row in block[2]]
    lines += ["", "Sources"] + [f"  {rid}: {cite} <{url}>" for rid, cite, url in doc.sources()]
    return "\n".join(lines)


@mcp.tool()
def assess_readiness(firm_id: int | None = None) -> dict:
    """DPDP Act 2023 / DPDP Rules 2025 readiness score (0-100) for a workspace, with the
    legal commencement dates. Leave firm_id empty for the fictional demo law firm."""
    with _session() as session:
        firm = _firm(session, firm_id)
        result = compliance.dpdp_assessment(session, firm)
        workspaces = [{"firm_id": f.id, "name": f.name, "demo": f.is_demo} for f in session.exec(select(Firm)).all()]
        return {
            "firm": firm.name, "firm_id": firm.id, "profile": "Law firm",
            "score": result.score, "band": result.band,
            "rules_applicable": result.applicable, "rules_met": result.met,
            "questions_answered": result.answered, "gaps": len(result.gaps),
            "top_gaps": [g.rule.id + " - " + g.rule.title for g in result.gaps[:5]],
            "deadlines": [{"id": d["id"], "date": d["date"].isoformat(), "title": d["title"],
                           "status": d["label"], "citation": d["citation"]} for d in compliance.deadlines()],
            "workspaces": workspaces,
            "note": "The score is Wolftech's readiness estimate, not a legal finding of compliance.",
            "disclaimer": DISCLAIMER,
        }


@mcp.tool()
def list_gaps(firm_id: int | None = None, limit: int = 10) -> dict:
    """Prioritised DPDP gap list for a workspace. Each gap carries its rule ID, the section or
    rule number, a link to the primary source, and a suggested fix."""
    with _session() as session:
        firm = _firm(session, firm_id)
        result = compliance.dpdp_assessment(session, firm)
        limit = max(1, min(int(limit), 50))
        return {"firm": firm.name, "score": result.score, "total_gaps": len(result.gaps),
                "gaps": [_gap(g) for g in result.gaps[:limit]], "disclaimer": DISCLAIMER}


@mcp.tool()
def generate_document(document: str, firm_id: int | None = None, save_pdf: bool = False) -> dict:
    """Generate a draft compliance document for a workspace. document is one of:
    privacy-notice, consent-text, retention-schedule, breach-response-plan,
    processor-checklist, grievance-procedure. Set save_pdf to also write a branded PDF
    into the local data/exports folder."""
    slug = document.strip().lower().replace(" ", "-").replace("_", "-")
    if slug not in DOC_SLUGS:
        raise ValueError("Unknown document. Choose one of: " + ", ".join(DOC_SLUGS))
    with _session() as session:
        firm = _firm(session, firm_id)
        doc = build_document(slug, firm, compliance.get_inventory(session, firm.id))
        out = {"firm": firm.name, "document": slug, "title": doc.title, "text": _doc_text(doc),
               "rules_cited": doc.rule_ids, "available_documents": [d[0] for d in DOCUMENTS],
               "disclaimer": DISCLAIMER}
        if save_pdf:
            folder = Path("data/exports")
            folder.mkdir(parents=True, exist_ok=True)
            path = folder / f"firm-{firm.id}-{slug}.pdf"
            path.write_bytes(render_pdf(doc, "Compliance Kit"))
            out["pdf_path"] = str(path.resolve())
        return out


@mcp.tool()
def run_health_check(firm_id: int | None = None, domain: str = "",
                     i_confirm_i_own_this_domain: bool = False) -> dict:
    """Cyber Health Check score for a workspace, with fixes ranked easiest first and CERT-In
    citations. If a domain is given AND i_confirm_i_own_this_domain is true, also runs passive
    checks on it (public DNS for SPF/DKIM/DMARC, TLS certificate, HTTP security headers).
    No port scanning or intrusive testing is ever performed."""
    with _session() as session:
        firm = _firm(session, firm_id)
        domain_error = ""
        if domain.strip():
            try:
                health.run_and_store(session, firm, domain, bool(i_confirm_i_own_this_domain))
            except (DomainCheckRefused, ValueError) as exc:
                domain_error = str(exc)
        result = health.health_assessment(session, firm)
        check = health.latest_domain_check(session, firm.id)
        out = {
            "firm": firm.name, "score": result.score, "grade": health.grade(result.score), "band": result.band,
            "checks_applicable": result.applicable, "checks_met": result.met,
            "fixes_easiest_first": [_gap(g) for g in result.gaps],
            "domain_check": {"domain": check.domain, "run_at": check.run_at.isoformat(),
                             "results": health.domain_results(check)} if check else None,
            "applicability_note": APPLICABILITY_NOTE,
            "disclaimer": DISCLAIMER,
        }
        if domain_error:
            out["domain_check_refused"] = domain_error
        return out


if __name__ == "__main__":
    db.init_db()
    mcp.run(transport="stdio")

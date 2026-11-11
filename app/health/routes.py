"""Cyber Health Check pages."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, Response
from sqlmodel import Session

from ..compliance.routes import load_firm
from ..compliance.service import get_answers, save_answers
from ..db import get_session
from ..pdf import render_pdf
from ..rules.certin import APPLICABILITY_NOTE, CERTIN_RULES, UNVERIFIED
from ..web import render
from . import service
from .domain_checks import DomainCheckRefused

router = APIRouter()
Db = Annotated[Session, Depends(get_session)]


@router.get("/firms/{firm_id}/health")
def questionnaire(request: Request, firm_id: int, session: Db):
    firm = load_firm(session, firm_id)
    sections: dict[str, list] = {}
    for r in CERTIN_RULES:
        sections.setdefault(r.section, []).append(r)
    return render(request, "assessment.html", firm=firm, sections=sections,
                  answers=get_answers(session, firm_id, "health"),
                  action=f"/firms/{firm_id}/health", product="health",
                  title="Cyber Health Check",
                  intro="About 10 minutes. One question per CERT-In rule. Not sure? Choose 'Partly'.",
                  rules_url="/rules/certin")


@router.post("/firms/{firm_id}/health")
async def save_questionnaire(request: Request, firm_id: int, session: Db):
    load_firm(session, firm_id)
    form = await request.form()
    save_answers(session, firm_id, "health", {r.id: str(form.get(r.id, "")) for r in CERTIN_RULES if r.id in form})
    return RedirectResponse(f"/firms/{firm_id}/health/report", status_code=303)


def _report_page(request: Request, session: Session, firm, error: str = "", domain: str = "", status_code: int = 200):
    check = service.latest_domain_check(session, firm.id)
    return render(request, "health_report.html", status_code=status_code, firm=firm,
                  result=service.health_assessment(session, firm), check=check,
                  results=service.domain_results(check), labels=service.STATUS_LABELS,
                  grade=service.grade, note=APPLICABILITY_NOTE, error=error,
                  domain=domain or (check.domain if check else ""))


@router.get("/firms/{firm_id}/health/report")
def report(request: Request, firm_id: int, session: Db):
    return _report_page(request, session, load_firm(session, firm_id))


@router.post("/firms/{firm_id}/health/domain")
async def run_domain(request: Request, firm_id: int, session: Db):
    firm = load_firm(session, firm_id)
    form = await request.form()
    domain = str(form.get("domain", ""))[:260]
    confirmed = form.get("ownership") == "yes"
    try:
        service.run_and_store(session, firm, domain, confirmed)
    except (DomainCheckRefused, ValueError) as exc:
        return _report_page(request, session, firm, error=str(exc), domain=domain, status_code=400)
    return RedirectResponse(f"/firms/{firm_id}/health/report#domain", status_code=303)


@router.get("/firms/{firm_id}/health/report.pdf")
def report_pdf(firm_id: int, session: Db):
    firm = load_firm(session, firm_id)
    doc = service.build_report(firm, service.health_assessment(session, firm),
                               service.latest_domain_check(session, firm_id))
    return Response(render_pdf(doc, "Cyber Health Check"), media_type="application/pdf",
                    headers={"Content-Disposition": 'inline; filename="wolftech-cyber-health-report.pdf"'})


@router.get("/rules/certin")
def rules_certin(request: Request):
    return render(request, "rules.html", title="CERT-In rule library",
                  intro="Mandatory Directions of 28 April 2022 and CERT-In's baseline guidance for MSMEs. " + APPLICABILITY_NOTE,
                  rules=CERTIN_RULES, unverified=UNVERIFIED, rulebook="docs/RULEBOOK_CERTIN.md")

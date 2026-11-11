"""Compliance Kit pages. Plain HTML forms, no JavaScript."""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, Response
from sqlmodel import Session

from ..db import get_session
from ..models import Firm
from ..pdf import render_pdf
from ..rules.base import DISCLAIMER
from ..rules.dpdp import DEADLINE_NOTE, DPDP_RULES, PENALTIES, UNVERIFIED
from ..scoring import ANSWER_LABELS, applicable_rules
from ..web import render
from . import service
from .documents import DOC_SLUGS, DOCUMENTS, build_document

router = APIRouter()
Db = Annotated[Session, Depends(get_session)]


def load_firm(session: Session, firm_id: int) -> Firm:
    firm = service.get_firm(session, firm_id)
    if firm is None:
        raise HTTPException(404, "Workspace not found")
    return firm


def _firm_from_form(form, firm: Firm | None = None) -> Firm:
    firm = firm or Firm(name="")
    firm.name = str(form.get("name", "")).strip()[:120]
    firm.city = str(form.get("city", "")).strip()[:80]
    try:
        firm.staff_count = max(0, min(100000, int(form.get("staff_count") or 0)))
    except ValueError:
        firm.staff_count = 0
    firm.contact_name = str(form.get("contact_name", "")).strip()[:120]
    firm.contact_email = str(form.get("contact_email", "")).strip()[:160]
    firm.contact_phone = str(form.get("contact_phone", "")).strip()[:40]
    firm.website = str(form.get("website", "")).strip()[:160]
    firm.has_website = bool(firm.website)
    firm.uses_processors = form.get("uses_processors") == "yes"
    firm.handles_children = form.get("handles_children") == "yes"
    return firm


@router.get("/firms/new")
def new_firm(request: Request):
    return render(request, "firm_form.html", firm=Firm(name=""), is_new=True, error="")


@router.post("/firms")
async def create_firm(request: Request, session: Db):
    form = await request.form()
    firm = _firm_from_form(form)
    if not firm.name:
        return render(request, "firm_form.html", firm=firm, is_new=True,
                      error="Please enter the firm's name.", status_code=400)
    session.add(firm)
    session.commit()
    session.refresh(firm)
    return RedirectResponse(f"/firms/{firm.id}/inventory", status_code=303)


@router.get("/firms/{firm_id}/profile")
def edit_firm(request: Request, firm_id: int, session: Db):
    return render(request, "firm_form.html", firm=load_firm(session, firm_id), is_new=False, error="")


@router.post("/firms/{firm_id}/profile")
async def update_firm(request: Request, firm_id: int, session: Db):
    firm = load_firm(session, firm_id)
    form = await request.form()
    firm = _firm_from_form(form, firm)
    if not firm.name:
        return render(request, "firm_form.html", firm=firm, is_new=False,
                      error="Please enter the firm's name.", status_code=400)
    session.add(firm)
    session.commit()
    return RedirectResponse(f"/firms/{firm_id}", status_code=303)


@router.get("/firms/{firm_id}/inventory")
def inventory(request: Request, firm_id: int, session: Db):
    firm = load_firm(session, firm_id)
    return render(request, "inventory.html", firm=firm, items=service.get_inventory(session, firm_id),
                  categories=service.CATEGORIES, bases=service.BASES)


@router.post("/firms/{firm_id}/inventory")
async def save_inventory(request: Request, firm_id: int, session: Db):
    load_firm(session, firm_id)
    form = await request.form()
    data: dict[str, dict[str, str]] = {}
    for cat in service.CATEGORIES:
        data[cat] = {f: str(form.get(f"{cat}__{f}", "")) for f in
                     ("held", "data_items", "purpose", "basis", "storage", "retention", "shared_with")}
    service.save_inventory(session, firm_id, data)
    return RedirectResponse(f"/firms/{firm_id}/assessment", status_code=303)


@router.get("/firms/{firm_id}/assessment")
def assessment(request: Request, firm_id: int, session: Db):
    firm = load_firm(session, firm_id)
    rules = applicable_rules(DPDP_RULES, firm.flags())
    sections: dict[str, list] = {}
    for r in rules:
        sections.setdefault(r.section, []).append(r)
    return render(request, "assessment.html", firm=firm, sections=sections,
                  answers=service.get_answers(session, firm_id, "dpdp"),
                  action=f"/firms/{firm_id}/assessment", product="dpdp",
                  title="Gap assessment", intro="One question per rule. Answer honestly: 'Partly' is fine.",
                  rules_url="/rules/dpdp")


@router.post("/firms/{firm_id}/assessment")
async def save_assessment(request: Request, firm_id: int, session: Db):
    load_firm(session, firm_id)
    form = await request.form()
    values = {r.id: str(form.get(r.id, "")) for r in DPDP_RULES if r.id in form}
    service.save_answers(session, firm_id, "dpdp", values)
    return RedirectResponse(f"/firms/{firm_id}/gaps", status_code=303)


@router.get("/firms/{firm_id}/gaps")
def gaps(request: Request, firm_id: int, session: Db):
    firm = load_firm(session, firm_id)
    return render(request, "gaps.html", firm=firm, result=service.dpdp_assessment(session, firm),
                  answers=service.get_answers(session, firm_id, "dpdp"), labels=ANSWER_LABELS,
                  deadline=service.next_deadline())


@router.get("/firms/{firm_id}/deadlines")
def deadlines(request: Request, firm_id: int, session: Db):
    firm = load_firm(session, firm_id)
    return render(request, "deadlines.html", firm=firm, deadlines=service.deadlines(),
                  note=DEADLINE_NOTE, penalties=PENALTIES)


@router.get("/firms/{firm_id}/documents")
def documents(request: Request, firm_id: int, session: Db):
    firm = load_firm(session, firm_id)
    return render(request, "documents.html", firm=firm, documents=DOCUMENTS)


@router.get("/firms/{firm_id}/documents/{slug}.pdf")
def document_pdf(firm_id: int, slug: str, session: Db):
    firm = load_firm(session, firm_id)
    if slug not in DOC_SLUGS:
        raise HTTPException(404, "Document not found")
    doc = build_document(slug, firm, service.get_inventory(session, firm_id))
    return Response(render_pdf(doc, "Compliance Kit"), media_type="application/pdf",
                    headers={"Content-Disposition": f'inline; filename="wolftech-{slug}.pdf"'})


@router.get("/firms/{firm_id}/documents/{slug}")
def document(request: Request, firm_id: int, slug: str, session: Db):
    firm = load_firm(session, firm_id)
    if slug not in DOC_SLUGS:
        raise HTTPException(404, "Document not found")
    doc = build_document(slug, firm, service.get_inventory(session, firm_id))
    return render(request, "document.html", firm=firm, doc=doc,
                  pdf_url=f"/firms/{firm_id}/documents/{slug}.pdf", back_url=f"/firms/{firm_id}/documents")


@router.get("/rules/dpdp")
def rules_dpdp(request: Request):
    return render(request, "rules.html", firm=None, title="DPDP rule library",
                  intro="Every scored rule, with its section or rule number and a link to the source.",
                  rules=DPDP_RULES, unverified=UNVERIFIED, disclaimer=DISCLAIMER,
                  rulebook="docs/RULEBOOK_DPDP.md")

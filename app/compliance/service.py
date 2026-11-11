"""Compliance Kit data access and assessment."""
from __future__ import annotations

from datetime import date

from sqlmodel import Session, select

from ..models import Answer, Firm, InventoryItem, now
from ..rules.dpdp import DEADLINES, DPDP_RULES
from ..scoring import Assessment, assess

CATEGORIES: dict[str, dict[str, str]] = {
    "client_files": {
        "label": "Client files",
        "hint": "Matter files, correspondence, pleadings, notes about clients and other parties.",
        "data_items": "Names, addresses, phone numbers, email addresses, case details, financial details",
        "purpose": "Providing legal services to the client",
    },
    "kyc_documents": {
        "label": "KYC documents",
        "hint": "Identity and address proofs collected at client intake.",
        "data_items": "Copies of identity and address documents, PAN, photographs",
        "purpose": "Confirming client identity at intake",
    },
    "employee_data": {
        "label": "Employee data",
        "hint": "Records of partners, associates, staff, interns and job applicants.",
        "data_items": "Names, contact details, bank details, salary, attendance, qualifications",
        "purpose": "Employment, payroll and statutory filings",
    },
    "visitor_records": {
        "label": "Visitor records",
        "hint": "Reception register, visitor app, CCTV footage.",
        "data_items": "Names, phone numbers, time of visit, CCTV images",
        "purpose": "Office security",
    },
    "vendor_contracts": {
        "label": "Vendor contracts",
        "hint": "Contact people at suppliers, contractors and consultants.",
        "data_items": "Names, phone numbers, email addresses, bank details of individual vendors",
        "purpose": "Managing and paying suppliers",
    },
}

BASES: dict[str, str] = {
    "consent": "Consent (Act s.6)",
    "voluntary": "Given voluntarily for a stated purpose (Act s.7(a))",
    "employment": "Employment purposes (Act s.7(i))",
    "legal_duty": "Legal duty or court order (Act s.7(d), s.7(e))",
    "unsure": "Not decided yet",
}


def get_firm(session: Session, firm_id: int) -> Firm | None:
    return session.get(Firm, firm_id)


def get_answers(session: Session, firm_id: int, product: str) -> dict[str, str]:
    rows = session.exec(
        select(Answer).where(Answer.firm_id == firm_id, Answer.product == product)
    ).all()
    return {r.question_id: r.value for r in rows}


def save_answers(session: Session, firm_id: int, product: str, values: dict[str, str]) -> None:
    existing = {
        r.question_id: r
        for r in session.exec(
            select(Answer).where(Answer.firm_id == firm_id, Answer.product == product)
        ).all()
    }
    for qid, value in values.items():
        value = value if value in ("yes", "partial", "no", "na", "") else ""
        row = existing.get(qid)
        if row is None:
            row = Answer(firm_id=firm_id, product=product, question_id=qid)
        row.value = value
        row.updated_at = now()
        session.add(row)
    session.commit()


def get_inventory(session: Session, firm_id: int) -> list[InventoryItem]:
    """Always returns one item per category, in a fixed order (unsaved defaults if missing)."""
    rows = {
        r.category: r
        for r in session.exec(select(InventoryItem).where(InventoryItem.firm_id == firm_id)).all()
    }
    items = []
    for key in CATEGORIES:
        items.append(rows.get(key) or InventoryItem(firm_id=firm_id, category=key))
    return items


def save_inventory(session: Session, firm_id: int, data: dict[str, dict[str, str]]) -> None:
    for item in get_inventory(session, firm_id):
        fields = data.get(item.category)
        if fields is None:
            continue
        item.held = fields.get("held") == "yes"
        item.data_items = fields.get("data_items", "").strip()[:500]
        item.purpose = fields.get("purpose", "").strip()[:500]
        basis = fields.get("basis", "unsure")
        item.basis = basis if basis in BASES else "unsure"
        item.storage = fields.get("storage", "").strip()[:300]
        item.retention = fields.get("retention", "").strip()[:300]
        item.shared_with = fields.get("shared_with", "").strip()[:300]
        session.add(item)
    session.commit()


def dpdp_assessment(session: Session, firm: Firm) -> Assessment:
    return assess(DPDP_RULES, get_answers(session, firm.id, "dpdp"), firm.flags())


def deadlines(today: date | None = None) -> list[dict]:
    today = today or date.today()
    out = []
    for d in DEADLINES:
        days = (d["date"] - today).days
        if days < 0:
            status, label = "past", f"In force since {d['date']:%d %B %Y}"
        elif days == 0:
            status, label = "today", "Starts today"
        else:
            status, label = "upcoming", f"{days} days left"
        out.append({**d, "days": days, "status": status, "label": label})
    return out


def next_deadline(today: date | None = None) -> dict | None:
    upcoming = [d for d in deadlines(today) if d["days"] >= 0]
    return upcoming[-1] if upcoming else None

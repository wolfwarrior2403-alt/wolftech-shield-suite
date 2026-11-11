"""Fictional demo workspace: "Sample Law Associates".

Everything here is invented. No real person, firm or domain is used
(.example is a reserved test domain).
"""
from __future__ import annotations

from sqlmodel import Session, select

from .models import Answer, DomainCheck, Firm, InventoryItem

DEMO_NAME = "Sample Law Associates"

DEMO_INVENTORY = [
    dict(category="client_files", held=True,
         data_items="Names, addresses, phone numbers, email addresses, case details, financial details",
         purpose="Providing legal services to the client", basis="voluntary",
         storage="Cloud document system; paper files scanned at intake",
         retention="Kept indefinitely (no schedule yet)", shared_with="Cloud storage provider (sample)"),
    dict(category="kyc_documents", held=True,
         data_items="Copies of identity and address documents, PAN, photographs",
         purpose="Confirming client identity at intake", basis="consent",
         storage="Shared office drive, scanned copies", retention="Kept with the client file",
         shared_with="Cloud storage provider (sample)"),
    dict(category="employee_data", held=True,
         data_items="Names, contact details, bank details, salary, attendance, qualifications",
         purpose="Employment, payroll and statutory filings", basis="employment",
         storage="Payroll software and HR folder", retention="Kept while employed, then not reviewed",
         shared_with="Payroll service (sample)"),
    dict(category="visitor_records", held=True,
         data_items="Names, phone numbers, time of visit, CCTV images",
         purpose="Office security", basis="voluntary",
         storage="Reception tablet app; CCTV recorder", retention="CCTV 30 days; register never deleted",
         shared_with="Visitor app vendor (sample)"),
    dict(category="vendor_contracts", held=True,
         data_items="Names, phone numbers, email addresses of vendor contacts",
         purpose="Managing and paying suppliers", basis="voluntary",
         storage="Accounts folder", retention="8 years with accounts records (firm practice)", shared_with=""),
]

DEMO_DPDP = {
    "DPDP-L01": "partial", "DPDP-A01": "yes",
    "DPDP-N01": "no", "DPDP-N02": "no", "DPDP-N03": "no",
    "DPDP-K01": "partial", "DPDP-K02": "no", "DPDP-K03": "partial",
    "DPDP-S01": "partial", "DPDP-S02": "yes", "DPDP-S03": "no", "DPDP-S04": "yes", "DPDP-S05": "no",
    "DPDP-A02": "partial",
    "DPDP-B01": "no", "DPDP-B02": "no",
    "DPDP-R01": "no", "DPDP-R02": "partial",
    "DPDP-G01": "partial", "DPDP-G02": "no",
    "DPDP-D01": "no", "DPDP-D02": "partial", "DPDP-D03": "partial", "DPDP-D04": "no",
    "DPDP-P01": "partial", "DPDP-P02": "no", "DPDP-P03": "no",
}

DEMO_HEALTH = {
    "CERTIN-D1": "partial", "CERTIN-D2": "no", "CERTIN-D3": "no", "CERTIN-D4": "no",
    "CERTIN-EAM.1": "partial", "CERTIN-NES.1": "yes", "CERTIN-NES.2": "partial", "CERTIN-NES.3": "na",
    "CERTIN-NES.4": "partial", "CERTIN-EMS.1": "yes", "CERTIN-EMS.2": "yes", "CERTIN-EMS.4": "no",
    "CERTIN-SC.3": "partial", "CERTIN-PM.1": "yes", "CERTIN-PM.2": "no",
    "CERTIN-IM.1": "no", "CERTIN-IM.2": "no", "CERTIN-AT.1": "no",
    "CERTIN-DPBP.1": "yes", "CERTIN-DPBP.2": "partial",
    "CERTIN-RPP.1": "partial", "CERTIN-RPP.2": "yes", "CERTIN-RPP.3": "partial",
    "CERTIN-ACIM.1": "yes", "CERTIN-ACIM.3": "no",
}

# Sample result so the demo works without internet. Clearly labelled as seeded.
DEMO_DOMAIN = "samplelaw.example"
DEMO_DOMAIN_RESULTS = (
    '[{"check": "SPF", "status": "pass", "summary": "SPF record found and ends with a strict or soft fail rule.", '
    '"detail": "v=spf1 include:_spf.mail.example ~all", "rule_id": "CERTIN-NES.4", "scored": true, "fix": ""},'
    ' {"check": "DMARC", "status": "fail", "summary": "No DMARC record found.", "detail": "", '
    '"rule_id": "CERTIN-NES.4", "scored": true, '
    '"fix": "Add a TXT record at _dmarc.samplelaw.example starting with v=DMARC1; p=quarantine; and a reporting address."},'
    ' {"check": "DKIM", "status": "info", "summary": "No DKIM key found on common selector names. This is not a failure: '
    'the selector name cannot be known from outside.", "detail": "", "rule_id": "CERTIN-NES.4", "scored": false, '
    '"fix": "Ask your email provider to confirm DKIM signing is switched on."},'
    ' {"check": "TLS certificate", "status": "pass", "summary": "Certificate is valid and matches the domain. 74 days to expiry.", '
    '"detail": "", "rule_id": "", "scored": false, "fix": ""},'
    ' {"check": "HTTP security headers", "status": "warn", "summary": "2 of 5 recommended headers present.", '
    '"detail": "Present: Strict-Transport-Security, X-Content-Type-Options. Missing: Content-Security-Policy, X-Frame-Options, Referrer-Policy.", '
    '"rule_id": "", "scored": false, "fix": "Ask your website developer to add the missing headers."},'
    ' {"check": "Note", "status": "info", "summary": "Sample result seeded for the demo. It is not a live lookup.", '
    '"detail": "", "rule_id": "", "scored": false, "fix": ""}]'
)


def _populate(session: Session, firm: Firm) -> None:
    for row in DEMO_INVENTORY:
        session.add(InventoryItem(firm_id=firm.id, **row))
    for qid, value in DEMO_DPDP.items():
        session.add(Answer(firm_id=firm.id, product="dpdp", question_id=qid, value=value))
    for qid, value in DEMO_HEALTH.items():
        session.add(Answer(firm_id=firm.id, product="health", question_id=qid, value=value))
    session.add(DomainCheck(firm_id=firm.id, domain=DEMO_DOMAIN, ownership_confirmed=True,
                            results_json=DEMO_DOMAIN_RESULTS))
    session.commit()


def _new_demo_firm() -> Firm:
    return Firm(
        name=DEMO_NAME, profile="law_firm", city="Ahmedabad", staff_count=12,
        contact_name="Office Manager (sample)", contact_email="privacy@samplelaw.example",
        contact_phone="000-0000-0000", website="https://www.samplelaw.example",
        has_website=True, uses_processors=True, handles_children=False, is_demo=True,
    )


def seed_demo(session: Session) -> Firm:
    firm = session.exec(select(Firm).where(Firm.is_demo == True)).first()  # noqa: E712
    if firm:
        return firm
    firm = _new_demo_firm()
    session.add(firm)
    session.commit()
    session.refresh(firm)
    _populate(session, firm)
    return firm


def reset_demo(session: Session) -> Firm:
    firm = session.exec(select(Firm).where(Firm.is_demo == True)).first()  # noqa: E712
    if firm:
        for model in (InventoryItem, Answer, DomainCheck):
            for row in session.exec(select(model).where(model.firm_id == firm.id)).all():
                session.delete(row)
        fresh = _new_demo_firm()
        for field in ("name", "city", "staff_count", "contact_name", "contact_email", "contact_phone",
                      "website", "has_website", "uses_processors", "handles_children"):
            setattr(firm, field, getattr(fresh, field))
        session.add(firm)
        session.commit()
        _populate(session, firm)
        return firm
    return seed_demo(session)

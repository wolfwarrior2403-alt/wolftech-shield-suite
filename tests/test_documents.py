from io import BytesIO

import pytest
from pypdf import PdfReader

from app.compliance import service
from app.compliance.documents import DOC_SLUGS, build_document
from app.pdf import render_pdf
from app.rules.base import DISCLAIMER
from app.rules.dpdp import DPDP_BY_ID


def demo(session):
    firm = service.get_firm(session, 1)
    return firm, service.get_inventory(session, 1)


def flat(doc) -> str:
    out = [doc.title]
    for b in doc.blocks:
        if b[0] == "table":
            out += b[1] + [c for row in b[2] for c in row]
        elif b[0] in ("ul", "ol"):
            out += b[1]
        else:
            out.append(b[1])
    return "\n".join(out)


def pdf_text(data: bytes) -> list[str]:
    return [" ".join(p.extract_text().split()) for p in PdfReader(BytesIO(data)).pages]


def test_there_are_six_documents():
    assert len(DOC_SLUGS) == 6


@pytest.mark.parametrize("slug", DOC_SLUGS)
def test_document_builds_with_disclaimer_firm_and_sources(session, slug):
    firm, inv = demo(session)
    doc = build_document(slug, firm, inv)
    assert doc.disclaimer == DISCLAIMER == "Draft for review by a qualified lawyer. Not legal advice."
    assert doc.firm_name == "Sample Law Associates"
    assert "Sample Law Associates" in flat(doc)
    assert doc.rule_ids and all(r in DPDP_BY_ID for r in doc.rule_ids)
    for _rid, cite, url in doc.sources():
        assert cite and url.startswith("https://")


@pytest.mark.parametrize("slug", DOC_SLUGS)
def test_pdf_export_carries_brand_and_disclaimer_on_every_page(session, slug):
    firm, inv = demo(session)
    data = render_pdf(build_document(slug, firm, inv))
    assert data.startswith(b"%PDF")
    pages = pdf_text(data)
    assert pages
    for text in pages:
        assert DISCLAIMER in text
        assert "WOLFTECH AI LABS" in text


def test_privacy_notice_covers_rule_3_items(session):
    text = flat(build_document("privacy-notice", *demo(session)))
    for needle in ("Client files", "KYC documents", "withdraw", "Data Protection Board",
                   "privacy@samplelaw.example", "90 days"):
        assert needle in text


def test_breach_plan_has_the_verified_timelines(session):
    text = flat(build_document("breach-response-plan", *demo(session)))
    assert "72 hours" in text and "Without delay" in text and "6 hours" in text
    assert "Rules r.7(2)(b)" in text


def test_retention_schedule_does_not_invent_other_law_periods(session):
    doc = build_document("retention-schedule", *demo(session))
    table = next(b for b in doc.blocks if b[0] == "table")
    assert all("Lawyer to confirm" in row[4] for row in table[2])
    assert all("1 year" in row[3] and "r.8(3)" in row[3] for row in table[2])


def test_children_block_only_when_firm_handles_children(session):
    firm, inv = demo(session)
    assert "under 18" not in flat(build_document("consent-text", firm, inv))
    firm.handles_children = True
    doc = build_document("consent-text", firm, inv)
    assert "under 18" in flat(doc) and "DPDP-CH01" in doc.rule_ids


def test_user_text_is_escaped_in_pdf(session):
    firm, inv = demo(session)
    firm.name = "A <b>& B</b> LLP"
    data = render_pdf(build_document("grievance-procedure", firm, inv))
    assert "A <b>& B</b> LLP" in pdf_text(data)[0]


def test_unknown_document_raises(session):
    with pytest.raises(KeyError):
        build_document("nope", *demo(session))

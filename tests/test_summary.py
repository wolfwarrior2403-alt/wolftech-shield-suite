"""One-page summary: same numbers as the full reports, five actions, one PDF page."""
from io import BytesIO

from pypdf import PdfReader

from app.compliance import service
from app.health import service as health_service
from app.models import Firm
from app.summary import DEFAULT_PENALTY, build_summary, penalty_for


def test_penalty_tiers():
    assert penalty_for("DPDP-S03")[0] == "Up to Rs 250 crore"
    assert penalty_for("DPDP-B01")[0] == "Up to Rs 200 crore"
    assert penalty_for("DPDP-CH01")[0] == "Up to Rs 200 crore"
    assert penalty_for("DPDP-K01") == DEFAULT_PENALTY


def test_summary_matches_full_reports(client, session):
    firm = session.get(Firm, 1)
    s = build_summary(session, firm)
    assert s.dpdp.score == service.dpdp_assessment(session, firm).score
    assert s.health.score == health_service.health_assessment(session, firm).score
    assert len(s.actions) == 5
    assert [a.product for a in s.actions] == ["DPDP"] * 3 + ["Cyber"] * 2
    # DPDP actions are the top of the gap list, in the same order
    assert [a.rule_id for a in s.actions[:3]] == [g.rule.id for g in s.dpdp.gaps[:3]]


def test_summary_page(client):
    r = client.get("/firms/1/summary")
    assert r.status_code == 200
    assert "Fix these five first" in r.text
    assert "<script" not in r.text
    assert " style=" not in r.text  # CSP style-src 'self' blocks inline styles


def test_summary_pdf_is_one_page(client):
    r = client.get("/firms/1/summary.pdf")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/pdf"
    assert len(PdfReader(BytesIO(r.content)).pages) == 1


def test_summary_for_new_firm(client):
    r = client.post("/firms", data={"name": "Empty Firm"}, follow_redirects=False)
    firm_url = r.headers["location"].rsplit("/", 1)[0]
    page = client.get(firm_url + "/summary")
    assert page.status_code == 200
    assert "Not started" in page.text
    pdf = client.get(firm_url + "/summary.pdf")
    assert len(PdfReader(BytesIO(pdf.content)).pages) == 1


def test_unknown_firm(client):
    assert client.get("/firms/999/summary").status_code == 404

"""Walks the Compliance Kit journey through the real routes."""
import re

from app.compliance.documents import DOC_SLUGS
from app.rules.base import DISCLAIMER
from app.rules.dpdp import DPDP_RULES

PAGES = ["/", "/firms/new", "/firms/1", "/firms/1/profile", "/firms/1/inventory", "/firms/1/assessment",
         "/firms/1/gaps", "/firms/1/documents", "/firms/1/deadlines", "/rules/dpdp"] + \
        [f"/firms/1/documents/{s}" for s in DOC_SLUGS]


def check_page(client, url):
    r = client.get(url)
    assert r.status_code == 200, url
    assert "Wolftech AI Labs" in r.text, url
    assert DISCLAIMER in r.text, url
    assert "<script" not in r.text.lower(), url
    # nothing is loaded from another site (plain links to sources are fine)
    assert not re.search(r'(src|action)="https?://', r.text), url
    assert not re.search(r'<link[^>]+href="https?://', r.text), url
    assert 'name="viewport"' in r.text, url
    return r


def test_every_page_loads_with_brand_disclaimer_and_no_scripts(client):
    for url in PAGES:
        check_page(client, url)


def test_security_headers(client):
    h = client.get("/").headers
    assert "default-src 'self'" in h["content-security-policy"]
    assert "script-src 'none'" in h["content-security-policy"]
    assert h["x-content-type-options"] == "nosniff"
    assert h["referrer-policy"] == "no-referrer"


def test_demo_workspace_is_fictional_and_mid_range(client):
    r = client.get("/firms/1")
    assert "Sample Law Associates" in r.text and "fictional sample data" in r.text
    score = int(re.search(r'class="num">(\d+)<', client.get("/firms/1/gaps").text).group(1))
    assert 20 <= score <= 60


def test_full_journey_for_a_new_firm(client):
    r = client.post("/firms", data={"name": "Test Chambers", "city": "Surat", "staff_count": "4",
                                    "contact_name": "Privacy Desk", "contact_email": "desk@test.example",
                                    "uses_processors": "yes", "handles_children": "yes"}, follow_redirects=False)
    assert r.status_code == 303
    base = r.headers["location"].rsplit("/", 1)[0]           # /firms/2
    assert "Not started" in client.get(base).text

    inv = {"client_files__held": "yes", "client_files__data_items": "Names", "client_files__purpose": "Legal services",
           "client_files__basis": "consent", "client_files__storage": "Laptop", "client_files__retention": "8 years",
           "client_files__shared_with": "Cloud vendor", "visitor_records__held": "no"}
    r = client.post(f"{base}/inventory", data=inv, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"].endswith("/assessment")

    page = client.get(f"{base}/assessment").text
    for rule in DPDP_RULES:                                  # children + vendor rules are on
        assert f'name="{rule.id}"' in page

    answers = {rule.id: "yes" for rule in DPDP_RULES}
    answers["DPDP-B02"] = "no"
    r = client.post(f"{base}/assessment", data=answers, follow_redirects=True)
    assert r.status_code == 200
    assert "Prioritised gap list (1)" in r.text
    assert "DPDP-B02" in r.text and "Rules r.7(2)" in r.text and "meity.gov.in" in r.text

    notice = client.get(f"{base}/documents/privacy-notice").text
    assert "Test Chambers" in notice and "desk@test.example" in notice and "Cloud vendor" in notice
    assert "Visitor records" not in notice
    for slug in DOC_SLUGS:
        pdf = client.get(f"{base}/documents/{slug}.pdf")
        assert pdf.status_code == 200 and pdf.headers["content-type"] == "application/pdf"
        assert pdf.content.startswith(b"%PDF")


def test_conditional_questions_hidden_when_not_applicable(client):
    page = client.get("/firms/1/assessment").text           # demo firm: no children's data
    assert 'name="DPDP-CH01"' not in page and 'name="DPDP-P01"' in page


def test_gap_links_to_rule_and_source(client):
    page = client.get("/firms/1/gaps").text
    assert 'href="/rules/dpdp#DPDP-B01"' in page
    assert "https://www.meity.gov.in/static/uploads/2025/11/" in page


def test_user_input_is_escaped(client):
    r = client.post("/firms", data={"name": "<img src=x onerror=alert(1)>", "uses_processors": "no",
                                    "handles_children": "no"}, follow_redirects=True)
    assert "<img src=x" not in r.text and "&lt;img src=x" in r.text


def test_validation_and_404s(client):
    assert client.post("/firms", data={"name": "  "}).status_code == 400
    assert client.get("/firms/999").status_code == 404
    assert client.get("/firms/1/documents/nope").status_code == 404
    assert client.get("/firms/1/documents/nope.pdf").status_code == 404


def test_demo_reset_restores_seed(client):
    client.post("/firms/1/assessment", data={r.id: "yes" for r in DPDP_RULES})
    assert "Prioritised gap list (0)" in client.get("/firms/1/gaps").text
    client.post("/demo/reset")
    assert "Prioritised gap list (0)" not in client.get("/firms/1/gaps").text


def test_deadline_page_shows_three_verified_dates(client):
    page = client.get("/firms/1/deadlines").text
    for needle in ("13 November 2025", "13 November 2026", "13 May 2027", "G.S.R. 843(E)", "Rs 250 crore"):
        assert needle in page

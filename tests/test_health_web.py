"""Walks the Cyber Health Check journey through the real routes (network faked)."""
import re
from io import BytesIO

from pypdf import PdfReader

from app.health import domain_checks as dc
from app.rules.base import DISCLAIMER
from app.rules.certin import CERTIN_RULES

from .test_web import check_page


def test_health_pages_load_cleanly(client):
    for url in ("/firms/1/health", "/firms/1/health/report", "/rules/certin"):
        check_page(client, url)


def test_demo_report_shows_score_fixes_and_seeded_domain_result(client):
    page = client.get("/firms/1/health/report").text
    score = int(re.search(r'class="num">(\d+)<', page).group(1))
    assert 25 <= score <= 70
    assert "Fixes, easiest first" in page and "Low effort" in page
    assert "samplelaw.example" in page and "Sample result seeded for the demo" in page
    assert "No port scanning" in page
    assert 'href="https://www.cert-in.org.in/PDF/' in page
    assert "not scored" in page                                   # TLS / headers honesty label


def test_seeded_dmarc_failure_caps_email_rule(client):
    answers = {r.id: "yes" for r in CERTIN_RULES}
    client.post("/firms/1/health", data=answers)
    page = client.get("/firms/1/health/report").text
    assert "Fixes, easiest first (1)" in page
    assert "The domain check found a problem with DMARC" in page


def test_questionnaire_saves_and_ranks(client):
    r = client.post("/firms", data={"name": "Health Test LLP", "uses_processors": "no", "handles_children": "no"},
                    follow_redirects=False)
    base = r.headers["location"].rsplit("/", 1)[0]
    form = client.get(f"{base}/health").text
    for rule in CERTIN_RULES:
        assert f'name="{rule.id}"' in form
    answers = {r.id: "yes" for r in CERTIN_RULES} | {"CERTIN-D4": "no", "CERTIN-RPP.3": "no", "CERTIN-NES.3": "na"}
    page = client.post(f"{base}/health", data=answers, follow_redirects=True).text
    assert "Fixes, easiest first (2)" in page
    assert page.index("Multi-factor authentication") < page.index("Logs kept for 180 days")   # Low before High
    assert "Direction (iv)" in page and "Mandatory" in page
    assert "Cyber health" in client.get(base).text


def test_domain_check_needs_ownership_tick(client):
    r = client.post("/firms/1/health/domain", data={"domain": "firm.in"})
    assert r.status_code == 400 and "confirm that you own or control" in r.text


def test_domain_check_rejects_ip_and_local_names(client):
    for bad in ("192.168.0.1", "localhost", "router.local"):
        r = client.post("/firms/1/health/domain", data={"domain": bad, "ownership": "yes"})
        assert r.status_code == 400, bad


def test_domain_check_runs_and_is_stored(client, monkeypatch):
    dns = {"firm.in": ["v=spf1 include:x -all"], "_dmarc.firm.in": ["v=DMARC1; p=reject"]}
    monkeypatch.setattr(dc, "dns_txt", lambda name: dns.get(name, []))
    monkeypatch.setattr(dc, "public_addresses", lambda d: ["93.184.216.34"])
    monkeypatch.setattr(dc, "tls_probe", lambda d: {"ok": True, "days_left": 60, "error": ""})
    monkeypatch.setattr(dc, "http_probe", lambda d: {"headers": {"strict-transport-security": "x"}, "error": ""})
    r = client.post("/firms/1/health/domain", data={"domain": "https://Firm.in/", "ownership": "yes"},
                    follow_redirects=True)
    assert r.status_code == 200
    assert "Results for firm.in" in r.text and "1 of 5 recommended headers" in r.text
    assert "DMARC record found with policy" in r.text
    assert "Sample result seeded" not in r.text                  # latest result replaces the seeded one


def test_pdf_report(client):
    r = client.get("/firms/1/health/report.pdf")
    assert r.status_code == 200 and r.content.startswith(b"%PDF")
    pages = [" ".join(p.extract_text().split()) for p in PdfReader(BytesIO(r.content)).pages]
    assert all(DISCLAIMER in p and "WOLFTECH AI LABS" in p for p in pages)
    text = " ".join(pages)
    assert "Cyber Health Check Report" in text and "Sample Law Associates" in text
    assert "easiest first" in text and "cert-in.org.in" in text
    assert "6 hours" in text and "samplelaw.example" in text

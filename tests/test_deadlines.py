from datetime import date

from app.compliance.service import deadlines, next_deadline
from app.rules.dpdp import DEADLINES

from .rulebook import DOCS


def test_dates_match_the_gazette_periods():
    by_id = {d["id"]: d["date"] for d in DEADLINES}
    assert by_id["DPDP-C01"] == date(2025, 11, 13)          # date of publication
    assert by_id["DPDP-C02"] == date(2026, 11, 13)          # one year
    assert by_id["DPDP-C03"] == date(2027, 5, 13)           # eighteen months


def test_dates_match_the_rule_book():
    text = (DOCS / "RULEBOOK_DPDP.md").read_text(encoding="utf-8")
    for d in DEADLINES:
        row = next(line for line in text.splitlines() if line.startswith(f"| {d['id']} "))
        assert f"{d['date'].day} {d['date']:%B %Y}" in row
        assert "VERIFIED" in row


def test_every_deadline_is_cited():
    assert all(d["citation"] and d["provisions"] for d in DEADLINES)


def test_day_counts_and_status():
    rows = {d["id"]: d for d in deadlines(date(2026, 11, 11))}
    assert rows["DPDP-C01"]["status"] == "past"
    assert rows["DPDP-C02"]["days"] == 2 and rows["DPDP-C02"]["label"] == "2 days left"
    assert rows["DPDP-C03"]["days"] == 183 and rows["DPDP-C03"]["status"] == "upcoming"


def test_status_on_and_after_the_day():
    assert {d["id"]: d["status"] for d in deadlines(date(2027, 5, 13))}["DPDP-C03"] == "today"
    assert all(d["status"] == "past" for d in deadlines(date(2027, 5, 14)))
    assert next_deadline(date(2027, 5, 14)) is None
    assert next_deadline(date(2026, 1, 1))["id"] == "DPDP-C03"

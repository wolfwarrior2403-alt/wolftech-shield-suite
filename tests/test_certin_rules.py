"""Gate: every rule in Health Check scoring has a test. One case per CERT-In rule."""
import pytest

from app.rules.certin import CERTIN_RULES, DIR, MSME
from app.scoring import assess

IDS = [r.id for r in CERTIN_RULES]


@pytest.mark.parametrize("rule", CERTIN_RULES, ids=IDS)
def test_rule_drives_score_and_fix_list(rule):
    base = {r.id: "yes" for r in CERTIN_RULES}

    missing = assess(CERTIN_RULES, {**base, rule.id: "no"}, order="effort")
    assert [g.rule.id for g in missing.gaps] == [rule.id]
    assert missing.gaps[0].rule.effort in ("Low", "Medium", "High")
    assert missing.gaps[0].rule.source.url.startswith("https://www.cert-in.org.in/")

    partly = assess(CERTIN_RULES, {**base, rule.id: "partial"}, order="effort")
    met = assess(CERTIN_RULES, base, order="effort")
    assert met.gaps == [] and met.score == 100
    assert missing.score < partly.score < 100


def test_directions_are_mandatory_and_guidance_is_labelled():
    for rule in CERTIN_RULES:
        if rule.id in ("CERTIN-D1", "CERTIN-D2", "CERTIN-D3", "CERTIN-D4"):
            assert rule.kind == "law" and rule.source is DIR and rule.weight == 3
            assert rule.citation.startswith("Direction (")
        else:
            assert rule.kind == "guidance" and rule.source is MSME
            assert rule.citation.startswith("Control ")
            assert rule.id.removeprefix("CERTIN-") in rule.citation   # e.g. "RPP.3"


def test_fixes_are_ranked_easiest_first():
    result = assess(CERTIN_RULES, {r.id: "no" for r in CERTIN_RULES}, order="effort")
    efforts = [g.rule.effort for g in result.gaps]
    rank = {"Low": 0, "Medium": 1, "High": 2}
    assert efforts == sorted(efforts, key=rank.get)
    low = [g for g in result.gaps if g.rule.effort == "Low"]
    assert [g.rule.weight for g in low] == sorted((g.rule.weight for g in low), reverse=True)


def test_questionnaire_covers_the_six_required_topics():
    sections = " ".join(sorted({r.section for r in CERTIN_RULES})).lower()
    for topic in ("backups", "passwords and mfa", "patching", "email security", "staff training", "incident plan"):
        assert topic in sections


def test_remote_access_can_be_not_applicable():
    answers = {r.id: "yes" for r in CERTIN_RULES}
    answers["CERTIN-NES.3"] = "na"
    result = assess(CERTIN_RULES, answers)
    assert result.score == 100 and result.applicable == len(CERTIN_RULES) - 1

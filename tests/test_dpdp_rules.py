"""Gate: every rule in scoring has a test. One parametrised case per DPDP rule."""
import pytest

from app.rules.dpdp import DPDP_RULES
from app.scoring import assess

FLAGS = {"uses_processors": True, "handles_children": True}


@pytest.mark.parametrize("rule", DPDP_RULES, ids=[r.id for r in DPDP_RULES])
def test_rule_drives_score_and_gap(rule):
    base = {r.id: "yes" for r in DPDP_RULES}

    missing = assess(DPDP_RULES, {**base, rule.id: "no"}, FLAGS)
    assert [g.rule.id for g in missing.gaps] == [rule.id]
    gap = missing.gaps[0]
    assert gap.status == "Missing"
    assert gap.rule.citation and gap.rule.source.url.startswith("https://")

    partly = assess(DPDP_RULES, {**base, rule.id: "partial"}, FLAGS)
    assert partly.gaps[0].status == "Partly in place"

    met = assess(DPDP_RULES, base, FLAGS)
    assert met.gaps == []
    assert missing.score <= partly.score <= met.score == 100
    assert missing.score < 100


CONDITIONAL = [r for r in DPDP_RULES if r.applies_if]


@pytest.mark.parametrize("rule", CONDITIONAL, ids=[r.id for r in CONDITIONAL])
def test_conditional_rule_ignored_when_flag_off(rule):
    result = assess(DPDP_RULES, {r.id: "yes" for r in DPDP_RULES if r.id != rule.id},
                    {**FLAGS, rule.applies_if: False})
    assert rule.id not in {g.rule.id for g in result.gaps}


def test_weights_follow_the_documented_tiers():
    weights = {r.id: r.weight for r in DPDP_RULES}
    for rid in ("DPDP-S01", "DPDP-S02", "DPDP-S03", "DPDP-S04", "DPDP-S05",
                "DPDP-B01", "DPDP-B02", "DPDP-CH01", "DPDP-CH02"):
        assert weights[rid] == 3, rid
    assert set(weights.values()) <= {1, 2, 3}

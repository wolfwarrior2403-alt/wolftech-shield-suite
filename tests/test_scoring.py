from app.rules.dpdp import DPDP_RULES
from app.scoring import assess, band_for

ALL_ON = {"uses_processors": True, "handles_children": True, "has_website": True}
ALL_OFF = {"uses_processors": False, "handles_children": False}


def answers(value, rules=DPDP_RULES):
    return {r.id: value for r in rules}


def test_all_yes_is_100_with_no_gaps():
    result = assess(DPDP_RULES, answers("yes"), ALL_ON)
    assert result.score == 100 and result.gaps == [] and result.band == "Strong"


def test_all_no_is_zero_and_every_rule_is_a_gap():
    result = assess(DPDP_RULES, answers("no"), ALL_ON)
    assert result.score == 0 and len(result.gaps) == len(DPDP_RULES)
    assert result.band == "Needs attention"


def test_all_partial_is_50():
    assert assess(DPDP_RULES, answers("partial"), ALL_ON).score == 50


def test_unanswered_counts_as_gap():
    result = assess(DPDP_RULES, {}, ALL_ON)
    assert result.score == 0 and result.answered == 0
    assert all(g.status == "Not answered" for g in result.gaps)
    assert not result.complete


def test_conditional_rules_switch_with_profile_flags():
    on = assess(DPDP_RULES, {}, ALL_ON)
    off = assess(DPDP_RULES, {}, ALL_OFF)
    assert on.applicable == len(DPDP_RULES)
    assert on.applicable - off.applicable == 5  # P01-P03, CH01-CH02
    off_ids = {g.rule.id for g in off.gaps}
    assert not any(i.startswith(("DPDP-P", "DPDP-CH")) for i in off_ids)


def test_na_is_excluded_only_where_allowed():
    a = answers("yes")
    a["DPDP-N02"] = "na"       # allowed
    r = assess(DPDP_RULES, a, ALL_ON)
    assert r.score == 100 and r.applicable == len(DPDP_RULES) - 1
    a["DPDP-S01"] = "na"       # not allowed: treated as not answered
    r = assess(DPDP_RULES, a, ALL_ON)
    assert r.score < 100 and "DPDP-S01" in {g.rule.id for g in r.gaps}


def test_weights_change_the_score():
    a = answers("yes")
    a["DPDP-S01"] = "no"   # weight 3
    heavy = assess(DPDP_RULES, a, ALL_ON).score
    a = answers("yes")
    a["DPDP-D04"] = "no"   # weight 1
    light = assess(DPDP_RULES, a, ALL_ON).score
    assert heavy < light < 100


def test_gaps_sorted_by_weight_then_no_before_partial():
    a = answers("yes")
    a.update({"DPDP-D04": "no", "DPDP-S01": "partial", "DPDP-B01": "no", "DPDP-N01": "no"})
    ids = [g.rule.id for g in assess(DPDP_RULES, a, ALL_ON).gaps]
    assert ids == ["DPDP-B01", "DPDP-S01", "DPDP-N01", "DPDP-D04"]


def test_cap_lowers_a_contradicted_answer():
    a = answers("yes")
    r = assess(DPDP_RULES, a, ALL_ON, caps={"DPDP-S01": ("partial", "check failed")})
    assert r.score < 100 and r.gaps[0].note == "check failed"


def test_garbage_answer_is_not_answered():
    r = assess(DPDP_RULES, {"DPDP-S01": "<script>"}, ALL_OFF)
    assert "DPDP-S01" in {g.rule.id for g in r.gaps}


def test_bands():
    assert band_for(None) == "Not started"
    assert band_for(80) == "Strong" and band_for(79) == "Getting there"
    assert band_for(50) == "Getting there" and band_for(49) == "Needs attention"

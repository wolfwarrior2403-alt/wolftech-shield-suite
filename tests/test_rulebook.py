"""Gate: every scored rule is in the rule book, VERIFIED, and cited."""
import pytest

from app.rules.dpdp import DPDP_RULES

from .rulebook import parse, scored_ids

BOOKS = [("RULEBOOK_DPDP.md", "DPDP-", DPDP_RULES)]
try:
    from app.rules.certin import CERTIN_RULES
    BOOKS.append(("RULEBOOK_CERTIN.md", "CERTIN-", CERTIN_RULES))
except ImportError:  # Health Check not built yet
    pass

PARAMS = pytest.mark.parametrize("filename,prefix,rules", BOOKS, ids=[b[0] for b in BOOKS])


@PARAMS
def test_code_and_rulebook_score_the_same_rules(filename, prefix, rules):
    assert {r.id for r in rules} == scored_ids(filename, prefix)


@PARAMS
def test_every_scored_rule_is_verified_and_cited(filename, prefix, rules):
    book = parse(filename, prefix)
    for rule in rules:
        row = book[rule.id]
        assert row["status"].startswith("VERIFIED"), rule.id
        assert "UNVERIFIED" not in row["status"], rule.id
        assert rule.citation.strip(), rule.id
        assert rule.source.url.startswith("https://"), rule.id
        assert rule.source.title, rule.id
        assert rule.question and rule.fix and rule.evidence and rule.requirement, rule.id


@PARAMS
def test_no_unverified_row_is_scored(filename, prefix, rules):
    code_ids = {r.id for r in rules}
    for rid, row in parse(filename, prefix).items():
        if not row["status"].startswith("VERIFIED"):
            assert not row["scored"].startswith("Yes"), rid
            assert rid not in code_ids, rid


@PARAMS
def test_rule_ids_unique(filename, prefix, rules):
    ids = [r.id for r in rules]
    assert len(ids) == len(set(ids))

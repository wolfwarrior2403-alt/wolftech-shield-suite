"""One scoring engine for both products. Method: docs/SPEC.md section 5."""
from __future__ import annotations

from dataclasses import dataclass, field

from .rules.base import Rule

VALUES = {"yes": 1.0, "partial": 0.5, "no": 0.0, "": 0.0}
ANSWER_LABELS = {"yes": "Yes", "partial": "Partly", "no": "No", "na": "Not applicable", "": "Not answered"}
GAP_LABELS = {"no": "Missing", "partial": "Partly in place", "": "Not answered"}
EFFORT_ORDER = {"Low": 0, "Medium": 1, "High": 2, "": 3}


@dataclass
class Gap:
    rule: Rule
    answer: str
    note: str = ""

    @property
    def status(self) -> str:
        return GAP_LABELS.get(self.answer, "Missing")

    @property
    def priority(self) -> str:
        return {3: "High", 2: "Medium", 1: "Low"}.get(self.rule.weight, "Medium")


@dataclass
class Assessment:
    score: int | None
    band: str
    gaps: list[Gap] = field(default_factory=list)
    applicable: int = 0
    answered: int = 0
    met: int = 0

    @property
    def complete(self) -> bool:
        return self.applicable > 0 and self.answered == self.applicable


def band_for(score: int | None) -> str:
    if score is None:
        return "Not started"
    if score >= 80:
        return "Strong"
    if score >= 50:
        return "Getting there"
    return "Needs attention"


def is_applicable(rule: Rule, flags: dict[str, bool]) -> bool:
    return not rule.applies_if or bool(flags.get(rule.applies_if))


def applicable_rules(rules: list[Rule], flags: dict[str, bool]) -> list[Rule]:
    return [r for r in rules if is_applicable(r, flags)]


def assess(
    rules: list[Rule],
    answers: dict[str, str],
    flags: dict[str, bool] | None = None,
    caps: dict[str, tuple[str, str]] | None = None,
    order: str = "weight",
) -> Assessment:
    """Score answers against rules.

    caps: rule_id -> (max answer, note). Used when a technical check contradicts
    a questionnaire answer (for example DNS shows no DMARC record).
    order: "weight" (highest legal exposure first) or "effort" (easiest first).
    """
    flags = flags or {}
    caps = caps or {}
    total = 0.0
    earned = 0.0
    gaps: list[Gap] = []
    applicable = answered = met = 0

    for rule in rules:
        if not is_applicable(rule, flags):
            continue
        value = (answers.get(rule.id) or "").strip().lower()
        if value not in ("yes", "partial", "no", "na", ""):
            value = ""
        if value == "na" and not rule.allow_na:
            value = ""
        if value == "na":
            continue
        note = ""
        if rule.id in caps:
            cap_value, cap_note = caps[rule.id]
            if VALUES[value] > VALUES[cap_value]:
                value, note = cap_value, cap_note
        applicable += 1
        if (answers.get(rule.id) or "").strip():
            answered += 1
        total += rule.weight
        earned += rule.weight * VALUES[value]
        if value == "yes":
            met += 1
        else:
            gaps.append(Gap(rule=rule, answer=value, note=note))

    score = round(100 * earned / total) if total else None
    if order == "effort":
        gaps.sort(key=lambda g: (EFFORT_ORDER.get(g.rule.effort, 3), -g.rule.weight, VALUES[g.answer], g.rule.id))
    else:
        gaps.sort(key=lambda g: (-g.rule.weight, VALUES[g.answer], g.rule.id))
    return Assessment(score=score, band=band_for(score), gaps=gaps,
                      applicable=applicable, answered=answered, met=met)

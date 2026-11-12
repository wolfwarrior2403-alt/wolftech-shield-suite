"""One-page summary for a firm's owner or CEO.

Short on purpose: two scores, the five things to fix first, the next legal
date and what is at stake. Everything is taken from the same deterministic
assessments as the full reports; nothing here is new scoring.
"""
from __future__ import annotations

from dataclasses import dataclass

from sqlmodel import Session

from .compliance import service
from .compliance.documents import Doc
from .health import service as health_service
from .models import Firm
from .scoring import Assessment, Gap

TOP_DPDP = 3
TOP_CYBER = 2

# Highest penalty in the Act's Schedule that a gap in each rule family exposes the firm to.
# Prefix of the DPDP rule ID -> (amount, Schedule item).
PENALTY_BY_PREFIX = {
    "DPDP-S": ("Up to Rs 250 crore", "Schedule item 1"),
    "DPDP-B": ("Up to Rs 200 crore", "Schedule item 2"),
    "DPDP-CH": ("Up to Rs 200 crore", "Schedule item 3"),
}
DEFAULT_PENALTY = ("Up to Rs 50 crore", "Schedule item 7")


def penalty_for(rule_id: str) -> tuple[str, str]:
    for prefix in sorted(PENALTY_BY_PREFIX, key=len, reverse=True):
        if rule_id.startswith(prefix):
            return PENALTY_BY_PREFIX[prefix]
    return DEFAULT_PENALTY


@dataclass
class Action:
    product: str      # "DPDP" or "Cyber"
    title: str
    fix: str
    rule_id: str
    citation: str
    tag: str          # priority (DPDP) or effort (cyber)
    stake: str        # penalty for DPDP, "" for cyber guidance


@dataclass
class Summary:
    firm: Firm
    dpdp: Assessment
    health: Assessment
    actions: list[Action]
    deadline: dict | None
    grade: str

    @property
    def started(self) -> bool:
        return bool(self.dpdp.answered or self.health.answered)


def _dpdp_action(gap: Gap) -> Action:
    amount, item = penalty_for(gap.rule.id)
    return Action("DPDP", gap.rule.title, gap.rule.fix, gap.rule.id, gap.rule.citation,
                  f"{gap.priority} priority", f"{amount} ({item})")


def _cyber_action(gap: Gap) -> Action:
    kind = "Mandatory CERT-In direction" if gap.rule.kind == "law" else "CERT-In guidance"
    return Action("Cyber", gap.rule.title, gap.rule.fix, gap.rule.id, gap.rule.citation,
                  f"{gap.rule.effort or 'Medium'} effort", kind)


def build_summary(session: Session, firm: Firm) -> Summary:
    dpdp = service.dpdp_assessment(session, firm)
    health = health_service.health_assessment(session, firm)
    # DPDP gaps are already ordered by legal exposure; cyber gaps easiest first.
    actions = [_dpdp_action(g) for g in dpdp.gaps[:TOP_DPDP]]
    actions += [_cyber_action(g) for g in health.gaps[:TOP_CYBER]]
    return Summary(firm=firm, dpdp=dpdp, health=health, actions=actions,
                   deadline=service.next_deadline(), grade=health_service.grade(health.score))


def _score(a: Assessment) -> str:
    return "Not started" if not a.answered or a.score is None else f"{a.score} / 100 ({a.band})"


def summary_doc(s: Summary) -> Doc:
    """The same content as the web page, as blocks for the branded PDF writer (fits on one A4 page)."""
    d = s.deadline
    blocks: list[tuple] = [
        ("table", ["", "Score", "What it means"], [
            ["DPDP readiness", _score(s.dpdp),
             f"{s.dpdp.met} of {s.dpdp.applicable} rules met, {len(s.dpdp.gaps)} gaps."],
            ["Cyber health", _score(s.health) + (f", grade {s.grade}" if s.health.answered else ""),
             f"{s.health.met} of {s.health.applicable} checks met, {len(s.health.gaps)} fixes."],
        ]),
    ]
    if d:
        blocks.append(("p", f"Next legal date: {d['date']:%d %B %Y} ({d['label']}). {d['title']}."))
    blocks.append(("h2", "Fix these five first"))
    if s.actions:
        rows = [[str(n), f"{a.title} ({a.product}, {a.rule_id})", a.fix, a.tag, a.stake]
                for n, a in enumerate(s.actions, 1)]
        blocks.append(("table", ["#", "What", "What to do", "Priority", "At stake"], rows))
    else:
        blocks.append(("p", "No open gaps from the answers given. Keep evidence for each rule."))
    blocks.append(("note", "Scores are Wolftech's readiness estimate, weighted by the penalty tiers in the DPDP Act's "
                           "Schedule. 'At stake' is the maximum penalty in the Schedule for that kind of breach, "
                           "not a prediction. The full gap list, cyber report and six draft documents are in the "
                           "workspace."))
    # No sources table: it would push the summary past one page. Rule IDs are in the
    # table, and every citation and link is in the full reports.
    return Doc("summary", "One-page summary", "For the firm's owner.", [], blocks, firm_name=s.firm.name)

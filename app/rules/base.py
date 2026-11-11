"""Shared rule types. Rules are code so they are versioned and tested.

Every scored rule must cite a primary source. See docs/RULEBOOK_*.md.
"""
from __future__ import annotations

from dataclasses import dataclass

DISCLAIMER = "Draft for review by a qualified lawyer. Not legal advice."


@dataclass(frozen=True)
class Source:
    key: str
    title: str
    url: str


@dataclass(frozen=True)
class Rule:
    id: str
    section: str          # questionnaire section heading
    title: str            # short name
    requirement: str      # plain-English requirement
    citation: str         # section / rule / direction number
    source: Source
    weight: int           # Wolftech prioritisation, not law
    question: str         # one question per rule
    evidence: str         # what to keep as proof
    fix: str              # what to do if it is a gap
    help: str = ""
    kind: str = "law"     # "law" or "guidance"
    applies_if: str = ""  # firm flag that must be true, or "" for always
    allow_na: bool = False
    effort: str = ""      # Low / Medium / High (health check only)

    @property
    def anchor(self) -> str:
        return self.id.replace(".", "-")

"""Database tables. See docs/SPEC.md section 3."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


def now() -> datetime:
    return datetime.now(timezone.utc)


class Firm(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    profile: str = "law_firm"
    city: str = ""
    staff_count: int = 0
    contact_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    website: str = ""
    has_website: bool = False
    uses_processors: bool = True
    handles_children: bool = False
    is_demo: bool = False
    created_at: datetime = Field(default_factory=now)

    def flags(self) -> dict[str, bool]:
        return {
            "has_website": self.has_website,
            "uses_processors": self.uses_processors,
            "handles_children": self.handles_children,
        }


class InventoryItem(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    firm_id: int = Field(foreign_key="firm.id", index=True)
    category: str
    held: bool = False
    data_items: str = ""
    purpose: str = ""
    basis: str = "unsure"
    storage: str = ""
    retention: str = ""
    shared_with: str = ""


class Answer(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    firm_id: int = Field(foreign_key="firm.id", index=True)
    product: str  # "dpdp" or "health"
    question_id: str
    value: str = ""
    updated_at: datetime = Field(default_factory=now)


class DomainCheck(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    firm_id: int = Field(foreign_key="firm.id", index=True)
    domain: str
    ownership_confirmed: bool = False
    run_at: datetime = Field(default_factory=now)
    results_json: str = "[]"

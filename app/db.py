"""SQLite engine and session. All data stays in one local file."""
from __future__ import annotations

import os
from pathlib import Path

from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from . import models  # noqa: F401  (registers tables)

_engine = None


def default_url() -> str:
    path = Path(os.environ.get("WOLFTECH_DB", "data/wolftech.db"))
    path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{path.as_posix()}"


def init_db(url: str | None = None):
    """Create the engine and tables. Use url='sqlite://' for an in-memory test database."""
    global _engine
    url = url or default_url()
    kwargs = {"connect_args": {"check_same_thread": False}}
    if url == "sqlite://":
        kwargs["poolclass"] = StaticPool
    _engine = create_engine(url, **kwargs)
    SQLModel.metadata.create_all(_engine)
    return _engine


def get_engine():
    if _engine is None:
        init_db()
    return _engine


def get_session():
    with Session(get_engine()) as session:
        yield session

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture()
def client():
    """Fresh in-memory database with the fictional demo workspace seeded (firm id 1)."""
    app = create_app("sqlite://")
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def session(client):
    from sqlmodel import Session

    from app import db
    with Session(db.get_engine()) as s:
        yield s

"""Firm types: same rules for everyone, wording and pre-filled answers follow the type."""
from app.compliance.documents import build_document
from app.compliance.service import get_inventory
from app.models import Firm
from app.profiles import PROFILES


def _new(client, profile):
    r = client.post("/firms", data={"name": f"Test {profile}", "profile": profile}, follow_redirects=False)
    return r.headers["location"].rsplit("/", 1)[0]


def test_every_profile_creates_a_workspace(client):
    for key, p in PROFILES.items():
        url = _new(client, key)
        assert p["label"] in client.get(url).text
        inv = client.get(url + "/inventory").text
        assert p["client_files"]["label"] in inv


def test_unknown_profile_falls_back(client):
    url = _new(client, "rocket_company")
    assert "Law firm" in client.get(url).text


def test_clinic_documents_say_patient_records(client, session):
    url = _new(client, "clinic")
    firm_id = int(url.rsplit("/", 1)[1])
    client.post(url + "/inventory", data={"client_files__held": "yes", "client_files__data_items": "x",
                                          "client_files__purpose": "treatment"})
    firm = session.get(Firm, firm_id)
    doc = build_document("privacy-notice", firm, get_inventory(session, firm_id))
    cells = [c for b in doc.blocks if b[0] == "table" for row in b[2] for c in row]
    assert "Patient records" in cells
    assert "Client files" not in cells


def test_profile_select_on_form(client):
    page = client.get("/firms/new").text
    for p in PROFILES.values():
        assert p["label"] in page

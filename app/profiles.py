"""Firm types. The rules are the same for every firm under the DPDP Act and the
CERT-In Directions; the type only changes wording and the typical answers we
pre-fill in the data inventory."""
from __future__ import annotations

PROFILES: dict[str, dict] = {
    "law_firm": {
        "label": "Law firm",
        "people": "Partners, associates and staff",
        "children_hint": "For example family, guardianship or juvenile matters.",
        "client_files": {
            "label": "Client files",
            "hint": "Matter files, correspondence, pleadings, notes about clients and other parties.",
            "data_items": "Names, addresses, phone numbers, email addresses, case details, financial details",
            "purpose": "Providing legal services to the client",
        },
    },
    "ca_firm": {
        "label": "CA / accounting firm",
        "people": "Partners, CAs, article assistants and staff",
        "children_hint": "For example minors' PAN, tax or investment records.",
        "client_files": {
            "label": "Client files",
            "hint": "Books of account, ITR and GST working papers, audit files, bank statements, client correspondence.",
            "data_items": "Names, PAN, Aadhaar, addresses, phone numbers, bank details, income and tax details",
            "purpose": "Accounting, audit, tax filing and advisory services",
        },
    },
    "clinic": {
        "label": "Clinic / healthcare",
        "people": "Doctors, nurses and staff",
        "children_hint": "For example patients under 18.",
        "client_files": {
            "label": "Patient records",
            "hint": "Case papers, prescriptions, test reports, appointment and billing records.",
            "data_items": "Names, ages, phone numbers, addresses, medical history, test reports, billing details",
            "purpose": "Treating patients and keeping medical records",
        },
    },
    "other": {
        "label": "Other business",
        "people": "Owners and staff",
        "children_hint": "For example students, customers or members under 18.",
        "client_files": {
            "label": "Customer records",
            "hint": "Customer accounts, orders, enquiries, invoices and correspondence.",
            "data_items": "Names, phone numbers, email addresses, addresses, order and payment details",
            "purpose": "Serving customers and running the business",
        },
    },
}
DEFAULT_PROFILE = "law_firm"


def profile(key: str | None) -> dict:
    return PROFILES.get(key or DEFAULT_PROFILE, PROFILES[DEFAULT_PROFILE])


def label(key: str | None) -> str:
    return profile(key)["label"]


def categories(key: str | None) -> dict[str, dict[str, str]]:
    """Inventory categories with the first one worded for this kind of firm."""
    from .compliance.service import CATEGORIES
    cats = {k: dict(v) for k, v in CATEGORIES.items()}
    cats["client_files"] = dict(profile(key)["client_files"])
    return cats

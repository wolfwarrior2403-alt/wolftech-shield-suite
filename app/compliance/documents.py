"""Draft document builder. Each document is a list of simple blocks that the
HTML template and the PDF writer both understand.

Text in [square brackets] is for the firm or its lawyer to complete.
No statutory retention period or regulator address is invented here.
"""
from __future__ import annotations

from contextvars import ContextVar

from dataclasses import dataclass, field
from datetime import date

from ..models import Firm, InventoryItem
from ..rules.base import DISCLAIMER
from ..rules.dpdp import DPDP_BY_ID
from .service import BASES, CATEGORIES


@dataclass
class Doc:
    slug: str
    title: str
    summary: str
    rule_ids: list[str]
    blocks: list[tuple] = field(default_factory=list)
    firm_name: str = ""
    generated_on: date = field(default_factory=date.today)
    disclaimer: str = DISCLAIMER
    extra_sources: list[tuple[str, str, str]] = field(default_factory=list)  # (id, citation, url)

    def sources(self) -> list[tuple[str, str, str]]:
        out = []
        for rid in self.rule_ids:
            rule = DPDP_BY_ID.get(rid)
            if rule:
                out.append((rule.id, f"{rule.citation} - {rule.source.title}", rule.source.url))
        return out + self.extra_sources


DOCUMENTS = [
    ("privacy-notice", "Privacy Notice", "What you tell people when you collect their data."),
    ("consent-text", "Consent Text", "Wording for asking permission, purpose by purpose."),
    ("retention-schedule", "Data Retention Schedule", "How long each record type is kept and when it is deleted."),
    ("breach-response-plan", "Breach Response Plan", "Who does what, and by when, if data is exposed or lost."),
    ("processor-checklist", "Processor Contract Checklist", "What every vendor contract should say."),
    ("grievance-procedure", "Grievance Procedure", "How complaints and data requests are handled."),
]
DOC_SLUGS = [d[0] for d in DOCUMENTS]


def _contact(firm: Firm) -> str:
    parts = [firm.contact_name or "[Name or role of privacy contact]",
             firm.contact_email or "[email]", firm.contact_phone or "[phone]"]
    return ", ".join(parts)


def _held(inventory: list[InventoryItem]) -> list[InventoryItem]:
    return [i for i in inventory if i.held]


_PROFILE: ContextVar[str | None] = ContextVar("wolftech_profile", default=None)


def _label(item: InventoryItem) -> str:
    if item.category == "client_files":
        from ..profiles import profile
        return profile(_PROFILE.get())["client_files"]["label"]
    return CATEGORIES[item.category]["label"]


def _or(value: str, placeholder: str) -> str:
    return value.strip() if value and value.strip() else placeholder


def build_document(slug: str, firm: Firm, inventory: list[InventoryItem]) -> Doc:
    builders = {
        "privacy-notice": _privacy_notice,
        "consent-text": _consent_text,
        "retention-schedule": _retention_schedule,
        "breach-response-plan": _breach_plan,
        "processor-checklist": _processor_checklist,
        "grievance-procedure": _grievance_procedure,
    }
    if slug not in builders:
        raise KeyError(slug)
    token = _PROFILE.set(firm.profile)
    try:
        doc = builders[slug](firm, inventory)
    finally:
        _PROFILE.reset(token)
    doc.firm_name = firm.name
    return doc


# ---------------------------------------------------------------- privacy notice

def _privacy_notice(firm: Firm, inventory: list[InventoryItem]) -> Doc:
    held = _held(inventory)
    rows = [[_label(i), _or(i.data_items, "[list the personal data]"),
             _or(i.purpose, "[state the purpose]"), BASES.get(i.basis, BASES["unsure"])] for i in held]
    if not rows:
        rows = [["[Record type]", "[Personal data]", "[Purpose]", "[Ground]"]]
    shared = sorted({i.shared_with.strip() for i in held if i.shared_with.strip()})
    b: list[tuple] = [
        ("p", f"This notice explains how {firm.name} uses your personal data. It is written to be "
              "read on its own. Please read it before you give us your data or your consent."),
        ("h2", "1. What personal data we collect and why"),
        ("table", ["Record", "Personal data we hold", "Why we use it and the service it enables", "Our ground"], rows),
        ("p", "We use your personal data only for the purposes listed above. We collect only what "
              "is needed for those purposes."),
        ("h2", "2. Who we share it with"),
        ("p", "We share personal data only where needed for the purposes above, with: "
              + ("; ".join(shared) if shared else "[list vendors and other recipients, or state 'no one']") + "."),
        ("h2", "3. How to withdraw your consent"),
        ("p", f"Where we rely on your consent, you can withdraw it at any time by writing to "
              f"{firm.contact_email or '[email]'}"
              + (f" or through {firm.website}" if firm.website else "")
              + ". Withdrawing is as easy as giving consent: one email is enough. We will stop using "
                "your data for that purpose within a reasonable time, unless a law requires or allows "
                "us to continue. Withdrawal does not affect what was done before it."),
        ("h2", "4. Your rights"),
        ("ul", [
            "Ask for a summary of the personal data we hold about you and what we do with it.",
            "Ask who we have shared your personal data with.",
            "Ask us to correct, complete or update your personal data.",
            "Ask us to erase your personal data, unless we still need it for the stated purpose or must keep it by law.",
            "Nominate another person to use these rights for you if you die or become incapacitated.",
            "Have your complaint handled through our grievance process.",
        ]),
        ("p", f"To use any right, write to {firm.contact_email or '[email]'} and give your full name and "
              "your client or file reference number (or the email address or mobile number you gave us) "
              "so that we can identify you."),
        ("h2", "5. Questions and complaints"),
        ("p", f"Contact for questions about your personal data: {_contact(firm)}."),
        ("p", "We will respond to a grievance within [30] days, and in any case within 90 days. If you "
              "are not satisfied after using our grievance process, you may complain to the Data "
              "Protection Board of India. [Lawyer to add the Board's current complaint channel.]"),
        ("h2", "6. Language"),
        ("p", "You may ask for this notice in English or in [Gujarati / Hindi / other language listed "
              "in the Eighth Schedule to the Constitution]."),
        ("note", "Fields in [square brackets] must be completed. The 30-day figure is the firm's own "
                 "choice; the legal limit is 90 days."),
    ]
    return Doc("privacy-notice", "Privacy Notice",
               "Give this with or before any request for consent.",
               ["DPDP-N01", "DPDP-N03", "DPDP-K02", "DPDP-G01", "DPDP-G02", "DPDP-D01", "DPDP-D02", "DPDP-D03", "DPDP-D04"], b)


# ------------------------------------------------------------------ consent text

def _consent_text(firm: Firm, inventory: list[InventoryItem]) -> Doc:
    consent_items = [i for i in _held(inventory) if i.basis in ("consent", "unsure")]
    purposes = [f"[  ] I agree to {firm.name} using my {_or(i.data_items, '[personal data]').lower()} "
                f"for: {_or(i.purpose, '[purpose]').lower()}. ({_label(i)})" for i in consent_items]
    if not purposes:
        purposes = [f"[  ] I agree to {firm.name} using my [personal data] for: [specific purpose]."]
    b: list[tuple] = [
        ("p", "Use this wording on your client intake form or engagement letter. Give the Privacy "
              "Notice with it or before it. Each box must be left empty for the person to tick; "
              "do not pre-tick boxes or combine purposes."),
        ("h2", "Consent wording"),
        ("p", f"I have read the Privacy Notice of {firm.name} dated [date / version]."),
        ("ul", purposes),
        ("p", "I understand that:"),
        ("ul", [
            "I am giving this consent freely. Each box is separate and I may leave any box empty.",
            f"I can withdraw any consent at any time by writing to {firm.contact_email or '[email]'}. "
            "Withdrawing is as easy as giving consent.",
            "My consent covers only the personal data needed for the purposes I have ticked.",
            f"I can contact {_contact(firm)} with any question about my personal data.",
            "I may ask for this text in English or in [Gujarati / Hindi / other Eighth Schedule language].",
        ]),
        ("p", "Name: ____________________   Signature: ____________________   Date: ____________"),
        ("h2", "Record to keep"),
        ("ul", [
            "The signed or electronically accepted form.",
            "The version and date of the Privacy Notice that was given.",
            "The date and method of consent, and any later withdrawal.",
        ]),
    ]
    rules = ["DPDP-K01", "DPDP-K02", "DPDP-K03", "DPDP-N01", "DPDP-N03"]
    if firm.handles_children:
        b += [
            ("h2", "If the person is under 18"),
            ("p", "I am the parent or lawful guardian of [child's name]. I am over 18. I consent to the "
                  "purposes ticked above on the child's behalf."),
            ("p", "Parent or guardian name: ____________________   Signature: ____________________"),
            ("p", "Identity and age of parent checked by: ____________   Document seen: ____________   Date: ________"),
            ("note", "Parental consent must be verifiable and the firm must check that the person is an identifiable adult."),
        ]
        rules += ["DPDP-CH01", "DPDP-CH02"]
    b.append(("note", "Not every use needs consent. Data a person gives voluntarily for a stated purpose, "
                      "employment data and data needed for a legal duty may rest on a legitimate use under "
                      "Act s.7. Your lawyer should confirm which ground applies to each record type."))
    return Doc("consent-text", "Consent Text",
               "Ask separately for each purpose. Keep proof.", rules, b)


# ------------------------------------------------------------ retention schedule

def _retention_schedule(firm: Firm, inventory: list[InventoryItem]) -> Doc:
    rows = []
    for i in inventory:
        if not i.held:
            continue
        rows.append([
            _label(i),
            _or(i.storage, "[where kept]"),
            _or(i.retention, "[not set]"),
            "At least 1 year from the date of processing (Rules r.8(3))",
            "[Lawyer to confirm any longer period required by other law]",
            "Review yearly; erase when no longer needed and no law requires retention",
        ])
    if not rows:
        rows = [["[Record type]", "[Where kept]", "[Current practice]",
                 "At least 1 year from the date of processing (Rules r.8(3))", "[Lawyer to confirm]", "[Action]"]]
    b: list[tuple] = [
        ("p", f"This schedule sets out how long {firm.name} keeps personal data and when it is erased."),
        ("h2", "1. Rules we follow"),
        ("ul", [
            "We erase personal data when the person withdraws consent or when the purpose is no longer "
            "served, whichever is earlier, unless a law requires us to keep it (Act s.8(7)).",
            "We keep personal data, associated traffic data and logs of processing for at least one year "
            "from the date of processing, and then erase them unless another law requires longer "
            "retention (Rules r.8(3)).",
            "We keep access logs for at least one year so that a breach can be detected and investigated (Rules r.6(1)(e)).",
            "We instruct our vendors to follow the same periods and to erase data when we tell them to (Act s.8(7)(b)).",
        ]),
        ("h2", "2. Schedule"),
        ("table", ["Record", "Where kept", "Current practice (from your inventory)", "DPDP minimum",
                   "Other law", "Action"], rows),
        ("h2", "3. Yearly deletion review"),
        ("ol", [
            "Each [April], the privacy contact lists records past their retention period.",
            "A partner confirms no law, live matter or dispute requires them to be kept.",
            "Records are erased from systems, backups (at next rotation) and vendor systems.",
            "The deletion is logged: what, when, by whom, approved by whom.",
        ]),
        ("note", "This kit does not state retention periods under other laws (for example professional "
                 "conduct, tax or limitation rules). Your lawyer must fill in the 'Other law' column."),
    ]
    return Doc("retention-schedule", "Data Retention Schedule",
               "How long each record type is kept.", ["DPDP-R01", "DPDP-R02", "DPDP-S05", "DPDP-P03"], b)


# ---------------------------------------------------------- breach response plan

def _breach_plan(firm: Firm, inventory: list[InventoryItem]) -> Doc:
    b: list[tuple] = [
        ("p", f"This plan tells everyone at {firm.name} what to do if personal data is exposed, lost, "
              "altered or made unavailable. A personal data breach includes unauthorised access and "
              "accidental disclosure, loss or destruction (Act s.2(u))."),
        ("h2", "1. People"),
        ("table", ["Role", "Person", "Contact"], [
            ["Breach lead", firm.contact_name or "[name]", f"{firm.contact_email or '[email]'} / {firm.contact_phone or '[phone]'}"],
            ["Deputy", "[name]", "[phone]"],
            ["IT support", "[vendor or person]", "[phone]"],
            ["Reviewing lawyer", "[name]", "[phone]"],
        ]),
        ("h2", "2. Timeline"),
        ("table", ["When", "What", "Source"], [
            ["Immediately", "Anyone who suspects a breach tells the breach lead. Contain it: change passwords, "
                            "isolate the device, stop the wrong email chain. Start an incident log with times.", "Internal step"],
            ["Within 6 hours of noticing", "If it is a cyber incident of a type listed by CERT-In (for example "
                                           "unauthorised access, ransomware, phishing, data breach, data leak), report to "
                                           "CERT-In: incident@cert-in.org.in, phone 1800-11-4949.", "CERT-In Directions 28 April 2022, direction (ii)"],
            ["Without delay", "First intimation to the Data Protection Board: description of the breach, its "
                              "nature, extent, timing, location and likely impact.", "Rules r.7(2)(a)"],
            ["Without delay", "Tell each affected person, in plain words, through their registered contact.", "Rules r.7(1)"],
            ["Within 72 hours of becoming aware", "Detailed report to the Board (see section 4). A longer period needs "
                                                  "the Board's permission on a written request.", "Rules r.7(2)(b)"],
            ["Afterwards", "Fix the cause, record lessons, update this plan.", "Internal step"],
        ]),
        ("h2", "3. Message to affected people (template)"),
        ("p", "Subject: Important notice about your personal data"),
        ("ol", [
            "What happened: [description of the breach, its nature, extent and when it occurred].",
            "What it may mean for you: [likely consequences relevant to the person].",
            "What we are doing: [measures taken and under way to reduce the risk].",
            "What you can do: [safety measures the person can take, for example change passwords, watch for suspicious calls].",
            f"Who to contact: {_contact(firm)}.",
        ]),
        ("h2", "4. Report to the Data Protection Board within 72 hours"),
        ("ol", [
            "Updated and detailed information about the breach.",
            "The broad facts: events, circumstances and reasons leading to the breach.",
            "Measures implemented or proposed to mitigate risk.",
            "Any findings about the person who caused the breach.",
            "Remedial measures taken to prevent recurrence.",
            "A report on the intimations given to affected people.",
        ]),
        ("h2", "5. Keep ready at all times"),
        ("ul", [
            "An exportable list of client and staff contact details.",
            "Access logs for at least one year (Rules r.6(1)(e)) and system logs for 180 days (CERT-In direction (iv)).",
            "Tested backups.",
            "[Lawyer to add the Board's current intimation channel and form.]",
        ]),
        ("note", "Penalty for failing to notify the Board or affected people of a breach: up to Rs 200 crore (Act Schedule, item 2)."),
    ]
    return Doc("breach-response-plan", "Breach Response Plan",
               "Who does what, and by when.", ["DPDP-B01", "DPDP-B02", "DPDP-S05"], b,
               extra_sources=[("CERTIN-D2", "Direction (ii) - CERT-In Directions No. 20(3)/2022-CERT-In, 28 April 2022",
                               "https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf")])


# ---------------------------------------------------------- processor checklist

def _processor_checklist(firm: Firm, inventory: list[InventoryItem]) -> Doc:
    vendors = sorted({i.shared_with.strip() for i in _held(inventory) if i.shared_with.strip()})
    vendor_rows = [[v, "[contract in place? yes / no]", "[security clause? yes / no]", "[renewal date]"] for v in vendors] \
        or [["[Vendor]", "[yes / no]", "[yes / no]", "[date]"]]
    b: list[tuple] = [
        ("p", f"A Data Processor is anyone who handles personal data on behalf of {firm.name}: cloud "
              "storage, email hosting, payroll, IT support, e-signature, document management, scanning "
              "and shredding services. The firm stays responsible for what they do (Act s.8(1))."),
        ("h2", "1. Your vendors (from your inventory)"),
        ("table", ["Vendor / recipient", "Written contract", "Security clause", "Renewal"], vendor_rows),
        ("h2", "2. Checklist for each contract"),
        ("table", ["#", "The contract should say", "Why", "Tick"], [
            ["1", "There is a valid written contract (or accepted written terms) covering the processing.", "Act s.8(2)", "[  ]"],
            ["2", "The vendor processes personal data only on the firm's instructions and only for the firm's purposes.", "Act s.8(1)", "[  ]"],
            ["3", "The vendor takes reasonable security safeguards to prevent a personal data breach, such as "
                  "encryption, access control, logging and backups.", "Rules r.6(1)(f); Act s.8(5)", "[  ]"],
            ["4", "The vendor tells the firm about any personal data breach without delay, with enough detail "
                  "for the firm to notify the Board and affected people within 72 hours.", "Rules r.7 (firm's duty)", "[  ]"],
            ["5", "The vendor stops processing when the firm says consent has been withdrawn.", "Act s.6(6)", "[  ]"],
            ["6", "The vendor erases personal data when the firm instructs, and at the end of the contract.", "Act s.8(7)(b)", "[  ]"],
            ["7", "The vendor keeps the data and processing logs for at least one year unless told otherwise by law.", "Rules r.8(3), Illustration Case 2", "[  ]"],
            ["8", "The vendor helps the firm answer access, correction and erasure requests.", "Act s.11, s.12 (firm's duty)", "[  ]"],
            ["9", "The vendor says where the data is stored and does not move it outside India without telling the firm.", "Act s.16; Rules r.15", "[  ]"],
        ]),
        ("note", "Items 4, 8 and 9 are practical clauses that help the firm meet its own duties. The Act "
                 "and Rules place those duties on the firm; they do not prescribe this exact contract wording."),
    ]
    return Doc("processor-checklist", "Processor Contract Checklist",
               "What every vendor contract should say.", ["DPDP-P01", "DPDP-P02", "DPDP-P03"], b)


# ----------------------------------------------------------- grievance procedure

def _grievance_procedure(firm: Firm, inventory: list[InventoryItem]) -> Doc:
    b: list[tuple] = [
        ("p", f"This procedure explains how {firm.name} handles questions, requests and complaints "
              "about personal data."),
        ("h2", "1. How to reach us"),
        ("p", f"Privacy contact: {_contact(firm)}."
              + (f" Website: {firm.website}." if firm.website else "")),
        ("p", "Please give your full name and your client or file reference number (or the email "
              "address or mobile number you gave us) so that we can identify you."),
        ("h2", "2. What you can ask for"),
        ("ul", [
            "A summary of your personal data and what we do with it (Act s.11).",
            "Who we shared it with (Act s.11).",
            "Correction, completion or updating of your data (Act s.12).",
            "Erasure of your data, unless it is still needed or must be kept by law (Act s.12).",
            "To nominate someone to act for you (Act s.14).",
            "To make a complaint about how we handled your data or your request (Act s.13).",
        ]),
        ("h2", "3. What we do"),
        ("table", ["Step", "Action", "Time"], [
            ["1", "Log the request in the grievance register and acknowledge it.", "[3 working days] (firm's choice)"],
            ["2", "Confirm the person's identity using the identifier they gave.", "[7 days] (firm's choice)"],
            ["3", "Privacy contact investigates and prepares the reply; a partner approves.", "[21 days] (firm's choice)"],
            ["4", "Send the reply, including the privacy contact's details.", "[30 days] and never more than 90 days (Rules r.14(3))"],
            ["5", "Record the outcome and any fix made.", "Same day"],
        ]),
        ("h2", "4. If you are not satisfied"),
        ("p", "You may ask a partner of the firm to review the reply. After you have used this process, "
              "you may complain to the Data Protection Board of India (Act s.13(3)). "
              "[Lawyer to add the Board's current complaint channel.]"),
        ("h2", "5. Grievance register (keep this)"),
        ("table", ["Ref", "Date received", "From", "What was asked", "Action taken", "Date closed"],
         [["[001]", "[date]", "[name / file no.]", "[access / correction / erasure / complaint]", "[action]", "[date]"]]),
        ("note", "The law requires a published response period that is reasonable and not more than 90 "
                 "days. The shorter targets above are the firm's own choice and can be changed."),
    ]
    return Doc("grievance-procedure", "Grievance Procedure",
               "How complaints and data requests are handled.",
               ["DPDP-G01", "DPDP-G02", "DPDP-D01", "DPDP-D02", "DPDP-D03", "DPDP-D04"], b)

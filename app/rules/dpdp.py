"""DPDP Act 2023 and DPDP Rules 2025 - scored rules.

Mirror of docs/RULEBOOK_DPDP.md. tests/test_rulebook.py keeps the two in step.
"""
from __future__ import annotations

from datetime import date

from .base import Rule, Source

ACT = Source(
    "ACT",
    "Digital Personal Data Protection Act, 2023 (No. 22 of 2023)",
    "https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf",
)
RULES = Source(
    "RULES",
    "Digital Personal Data Protection Rules, 2025, G.S.R. 846(E)",
    "https://www.meity.gov.in/static/uploads/2025/11/53450e6e5dc0bfa85ebd78686cadad39.pdf",
)
COMM = Source(
    "COMM",
    "Commencement notification G.S.R. 843(E), Gazette of India Extraordinary No. 757, "
    "13 November 2025 (Gazette ID CG-DL-E-14112025-267647)",
    "https://egazette.gov.in",
)

S_BASIS = "1. Know your data and your grounds"
S_NOTICE = "2. Notice and consent"
S_SECURITY = "3. Keeping data safe"
S_BREACH = "4. If something goes wrong"
S_RETENTION = "5. Keeping and deleting data"
S_RIGHTS = "6. People's rights and complaints"
S_VENDORS = "7. Vendors who handle data for you"
S_CHILDREN = "8. Children's data"

DPDP_RULES: list[Rule] = [
    Rule(
        id="DPDP-L01", section=S_BASIS, title="Lawful ground for every use of personal data",
        requirement="Only process personal data for a lawful purpose, and either with the person's "
                    "consent or for a legitimate use listed in the Act (for example data given "
                    "voluntarily for a stated purpose, employment, or a legal duty).",
        citation="Act s.4(1), s.7(a), 7(d), 7(e), 7(i)", source=ACT, weight=2,
        question="Do you have a written list of the personal data you hold, why you hold it, and "
                 "the ground you rely on for each type?",
        help="The data inventory in this kit is a starting point. Each row needs a reason and a ground.",
        evidence="A register of personal data with purpose and ground for each type.",
        fix="Complete the data inventory for all five record types and pick a ground for each. "
            "Ask your lawyer to confirm the grounds.",
    ),
    Rule(
        id="DPDP-N01", section=S_NOTICE, title="Clear, stand-alone privacy notice",
        requirement="When asking for consent, give a notice that stands on its own, is in clear and "
                    "plain language, lists the personal data item by item, states the specific "
                    "purpose, and tells the person how to withdraw consent, use their rights and "
                    "complain to the Data Protection Board.",
        citation="Act s.5(1); Rules r.3(a), 3(b), 3(c)", source=RULES, weight=2,
        question="Do clients and others get a clear, separate privacy notice when you ask for "
                 "their personal data?",
        help="A notice buried inside the engagement letter does not count as stand-alone.",
        evidence="The notice text, and where and when it is given.",
        fix="Use the Privacy Notice in the Documents section. Give it with your client intake "
            "form and put it on your website.",
    ),
    Rule(
        id="DPDP-N02", section=S_NOTICE, title="Notice to existing clients",
        requirement="For people who gave consent before the Act started, send the same kind of "
                    "notice as soon as reasonably practicable.",
        citation="Act s.5(2)", source=ACT, weight=2,
        question="Have you planned how to send the privacy notice to existing clients and contacts "
                 "whose data you already hold?",
        help="Choose 'Not applicable' only if you hold no personal data collected on consent before 13 May 2027.",
        evidence="List of existing contacts and a record that the notice was sent.",
        fix="Export your client contact list and schedule one email or letter with the Privacy Notice.",
        allow_na=True,
    ),
    Rule(
        id="DPDP-N03", section=S_NOTICE, title="Notice available in the person's language",
        requirement="Offer the notice and the consent request in English or any language listed in "
                    "the Eighth Schedule to the Constitution, at the person's option.",
        citation="Act s.5(3), s.6(3)", source=ACT, weight=1,
        question="Can a person read your notice and consent request in English or in an Indian "
                 "language they choose (for example Gujarati or Hindi)?",
        evidence="Translated versions of the notice and consent text.",
        fix="Have the Privacy Notice and Consent Text translated into the languages your clients use.",
    ),
    Rule(
        id="DPDP-K01", section=S_NOTICE, title="Real, specific consent",
        requirement="Consent must be free, specific, informed, unconditional and unambiguous, given "
                    "by a clear affirmative action, and limited to the data necessary for the purpose.",
        citation="Act s.6(1)", source=ACT, weight=2,
        question="When you rely on consent, does the person actively agree (signs or ticks a box "
                 "themselves) to each specific purpose, with no pre-ticked or bundled consent?",
        evidence="Consent wording; unticked boxes or signatures per purpose.",
        fix="Replace blanket consent wording with the Consent Text in the Documents section.",
    ),
    Rule(
        id="DPDP-K02", section=S_NOTICE, title="Easy withdrawal of consent",
        requirement="Make withdrawing consent as easy as giving it. After withdrawal, stop "
                    "processing within a reasonable time and make processors stop, unless a law "
                    "requires or allows you to continue.",
        citation="Act s.6(4), s.6(6); Rules r.3(c)(i)", source=ACT, weight=2,
        question="Can a person withdraw consent as easily as they gave it, and do you then stop "
                 "using their data (and tell your vendors to stop)?",
        evidence="Withdrawal method; a log of withdrawals acted on.",
        fix="Name one email address for withdrawals, state it in the notice, and keep a withdrawal log.",
    ),
    Rule(
        id="DPDP-K03", section=S_NOTICE, title="Proof of notice and consent",
        requirement="Be able to prove that notice was given and consent was obtained. The burden "
                    "of proof is on the firm.",
        citation="Act s.6(10)", source=ACT, weight=2,
        question="Do you keep dated records showing who was given which notice and who consented to what?",
        evidence="Dated consent records linked to the notice version.",
        fix="Keep the signed consent form (or the email reply) in each client file with the notice version and date.",
    ),
    Rule(
        id="DPDP-S01", section=S_SECURITY, title="Encryption and similar safeguards",
        requirement="Protect personal data with reasonable security safeguards, including measures "
                    "such as encryption, obfuscation, masking or virtual tokens.",
        citation="Act s.8(5); Rules r.6(1)(a)", source=RULES, weight=3,
        question="Are the laptops, phones, backups and document systems that hold personal data encrypted?",
        help="For example BitLocker or FileVault on laptops, a screen lock on phones, encrypted backups.",
        evidence="Encryption status of each device and backup.",
        fix="Switch on disk encryption on every laptop and phone used for work, and encrypt backups.",
    ),
    Rule(
        id="DPDP-S02", section=S_SECURITY, title="Access control",
        requirement="Control who can access the computers and systems that hold personal data.",
        citation="Rules r.6(1)(b)", source=RULES, weight=3,
        question="Does each person have their own login, with access only to the files they need, "
                 "and is access removed when someone leaves?",
        evidence="User list by role; leaver checklist.",
        fix="Stop shared logins, set folder permissions by team, and add account removal to your exit checklist.",
    ),
    Rule(
        id="DPDP-S03", section=S_SECURITY, title="Access logs and review",
        requirement="Keep logs of access to personal data, and monitor and review them so that "
                    "unauthorised access can be detected, investigated and fixed.",
        citation="Rules r.6(1)(c)", source=RULES, weight=3,
        question="Are access logs switched on for your document system, email and cloud storage, "
                 "and does someone review them?",
        evidence="Logging settings; name of reviewer; review dates.",
        fix="Switch on audit logs in your email and cloud storage admin console and review them monthly.",
    ),
    Rule(
        id="DPDP-S04", section=S_SECURITY, title="Backups so work can continue",
        requirement="Have reasonable measures, such as data backups, to keep working if data is "
                    "destroyed or access is lost.",
        citation="Rules r.6(1)(d)", source=RULES, weight=3,
        question="Do you back up personal data regularly and have you tested restoring it?",
        evidence="Backup schedule and a restore test record.",
        fix="Set an automatic daily or weekly backup and test one restore this month.",
    ),
    Rule(
        id="DPDP-S05", section=S_SECURITY, title="Keep logs for one year",
        requirement="Keep access logs and personal data for one year for breach detection and "
                    "investigation, unless another law requires otherwise.",
        citation="Rules r.6(1)(e)", source=RULES, weight=3,
        question="Are your access logs kept for at least one year?",
        help="Many cloud services keep logs for only 30 to 180 days unless you change the setting.",
        evidence="Log retention setting of one year or more.",
        fix="Set log retention to at least 365 days, or export logs monthly to secure storage.",
    ),
    Rule(
        id="DPDP-A02", section=S_SECURITY, title="Policies, roles and training",
        requirement="Put in place technical and organisational measures so that the Act, the Rules "
                    "and the security safeguards are actually followed.",
        citation="Act s.8(4); Rules r.6(1)(g)", source=ACT, weight=2,
        question="Is one named person responsible for data protection, with a short written policy "
                 "and staff who have been trained on it?",
        evidence="Named owner; written policy; training record.",
        fix="Appoint a privacy lead, adopt a two-page data protection policy and brief all staff.",
    ),
    Rule(
        id="DPDP-B01", section=S_BREACH, title="Tell affected people about a breach",
        requirement="On becoming aware of a personal data breach, tell each affected person without "
                    "delay, in plain words: what happened, likely consequences, what the firm is "
                    "doing, what they can do, and a contact for questions.",
        citation="Act s.8(6); Rules r.7(1)", source=RULES, weight=3,
        question="Do you have a written plan and a ready message for telling affected people "
                 "about a data breach without delay?",
        evidence="Breach response plan with a message template.",
        fix="Adopt the Breach Response Plan in the Documents section and keep client contact lists exportable.",
    ),
    Rule(
        id="DPDP-B02", section=S_BREACH, title="Tell the Data Protection Board about a breach",
        requirement="On becoming aware of a breach, tell the Data Protection Board without delay, "
                    "and give detailed information within 72 hours (or a longer period the Board "
                    "allows on written request).",
        citation="Act s.8(6); Rules r.7(2)", source=RULES, weight=3,
        question="Does your plan name who informs the Data Protection Board, first without delay "
                 "and then with full details within 72 hours?",
        evidence="Breach plan with the two-step Board timeline and a named owner.",
        fix="Name a breach lead and a deputy, and add the 72-hour checklist from the Breach Response Plan.",
    ),
    Rule(
        id="DPDP-R01", section=S_RETENTION, title="Delete data that is no longer needed",
        requirement="Erase personal data when consent is withdrawn or when the purpose is no longer "
                    "served, unless a law requires it to be kept. Make processors erase it too.",
        citation="Act s.8(7)", source=ACT, weight=2,
        question="Do you have a retention schedule and do you actually delete personal data when "
                 "it is no longer needed?",
        evidence="Retention schedule; deletion log.",
        fix="Adopt the Data Retention Schedule in the Documents section and run a deletion review every year.",
    ),
    Rule(
        id="DPDP-R02", section=S_RETENTION, title="One-year minimum retention",
        requirement="Keep personal data, associated traffic data and processing logs for at least "
                    "one year from the date of processing, then erase unless another law requires "
                    "longer retention.",
        citation="Rules r.8(3)", source=RULES, weight=2,
        question="Does your retention practice keep personal data and processing logs for at least "
                 "one year before deletion?",
        help="This minimum applies even when the purpose has ended. Ask your lawyer how it fits with client instructions to delete.",
        evidence="Retention schedule showing the one-year minimum.",
        fix="Add the one-year minimum to your retention schedule and to vendor contracts.",
    ),
    Rule(
        id="DPDP-G01", section=S_RIGHTS, title="Published privacy contact",
        requirement="Prominently publish the business contact details of a person who can answer "
                    "questions about data processing, and include them in every reply to a rights request.",
        citation="Act s.8(9); Rules r.9", source=RULES, weight=2,
        question="Is a privacy contact (name or role, email, phone) shown clearly on your website "
                 "or notice, and included in your replies to requests?",
        evidence="Contact shown on website/notice; reply template.",
        fix="Add the privacy contact to your website footer, notice and email reply template.",
    ),
    Rule(
        id="DPDP-G02", section=S_RIGHTS, title="Grievance process with a published time limit",
        requirement="Run an effective grievance redressal system and publish the period for "
                    "answering grievances. It must be reasonable and not more than 90 days.",
        citation="Act s.8(10), s.13; Rules r.14(3)", source=RULES, weight=2,
        question="Do you have a written complaints (grievance) process with a published response "
                 "time of 90 days or less?",
        evidence="Grievance procedure; published response time; grievance register.",
        fix="Adopt the Grievance Procedure in the Documents section and start a grievance register.",
    ),
    Rule(
        id="DPDP-D01", section=S_RIGHTS, title="Published way to make a rights request",
        requirement="Prominently publish how a person can make a rights request and what "
                    "identifier is needed to identify them.",
        citation="Rules r.14(1), 14(5)", source=RULES, weight=2,
        question="Have you published how a person can ask to see, correct or erase their data, and "
                 "what details they must give to identify themselves?",
        evidence="Published 'how to make a request' text.",
        fix="Publish the request steps from the Privacy Notice on your website and intake form.",
    ),
    Rule(
        id="DPDP-D02", section=S_RIGHTS, title="Answering access requests",
        requirement="On request, give the person a summary of their personal data and how it is "
                    "used, and the identities of those it was shared with.",
        citation="Act s.11(1)", source=ACT, weight=2,
        question="Could you give a person a summary of the data you hold on them and a list of who "
                 "you shared it with?",
        evidence="Access reply template; list of recipients per record type.",
        fix="Use the data inventory to prepare a standard access reply listing data, uses and recipients.",
    ),
    Rule(
        id="DPDP-D03", section=S_RIGHTS, title="Correcting and erasing on request",
        requirement="On request, correct, complete or update personal data, and erase it unless it "
                    "is still needed for the purpose or must be kept by law.",
        citation="Act s.12", source=ACT, weight=2,
        question="Do you have a process to correct, update or erase a person's data when they ask, "
                 "and to record what you did?",
        evidence="Request log showing action taken and date.",
        fix="Add correction and erasure steps to the Grievance Procedure and keep a request log.",
    ),
    Rule(
        id="DPDP-D04", section=S_RIGHTS, title="Nominee for data rights",
        requirement="Let a person nominate someone to use their data rights if they die or become incapacitated.",
        citation="Act s.14; Rules r.14(4)", source=ACT, weight=1,
        question="Can a person nominate someone to act for them on their data if they die or are incapacitated?",
        evidence="Nomination method in the procedure or intake form.",
        fix="Add an optional nominee line to the client intake form.",
    ),
    Rule(
        id="DPDP-A01", section=S_BASIS, title="Accurate and complete data",
        requirement="Where personal data is likely to be used for a decision about the person or "
                    "shared with another Data Fiduciary, make sure it is complete, accurate and consistent.",
        citation="Act s.8(3)", source=ACT, weight=1,
        question="Do you check that personal data is accurate and up to date before relying on it "
                 "or sharing it?",
        evidence="Intake checks; periodic update of contact details.",
        fix="Confirm client details at the start of each new matter and before filing or sharing.",
    ),
    Rule(
        id="DPDP-P01", section=S_VENDORS, title="Written contract with every processor",
        requirement="Use a Data Processor only under a valid contract. The firm stays responsible "
                    "for what the processor does.",
        citation="Act s.8(1), s.8(2)", source=ACT, weight=2,
        question="Do you have a written contract with every vendor that handles personal data for "
                 "you (cloud storage, payroll, IT support, e-signature)?",
        evidence="Vendor list; signed contracts.",
        fix="List all vendors that touch personal data and get a signed contract or accepted terms for each.",
        applies_if="uses_processors",
    ),
    Rule(
        id="DPDP-P02", section=S_VENDORS, title="Security clause in processor contracts",
        requirement="The contract with each processor must contain an appropriate clause requiring "
                    "reasonable security safeguards.",
        citation="Rules r.6(1)(f)", source=RULES, weight=2,
        question="Do those vendor contracts include a clause requiring the vendor to keep the data secure?",
        evidence="Security clause in each contract.",
        fix="Check each contract against the Processor Contract Checklist in the Documents section.",
        applies_if="uses_processors",
    ),
    Rule(
        id="DPDP-P03", section=S_VENDORS, title="Processors must stop, erase and retain on instruction",
        requirement="Be able to make each processor stop processing when consent is withdrawn, "
                    "erase data when told, and keep data and logs for the one-year minimum.",
        citation="Act s.6(6), s.8(7)(b); Rules r.8(3) Illustration Case 2", source=ACT, weight=2,
        question="Can you make each vendor stop using, delete, or keep data and logs when you instruct them to?",
        evidence="Contract clauses on stop, erase and retention.",
        fix="Add stop, erase and one-year retention clauses when contracts are next renewed.",
        applies_if="uses_processors",
    ),
    Rule(
        id="DPDP-CH01", section=S_CHILDREN, title="Verifiable parental consent",
        requirement="Before processing a child's personal data (anyone under 18), obtain verifiable "
                    "consent of the parent and check that the person is an identifiable adult.",
        citation="Act s.9(1); Rules r.10(1)", source=RULES, weight=3,
        question="Before handling data about anyone under 18, do you get the parent's consent and "
                 "check the parent's identity and age?",
        evidence="Parent consent record with identity and age check.",
        fix="Add a parent or guardian consent and ID check step to intake for matters involving minors.",
        applies_if="handles_children",
    ),
    Rule(
        id="DPDP-CH02", section=S_CHILDREN, title="No tracking or advertising aimed at children",
        requirement="Do not process a child's data in a way likely to harm the child, and do not "
                    "track, behaviourally monitor or target advertising at children.",
        citation="Act s.9(2), s.9(3)", source=ACT, weight=3,
        question="Can you confirm that children's data is never used for tracking, profiling or marketing?",
        evidence="Written confirmation; marketing lists exclude minors.",
        fix="Exclude minors' data from all marketing and analytics tools and record the confirmation.",
        applies_if="handles_children",
    ),
]

DPDP_BY_ID = {r.id: r for r in DPDP_RULES}

# ---- Commencement dates: COMM clauses (a)-(c) and Rules r.1(2)-(4) -------------

DEADLINES = [
    {
        "id": "DPDP-C01",
        "date": date(2025, 11, 13),
        "title": "Phase 1 - Act switched on, Board set up",
        "provisions": "Act s.1(2), 2, 18-26, 35, 38-43, 44(1), 44(3); Rules 1, 2, 17-21",
        "meaning": "Definitions, the Data Protection Board of India and rule-making powers are in "
                   "force. No day-to-day duty for a small firm yet.",
        "citation": "G.S.R. 843(E) clause (a); Rules r.1(2)",
    },
    {
        "id": "DPDP-C02",
        "date": date(2026, 11, 13),
        "title": "Phase 2 - Consent Managers can register",
        "provisions": "Act s.6(9), s.27(1)(d); Rule 4",
        "meaning": "Companies can register with the Board as Consent Managers. A law firm does not "
                   "need to act, but clients may later manage consent through such a service.",
        "citation": "G.S.R. 843(E) clause (b); Rules r.1(3)",
    },
    {
        "id": "DPDP-C03",
        "date": date(2027, 5, 13),
        "title": "Phase 3 - All main duties apply",
        "provisions": "Act s.3-5, 6(1)-(8), 6(10), 7-17, 27 (rest), 28-34, 36, 37, 44(2); "
                      "Rules 3, 5-16, 22, 23",
        "meaning": "Notice, consent, security safeguards, breach notification, retention and "
                   "erasure, people's rights, grievance handling and penalties all apply from this "
                   "day. Your firm should be ready before it.",
        "citation": "G.S.R. 843(E) clause (c); Rules r.1(4)",
    },
]

DEADLINE_NOTE = (
    "Dates count from Gazette publication. The Gazette issue is dated 13 November 2025; its "
    "electronic ID suggests upload on 14 November 2025. We use the earlier date. Your lawyer "
    "should confirm the exact day."
)

PENALTIES = [
    ("Failing to take reasonable security safeguards (s.8(5))", "Up to Rs 250 crore", "Schedule item 1"),
    ("Failing to notify the Board or affected people of a breach (s.8(6))", "Up to Rs 200 crore", "Schedule item 2"),
    ("Breach of children's data obligations (s.9)", "Up to Rs 200 crore", "Schedule item 3"),
    ("Breach of Significant Data Fiduciary obligations (s.10)", "Up to Rs 150 crore", "Schedule item 4"),
    ("Breach of any other provision of the Act or Rules", "Up to Rs 50 crore", "Schedule item 7"),
]

UNVERIFIED = [
    ("DPDP-I02", "How far the exemption for processing 'necessary for enforcing any legal right or "
                 "claim' (Act s.17(1)(a)) covers a law firm's client files. The kit does not rely on it."),
    ("DPDP-I06", "Whether any country or class of data has been restricted for transfer outside India (Act s.16; Rules r.15)."),
    ("DPDP-I07", "Whether any class of small firms has been exempted under Act s.17(3) or s.17(5)."),
    ("DPDP-I08", "A reported corrigendum G.S.R. 892(E) to rule 1 of the Rules was not seen."),
    ("DPDP-I09", "Whether any firm has been notified as a Significant Data Fiduciary."),
    ("DPDP-C0x", "The exact day of Gazette publication (13 or 14 November 2025), which moves the later dates by one day."),
]

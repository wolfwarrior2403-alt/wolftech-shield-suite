"""Builds the public guidance document from one source:

    docs/GUIDE.md
    docs/Wolftech-Shield-Suite-Guide.pdf

Run:  python scripts/build_guide.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.compliance.documents import Doc  # noqa: E402
from app.pdf import render_pdf  # noqa: E402
from app.rules.certin import CERTIN_RULES  # noqa: E402
from app.rules.dpdp import DEADLINES, DPDP_RULES  # noqa: E402

TITLE = "Wolftech Shield Suite - Guide"

BLOCKS: list[tuple] = [
    ("p", "Wolftech Shield Suite helps a small Indian firm do two things: get ready for the Digital Personal "
          "Data Protection (DPDP) Act 2023, and check its basic cyber security against CERT-In's directions and "
          "guidance. This guide explains what it does, how to use it, and how to connect it to an AI assistant."),
    ("note", "The suite is a readiness tool. It does not certify compliance and it is not legal advice. Every "
             "document it produces is a draft for a qualified lawyer to review."),

    ("h2", "1. Who it is for"),
    ("ul", [
        "Small professional firms that hold personal data: law firms first, other profiles to follow.",
        "The managing partner or office manager who must get the firm ready, without a compliance team.",
        "The firm's lawyer, who receives cited drafts instead of a blank page.",
    ]),

    ("h2", "2. The dates that matter"),
    ("table", ["Date", "What starts", "Source"],
     [[f"{d['date']:%d %B %Y}", d["title"] + ". " + d["meaning"], d["citation"]] for d in DEADLINES]),
    ("p", "Dates count from publication in the Gazette of India. The Gazette issue is dated 13 November 2025 and "
          "appears to have been uploaded on 14 November 2025, so the later dates may fall one day later. Ask your "
          "lawyer to confirm the exact day."),

    ("h2", "3. What is inside"),
    ("table", ["Product", "What you do", "What you get"], [
        ["Compliance Kit", "Describe the firm, list the personal data it holds, answer one plain-English question per rule.",
         "A readiness score out of 100; a prioritised gap list where every gap shows its section or rule number and a "
         "link to the source; six draft documents as PDF; a deadline tracker."],
        ["Cyber Health Check", "Answer a short security questionnaire. Optionally check your own domain.",
         "A score and grade; fixes ranked easiest first; a PDF report with CERT-In citations."],
    ]),

    ("h2", "4. Compliance Kit, step by step"),
    ("ol", [
        "Start a workspace. Enter the firm name, city, number of people and a privacy contact. Say whether outside "
        "vendors handle data for you and whether you hold data about anyone under 18.",
        "Data inventory. For client files, KYC documents, employee data, visitor records and vendor contracts, say "
        "what is in each, why you keep it, where it is stored, how long, and who it is shared with.",
        "Gap assessment. Answer Yes, Partly or No to one question per rule. The citation is shown under each question.",
        "Gap list. Read the gaps from the top. Each one has the rule in plain English, the citation, a source link, "
        "a suggested fix and the evidence to keep.",
        "Documents. Download the six drafts and give them to your lawyer.",
    ]),
    ("p", f"The kit scores {len(DPDP_RULES)} rules taken from the Act and the Rules. Rules about children's data and "
          "about vendors switch on only if they apply to your firm."),
    ("table", ["Document", "Use it for"], [
        ["Privacy Notice", "Telling people what data you collect, why, and how to use their rights."],
        ["Consent Text", "Asking permission separately for each purpose, and keeping proof."],
        ["Data Retention Schedule", "Recording how long each record type is kept and when it is erased."],
        ["Breach Response Plan", "Who does what, and by when, if data is exposed or lost."],
        ["Processor Contract Checklist", "Checking what each vendor contract should say."],
        ["Grievance Procedure", "Handling complaints and data requests within the legal time limit."],
    ]),
    ("p", "Text in [square brackets] is left for you or your lawyer to complete. Where the law does not give a "
          "number, the kit does not guess one."),

    ("h2", "5. Cyber Health Check, step by step"),
    ("ol", [
        "Answer the questionnaire: backups, passwords and MFA, patching, email security, staff training, incident "
        "plan, logs, devices and network.",
        "Optional: enter your own domain and tick the box confirming that you own or control it.",
        "Read the report. Low-effort fixes are at the top. Mandatory CERT-In directions are tagged.",
        "Download the PDF report.",
    ]),
    ("p", f"The check scores {len(CERTIN_RULES)} rules. Four come from the mandatory CERT-In Directions of 28 April "
          "2022 (report listed incidents within 6 hours, name a Point of Contact, keep logs for 180 days in India, "
          "synchronise clocks). The rest come from CERT-In's 15 Elemental Cyber Defense Controls for MSMEs, which "
          "are baseline guidance, not law."),
    ("h2", "6. What the domain check does and does not do"),
    ("table", ["It does", "It never does"], [
        ["Look up public DNS records for SPF, DMARC and DKIM.", "Scan ports."],
        ["Make one secure connection to read your website certificate.", "Guess paths or try to log in."],
        ["Request your home page once to read its security headers.", "Check a domain you have not confirmed you own."],
    ]),
    ("p", "SPF and DMARC results count towards the email rule (CERT-In control NES.4). Certificate and header "
          "results are shown as good practice and are not scored, because no specific CERT-In rule requiring them "
          "was found."),

    ("h2", "7. How the score works"),
    ("ul", [
        "Yes counts in full, Partly counts half, No and unanswered count zero. Not applicable is left out.",
        "Each rule has a weight. For DPDP, weights follow the penalty tiers in the Act's Schedule, so security "
        "safeguards and breach notification come first.",
        "Bands: 80 and above is Strong, 50 to 79 is Getting there, below 50 is Needs attention.",
        "The weights, bands and effort labels are Wolftech's prioritisation. They are not set by law, and a high "
        "score is not a finding of compliance.",
    ]),

    ("h2", "8. Where every rule comes from"),
    ("p", "Each scored rule cites a primary source by section, rule or direction number. A rule that could not be "
          "confirmed in a primary source is marked UNVERIFIED in the rule books and is left out of scoring."),
    ("table", ["Source", "Published by"], [
        ["Digital Personal Data Protection Act, 2023 (No. 22 of 2023)", "Gazette of India; Ministry of Electronics and IT"],
        ["Digital Personal Data Protection Rules, 2025, G.S.R. 846(E)", "Gazette of India; Ministry of Electronics and IT"],
        ["Commencement notification G.S.R. 843(E), 13 November 2025", "Gazette of India"],
        ["CERT-In Directions No. 20(3)/2022-CERT-In, 28 April 2022", "Indian Computer Emergency Response Team"],
        ["15 Elemental Cyber Defense Controls for MSMEs, Version 1.0, 1 September 2025", "Indian Computer Emergency Response Team"],
    ]),

    ("h2", "9. Your data"),
    ("ul", [
        "Everything is stored in one file on the machine that runs the suite.",
        "The pages contain no JavaScript, no analytics and no third-party scripts.",
        "The only outbound traffic is the domain check, and only when you start it.",
        "The public demo uses a fictional firm, Sample Law Associates. No real names are used.",
    ]),

    ("h2", "10. Connect an AI assistant (MCP)"),
    ("p", "The suite includes a Model Context Protocol (MCP) server, so an AI assistant can read a workspace and "
          "produce the same cited results. It runs on your own machine and talks to the assistant over standard "
          "input and output. There is no hosted endpoint: your data does not go to a Wolftech server."),
    ("ol", [
        "Install the suite and its requirements (see the README).",
        "In your MCP client's settings, add a server named wolftech-shield-suite.",
        "Set the command to the Python program in the suite's .venv folder, and the argument to the full path of mcp_server.py.",
        "Restart the client. Four tools appear.",
    ]),
    ("table", ["Tool", "What it returns"], [
        ["assess_readiness", "DPDP readiness score, band, counts and the legal dates."],
        ["list_gaps", "Prioritised gaps, each with rule ID, citation, source link and fix."],
        ["generate_document", "One of the six drafts as text, optionally saved as a branded PDF."],
        ["run_health_check", "Health score and fixes, easiest first. Runs the domain check only when ownership is confirmed."],
    ]),

    ("h2", "11. Limits"),
    ("ul", [
        "One profile so far: Law firm. English only.",
        "No user accounts. Run it on a machine you control; do not put real data on a public demo link.",
        "It does not file anything with the Data Protection Board or CERT-In.",
        "It is not a security audit. No penetration testing or vulnerability scanning is performed.",
        "Whether the CERT-In Directions apply to your firm as a 'body corporate' is a question for your lawyer.",
    ]),

    ("h2", "12. Contact"),
    ("p", "Wolftech AI Labs, Ahmedabad. [Add contact email, phone and website address before publishing.]"),
]


def to_markdown(doc: Doc) -> str:
    out = [f"# {doc.title}", "", f"_{doc.disclaimer}_", "", f"Wolftech AI Labs - {doc.generated_on:%d %B %Y}", ""]
    for block in doc.blocks:
        kind = block[0]
        if kind == "h2":
            out += [f"## {block[1]}", ""]
        elif kind == "p":
            out += [block[1], ""]
        elif kind == "note":
            out += [f"> {block[1]}", ""]
        elif kind == "ul":
            out += [f"- {i}" for i in block[1]] + [""]
        elif kind == "ol":
            out += [f"{n}. {i}" for n, i in enumerate(block[1], 1)] + [""]
        elif kind == "table":
            out.append("| " + " | ".join(block[1]) + " |")
            out.append("|" + "---|" * len(block[1]))
            out += ["| " + " | ".join(c.replace("|", "/") for c in row) + " |" for row in block[2]]
            out.append("")
    return "\n".join(out)


def build() -> Doc:
    return Doc("guide", TITLE, "Public guidance document.", [], BLOCKS, firm_name="Wolftech AI Labs")


if __name__ == "__main__":
    doc = build()
    docs = ROOT / "docs"
    (docs / "GUIDE.md").write_text(to_markdown(doc), encoding="utf-8", newline="\n")
    (docs / "Wolftech-Shield-Suite-Guide.pdf").write_bytes(render_pdf(doc, "Guide"))
    print("wrote", docs / "GUIDE.md", "and", docs / "Wolftech-Shield-Suite-Guide.pdf")

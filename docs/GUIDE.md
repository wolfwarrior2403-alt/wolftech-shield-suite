# Wolftech Shield Suite - Guide

_Draft for review by a qualified lawyer. Not legal advice._

Wolftech AI Labs - 11 November 2026

Wolftech Shield Suite helps a small Indian firm do two things: get ready for the Digital Personal Data Protection (DPDP) Act 2023, and check its basic cyber security against CERT-In's directions and guidance. This guide explains what it does, how to use it, and how to connect it to an AI assistant.

> The suite is a readiness tool. It does not certify compliance and it is not legal advice. Every document it produces is a draft for a qualified lawyer to review.

## 1. Who it is for

- Small professional firms that hold personal data: law firms first, other profiles to follow.
- The managing partner or office manager who must get the firm ready, without a compliance team.
- The firm's lawyer, who receives cited drafts instead of a blank page.

## 2. The dates that matter

| Date | What starts | Source |
|---|---|---|
| 13 November 2025 | Phase 1 - Act switched on, Board set up. Definitions, the Data Protection Board of India and rule-making powers are in force. No day-to-day duty for a small firm yet. | G.S.R. 843(E) clause (a); Rules r.1(2) |
| 13 November 2026 | Phase 2 - Consent Managers can register. Companies can register with the Board as Consent Managers. A law firm does not need to act, but clients may later manage consent through such a service. | G.S.R. 843(E) clause (b); Rules r.1(3) |
| 13 May 2027 | Phase 3 - All main duties apply. Notice, consent, security safeguards, breach notification, retention and erasure, people's rights, grievance handling and penalties all apply from this day. Your firm should be ready before it. | G.S.R. 843(E) clause (c); Rules r.1(4) |

Dates count from publication in the Gazette of India. The Gazette issue is dated 13 November 2025 and appears to have been uploaded on 14 November 2025, so the later dates may fall one day later. Ask your lawyer to confirm the exact day.

## 3. What is inside

| Product | What you do | What you get |
|---|---|---|
| Compliance Kit | Describe the firm, list the personal data it holds, answer one plain-English question per rule. | A readiness score out of 100; a prioritised gap list where every gap shows its section or rule number and a link to the source; six draft documents as PDF; a deadline tracker. |
| Cyber Health Check | Answer a short security questionnaire. Optionally check your own domain. | A score and grade; fixes ranked easiest first; a PDF report with CERT-In citations. |

## 4. Compliance Kit, step by step

1. Start a workspace. Enter the firm name, city, number of people and a privacy contact. Say whether outside vendors handle data for you and whether you hold data about anyone under 18.
2. Data inventory. For client files, KYC documents, employee data, visitor records and vendor contracts, say what is in each, why you keep it, where it is stored, how long, and who it is shared with.
3. Gap assessment. Answer Yes, Partly or No to one question per rule. The citation is shown under each question.
4. Gap list. Read the gaps from the top. Each one has the rule in plain English, the citation, a source link, a suggested fix and the evidence to keep.
5. Documents. Download the six drafts and give them to your lawyer.

The kit scores 29 rules taken from the Act and the Rules. Rules about children's data and about vendors switch on only if they apply to your firm.

| Document | Use it for |
|---|---|
| Privacy Notice | Telling people what data you collect, why, and how to use their rights. |
| Consent Text | Asking permission separately for each purpose, and keeping proof. |
| Data Retention Schedule | Recording how long each record type is kept and when it is erased. |
| Breach Response Plan | Who does what, and by when, if data is exposed or lost. |
| Processor Contract Checklist | Checking what each vendor contract should say. |
| Grievance Procedure | Handling complaints and data requests within the legal time limit. |

Text in [square brackets] is left for you or your lawyer to complete. Where the law does not give a number, the kit does not guess one.

## 5. Cyber Health Check, step by step

1. Answer the questionnaire: backups, passwords and MFA, patching, email security, staff training, incident plan, logs, devices and network.
2. Optional: enter your own domain and tick the box confirming that you own or control it.
3. Read the report. Low-effort fixes are at the top. Mandatory CERT-In directions are tagged.
4. Download the PDF report.

The check scores 25 rules. Four come from the mandatory CERT-In Directions of 28 April 2022 (report listed incidents within 6 hours, name a Point of Contact, keep logs for 180 days in India, synchronise clocks). The rest come from CERT-In's 15 Elemental Cyber Defense Controls for MSMEs, which are baseline guidance, not law.

## 6. What the domain check does and does not do

| It does | It never does |
|---|---|
| Look up public DNS records for SPF, DMARC and DKIM. | Scan ports. |
| Make one secure connection to read your website certificate. | Guess paths or try to log in. |
| Request your home page once to read its security headers. | Check a domain you have not confirmed you own. |

SPF and DMARC results count towards the email rule (CERT-In control NES.4). Certificate and header results are shown as good practice and are not scored, because no specific CERT-In rule requiring them was found.

## 7. How the score works

- Yes counts in full, Partly counts half, No and unanswered count zero. Not applicable is left out.
- Each rule has a weight. For DPDP, weights follow the penalty tiers in the Act's Schedule, so security safeguards and breach notification come first.
- Bands: 80 and above is Strong, 50 to 79 is Getting there, below 50 is Needs attention.
- The weights, bands and effort labels are Wolftech's prioritisation. They are not set by law, and a high score is not a finding of compliance.

## 8. Where every rule comes from

Each scored rule cites a primary source by section, rule or direction number. A rule that could not be confirmed in a primary source is marked UNVERIFIED in the rule books and is left out of scoring.

| Source | Published by |
|---|---|
| Digital Personal Data Protection Act, 2023 (No. 22 of 2023) | Gazette of India; Ministry of Electronics and IT |
| Digital Personal Data Protection Rules, 2025, G.S.R. 846(E) | Gazette of India; Ministry of Electronics and IT |
| Commencement notification G.S.R. 843(E), 13 November 2025 | Gazette of India |
| CERT-In Directions No. 20(3)/2022-CERT-In, 28 April 2022 | Indian Computer Emergency Response Team |
| 15 Elemental Cyber Defense Controls for MSMEs, Version 1.0, 1 September 2025 | Indian Computer Emergency Response Team |

## 9. Your data

- Everything is stored in one file on the machine that runs the suite.
- The pages contain no JavaScript, no analytics and no third-party scripts.
- The only outbound traffic is the domain check, and only when you start it.
- The public demo uses a fictional firm, Sample Law Associates. No real names are used.

## 10. Connect an AI assistant (MCP)

The suite includes a Model Context Protocol (MCP) server, so an AI assistant can read a workspace and produce the same cited results. It runs on your own machine and talks to the assistant over standard input and output. There is no hosted endpoint: your data does not go to a Wolftech server.

1. Install the suite and its requirements (see the README).
2. In your MCP client's settings, add a server named wolftech-shield-suite.
3. Set the command to the Python program in the suite's .venv folder, and the argument to the full path of mcp_server.py.
4. Restart the client. Four tools appear.

| Tool | What it returns |
|---|---|
| assess_readiness | DPDP readiness score, band, counts and the legal dates. |
| list_gaps | Prioritised gaps, each with rule ID, citation, source link and fix. |
| generate_document | One of the six drafts as text, optionally saved as a branded PDF. |
| run_health_check | Health score and fixes, easiest first. Runs the domain check only when ownership is confirmed. |

## 11. Limits

- One profile so far: Law firm. English only.
- No user accounts. Run it on a machine you control; do not put real data on a public demo link.
- It does not file anything with the Data Protection Board or CERT-In.
- It is not a security audit. No penetration testing or vulnerability scanning is performed.
- Whether the CERT-In Directions apply to your firm as a 'body corporate' is a question for your lawyer.

## 12. Contact

Wolftech AI Labs, Ahmedabad. [Add contact email, phone and website address before publishing.]

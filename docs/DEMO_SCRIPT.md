# 5-minute demo script

Audience: a managing partner of a small law firm. Device: laptop or phone.
Before you start: run the app, open http://localhost:8000, click **Reset demo**.

Say once, early: *"Everything you see is fictional sample data. Nothing leaves
this machine. And every document is a draft for your lawyer to review, not legal
advice."*

## 0:00 - The problem (30 seconds)

Screen: home page.

- "The DPDP Act is switching on in phases. Look at this card."
- Point at **Next legal date: 13 May 2027** and the day counter.
- "From that day a firm must give proper notices, keep data secure, report
  breaches within 72 hours, and answer people's requests. Penalties go up to
  Rs 250 crore. Most small firms have not started."

## 0:30 - Open the workspace (30 seconds)

Click **Open** on Sample Law Associates.

- "This is a 12-person law firm in Ahmedabad. Readiness score: 30 out of 100."
- Point at the three legal dates. "Phase 1 is in force. Phase 2 lands on
  13 November 2026. Phase 3 is the big one."

## 1:00 - Data inventory (40 seconds)

Click **1. Data inventory**.

- "We start with what the firm actually holds: client files, KYC documents,
  employee data, visitor records, vendor contracts."
- Scroll one card. "Plain questions. What is in it, why, where it is kept, how
  long, who it is shared with. We pre-fill typical answers for a law firm."

## 1:40 - Assessment and gaps (70 seconds)

Click **2. Assessment**. Scroll briefly.

- "One question per rule. Yes, Partly or No. Under each question you can see the
  exact section it comes from."

Click **3. Gaps**.

- "This is the pay-off. 24 gaps, the most serious first."
- Open the first gap. "No breach plan. Here is the rule in plain English, the
  citation, Rules rule 7, and a link to the Government's own PDF. And here is
  the fix."
- "We never invent a rule. If we could not verify something in a primary
  source, it is marked unverified and it does not affect the score." (Optional:
  click **DPDP rules** in the top bar and scroll to the bottom to show the
  unverified list.)

## 2:50 - Documents (60 seconds)

Click **4. Documents**.

- "Six drafts, filled with this firm's own data."
- Click **Preview** on Breach Response Plan. "Who does what, and by when:
  6 hours for CERT-In, without delay and 72 hours for the Data Protection Board.
  Every deadline has its source."
- Click **Download PDF**. "Branded, with the lawyer-review line on every page.
  Hand this to your lawyer."
- Mention: "Where the law does not give a number, for example retention under
  other laws, we leave a bracket for the lawyer. We do not guess."

## 3:50 - Cyber Health Check (60 seconds)

Click **Cyber Health Check** in the tab bar, then **Save and see results** (or
open the report directly from the workspace page).

- "Second product. Score 45, grade D. Mapped to CERT-In."
- Scroll to **Check your own domain**. "You type your own domain and confirm you
  own it. We only read public records: SPF, DKIM, DMARC, the certificate and the
  security headers. No scanning."
- Point at the DMARC result: **Fail**. "Anyone can send email pretending to be
  this firm. Here is the exact DNS record to add." (The demo result is a seeded
  sample, labelled as such, because the demo domain is not real.)
- Scroll to **Fixes, easiest first**. "Low-effort fixes on top. Mandatory
  CERT-In directions are tagged."

## 4:50 - Close (10 seconds)

- "Fifteen minutes of questions gives you a score, a to-do list tied to the law,
  and six documents for your lawyer. Shall we set up your firm?"
- Click **Workspaces** > **Start a new workspace** if they say yes.

## If asked

- **"Is this legal advice?"** No. It is a readiness tool. A lawyer must review.
- **"Where is my data?"** In one file on this machine. No cloud, no analytics.
- **"What about the exact deadline day?"** The Gazette is dated 13 November 2025
  and was uploaded on the 14th. We use the 13th to be safe; your lawyer confirms.
- **"Does CERT-In apply to my firm?"** The Directions cover a "body corporate".
  Whether your firm is one is a question for your lawyer; we flag it openly.
- **"Can an AI assistant use this?"** Yes, through the MCP server (four tools).

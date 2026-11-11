# Wolftech Shield Suite

By Wolftech AI Labs, Ahmedabad. Two products for small Indian firms in one local app.

- **Compliance Kit** - get ready for the Digital Personal Data Protection Act 2023
  and the DPDP Rules 2025. First profile: Law firm.
- **Cyber Health Check** - a scored security check mapped to the CERT-In
  Directions of 28 April 2022 and CERT-In's 15 baseline controls for MSMEs.

> Draft for review by a qualified lawyer. Not legal advice.

## Run it

Needs Python 3.12 or newer (built and tested on Python 3.14.3, Windows 11).

Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python -m uvicorn app.main:app --port 8000
```

macOS / Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m uvicorn app.main:app --port 8000
```

Open http://localhost:8000 and click **Open** on "Sample Law Associates" (a
fictional demo workspace). **Reset demo** restores it at any time.

## Run the tests

```bash
.venv/Scripts/python -m pytest        # Windows
.venv/bin/python -m pytest            # macOS / Linux
```

187 tests. They never touch the internet. They include one test per scored rule,
and a check that every scored rule in the code is marked VERIFIED, with a
citation, in the rule books.

## What is where

| Path | What |
|---|---|
| `docs/RULEBOOK_DPDP.md` | Every DPDP rule: plain-English requirement, citation, verified or not, scored or not |
| `docs/RULEBOOK_CERTIN.md` | Same for the CERT-In Directions and MSME controls |
| `docs/SPEC.md` | Journeys, data model, architecture, scoring method, threat model, test plan |
| `docs/DEMO_SCRIPT.md` | 5-minute demo walkthrough |
| `app/rules/` | The rules as code (`dpdp.py`, `certin.py`) |
| `app/scoring.py` | The scoring engine used by both products |
| `app/compliance/` | Onboarding, data inventory, gap assessment, six documents, deadlines |
| `app/health/` | Health questionnaire, passive domain checks, report |
| `app/pdf.py` | Branded PDF writer |
| `app/seed.py` | The fictional demo workspace |
| `mcp_server.py` | MCP server |
| `render.yaml` | Render deployment (demo only) |

## Where your data goes

Nowhere. Everything is stored in one SQLite file, `data/wolftech.db` (change
the location with the `WOLFTECH_DB` environment variable). The pages contain no
JavaScript, no analytics, no external fonts and no third-party scripts, and a
strict Content-Security-Policy enforces that.

The only outbound traffic is the domain check, and only when you start it.

## The domain check

Passive only, and only after you tick "I confirm that I own or control this
domain":

- public DNS TXT lookups for SPF, DMARC and DKIM (common selector names);
- one TLS handshake on port 443 to read the certificate;
- one HTTPS request for the home page to read its security headers.

No port scanning, no path guessing, no login attempts. IP addresses, `localhost`
and private or reserved names are refused, and a domain that resolves to a
private address is not contacted.

SPF and DMARC results count towards the email rule (CERT-In control NES.4). TLS
and header results are shown as good practice and are **not scored**, because no
primary-source CERT-In rule was found that requires them.

## MCP server

Uses the MCP Python SDK v2 (`MCPServer`). Start it over stdio:

```bash
.venv/Scripts/python mcp_server.py
```

Example client configuration (adjust the paths):

```json
{
  "mcpServers": {
    "wolftech-shield-suite": {
      "command": "C:/path/to/wolftech-shield-suite/.venv/Scripts/python.exe",
      "args": ["C:/path/to/wolftech-shield-suite/mcp_server.py"],
      "cwd": "C:/path/to/wolftech-shield-suite"
    }
  }
}
```

| Tool | What it returns |
|---|---|
| `assess_readiness(firm_id?)` | DPDP readiness score, band, counts, legal dates, list of workspaces |
| `list_gaps(firm_id?, limit?)` | Prioritised gaps, each with rule ID, citation, source link and fix |
| `generate_document(document, firm_id?, save_pdf?)` | One of the six drafts as text, optionally saved as a branded PDF in `data/exports/` |
| `run_health_check(firm_id?, domain?, i_confirm_i_own_this_domain?)` | Health score, fixes easiest first, and (only with confirmation) passive domain results |

Leave `firm_id` empty to use the demo workspace.

## Deploy a demo on Render

`render.yaml` is a Render Blueprint: in Render choose New > Blueprint and point
it at this repository.

Read this first:

- **There is no login.** Anyone with the URL can see and change everything.
  Host the fictional demo only. Never put a real firm's data on a public URL.
- The free plan has no persistent disk, so data resets when the service restarts.
- The blueprint has **not been deployed or tested on Render**. `PYTHON_VERSION`
  is set to the version used in development (3.14.3); lower it if Render does
  not offer that version yet.

## Limits (see `docs/SPEC.md` section 8)

No user accounts. One profile (Law firm). English only. No encryption of the
SQLite file (use disk encryption on the machine). Not a substitute for a lawyer
or a security audit.

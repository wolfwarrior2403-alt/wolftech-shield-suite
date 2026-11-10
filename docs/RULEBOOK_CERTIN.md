# Rule Book - CERT-In Directions and MSME Guidance

Draft for review by a qualified lawyer. Not legal advice.

Prepared by Wolftech AI Labs on 11 November 2026. Every row was written from the
text of the primary source named in the row.

## 1. Sources read

| Key | Document | Official location | Copy actually read |
|---|---|---|---|
| DIR | CERT-In Directions No. 20(3)/2022-CERT-In dated 28 April 2022, under section 70B(6) of the Information Technology Act, 2000 | https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf | Official PDF, read directly (8 pages) |
| MSME | CERT-In "15 Elemental Cyber Defense Controls for Micro, Small, and Medium Enterprises (MSMEs)", Version 1.0 dated 01.09.2025 | https://www.cert-in.org.in/PDF/Elemental_Cyber_Defense_Controls_for_MSME.pdf | Official PDF, read directly (11 pages) |

## 2. Two different kinds of rule

- **Directions (DIR)** are mandatory. The text says entities "shall" comply, and
  that non-compliance "may invite punitive action under sub-section (7) of the
  section 70B of the IT Act, 2000".
- **MSME controls (MSME)** are baseline guidance. The text says MSMEs "may use"
  the 45 recommendations to self-assess and "may conduct Baseline Audits" yearly.
  The Health Check labels these as "CERT-In baseline guidance", never as law.

Status words are the same as in RULEBOOK_DPDP.md. Only VERIFIED rules are scored.

## 3. CERT-In Directions of 28 April 2022

"Applies to" in the text: "service providers, intermediaries, data centres, body
corporate and Government organisations".

| ID | Plain-English requirement | Applies to | Evidence needed | Source | Status | Scored |
|---|---|---|---|---|---|---|
| CERTIN-D1 | Synchronise the clocks of all IT systems with the NTP server of NIC or NPL, or an NTP server traceable to them. | All covered entities | Time-sync setting on computers, servers, router | DIR direction (i) | VERIFIED | Yes |
| CERTIN-D2 | Report the cyber incidents listed in Annexure I to CERT-In within 6 hours of noticing them or being told about them. Channels given in the text: email incident@cert-in.org.in, phone 1800-11-4949, fax 1800-11-6969. | All covered entities | Incident plan naming who reports, the 6-hour clock and the CERT-In contact details | DIR direction (ii), Annexure I | VERIFIED | Yes |
| CERTIN-D3 | Designate a Point of Contact for CERT-In and send the details (name, designation, organisation, address, email, mobile, phone, fax) to info@cert-in.org.in in the Annexure II format; keep them updated. Act on CERT-In orders and information requests within the time stated. | All covered entities | Copy of the Point of Contact email sent to CERT-In | DIR direction (iii), Annexure II | VERIFIED | Yes |
| CERTIN-D4 | Switch on logs for all IT systems and keep them securely for a rolling 180 days, stored within India. Give them to CERT-In with an incident report or when ordered. | All covered entities | Log settings on firewall/router, servers, cloud accounts; retention of 180 days; storage location | DIR direction (iv) | VERIFIED | Yes |
| CERTIN-D5 | Data centres, VPS providers, cloud providers and VPN providers must keep subscriber records for 5 years. | Only those provider types (not a typical small firm) | None for a typical small firm | DIR direction (v) | VERIFIED | No (info) |
| CERTIN-D6 | Virtual asset service providers, exchanges and custodian wallets must keep KYC and transaction records for 5 years. | Only those provider types | None for a typical small firm | DIR direction (vi) | VERIFIED | No (info) |
| CERTIN-D7 | Failure to furnish information or comply may invite punitive action under IT Act s.70B(7) and other laws. | All covered entities | - | DIR, closing paragraphs | VERIFIED | No (info) |
| CERTIN-D8 | The Directions "become effective after 60 days from the date on which it is issued" (issued 28 April 2022). | - | - | DIR, last paragraph | VERIFIED | No (info) |
| CERTIN-U1 | Whether a given small firm (for example a partnership or LLP law firm) is a "body corporate" for these Directions. The Directions do not define the term; it depends on the IT Act and CERT-In's FAQs, which were not read from a primary source. | - | - | - | UNVERIFIED - lawyer to confirm; the Health Check states this openly |
| CERTIN-U2 | The exact section 70B(7) penalty amount, and any later extension of the start date for MSMEs. | - | - | - | UNVERIFIED - not read in a primary source; not shown as fact |

Annexure I incident types (VERIFIED, DIR Annexure I): targeted scanning or
probing of critical networks; compromise of critical systems or information;
unauthorised access to IT systems or data; website defacement or intrusion;
malicious code attacks (virus, worm, Trojan, bots, spyware, ransomware,
cryptominers); attacks on servers and network devices; identity theft, spoofing
and phishing; DoS and DDoS; attacks on critical infrastructure, SCADA, OT and
wireless networks; attacks on applications such as e-governance and e-commerce;
data breach; data leak; attacks on IoT devices; attacks affecting digital
payment systems; attacks through malicious mobile apps; fake mobile apps;
unauthorised access to social media accounts; attacks or suspicious activity
affecting cloud systems; attacks affecting big data, blockchain, virtual assets,
robotics, 3D/4D printing, drones; attacks affecting AI and ML systems.

## 4. CERT-In 15 Elemental Cyber Defense Controls for MSMEs (guidance)

Applies to: enterprises classified as MSMEs under the MSME Ministry notification
S.O. 1702(E) of 1 June 2020 (as stated in the document's introduction). All 45
recommendations are listed. "Scored: Yes" marks the ones the Health Check asks
about or tests.

| ID | Plain-English recommendation | Evidence needed | Source | Status | Scored |
|---|---|---|---|---|---|
| CERTIN-EAM.1 | Keep one up-to-date inventory of all hardware, software and information assets, with sensitive ones labelled. | Asset list | MSME control 1, EAM.1 | VERIFIED | Yes |
| CERTIN-EAM.2 | Track each asset from purchase to secure disposal. | Asset list with status | MSME control 1, EAM.2 | VERIFIED | No (info) |
| CERTIN-NES.1 | Use a properly configured firewall at the network edge and switch on the firewall on each computer. | Router/firewall settings; PC firewall on | MSME control 2, NES.1 | VERIFIED | Yes |
| CERTIN-NES.2 | Secure Wi-Fi with WPA2/WPA3 and strong passwords, no default credentials, and a separate guest network. | Wi-Fi settings | MSME control 2, NES.2 | VERIFIED | Yes |
| CERTIN-NES.3 | Use an encrypted VPN with MFA for remote access. | VPN settings | MSME control 2, NES.3 | VERIFIED | Yes |
| CERTIN-NES.4 | Protect email from phishing and spoofing using SPF, DKIM and DMARC. | DNS records for the email domain | MSME control 2, NES.4 | VERIFIED | Yes (questionnaire and passive DNS check) |
| CERTIN-EMS.1 | Install licensed antivirus or endpoint protection on all devices; do not disable built-in OS security. | Antivirus status on each device | MSME control 3, EMS.1 | VERIFIED | Yes |
| CERTIN-EMS.2 | Do not use pirated or unauthorised software; only authorised people install software. | Software list; admin rights list | MSME control 3, EMS.2 | VERIFIED | Yes |
| CERTIN-EMS.3 | Onboard with CERT-In's Cyber Swachhta Kendra for malware and botnet alerts. | Registration confirmation | MSME control 3, EMS.3 | VERIFIED | No (info) |
| CERTIN-EMS.4 | Restrict USB and removable media; consider disabling autorun. | Device policy | MSME control 3, EMS.4 | VERIFIED | Yes |
| CERTIN-SC.1 | Keep baseline secure configurations for operating systems, network devices, browsers and software. | Configuration checklist | MSME control 4, SC.1 | VERIFIED | No (info) |
| CERTIN-SC.2 | Disable unnecessary features, ports, services and default applications. | Configuration checklist | MSME control 4, SC.2 | VERIFIED | No (info) |
| CERTIN-SC.3 | Remove unused software and change all default passwords and settings before use. | Router/printer/CCTV admin passwords changed | MSME control 4, SC.3 | VERIFIED | Yes |
| CERTIN-PM.1 | Regularly apply security patches and updates to operating systems, applications and firmware. | Update settings; last-patched dates | MSME control 5, PM.1 | VERIFIED | Yes |
| CERTIN-PM.2 | Watch vendor and CERT-In advisories for new patches and vulnerabilities. | Advisory subscription | MSME control 5, PM.2 | VERIFIED | Yes |
| CERTIN-IM.1 | Write a formal Incident Response Plan covering reporting, containment, investigation, recovery and communication. | The plan | MSME control 6, IM.1 | VERIFIED | Yes |
| CERTIN-IM.2 | Test the Incident Response Plan regularly. | Date and notes of last drill | MSME control 6, IM.2 | VERIFIED | Yes |
| CERTIN-IM.3 | Follow the section 70B(6) Directions, including reporting incidents to CERT-In within 6 hours. | See CERTIN-D2 | MSME control 6, IM.3 | VERIFIED | No (scored once under CERTIN-D2) |
| CERTIN-LM.1 | Switch on logging on all key systems and keep system and application logs for at least 180 days, stored within India. | See CERTIN-D4 | MSME control 7, LM.1 | VERIFIED | No (scored once under CERTIN-D4) |
| CERTIN-LM.2 | Continuously monitor network activity and privileged user actions. | Monitoring tool or review record | MSME control 7, LM.2 | VERIFIED | No (info) |
| CERTIN-LM.3 | Consider deploying security monitoring tools. | - | MSME control 7, LM.3 | VERIFIED | No (info) |
| CERTIN-AT.1 | Run basic cybersecurity awareness training at least twice a year for all employees and contractors (phishing, passwords, social engineering, BYOD, safe internet and email use). | Training dates and attendance | MSME control 8, AT.1 | VERIFIED | Yes |
| CERTIN-AT.2 | Take part in CERT-In awareness workshops and drills. | Participation record | MSME control 8, AT.2 | VERIFIED | No (info) |
| CERTIN-TPRM.1 | Do due diligence on each vendor based on business impact and likelihood of compromise. | Vendor checklist | MSME control 9, TPRM.1 | VERIFIED | No (info) |
| CERTIN-TPRM.2 | Hold vendors to the same security standards as the firm. | Contract clause | MSME control 9, TPRM.2 | VERIFIED | No (info) |
| CERTIN-DPBP.1 | Back up on a regular schedule (daily or weekly) and keep encrypted copies offsite and offline. | Backup job settings; location of copies | MSME control 10, DPBP.1 | VERIFIED | Yes |
| CERTIN-DPBP.2 | Test restoring from backup periodically. | Date of last restore test | MSME control 10, DPBP.2 | VERIFIED | Yes |
| CERTIN-DPBP.3 | Keep a minimum Business Continuity Plan for critical applications. | The plan | MSME control 10, DPBP.3 | VERIFIED | No (info) |
| CERTIN-DPBP.4 | Dispose of physical and digital media securely (sanitise or destroy). | Disposal record | MSME control 10, DPBP.4 | VERIFIED | No (info) |
| CERTIN-GC.1 | Name one security in-charge / single point of contact for CERT-In and regulators. | Named person | MSME control 11, GC.1 | VERIFIED | No (scored once under CERTIN-D3) |
| CERTIN-GC.2 | Approve an Information Security Policy sized to the firm. | The policy | MSME control 11, GC.2 | VERIFIED | No (info) |
| CERTIN-GC.3 | Review security policies periodically. | Review date | MSME control 11, GC.3 | VERIFIED | No (info) |
| CERTIN-GC.4 | Follow guidelines and directions from CERT-In and regulators. | - | MSME control 11, GC.4 | VERIFIED | No (info) |
| CERTIN-RPP.1 | Enforce strong, unique passwords (minimum 8 to 12 characters, mixed character types), set expiry, restrict reuse, and tell staff not to share credentials. | Password policy; password manager | MSME control 12, RPP.1 | VERIFIED | Yes |
| CERTIN-RPP.2 | Lock accounts temporarily after 3 to 5 failed logins. | Lockout setting | MSME control 12, RPP.2 | VERIFIED | Yes |
| CERTIN-RPP.3 | Switch on Multi-Factor Authentication for all critical systems, admin accounts and remote access. | MFA status on email, cloud storage, banking, admin accounts | MSME control 12, RPP.3 | VERIFIED | Yes |
| CERTIN-RPP.4 | Store passwords using secure encryption and hashing. | Applies to firms that build software | MSME control 12, RPP.4 | VERIFIED | No (info) |
| CERTIN-ACIM.1 | Give each person their own user ID; no shared accounts. | User list | MSME control 13, ACIM.1 | VERIFIED | Yes |
| CERTIN-ACIM.2 | Give access by role and least privilege. | Access list by role | MSME control 13, ACIM.2 | VERIFIED | No (info) |
| CERTIN-ACIM.3 | Review access at least quarterly and immediately on role change or exit, using an offboarding checklist. | Offboarding checklist; review date | MSME control 13, ACIM.3 | VERIFIED | Yes |
| CERTIN-ACIM.4 | Give admin rights only when essential; separate duties. | Admin list | MSME control 13, ACIM.4 | VERIFIED | No (info) |
| CERTIN-PS.1 | Control physical access to server rooms and network equipment; monitor with CCTV. | Locks, access records | MSME control 14, PS.1 | VERIFIED | No (info) |
| CERTIN-PS.2 | Use an asset-return checklist for every employee exit. | Checklist | MSME control 14, PS.2 | VERIFIED | No (info) |
| CERTIN-VAA.1 | Have an independent third party assess vulnerabilities of business-critical assets at least once a year and fix what is found. | Assessment report | MSME control 15, VAA.1 | VERIFIED | No (info) |
| CERTIN-VAA.2 | Do periodic risk assessments. | Risk register | MSME control 15, VAA.2 | VERIFIED | No (info) |

## 5. Passive domain checks and how they map to rules

| Check | What is looked up | Rule | Scored |
|---|---|---|---|
| SPF | Public DNS TXT record on the domain | CERTIN-NES.4 | Yes |
| DMARC | Public DNS TXT record at `_dmarc.<domain>` | CERTIN-NES.4 | Yes |
| DKIM | Public DNS TXT record at common selector names. A missing result is "not found on common selectors", not a failure, because the selector name cannot be known from outside. | CERTIN-NES.4 | Only when found (never counted against the firm) |
| TLS certificate | Certificate presented on port 443 of the domain: valid, matches the name, days to expiry | **No specific CERT-In rule was found that requires this.** Shown as good practice. | No (info) |
| HTTP security headers | Response headers from one HTTPS GET of the home page: HSTS, Content-Security-Policy, X-Content-Type-Options, X-Frame-Options, Referrer-Policy | **No specific CERT-In rule was found that requires these headers.** Shown as good practice. | No (info) |

All checks read only public information, make no login attempts, scan no ports
and run only after the user confirms they own the domain.

## 6. Gate check

- Scored rules: CERTIN-D1, D2, D3, D4, EAM.1, NES.1, NES.2, NES.3, NES.4, EMS.1,
  EMS.2, EMS.4, SC.3, PM.1, PM.2, IM.1, IM.2, AT.1, DPBP.1, DPBP.2, RPP.1, RPP.2,
  RPP.3, ACIM.1, ACIM.3 (25 rules).
- Every scored rule above is VERIFIED and carries a direction or control number
  and a source link. `tests/test_rulebook.py` checks the code against this file.

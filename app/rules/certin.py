"""CERT-In Directions (mandatory) and MSME baseline controls (guidance) - scored rules.

Mirror of docs/RULEBOOK_CERTIN.md. tests/test_rulebook.py keeps the two in step.
"""
from __future__ import annotations

from .base import Rule, Source

DIR = Source(
    "DIR",
    "CERT-In Directions No. 20(3)/2022-CERT-In, 28 April 2022 (IT Act s.70B(6))",
    "https://www.cert-in.org.in/PDF/CERT-In_Directions_70B_28.04.2022.pdf",
)
MSME = Source(
    "MSME",
    "CERT-In 15 Elemental Cyber Defense Controls for MSMEs, Version 1.0, 1 September 2025",
    "https://www.cert-in.org.in/PDF/Elemental_Cyber_Defense_Controls_for_MSME.pdf",
)

S_BACKUP = "1. Backups"
S_PASSWORDS = "2. Passwords and MFA"
S_PATCHING = "3. Patching and software"
S_EMAIL = "4. Email security"
S_TRAINING = "5. Staff training"
S_INCIDENT = "6. Incident plan and reporting"
S_LOGS = "7. Logs and clocks"
S_DEVICES = "8. Devices and network"


def _g(id, section, title, requirement, control, weight, effort, question, evidence, fix, **kw) -> Rule:
    return Rule(id=id, section=section, title=title, requirement=requirement, citation=control,
                source=MSME, weight=weight, effort=effort, question=question, evidence=evidence,
                fix=fix, kind="guidance", **kw)


def _d(id, section, title, requirement, direction, effort, question, evidence, fix, **kw) -> Rule:
    return Rule(id=id, section=section, title=title, requirement=requirement, citation=direction,
                source=DIR, weight=3, effort=effort, question=question, evidence=evidence,
                fix=fix, kind="law", **kw)


CERTIN_RULES: list[Rule] = [
    # ------------------------------------------------------------------ backups
    _g("CERTIN-DPBP.1", S_BACKUP, "Regular, encrypted, offsite backups",
       "Back up on a regular schedule (daily or weekly) and keep encrypted copies offsite and offline.",
       "Control 10, DPBP.1", 3, "Medium",
       "Are your important files backed up automatically at least weekly, with an encrypted copy kept "
       "away from the office network?",
       "Backup job settings; where copies are kept.",
       "Set an automatic daily backup to an encrypted cloud or external drive, and keep one copy disconnected."),
    _g("CERTIN-DPBP.2", S_BACKUP, "Tested restore",
       "Test restoring from backup periodically.",
       "Control 10, DPBP.2", 2, "Low",
       "Have you restored a file from backup in the last six months to prove it works?",
       "Date of last restore test.",
       "Restore one folder from backup today and note the date. Repeat every six months."),
    # ---------------------------------------------------------------- passwords
    _g("CERTIN-RPP.1", S_PASSWORDS, "Strong, unique passwords",
       "Enforce strong, unique passwords (minimum 8 to 12 characters, mixed character types), set "
       "expiry, restrict reuse, and tell staff not to share credentials.",
       "Control 12, RPP.1", 2, "Low",
       "Does everyone use strong, different passwords for work accounts (for example through a password manager)?",
       "Password policy; password manager in use.",
       "Set a minimum length of 12 in your email and cloud admin settings and roll out a password manager."),
    _g("CERTIN-RPP.2", S_PASSWORDS, "Account lockout",
       "Lock accounts temporarily after 3 to 5 failed login attempts.",
       "Control 12, RPP.2", 2, "Low",
       "Do work accounts lock for a while after a few wrong password attempts?",
       "Lockout setting.",
       "Switch on account lockout (3 to 5 attempts) in your email, cloud and Windows settings."),
    _g("CERTIN-RPP.3", S_PASSWORDS, "Multi-factor authentication",
       "Switch on Multi-Factor Authentication for all critical systems, admin accounts and remote access.",
       "Control 12, RPP.3", 3, "Low",
       "Is MFA (a code or app prompt as well as a password) switched on for email, cloud storage, "
       "banking and all admin accounts?",
       "MFA status for each system.",
       "Switch on MFA for every email and cloud account this week, starting with partners and admins."),
    _g("CERTIN-ACIM.1", S_PASSWORDS, "No shared accounts",
       "Give each person their own user ID; no shared accounts.",
       "Control 13, ACIM.1", 2, "Medium",
       "Does every person have their own login, with no shared usernames and passwords?",
       "User list.",
       "Create individual accounts and retire shared ones such as 'office' or 'admin'."),
    _g("CERTIN-ACIM.3", S_PASSWORDS, "Access removed when people leave",
       "Review access at least quarterly and immediately on role change or exit, using an offboarding checklist.",
       "Control 13, ACIM.3", 2, "Low",
       "When someone leaves or changes role, is their access removed the same day, and do you review "
       "access every quarter?",
       "Offboarding checklist; date of last review.",
       "Write a one-page leaver checklist (email, cloud, laptop, keys) and set a quarterly calendar reminder."),
    # ----------------------------------------------------------------- patching
    _g("CERTIN-PM.1", S_PATCHING, "Security updates applied",
       "Regularly apply security patches and updates to operating systems, applications and firmware.",
       "Control 5, PM.1", 3, "Low",
       "Are automatic updates switched on for computers, phones, browsers and the office router?",
       "Update settings; last update dates.",
       "Switch on automatic updates everywhere and update the router firmware."),
    _g("CERTIN-PM.2", S_PATCHING, "Watching security advisories",
       "Watch vendor and CERT-In advisories for new patches and vulnerabilities.",
       "Control 5, PM.2", 2, "Low",
       "Does someone watch CERT-In and vendor security advisories for the software you use?",
       "Advisory subscription or bookmark; named person.",
       "Name one person to check CERT-In advisories at cert-in.org.in weekly."),
    _g("CERTIN-EMS.2", S_PATCHING, "Only licensed, authorised software",
       "Do not use pirated or unauthorised software; only authorised people install software.",
       "Control 3, EMS.2", 2, "Medium",
       "Is all software licensed, and can only an authorised person install new software?",
       "Software list; who has admin rights.",
       "Remove unlicensed software and take admin rights away from day-to-day user accounts."),
    # -------------------------------------------------------------------- email
    _g("CERTIN-NES.4", S_EMAIL, "SPF, DKIM and DMARC",
       "Protect email from phishing and spoofing using SPF, DKIM and DMARC.",
       "Control 2, NES.4", 2, "Medium",
       "Has your email domain been set up with SPF, DKIM and DMARC so that others cannot send email pretending to be you?",
       "DNS records for the email domain.",
       "Ask your email provider or IT helper to publish SPF, DKIM and DMARC records. Run the domain check to confirm.",
       help="Not sure? Answer 'Partly' and run the domain check on the report page."),
    # ----------------------------------------------------------------- training
    _g("CERTIN-AT.1", S_TRAINING, "Awareness training twice a year",
       "Run basic cybersecurity awareness training at least twice a year for all employees and "
       "contractors (phishing, passwords, social engineering, safe internet and email use).",
       "Control 8, AT.1", 2, "Medium",
       "Do all staff get basic cyber security training at least twice a year?",
       "Training dates and attendance.",
       "Book two 45-minute sessions a year covering phishing, passwords and safe handling of client files."),
    # ----------------------------------------------------------------- incident
    _g("CERTIN-IM.1", S_INCIDENT, "Written incident response plan",
       "Write a formal Incident Response Plan covering reporting, containment, investigation, "
       "recovery and communication.",
       "Control 6, IM.1", 2, "Medium",
       "Do you have a written plan for what to do in a cyber incident (who to call, how to contain it, how to recover)?",
       "The plan.",
       "Start from the Breach Response Plan in the Compliance Kit and add IT recovery steps."),
    _g("CERTIN-IM.2", S_INCIDENT, "Plan tested",
       "Test the Incident Response Plan regularly.",
       "Control 6, IM.2", 2, "Medium",
       "Have you practised the plan (for example a one-hour table-top exercise) in the last year?",
       "Date and notes of last exercise.",
       "Run a one-hour table-top exercise: 'a partner's laptop is stolen' or 'ransomware on the file server'."),
    _d("CERTIN-D2", S_INCIDENT, "Report incidents to CERT-In within 6 hours",
       "Report the cyber incidents listed in Annexure I to CERT-In within 6 hours of noticing them "
       "or being told about them (incident@cert-in.org.in, phone 1800-11-4949).",
       "Direction (ii) and Annexure I", "Low",
       "Does someone know that listed cyber incidents must be reported to CERT-In within 6 hours, and how to do it?",
       "Incident plan naming the reporter, the 6-hour clock and CERT-In contact details.",
       "Add the CERT-In reporting step and contact details to your incident plan and name who reports."),
    _d("CERTIN-D3", S_INCIDENT, "Point of Contact registered with CERT-In",
       "Designate a Point of Contact for CERT-In and send the details to info@cert-in.org.in in the "
       "Annexure II format; keep them updated.",
       "Direction (iii) and Annexure II", "Low",
       "Have you named a Point of Contact for CERT-In and emailed the details to CERT-In?",
       "Copy of the Point of Contact email.",
       "Email name, designation, organisation, address, email and phone numbers to info@cert-in.org.in."),
    # --------------------------------------------------------------------- logs
    _d("CERTIN-D4", S_LOGS, "Logs kept for 180 days in India",
       "Switch on logs for all IT systems and keep them securely for a rolling 180 days, stored "
       "within India.",
       "Direction (iv)", "High",
       "Are logs switched on for your router or firewall, servers and cloud accounts, and kept for at least 180 days in India?",
       "Log settings; retention period; storage location.",
       "Switch on logging on the router and cloud admin consoles, set retention to 180 days or more, "
       "and confirm the storage region with each provider.",
       help="DPDP Rules r.6(1)(e) separately asks for one year of access logs for personal data."),
    _d("CERTIN-D1", S_LOGS, "Clocks synchronised to Indian standard time servers",
       "Synchronise the clocks of all IT systems with the NTP server of NIC or NPL, or an NTP "
       "server traceable to them.",
       "Direction (i)", "Low",
       "Are the clocks on your computers, servers and router set to synchronise automatically with "
       "NIC or NPL time servers (or a source traceable to them)?",
       "Time-sync setting on each system.",
       "Ask your IT helper to point time synchronisation at NIC or NPL time servers."),
    # ------------------------------------------------------------------ devices
    _g("CERTIN-EAM.1", S_DEVICES, "List of devices, software and data",
       "Keep one up-to-date inventory of all hardware, software and information assets, with "
       "sensitive ones labelled.",
       "Control 1, EAM.1", 2, "Medium",
       "Do you keep an up-to-date list of all laptops, phones, servers, software and where sensitive data is kept?",
       "Asset list.",
       "Make a one-sheet list: device, user, serial number, software, what client data it holds."),
    _g("CERTIN-NES.1", S_DEVICES, "Firewall on the network and each computer",
       "Use a properly configured firewall at the network edge and switch on the firewall on each computer.",
       "Control 2, NES.1", 2, "Low",
       "Is a firewall switched on at the office internet connection and on every computer?",
       "Router or firewall settings; computer firewall status.",
       "Check the built-in firewall is on for every computer and that the router firewall is enabled."),
    _g("CERTIN-NES.2", S_DEVICES, "Secure office Wi-Fi",
       "Secure Wi-Fi with WPA2/WPA3 and strong passwords, no default credentials, and a separate guest network.",
       "Control 2, NES.2", 2, "Low",
       "Is the office Wi-Fi protected with WPA2 or WPA3 and a strong password, with a separate network for guests?",
       "Wi-Fi settings.",
       "Set WPA2/WPA3, change the Wi-Fi password and create a guest network for clients and visitors."),
    _g("CERTIN-NES.3", S_DEVICES, "Secure remote access",
       "Use an encrypted VPN with MFA for remote access.",
       "Control 2, NES.3", 2, "Medium",
       "If people reach office systems from outside, do they use an encrypted VPN with MFA?",
       "VPN settings.",
       "Replace any open remote-desktop access with a VPN that requires MFA.",
       help="Choose 'Not applicable' if nobody connects to office systems remotely.", allow_na=True),
    _g("CERTIN-EMS.1", S_DEVICES, "Antivirus on every device",
       "Install licensed antivirus or endpoint protection on all devices; do not disable built-in OS security.",
       "Control 3, EMS.1", 2, "Low",
       "Does every computer have antivirus or endpoint protection switched on and updating?",
       "Antivirus status per device.",
       "Confirm the built-in or licensed antivirus is on and updating on each computer."),
    _g("CERTIN-EMS.4", S_DEVICES, "USB and removable media controlled",
       "Restrict USB and removable media; consider disabling autorun.",
       "Control 3, EMS.4", 2, "Medium",
       "Is the use of USB drives restricted or controlled, with autorun switched off?",
       "Device policy.",
       "Disable autorun, and allow only firm-issued encrypted USB drives."),
    _g("CERTIN-SC.3", S_DEVICES, "Default passwords changed",
       "Remove unused software and change all default passwords and settings before use.",
       "Control 4, SC.3", 2, "Low",
       "Have the default admin passwords been changed on the router, printers, CCTV and other office devices?",
       "Confirmation for each device.",
       "Change the admin password on the router, printers and CCTV recorder today."),
]

CERTIN_BY_ID = {r.id: r for r in CERTIN_RULES}

UNVERIFIED = [
    ("CERTIN-U1", "Whether a given small firm (for example a partnership or LLP law firm) is a 'body corporate' "
                  "covered by the 28 April 2022 Directions. Ask your lawyer. The Health Check treats the "
                  "Directions as applicable so that nothing is missed."),
    ("CERTIN-U2", "The exact penalty amount under IT Act s.70B(7), and any later extension of the start date for MSMEs."),
    ("TLS/headers", "No specific CERT-In rule was found that requires a particular TLS or HTTP header setup. "
                    "These checks are shown as good practice and are not scored."),
]

APPLICABILITY_NOTE = (
    "Directions D1 to D4 are mandatory for 'service providers, intermediaries, data centres, body corporate "
    "and Government organisations'. Whether your firm is a 'body corporate' is for your lawyer to confirm. "
    "All other items are CERT-In baseline guidance for MSMEs, not law."
)

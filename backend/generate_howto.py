"""
Generates CyberAudit_HowToUse.pdf — a visual step-by-step usage guide
with screenshots from the actual running application.
Run: python generate_howto.py
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (  # type: ignore[import-untyped]
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,  # type: ignore[import-untyped]
    HRFlowable, PageBreak, Image, KeepTogether  # type: ignore[import-untyped]
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os, glob

OUTPUT = os.path.join(os.path.dirname(__file__), "..", "CyberAudit_HowToUse.pdf")
BRAIN  = r"C:\Users\nisha\.gemini\antigravity\brain\6035bbeb-aabf-4f84-9d71-81da11d7eccc"

# Direct screenshot paths (fresh captures March 2026)
SHOTS = {
    "live_feed":   "live_threat_feed_new_1773950060430.png",
    "explain":     "explain_modal_new_1773950087621.png",
    "analytics":   "ai_analytics_new_1773950105311.png",
    "verifier":    "verifier_new_1773950106306.png",
    "profiler":    "profiler_new_1773950112916.png",
    "forensics":   "forensics_new_1773950128492.png",
    "settings":    "settings_new_1773950129170.png",
}

def find_shot(key):
    path = os.path.join(BRAIN, SHOTS.get(key, ""))
    return path if os.path.exists(path) else None

# ── Colours ────────────────────────────────────────────────────────────────────
CYAN   = colors.HexColor("#00c8ff")
DARK   = colors.HexColor("#0d0d18")
MID    = colors.HexColor("#111128")
WHITE  = colors.white
GREY   = colors.HexColor("#64748b")
GREEN  = colors.HexColor("#00ff87")
AMBER  = colors.HexColor("#ffd700")
RED    = colors.HexColor("#ff003c")

# ── Styles ─────────────────────────────────────────────────────────────────────
base = getSampleStyleSheet()
def s(name, **kw): return ParagraphStyle(name, parent=base["Normal"], **kw)

H1   = s("H1", fontSize=24, textColor=CYAN, fontName="Helvetica-Bold",
          spaceAfter=4, spaceBefore=16)
H2   = s("H2", fontSize=14, textColor=WHITE, fontName="Helvetica-Bold",
          spaceAfter=4, spaceBefore=12)
H3   = s("H3", fontSize=11, textColor=CYAN, fontName="Helvetica-Bold",
          spaceAfter=3, spaceBefore=8)
BOD  = s("BOD", fontSize=10, textColor=colors.HexColor("#cbd5e1"),
          spaceAfter=4, leading=15)
COD  = s("COD", fontSize=8, textColor=GREEN, fontName="Courier",
          backColor=MID, spaceAfter=6, leading=12)
NUM  = s("NUM", fontSize=28, textColor=CYAN, fontName="Helvetica-Bold",
          alignment=TA_CENTER)
BUL  = s("BUL", fontSize=10, textColor=colors.HexColor("#cbd5e1"),
          leftIndent=16, spaceAfter=3, leading=14)
CAP  = s("CAP", fontSize=28, textColor=CYAN, fontName="Helvetica-Bold",
          alignment=TA_CENTER, spaceAfter=6)
SUB2 = s("SUB2", fontSize=12, textColor=GREY, alignment=TA_CENTER, spaceAfter=30)
TIP  = s("TIP", fontSize=9, textColor=AMBER, fontName="Helvetica-Oblique",
          backColor=colors.HexColor("#1a1600"), leftIndent=10,
          borderPadding=(4,8,4,8), spaceAfter=8, leading=14)

def hr(): return HRFlowable(width="100%", thickness=0.5, color=CYAN,
                             spaceAfter=6, spaceBefore=4)
def sp(n=1): return Spacer(1, n*0.3*cm)
def h1(t): return Paragraph(t, H1)
def h2(t): return Paragraph(t, H2)
def h3(t): return Paragraph(t, H3)
def p(t):  return Paragraph(t, BOD)
def bul(t):return Paragraph(f"• &nbsp;{t}", BUL)
def cod(t):return Paragraph(t.replace("\n","<br/>").replace(" ","&nbsp;"), COD)
def tip(t):return Paragraph(f"💡 &nbsp;{t}", TIP)

def screenshot(pattern, caption, width=15*cm):
    path = find_shot(pattern)
    if not path:
        return p(f"[Screenshot: {caption}]")
    img = Image(path, width=width, height=width*0.55)
    cap = Paragraph(caption, s("ic", fontSize=8, textColor=GREY,
                                alignment=TA_CENTER, spaceAfter=6))
    return KeepTogether([img, cap, sp(0.5)])

def step_box(number, title, items):
    """A numbered step card."""
    elems = []
    elems.append(Paragraph(f"<b><font color='#00c8ff'>Step {number}</font> — {title}</b>", H2))
    for item in items:
        elems.append(bul(item))
    return KeepTogether(elems)

# ── Document ───────────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm,
    topMargin=2.5*cm, bottomMargin=2*cm,
    title="CyberAudit — How To Use Guide",
)

story = []

# ── COVER ──────────────────────────────────────────────────────────────────────
story += [
    sp(6),
    Paragraph("CyberAudit", CAP),
    Paragraph("How To Use — Complete Step-by-Step Guide", SUB2),
    hr(),
    Paragraph("With Live Screenshots from the Running Application",
              s("cv", fontSize=10, textColor=GREY, alignment=TA_CENTER)),
    sp(4), PageBreak(),
]

# ── STARTING THE SYSTEM ────────────────────────────────────────────────────────
story += [h1("Part 1: Starting the System"), hr()]
story.append(p("Every time you want to use CyberAudit, open <b>3 CMD windows</b> and run one command in each:"))
story.append(sp())

start_steps = [
    ("CMD Window 1", "Start the Python Backend",
     "uvicorn main:app --reload --port 8000",
     "e:\\Blockchain project\\backend",
     "Starts the AI + API server. Wait for 'Application startup complete.'"),
    ("CMD Window 2", "Start the React Frontend",
     "npm run dev",
     "e:\\Blockchain project\\frontend",
     "Starts the web UI. Shows 'Local: http://localhost:5173'."),
    ("CMD Window 3", "Seed Demo Data (first time only)",
     "python simulate_events.py",
     "e:\\Blockchain project\\backend",
     "Sends 220 realistic cybersecurity events. Wait for 'Done: 220 succeeded'."),
]

for win, title, cmd, cwd, desc in start_steps:
    story.append(KeepTogether([
        h3(f"{win} — {title}"),
        p(f"<b>Folder:</b> {cwd}"),
        cod(cmd),
        p(f"<i>{desc}</i>"),
        sp(0.5),
    ]))

story.append(sp())
story.append(tip("MongoDB runs as a Windows service automatically — no separate command needed. If needed, use Admin CMD: net start MongoDB"))
story.append(sp())
story.append(h3("Then open your browser:"))
story.append(cod("http://localhost:5173"))
story.append(sp())
story.append(h3("If you need to reset data (avoid duplicates):"))
story.append(cod("cd \"e:\\Blockchain project\\backend\"\npython clear_db.py\npython simulate_events.py"))
story.append(PageBreak())

# ── PAGE 1: LIVE THREAT FEED ───────────────────────────────────────────────────
story += [h1("Part 2: Using the Dashboard"), hr(),
          h2("Page 1 — Live Threat Feed"), sp(0.5)]

story.append(screenshot("live_feed", "Live Threat Feed — http://localhost:5173/"))
story.append(sp())

story.append(p("This is your <b>main command center</b>. It shows every security event as it happens."))
story.append(sp())

story += [
    h3("What you see on this page:"),
    bul("<b>Total Events</b> — how many events are stored in total"),
    bul("<b>High Severity</b> — count of CRITICAL + HIGH events that need attention"),
    bul("<b>Anomalies</b> — events flagged by the Isolation Forest AI as statistically unusual"),
    bul("<b>Avg Risk Score</b> — average danger level (0–100) across all events"),
    bul("<b>Event Stream</b> — live feed of each event with severity badge, threat label, user, IP, risk bar"),
    sp(),
    h3("How to read an event card:"),
    bul("<b>GREEN badge (LOW/INFO)</b> — normal or low-risk activity"),
    bul("<b>YELLOW badge (MEDIUM)</b> — suspicious, worth investigating"),
    bul("<b>ORANGE/RED badge (HIGH/CRITICAL)</b> — active threat, take action"),
    bul("<b>⚠ ANOMALY tag</b> — AI flagged this as statistically unusual (even if severity looks low)"),
    bul("<b>Probe / DoS / R2L / U2R</b> — threat classification from Random Forest AI"),
    bul("<b>Risk bar</b> — visual 0–100 score. Red = dangerous, Green = safe"),
    sp(),
    h3("[NEW] Using the AI Explain Button:"),
    bul("HIGH and CRITICAL event cards show a blue '🤖 Explain' button"),
    bul("Click it — a modal opens showing AI-generated analysis"),
    bul("<b>Summary</b> — plain-English description of what happened"),
    bul("<b>Attack Pattern</b> — how the attacker operates"),
    bul("<b>MITRE ATT&CK</b> — official technique ID (e.g. T1110.001 Brute Force)"),
    bul("<b>Recommended Action</b> — step-by-step response for your team"),
    bul("<b>Why Flagged</b> — the ML model's reasoning"),
    bul("Second click on the same event loads instantly from cache"),
    sp(),
    tip("Click the Refresh button top-right to reload the latest events from the database."),
    sp(),
]

story += [
    h3("[NEW] AI Explain Modal — What it looks like:"),
    screenshot("explain", "AI Threat Explanation modal showing MITRE ATT\u0026CK analysis"),
    sp(0.3),
]

story.append(PageBreak())

# ── PAGE 2: AI ANALYTICS ───────────────────────────────────────────────────────
story += [h2("Page 2 — AI Analytics"), sp(0.5)]
story.append(screenshot("analytics", "AI Analytics — http://localhost:5173/analytics"))
story.append(sp())

story.append(p("This page shows <b>charts and intelligence reports</b> based on all stored events."))
story.append(sp())

story += [
    h3("Charts on this page:"),
    bul("<b>Threat Type Distribution</b> — pie chart showing Normal vs Probe vs DoS vs R2L vs U2R breakdown"),
    bul("<b>Risk Score Timeline</b> — line chart showing how the average danger level changed over time"),
    bul("<b>Top Risky IPs</b> — bar chart of source IPs with the highest average risk scores"),
    bul("<b>Top Risky Users</b> — bar chart of user accounts causing the most risk"),
    bul("<b>Hourly Activity Heatmap</b> — which hours of the day see the most suspicious events"),
    sp(),
    h3("How to use it:"),
    bul("Look at the Threat Distribution to understand your attack mix (are most attacks probes or intrusions?)"),
    bul("Use the Risk Timeline to spot when attacks spiked"),
    bul("Check Top Risky IPs to block repeat offenders at the firewall"),
    bul("Check Top Risky Users to identify compromised accounts or insider threats"),
    tip("Use this page for weekly security briefings or to explain the security situation to management."),
    sp(),
]

story.append(PageBreak())

# ── PAGE 3: VERIFIER ──────────────────────────────────────────────────────────
story += [h2("Page 3 — Blockchain Verifier"), sp(0.5)]
story.append(screenshot("verifier", "Blockchain Verifier — http://localhost:5173/verify"))
story.append(sp())

story.append(p("This page <b>proves whether a log entry is authentic</b> by comparing it against the blockchain. "
               "If anyone edited the log after it was saved, this page will catch it."))
story.append(sp())

story += [
    h3("How to verify a log:"),
    bul("Step 1: Go to the Forensics page, click 'Apply Filters' to load events"),
    bul("Step 2: Copy the Log ID from any event row (it looks like: 67abc123def456...)"),
    bul("Step 3: Come to this page, paste the Log ID in the input field"),
    bul("Step 4: Click 'Verify' — the system recomputes the SHA-256 hash and checks the blockchain"),
    sp(),
    h3("Results:"),
    bul("<b>✅ VERIFIED</b> — The log is authentic. The hash from the database matches the hash on the Ethereum blockchain."),
    bul("<b>❌ TAMPERED</b> — Someone modified the log entry. The recomputed hash doesn't match the blockchain record."),
    sp(),
    tip("Use this after a security incident to prove in court or to management that the logs are unaltered evidence."),
    sp(),
]

story.append(PageBreak())

# ── PAGE 4: PROFILER ──────────────────────────────────────────────────────────
story += [h2("Page 4 — Behavioral Profiler"), sp(0.5)]
story.append(screenshot("profiler", "Behavioral Profiler — http://localhost:5173/profile"))
story.append(sp())

story.append(p("This page shows <b>per-user behavioral analysis</b>. The AI learns each user's normal "
               "behavior and flags when they deviate from it."))
story.append(sp())

story += [
    h3("How to use it:"),
    bul("Select a user from the dropdown (alice.smith, bob.jones, etc.)"),
    bul("See their Deviation Score (0–100): how far their recent behavior is from their normal baseline"),
    bul("See their Risk Timeline: how their personal risk score has changed over time"),
    bul("Read their Behavioral Flags: specific reasons why they were flagged"),
    sp(),
    h3("Common behavioral flags:"),
    bul("<b>New IP address detected</b> — user logged in from an IP they've never used before"),
    bul("<b>Unusual activity time</b> — activity at 3AM when user normally works 9AM–6PM"),
    bul("<b>High frequency event</b> — 50 failed logins when user normally has 2–3 per day"),
    bul("<b>Risk spike</b> — current risk score is 2x above their personal average"),
    sp(),
    tip("A high deviation score doesn't always mean the user is malicious — it could mean their account was compromised by an attacker."),
    sp(),
]

story.append(PageBreak())

# ── PAGE 5: FORENSICS ─────────────────────────────────────────────────────────
story += [h2("Page 5 — Forensic Report"), sp(0.5)]
story.append(screenshot("forensics", "Forensic Report — http://localhost:5173/forensics"))
story.append(sp())

story.append(p("This is your <b>investigation and reporting tool</b>. Filter events, dig deep into incidents, "
               "and export professional PDF reports."))
story.append(sp())

story += [
    h3("How to use the filters:"),
    bul("<b>Severity filter</b>: Choose CRITICAL, HIGH, MEDIUM, LOW, or INFO to focus on specific danger levels"),
    bul("<b>Threat Label filter</b>: Choose Probe, DoS, R2L, U2R to filter by attack type"),
    bul("<b>User ID filter</b>: Type a username (e.g. alice.smith) to see only their events"),
    bul("Click '<b>Apply Filters</b>' to load the matching events"),
    sp(),
    h3("Reading the table columns:"),
    bul("<b>Event</b> — description, user, IP, timestamp"),
    bul("<b>Severity</b> — colour-coded badge"),
    bul("<b>Risk</b> — number (0–100) + visual bar"),
    bul("<b>Threat</b> — AI classification label"),
    bul("<b>TX Hash</b> — blockchain transaction hash (if blockchain is connected)"),
    bul("<b>Anomaly</b> — YES (red) or No (green)"),
    sp(),
    h3("Exporting a PDF report:"),
    bul("Apply your filters first to get the events you want"),
    bul("Click the '<b>Export PDF</b>' button (top right)"),
    bul("A professional dark-themed PDF downloads with all event details + summary stats"),
    tip("Export a 'HIGH severity only' PDF after every incident — it becomes your official security report."),
    sp(),
]

story.append(PageBreak())

# ── PAGE 6: SETTINGS ─────────────────────────────────────────────────────────
story += [h2("Page 6 [NEW] — Settings"), sp(0.5)]
story.append(screenshot("settings", "Settings — http://localhost:5173/settings"))
story.append(sp())
story.append(p("This page lets you <b>configure the real-time alert system</b> and view alert history."))
story.append(sp())
story += [
    h3("What you can configure:"),
    bul("<b>Minimum Severity</b> — choose the lowest severity that triggers alerts"),
    bul("<b>Risk Score Threshold</b> — alerts fire when risk_score exceeds this value (0–100)"),
    bul("<b>Email Alerts</b> — enable and enter the recipient email address"),
    bul("<b>Slack Alerts</b> — enable and paste your Slack Incoming Webhook URL"),
    bul("<b>Trigger Rules</b> — 5 toggle switches to enable/disable individual alert rules"),
    bul("<b>Alert History feed</b> — scroll down to see the last 20 alerts that fired"),
    sp(),
    h3("5 Alert Trigger Rules:"),
    bul("<b>Severity Rule</b> — fires when severity ≥ your minimum threshold"),
    bul("<b>Risk Score Rule</b> — fires when risk_score > your threshold (e.g. 75)"),
    bul("<b>Anomaly Rule</b> — fires when Isolation Forest flags an anomaly at MEDIUM+ severity"),
    bul("<b>IP Rate Rule</b> — fires when same IP sends 5+ events in 60 seconds"),
    bul("<b>User Rate Rule</b> — fires when same user has 3+ HIGH events in 5 minutes"),
    sp(),
    tip("After clicking 'Save Settings', the next event will immediately use your new thresholds."),
    sp(),
]

story.append(PageBreak())

# ── COMMON WORKFLOWS ──────────────────────────────────────────────────────────
story += [h1("Part 3: Common Workflows"), hr()]

workflows = [
    ("Responding to an Active Attack",
     "Detecting and responding to a live brute-force attempt",
     [
         "Open Live Threat Feed — watch for HIGH/CRITICAL events in real time",
         "Look for repeated 'brute_force' or 'failed_login' events from the same IP",
         "Note the source IP address",
         "Go to AI Analytics → Top Risky IPs to confirm the IP is a repeat offender",
         "Go to Behavioral Profiler → check if any user account is being targeted",
         "Block the IP at your firewall/router level",
         "Go to Forensics → filter by that IP → Export PDF → send to your manager",
     ]),
    ("Investigating a Suspected Insider Threat",
     "A user is downloading sensitive data outside business hours",
     [
         "Go to Behavioral Profiler → select the suspected user",
         "Check their Deviation Score — high score confirms abnormal behavior",
         "Read the Behavioral Flags — look for 'Unusual activity time' + 'New IP'",
         "Go to Forensics → filter by User ID → look for 'data_exfiltration' events",
         "Copy a Log ID → go to Blockchain Verifier → confirm the log is VERIFIED (unaltered)",
         "Export PDF from Forensics as evidence for HR or legal team",
     ]),
    ("Producing a Weekly Security Report",
     "Create a summary for management every week",
     [
         "Go to AI Analytics → screenshot the Threat Distribution chart",
         "Note: total events, critical count, anomaly count, avg risk score",
         "Go to Forensics → no filters → Apply Filters → Export PDF",
         "The PDF has all events, summary stats, and full details — ready to present",
     ]),
    ("Proving Logs Haven't Been Altered (Compliance Audit)",
     "Demonstrating log integrity to auditors (GDPR, SOX, PCI-DSS)",
     [
         "Go to Forensics → apply no filters → load all events",
         "Pick 5 random events, copy their Log IDs",
         "Go to Blockchain Verifier → paste each ID → confirm VERIFIED",
         "This proves the audit trail is tamper-proof and legally admissible",
     ]),
]

for title, scenario, steps in workflows:
    story.append(KeepTogether([
        h2(title),
        p(f"<i>Scenario: {scenario}</i>"),
        sp(0.3),
        *[bul(f"Step {i+1}: {s}") for i, s in enumerate(steps)],
        sp(),
    ]))

# ── NEW: LLM EXPLAIN + ALERTS ─────────────────────────────────────────────────
story += [
    h2("[NEW] Using AI Threat Explanation"),
    p("<i>Scenario: You see a HIGH severity brute_force attack and want to understand it</i>"),
    sp(0.3),
    bul("Step 1: On the Live Threat Feed, find any HIGH or CRITICAL event card"),
    bul("Step 2: Click the blue '🤖 Explain' button on the card"),
    bul("Step 3: A modal opens — wait 3–10 seconds for AI analysis"),
    bul("Step 4: Read the 6 sections: Summary, Why Flagged, Attack Pattern, MITRE ATT&CK, Recommended Action, Confidence Reasoning"),
    bul("Step 5: Use the Recommended Action steps to respond to the threat"),
    bul("Step 6: Click the same event again — loads instantly from cache"),
    sp(),
    tip("The AI Explain feature works without an Anthropic API key — it uses built-in local analysis based on your log's own data."),
    sp(),
    h2("[NEW] Setting Up and Using Alerts"),
    p("<i>Scenario: You want to get email notifications when a critical attack is detected</i>"),
    sp(0.3),
    bul("Step 1: Go to Settings page (⚙ icon in navbar, or http://localhost:5173/settings)"),
    bul("Step 2: Set Minimum Severity to 'HIGH' and Risk Threshold to 75"),
    bul("Step 3: Enable 'Email Alerts' toggle — enter your Gmail address and App Password"),
    bul("Step 4: Enable 'Slack Alerts' toggle — paste your Slack Webhook URL"),
    bul("Step 5: Make sure all 5 Trigger Rules are enabled"),
    bul("Step 6: Click 'Save Settings' — green toast confirms success"),
    bul("Step 7: Run python simulate_events.py — alerts fire within seconds for HIGH/CRITICAL events"),
    bul("Step 8: Scroll down on Settings page to see Alert History feed"),
    sp(),
    tip("How to get Gmail App Password: Google Account → Security → 2-Step Verification → App Passwords → Mail"),
    sp(),
]

story.append(PageBreak())

# ── QUICK REFERENCE ───────────────────────────────────────────────────────────
story += [h1("Part 4: Quick Reference"), hr()]

story.append(h2("Severity Levels"))
sev = [
    ["Badge", "Score Range", "Meaning", "Action"],
    ["INFO",     "0–15",  "Normal activity",           "No action needed"],
    ["LOW",      "16–35", "Slightly unusual",           "Monitor, log for records"],
    ["MEDIUM",   "36–59", "Suspicious activity",        "Investigate within 24 hours"],
    ["HIGH",     "60–79", "Likely attack in progress",  "Respond within 1 hour"],
    ["CRITICAL", "80–100","Active breach/compromise",   "Immediate response required"],
]
t = Table(sev, colWidths=[2.5*cm, 3*cm, 5.5*cm, 5*cm])
t.setStyle(TableStyle([
    ("BACKGROUND",   (0,0),(-1,0), MID),
    ("TEXTCOLOR",    (0,0),(-1,0), CYAN),
    ("FONTNAME",     (0,0),(-1,0), "Helvetica-Bold"),
    ("FONTSIZE",     (0,0),(-1,-1), 9),
    ("TEXTCOLOR",    (0,1),(-1,-1), colors.HexColor("#cbd5e1")),
    ("ROWBACKGROUNDS",(0,1),(-1,-1), [DARK, MID]),
    ("GRID",         (0,0),(-1,-1), 0.25, GREY),
    ("PADDING",      (0,0),(-1,-1), 5),
]))
story += [t, sp()]

story.append(h2("Threat Labels (AI Classification)"))
thr = [
    ["Label",  "Full Name",                  "What it Means"],
    ["Normal", "Legitimate Traffic",          "Regular user activity — no concern"],
    ["Probe",  "Network Reconnaissance",      "Attacker mapping your network (port scans, pings)"],
    ["DoS",    "Denial of Service",           "Flooding attack to crash your services"],
    ["R2L",    "Remote to Local Intrusion",   "Attacker trying to gain unauthorized local access"],
    ["U2R",    "User to Root Escalation",     "Attacker trying to become administrator/root"],
]
t2 = Table(thr, colWidths=[2.5*cm, 5*cm, 8.5*cm])
t2.setStyle(TableStyle([
    ("BACKGROUND",   (0,0),(-1,0), MID),
    ("TEXTCOLOR",    (0,0),(-1,0), CYAN),
    ("FONTNAME",     (0,0),(-1,0), "Helvetica-Bold"),
    ("FONTSIZE",     (0,0),(-1,-1), 9),
    ("TEXTCOLOR",    (0,1),(-1,-1), colors.HexColor("#cbd5e1")),
    ("ROWBACKGROUNDS",(0,1),(-1,-1), [DARK, MID]),
    ("GRID",         (0,0),(-1,-1), 0.25, GREY),
    ("PADDING",      (0,0),(-1,-1), 5),
]))
story += [t2, sp()]

story.append(h2("URL Reference"))
urls = [
    ["URL", "Page"],
    ["http://localhost:5173/",          "Live Threat Feed (main dashboard)"],
    ["http://localhost:5173/analytics", "AI Analytics (charts)"],
    ["http://localhost:5173/verify",    "Blockchain Verifier"],
    ["http://localhost:5173/profile",   "Behavioral Profiler"],
    ["http://localhost:5173/forensics", "Forensic Report + PDF Export"],
    ["http://localhost:5173/settings",  "[NEW] Settings — Alert Config"],
    ["http://localhost:8000/docs",      "Backend API (Swagger interactive docs)"],
]
t3 = Table(urls, colWidths=[8*cm, 8*cm])
t3.setStyle(TableStyle([
    ("BACKGROUND",   (0,0),(-1,0), MID),
    ("TEXTCOLOR",    (0,0),(-1,0), CYAN),
    ("FONTNAME",     (0,0),(-1,0), "Helvetica-Bold"),
    ("FONTSIZE",     (0,0),(-1,-1), 9),
    ("TEXTCOLOR",    (0,1),(-1,-1), GREEN),
    ("ROWBACKGROUNDS",(0,1),(-1,-1), [DARK, MID]),
    ("GRID",         (0,0),(-1,-1), 0.25, GREY),
    ("PADDING",      (0,0),(-1,-1), 5),
]))
story += [t3, sp()]

# Footer
story += [
    hr(),
    Paragraph("CyberAudit — How To Use Guide  |  Generated March 2026",
              s("f", fontSize=8, textColor=GREY, alignment=TA_CENTER))
]

def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(DARK)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY)
    canvas.drawCentredString(A4[0]/2, 1.2*cm, f"Page {doc.page}")
    canvas.restoreState()

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF generated: {os.path.abspath(OUTPUT)}")

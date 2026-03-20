"""
Generates a downloadable PDF project guide for CyberAudit.
Run: python generate_docs.py
Output: CyberAudit_Project_Guide.pdf  (in the project root)
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (  # type: ignore[import-untyped]
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,  # type: ignore[import-untyped]
    HRFlowable, PageBreak  # type: ignore[import-untyped]
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "..", "CyberAudit_Project_Guide.pdf")

# ── Colour palette ─────────────────────────────────────────────────────────────
CYAN   = colors.HexColor("#00c8ff")
DARK   = colors.HexColor("#0d0d18")
MID    = colors.HexColor("#111128")
PURPLE = colors.HexColor("#8b5cf6")
GREEN  = colors.HexColor("#00ff87")
YELLOW = colors.HexColor("#ffd700")
RED    = colors.HexColor("#ff003c")
GREY   = colors.HexColor("#64748b")
WHITE  = colors.white

# ── Styles ─────────────────────────────────────────────────────────────────────
base = getSampleStyleSheet()

def style(name, parent="Normal", **kw):
    s = ParagraphStyle(name, parent=base[parent], **kw)
    return s

H1  = style("H1",  "Heading1", fontSize=26, textColor=CYAN,   spaceAfter=6,  spaceBefore=18, fontName="Helvetica-Bold")
H2  = style("H2",  "Heading2", fontSize=16, textColor=WHITE,  spaceAfter=4,  spaceBefore=14, fontName="Helvetica-Bold")
H3  = style("H3",  "Heading3", fontSize=12, textColor=CYAN,   spaceAfter=3,  spaceBefore=10, fontName="Helvetica-Bold")
BOD = style("BOD", "Normal",   fontSize=10, textColor=colors.HexColor("#cbd5e1"), spaceAfter=4, leading=15)
COD = style("COD", "Normal",   fontSize=8,  textColor=GREEN, fontName="Courier",
            backColor=MID, borderPadding=(4,6,4,6), spaceAfter=6, leading=12)
SUB = style("SUB", "Normal",   fontSize=9,  textColor=GREY,  spaceAfter=8,  fontName="Helvetica-Oblique")
BUL = style("BUL", "Normal",   fontSize=10, textColor=colors.HexColor("#cbd5e1"),
            leftIndent=18, spaceAfter=3, leading=14, bulletIndent=6)
CAP = style("CAP", "Normal",   fontSize=22, textColor=CYAN, fontName="Helvetica-Bold",
            alignment=TA_CENTER, spaceAfter=6)
SUB2= style("SUB2","Normal",   fontSize=12, textColor=GREY,  alignment=TA_CENTER, spaceAfter=30)

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=CYAN, spaceAfter=8, spaceBefore=4)

def h1(t): return Paragraph(t, H1)
def h2(t): return Paragraph(t, H2)
def h3(t): return Paragraph(t, H3)
def p(t):  return Paragraph(t, BOD)
def code(t):return Paragraph(t.replace("\n","<br/>").replace(" ","&nbsp;"), COD)
def sub(t): return Paragraph(t, SUB)
def sp(n=1):return Spacer(1, n*0.3*cm)
def bul(t): return Paragraph(f"• &nbsp;{t}", BUL)

def table(data, col_widths, header=True):
    t = Table(data, colWidths=col_widths)
    style_cmds = [
        ("BACKGROUND",  (0,0), (-1,0 if header else -1), MID),
        ("TEXTCOLOR",   (0,0), (-1,0), CYAN),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,-1), 9),
        ("TEXTCOLOR",   (0,1), (-1,-1), colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [DARK, MID]),
        ("GRID",        (0,0), (-1,-1), 0.25, GREY),
        ("PADDING",     (0,0), (-1,-1), 5),
        ("VALIGN",      (0,0), (-1,-1), "TOP"),
    ]
    t.setStyle(TableStyle(style_cmds))
    return t

# ── Build document ──────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm,
    topMargin=2.5*cm, bottomMargin=2*cm,
    title="CyberAudit Project Guide",
    author="AI-Generated Documentation",
)

story = []

# ─── COVER PAGE ────────────────────────────────────────────────────────────────
story += [
    sp(4),
    Paragraph("CyberAudit", CAP),
    Paragraph("AI-Powered Blockchain Audit Log System — v2.0", SUB2),
    hr(),
    Paragraph("Complete Project Guide — A to Z", style("cov","Normal",fontSize=14,
              textColor=GREY, alignment=TA_CENTER, spaceAfter=4)),
    Paragraph("Threat Detection · Blockchain Integrity · LLM Explanations · Real-Time Alerts · Docker", style("cov2","Normal",
              fontSize=10, textColor=colors.HexColor("#334155"), alignment=TA_CENTER)),
    sp(2),
    table([
        ["Feature", "Status"],
        ["ML Anomaly Detection (Isolation Forest)",         "✅ Included"],
        ["Threat Classification (Random Forest)",           "✅ Included"],
        ["Blockchain Integrity Verification",               "✅ Included"],
        ["LLM Threat Explanation (Claude + local fallback)","✅ NEW in v2.0"],
        ["Real-time Email + Slack Alert System",            "✅ NEW in v2.0"],
        ["Docker Containerization (docker-compose)",        "✅ NEW in v2.0"],
    ], [10*cm, 4*cm]),
    sp(2),
    PageBreak(),
]

# ─── 1. WHAT IS THIS PROJECT ───────────────────────────────────────────────────
story += [h1("1. What Is This Project?"), hr()]
story.append(p(
    "CyberAudit is an <b>enterprise-grade cybersecurity audit log platform</b> that monitors "
    "network events in real time, analyzes each one with machine-learning models to detect "
    "threats, and stores tamper-proof cryptographic proof of every log entry on an Ethereum "
    "blockchain. If anyone modifies or deletes a log after the fact, the system instantly "
    "detects the tampering."
))
story.append(sp())
story.append(p("<b>Think of it as:</b> A smart CCTV system for your entire network — every "
               "frame is analyzed by AI before it's saved, and the footage is locked on a "
               "blockchain that nobody — not even the admin — can alter."))
story.append(sp())

# ─── 2. REAL-WORLD USE CASE ────────────────────────────────────────────────────
story += [h1("2. Real-World Use Case"), hr()]
story.append(p("Any company running servers, handling user data, or subject to compliance "
               "regulation (HIPAA, GDPR, PCI-DSS, SOX) needs audit logs. Traditional logs have "
               "one fatal weakness: a skilled attacker with database access can delete or alter "
               "entries to hide their tracks. CyberAudit eliminates this weakness."))
story.append(sp())
story.append(h3("Scenario"))
for b in [
    "Employee alice.smith logs in at 3AM from an IP address never seen before",
    "A brute-force attack tries 5,000 password combinations in 10 seconds",
    "An insider copies 500MB of customer data to an external IP",
    "An attacker tries to escalate privileges to root on a web server",
]:
    story.append(bul(b))
story.append(sp())
story.append(p("Each event is captured, AI-analyzed, risk-scored (0–100), and locked on the "
               "blockchain in under 200ms. Security teams see it in real time on the dashboard."))
story.append(sp())

# ─── 3. SYSTEM ARCHITECTURE ───────────────────────────────────────────────────
story += [h1("3. System Architecture"), hr()]
story.append(p("The system has three layers that work together:"))
arch = [
    ["Layer", "Technology", "Role"],
    ["Smart Contract", "Solidity + Hardhat", "Stores SHA-256 hash of every log on Ethereum blockchain"],
    ["Backend API",    "Python FastAPI",     "Receives events, runs ML pipeline, saves to MongoDB + blockchain"],
    ["ML Models",      "Scikit-learn",       "Isolation Forest (anomaly) + Random Forest (threat classification)"],
    ["Database",       "MongoDB + Motor",    "Stores full log documents off-chain"],
    ["Frontend",       "React + Vite",       "Real-time dashboard with 5 pages"],
    ["Wallet Auth",    "MetaMask + Ethers.js","Ethereum wallet login, connect to Hardhat local network"],
]
story.append(table(arch, [3.5*cm, 4*cm, 8.5*cm]))
story.append(sp())

# ─── 4. DATA FLOW ─────────────────────────────────────────────────────────────
story += [h1("4. How Data Flows (Step by Step)"), hr()]
steps = [
    ("Step 1", "Event Arrives",        "A security event (login, attack, scan) is sent via POST /api/logs"),
    ("Step 2", "Anomaly Detection",    "Isolation Forest decides: is this statistically unusual? Returns anomaly score 0.0–1.0"),
    ("Step 3", "Threat Classification","Random Forest classifies: Normal / Probe / DoS / R2L / U2R with confidence %"),
    ("Step 4", "Risk Scoring",         "Combines threat label + anomaly score + event type + time of day → score 0–100"),
    ("Step 5", "Behavioral Profiling", "Compares event against user's historical baseline, flags deviations"),
    ("Step 6", "Blockchain Hash",      "SHA-256 hash of the entire log document written to Ethereum smart contract"),
    ("Step 7", "MongoDB Storage",      "Full log document saved to MongoDB"),
    ("Step 8", "SSE Broadcast",        "Event pushed in real-time to all connected dashboard browsers"),
]
for step, title, desc in steps:
    story.append(p(f"<b><font color='#00c8ff'>{step}</font> — {title}:</b> {desc}"))
story.append(sp())

# ─── 5. AI MODELS ─────────────────────────────────────────────────────────────
story += [h1("5. AI/ML Models Explained"), hr()]

story.append(h3("Isolation Forest (Anomaly Detection — Unsupervised)"))
story.append(p("Trained on 7,200 synthetic NSL-KDD-style network events. Learns the statistical "
               "shape of normal traffic. Any event that is difficult to isolate from normal "
               "clusters is flagged as an anomaly."))
for b in [
    "No labeled attack data needed — finds unknown/zero-day attack patterns",
    "Output: is_anomaly (true/false) + anomaly_score (0.0–1.0)",
    "Score closer to 1.0 = more anomalous",
]:
    story.append(bul(b))
story.append(sp())

story.append(h3("Random Forest (Threat Classification — Supervised)"))
story.append(p("Classifies every event into one of 5 NSL-KDD threat categories:"))
cats = [
    ["Class", "Meaning", "Examples"],
    ["Normal", "Legitimate traffic", "Successful login, file read, service start"],
    ["Probe",  "Network reconnaissance", "Port scan, ping sweep, service enumeration"],
    ["DoS",    "Denial of Service", "SYN flood, UDP flood, bandwidth exhaustion"],
    ["R2L",    "Remote to Local intrusion", "Brute force, password spray, unauthorized access"],
    ["U2R",    "User to Root privilege escalation", "Sudo exploit, kernel exploit, SUID abuse"],
]
story.append(table(cats, [2.5*cm, 5*cm, 8.5*cm]))
story.append(sp())

story.append(h3("Risk Scorer"))
story.append(p("Combines multiple signals into a single 0–100 risk score:"))
risk_map = [
    ["Score Range", "Severity", "Meaning"],
    ["0–15",  "INFO",     "Normal operations, no concern"],
    ["16–35", "LOW",      "Slightly unusual, worth noting"],
    ["36–59", "MEDIUM",   "Suspicious, investigate soon"],
    ["60–79", "HIGH",     "Likely attack, respond quickly"],
    ["80–100","CRITICAL", "Active breach, immediate action"],
]
story.append(table(risk_map, [3*cm, 3*cm, 10*cm]))
story.append(sp())

story.append(h3("Behavioral Profiler"))
story.append(p("Maintains a rolling baseline for each user: their usual IPs, working hours, "
               "event type frequencies, and average risk. Flags statistical deviations like:"))
for b in [
    "New IP address never seen before for this user",
    "Login at an unusual hour (e.g. 3AM when typical is 9AM–6PM)",
    "High frequency of a particular event type (e.g. 50 failed logins in 5 mins)",
    "Risk score 2x above user's personal average",
]:
    story.append(bul(b))
story.append(sp())

# ─── 6. BLOCKCHAIN ──────────────────────────────────────────────────────────────
story += [h1("6. Why Blockchain? (The Core Innovation)"), hr()]
story.append(p("The blockchain serves as an <b>immutable receipt printer</b>. When a log is saved:"))
story.append(code(
    "hash = SHA-256( entire log document JSON )\n"
    "smart_contract.store(log_id, hash, risk_score, threat_label, timestamp)"
))
story.append(p("The smart contract is deployed on Ethereum (local Hardhat node). Once written, "
               "no admin password, no SQL query, no system-level access can alter it."))
story.append(sp())
story.append(p("<b>Verification flow (Blockchain Verifier page):</b>"))
for b in [
    "User provides a Log ID",
    "System fetches the current log from MongoDB and recomputes SHA-256",
    "System fetches the original hash from the smart contract on-chain",
    "If hashes match → ✅ VERIFIED (log is authentic)",
    "If hashes differ → ❌ TAMPERED (log was modified after being saved)",
]:
    story.append(bul(b))
story.append(sp())
story.append(p("<b>Use cases:</b> Legal evidence preservation, GDPR compliance, PCI-DSS audit "
               "trails, insurance claims, SOX financial audit logs."))

story.append(PageBreak())

# ─── 7. DASHBOARD PAGES ────────────────────────────────────────────────────────
story += [h1("7. The 6 Dashboard Pages"), hr()]
pages = [
    ("Live Threat Feed  /",
     "Real-time event stream. Each card shows severity, threat label, anomaly flag, risk bar. "
     "HIGH/CRITICAL cards have an AI Explain button. Top stats: Total Events, High Severity, Anomalies, Avg Risk.",
     "Incident response triage. Watching attacks live."),
    ("AI Analytics  /analytics",
     "Charts: Threat Distribution pie, Risk Timeline line, Top Risky IPs bar, Top Risky Users bar, Hourly Heatmap.",
     "Weekly security briefings. Spotting attack trends."),
    ("Blockchain Verifier  /verify",
     "Enter a Log ObjectID → recomputes SHA-256 → compares with on-chain hash → VERIFIED or TAMPERED.",
     "Forensic investigations. Proving log integrity in audits."),
    ("Behavioral Profiler  /profile",
     "Select a user → see deviation score, risk timeline, known IPs, behavioral flags.",
     "Insider threat detection. Compromised account detection."),
    ("Forensic Report  /forensics",
     "Filter events by severity/threat/user. Paginated table. One-click PDF export. AI Explain buttons.",
     "Post-incident reports. Management briefings."),
    ("Settings  /settings",
     "Configure alert thresholds (severity level, risk score), enable Email/Slack, view alert history feed.",
     "Day-to-day alert tuning. On-call engineer setup."),
]
page_data = [["Page", "What It Shows", "Best Used For"]]
for name, what, use in pages:
    page_data.append([name, what, use])
story.append(table(page_data, [4*cm, 7*cm, 5*cm]))
story.append(sp())

# ─── 8. HOW TO START ──────────────────────────────────────────────────────────
story += [h1("8. How to Start the Project"), hr()]
story.append(sub("Open 3 CMD windows and run one command in each."))
story.append(sp())

cmds = [
    ("CMD Terminal 1 — FastAPI Backend (required)",
     "cd \"e:\\Blockchain project\\backend\"\nuvicorn main:app --reload --port 8000"),
    ("CMD Terminal 2 — React Frontend (required)",
     "cd \"e:\\Blockchain project\\frontend\"\nnpm run dev"),
    ("CMD Terminal 3 — Seed Demo Data (first time only)",
     "cd \"e:\\Blockchain project\\backend\"\npython simulate_events.py"),
]
for title, cmd in cmds:
    story.append(h3(title))
    story.append(code(cmd))
    story.append(sp())

story.append(h3("Then open your browser:"))
story.append(code("http://localhost:5173"))
story.append(sp())

story.append(h3("Note: MongoDB"))
story.append(p("MongoDB runs as a Windows service automatically. No separate command needed. "
               "If it is not running, use an Admin CMD: net start MongoDB"))
story.append(sp())

story.append(h3("Clear and reset data:"))
story.append(code("cd \"e:\\Blockchain project\\backend\"\npython clear_db.py\npython simulate_events.py"))
story.append(sp())

story += [h2("8b. Run with Docker (One Command)"), hr()]
story.append(p("Requires Docker Desktop installed. Creates, links, and starts all 4 containers automatically."))
story.append(code("docker-compose up --build"))
for b in [
    "http://localhost:80 → CyberAudit dashboard (nginx)",
    "http://localhost:8000 → FastAPI backend",
    "http://localhost:8000/docs → Swagger API explorer",
    "http://localhost:8545 → Hardhat blockchain RPC",
    "http://localhost:27017 → MongoDB",
]:
    story.append(bul(b))
story.append(sp())
story.append(h3("Docker .env (project root):"))
story.append(code(
    "ANTHROPIC_API_KEY=sk-ant-...\n"
    "SMTP_USER=your@gmail.com\n"
    "SMTP_PASSWORD=xxxx xxxx xxxx xxxx\n"
    "SLACK_WEBHOOK_URL=https://hooks.slack.com/services/..."
))

story.append(PageBreak())

# ─── 9. API REFERENCE ─────────────────────────────────────────────────────────
story += [h1("9. API Reference"), hr()]
story.append(p("The backend runs at <b>http://localhost:8000</b>. "
               "Full interactive docs at <b>http://localhost:8000/docs</b>"))
story.append(sp())
api = [
    ["Method", "Endpoint", "Description"],
    ["POST",   "/api/logs",                "Ingest event — runs full ML pipeline + alert engine"],
    ["GET",    "/api/logs",                "List logs with filters: severity, threat_label, user_id"],
    ["GET",    "/api/logs/stream",         "SSE real-time stream (Live Feed page)"],
    ["GET",    "/api/logs/analytics",      "Aggregated stats for AI Analytics charts"],
    ["GET",    "/api/logs/{id}/explain",   "[NEW] LLM threat explanation with MITRE ATT&CK"],
    ["GET",    "/api/verify/{log_id}",     "Verify log integrity against blockchain hash"],
    ["GET",    "/api/profile",             "List all user behavioral profiles"],
    ["GET",    "/api/profile/{user_id}",   "Get a specific user's behavioral analysis"],
    ["GET",    "/api/settings",            "[NEW] Get alert configuration"],
    ["POST",   "/api/settings",            "[NEW] Save alert configuration"],
    ["GET",    "/api/alerts/history",      "[NEW] Alert history (last 20 fired)"],
    ["GET",    "/health",                  "Backend health check"],
    ["GET",    "/docs",                    "Interactive Swagger API explorer"],
]
story.append(table(api, [2*cm, 5.5*cm, 8.5*cm]))
story.append(sp())

# ─── 10. PROJECT FILES ────────────────────────────────────────────────────────
story += [h1("10. Key Project Files"), hr()]
files = [
    ["File", "Purpose"],
    ["contracts/AuditLog.sol",            "Ethereum smart contract — stores log hashes immutably"],
    ["hardhat.config.js",                 "Hardhat config — Solidity 0.8.26, localhost network"],
    ["scripts/deploy.js",                 "Deploys AuditLog.sol to local Hardhat node"],
    ["backend/main.py",                   "FastAPI app entry — CORS, routers, startup warmup"],
    ["backend/simulate_events.py",        "Sends 220 realistic cybersecurity events for demo"],
    ["backend/clear_db.py",               "Utility to wipe all MongoDB logs"],
    ["backend/.env",                      "Environment variables (RPC URL, contract address, MongoDB URI)"],
    ["backend/models/train_models.py",    "Trains Isolation Forest + Random Forest on 7,200 samples"],
    ["backend/models/anomaly_detector.py","Isolation Forest inference wrapper"],
    ["backend/models/threat_classifier.py","Random Forest inference wrapper"],
    ["backend/models/risk_scorer.py",     "Computes 0-100 risk score + severity mapping"],
    ["backend/models/behavioral_profiler.py","Per-user behavioral baseline + deviation scoring"],
    ["backend/routes/logs.py",            "POST/GET /api/logs, SSE stream, analytics endpoint"],
    ["backend/routes/verify.py",          "GET /api/verify/{log_id} — blockchain integrity check"],
    ["backend/routes/profile.py",         "GET /api/profile — behavioral profiler endpoints"],
    ["backend/db/mongo_client.py",        "MongoDB async client with in-memory fallback"],
    ["backend/blockchain/web3_client.py", "Web3 client — hash computation + on-chain storage"],
    ["frontend/src/App.jsx",              "Root component — routing + MetaMask wallet connect"],
    ["frontend/src/api/client.js",        "Axios API functions for all backend endpoints"],
    ["frontend/src/pages/Dashboard.jsx",  "Live Threat Feed page with SSE stream"],
    ["frontend/src/pages/AIAnalytics.jsx","Charts and analytics dashboard"],
    ["frontend/src/pages/BlockchainVerifier.jsx","Log integrity verification UI"],
    ["frontend/src/pages/BehavioralProfiler.jsx","Per-user behavioral analysis UI"],
    ["frontend/src/pages/ForensicReport.jsx","Filtered log table + PDF export"],
    ["frontend/vite.config.js",           "Vite config — proxies /api to localhost:8000"],
]
story.append(table(files, [7*cm, 9*cm]))
story.append(sp())

# ─── 11. ENV VARIABLES ────────────────────────────────────────────────────────
story += [h1("11. Environment Variables"), hr()]
story.append(p("File: <b>backend/.env</b>"))
story.append(code(
    "HARDHAT_RPC_URL=http://127.0.0.1:8545\n"
    "CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3\n"
    "MONGO_URI=mongodb://localhost:27017\n"
    "MONGO_DB=audit_log_db\n"
    "BACKEND_PORT=8000"
))
story.append(sp())

# ─── 12. FEATURES SUMMARY ─────────────────────────────────────────────────────
story += [h1("12. Feature Summary"), hr()]
features = [
    "Real-time cybersecurity event ingestion via REST API",
    "Isolation Forest unsupervised anomaly detection",
    "Random Forest supervised threat classification (5 classes: Normal/Probe/DoS/R2L/U2R)",
    "Hybrid risk scorer (0–100) with 5 severity levels",
    "Per-user behavioral profiling and deviation alerting",
    "SHA-256 log hashing + Ethereum smart contract storage for tamper detection",
    "Live event stream via Server-Sent Events (no polling)",
    "AI Analytics with 5 chart types (pie, line, bar, heatmap)",
    "Blockchain Verifier — instant VERIFIED/TAMPERED result for any log",
    "Behavioral Profiler with deviation meter and flag breakdown",
    "Forensic Report with advanced filters and one-click PDF export",
    "MetaMask wallet authentication with auto Hardhat network setup",
    "Automatic in-memory fallback when MongoDB is unavailable",
    "Graceful blockchain-unavailable fallback when web3.py is not installed",
    "Dark glassmorphic cyber-themed UI with Framer Motion animations",
]
for f in [
    "Real-time cybersecurity event ingestion via REST API",
    "Isolation Forest unsupervised anomaly detection",
    "Random Forest supervised threat classification (5 classes: Normal/Probe/DoS/R2L/U2R)",
    "Hybrid risk scorer (0–100) with 5 severity levels",
    "Per-user behavioral profiling and deviation alerting",
    "SHA-256 log hashing + Ethereum smart contract storage for tamper detection",
    "Live event stream via Server-Sent Events (no polling)",
    "AI Analytics with 5 chart types (pie, line, bar, heatmap)",
    "Blockchain Verifier — instant VERIFIED/TAMPERED result for any log",
    "Behavioral Profiler with deviation meter and flag breakdown",
    "Forensic Report with advanced filters and one-click PDF export",
    "MetaMask wallet authentication with auto Hardhat network setup",
    "[NEW] LLM Threat Explanation — AI-generated MITRE ATT&CK analysis per event",
    "[NEW] Local fallback explanation engine — works without API credits",
    "[NEW] Real-time Email Alerts via Gmail SMTP with HTML templates",
    "[NEW] Slack Alerts via Incoming Webhooks with Block Kit formatting",
    "[NEW] 5 alert trigger rules: severity, risk score, anomaly, IP rate, user rate",
    "[NEW] 10-minute alert cooldown to prevent notification flooding",
    "[NEW] Settings page — configure thresholds, channels, view alert history",
    "[NEW] Docker Compose — one-command full-stack deployment",
    "[NEW] Multi-stage frontend Docker build (Node build → Nginx serve)",
    "[NEW] Nginx reverse proxy with SSE support and static asset caching",
    "Automatic in-memory fallback when MongoDB is unavailable",
    "Dark glassmorphic cyber-themed UI with Framer Motion animations",
]:
    story.append(bul(f))
story.append(sp())

# ─── FOOTER ───────────────────────────────────────────────────────────────────
story += [
    hr(),
    Paragraph(
        "CyberAudit — AI-Powered Blockchain Audit Log System &nbsp;|&nbsp; "
        "Generated March 2026",
        style("footer","Normal",fontSize=8,textColor=GREY,alignment=TA_CENTER)
    )
]

# ── Build ──────────────────────────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(DARK)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    # page number
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY)
    canvas.drawCentredString(A4[0]/2, 1.2*cm, f"Page {doc.page}")
    canvas.restoreState()

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF generated: {os.path.abspath(OUTPUT)}")

"""
Generates CyberAudit_API_Documentation.pdf
Covers all backend REST endpoints AND frontend API client functions with
full request/response schemas, links, and examples.
Run: python generate_api_docs.py
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "..", "CyberAudit_API_Documentation.pdf")

# ── Palette ────────────────────────────────────────────────────────────────────
CYAN   = colors.HexColor("#00c8ff")
DARK   = colors.HexColor("#0d0d18")
MID    = colors.HexColor("#111128")
PURPLE = colors.HexColor("#8b5cf6")
GREEN  = colors.HexColor("#00cc66")
AMBER  = colors.HexColor("#ffd700")
RED    = colors.HexColor("#ff4444")
BLUE   = colors.HexColor("#3b82f6")
ORANGE = colors.HexColor("#f97316")
GREY   = colors.HexColor("#64748b")
WHITE  = colors.white

METHOD_COLORS = {
    "GET":    colors.HexColor("#22c55e"),
    "POST":   colors.HexColor("#3b82f6"),
    "PUT":    colors.HexColor("#f97316"),
    "DELETE": colors.HexColor("#ef4444"),
    "STREAM": colors.HexColor("#8b5cf6"),
}

base = getSampleStyleSheet()
def s(name, **kw): return ParagraphStyle(name, parent=base["Normal"], **kw)

H1  = s("H1",  fontSize=22, textColor=CYAN,   fontName="Helvetica-Bold", spaceAfter=4,  spaceBefore=16)
H2  = s("H2",  fontSize=14, textColor=WHITE,  fontName="Helvetica-Bold", spaceAfter=4,  spaceBefore=12)
H3  = s("H3",  fontSize=11, textColor=CYAN,   fontName="Helvetica-Bold", spaceAfter=3,  spaceBefore=8)
H4  = s("H4",  fontSize=10, textColor=AMBER,  fontName="Helvetica-Bold", spaceAfter=2,  spaceBefore=6)
BOD = s("BOD", fontSize=9,  textColor=colors.HexColor("#cbd5e1"), spaceAfter=3,  leading=14)
COD = s("COD", fontSize=8,  textColor=GREEN,  fontName="Courier",
        backColor=MID, spaceAfter=5, leading=12, leftIndent=6)
URL = s("URL", fontSize=10, textColor=CYAN,   fontName="Courier", spaceAfter=3)
CAP = s("CAP", fontSize=24, textColor=CYAN,   fontName="Helvetica-Bold", alignment=TA_CENTER, spaceAfter=4)
SUB = s("SUB", fontSize=11, textColor=GREY,   alignment=TA_CENTER, spaceAfter=6)
GRY = s("GRY", fontSize=8,  textColor=GREY,   spaceAfter=3)
BUL = s("BUL", fontSize=9,  textColor=colors.HexColor("#cbd5e1"), leftIndent=14, spaceAfter=2, leading=13)

def hr(color=CYAN): return HRFlowable(width="100%", thickness=0.5, color=color, spaceAfter=6, spaceBefore=4)
def sp(n=1):        return Spacer(1, n * 0.28 * cm)
def h1(t):          return Paragraph(t, H1)
def h2(t):          return Paragraph(t, H2)
def h3(t):          return Paragraph(t, H3)
def h4(t):          return Paragraph(t, H4)
def p(t):           return Paragraph(t, BOD)
def bul(t):         return Paragraph(f"• &nbsp;{t}", BUL)
def cod(t):         return Paragraph(t.replace("\n","<br/>").replace(" ","&nbsp;").replace("\t","&nbsp;&nbsp;&nbsp;&nbsp;"), COD)
def url(t):         return Paragraph(t, URL)
def gry(t):         return Paragraph(t, GRY)

def method_badge(method):
    color = METHOD_COLORS.get(method, GREY)
    return Paragraph(
        f'<font color="white" name="Helvetica-Bold">&nbsp;{method}&nbsp;</font>',
        s(f"mb{method}", fontSize=8, fontName="Helvetica-Bold",
          textColor=WHITE, backColor=color, spaceAfter=0)
    )

def endpoint_table(rows, col_widths):
    """rows = list of (key, value) pairs displayed as a slim table."""
    data = [[Paragraph(f"<b>{k}</b>", s("ek", fontSize=8, textColor=GREY, fontName="Helvetica-Bold")),
             Paragraph(str(v),       s("ev", fontSize=8, textColor=colors.HexColor("#cbd5e1"), fontName="Courier"))]
            for k, v in rows]
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND",  (0,0),(-1,-1), DARK),
        ("GRID",        (0,0),(-1,-1), 0.25, GREY),
        ("PADDING",     (0,0),(-1,-1), 4),
        ("VALIGN",      (0,0),(-1,-1), "TOP"),
    ]))
    return t

def big_table(data, col_widths, header=True):
    t = Table(data, colWidths=col_widths)
    cmds = [
        ("BACKGROUND",   (0,0),(-1, 0 if header else -1), MID),
        ("TEXTCOLOR",    (0,0),(-1,0), CYAN),
        ("FONTNAME",     (0,0),(-1,0), "Helvetica-Bold"),
        ("FONTSIZE",     (0,0),(-1,-1), 8),
        ("TEXTCOLOR",    (0,1),(-1,-1), colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [DARK, MID]),
        ("GRID",         (0,0),(-1,-1), 0.25, GREY),
        ("PADDING",      (0,0),(-1,-1), 5),
        ("VALIGN",       (0,0),(-1,-1), "TOP"),
    ]
    t.setStyle(TableStyle(cmds))
    return t

# ──────────────────────────────────────────────────────────────────────────────
# HELPER: single full endpoint doc block
# ──────────────────────────────────────────────────────────────────────────────
def endpoint_block(method, path, title, description,
                   base_url, params=None, body=None, response=None,
                   alt_response=None, example_response=None, frontend_fn=None, notes=None):
    color = METHOD_COLORS.get(method, GREY)
    items = [
        # Method + path header
        KeepTogether([
            Table([[
                Paragraph(f'<font color="white"><b>&nbsp;{method}&nbsp;</b></font>',
                          s(f"m{method}", fontSize=9, fontName="Helvetica-Bold",
                            textColor=WHITE, backColor=color)),
                Paragraph(f'<font color="#00c8ff" name="Courier"><b>{path}</b></font>',
                          s("ep", fontSize=11, fontName="Courier", textColor=CYAN)),
            ]], colWidths=[1.6*cm, 14.4*cm]),
        ]),
        sp(0.3),
        Paragraph(f"<b>{title}</b>", H3),
        p(description),
        sp(0.3),
        p(f"<b>Full URL:</b>"),
        url(f"{base_url}{path}"),
        sp(0.3),
    ]

    if params:
        items.append(h4("Query / Path Parameters"))
        pdata = [["Parameter", "Type", "Required", "Description"]]
        for row in params:
            pdata.append(row)
        items.append(big_table(pdata, [3.5*cm, 2*cm, 2*cm, 8.5*cm]))
        items.append(sp(0.3))

    if body:
        items.append(h4("Request Body (JSON)"))
        items.append(cod(body))
        items.append(sp(0.3))

    if response:
        items.append(h4("Response (JSON)"))
        items.append(cod(response))
        items.append(sp(0.3))

    if alt_response:
        for label, resp in alt_response:
            items.append(gry(f"  — {label}"))
            items.append(cod(resp))
            items.append(sp(0.2))

    if example_response:
        items.append(h4("Example Response"))
        items.append(cod(example_response))
        items.append(sp(0.3))

    if frontend_fn:
        items.append(h4("Frontend Function (api/client.js)"))
        items.append(cod(frontend_fn))
        items.append(sp(0.3))

    if notes:
        for note in notes:
            items.append(bul(note))
        items.append(sp(0.3))

    items.append(hr(GREY))
    items.append(sp(0.2))
    return items

# ══════════════════════════════════════════════════════════════════════════════
# BUILD PDF
# ══════════════════════════════════════════════════════════════════════════════
doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm,
    topMargin=2.5*cm, bottomMargin=2*cm,
    title="CyberAudit API Documentation",
)

story = []
BACKEND = "http://localhost:8000"
FRONTEND = "http://localhost:5173"

# ── COVER ──────────────────────────────────────────────────────────────────────
story += [
    sp(5),
    Paragraph("CyberAudit", CAP),
    Paragraph("Complete API Documentation", SUB),
    hr(),
    Paragraph("Backend REST API  ·  Frontend API Client  ·  Smart Contract Interface",
              s("cv", fontSize=10, textColor=GREY, alignment=TA_CENTER)),
    sp(2),
    big_table([
        ["Service",     "Base URL",                      "Status"],
        ["Backend API", "http://localhost:8000",          "FastAPI / Uvicorn"],
        ["Frontend",    "http://localhost:5173",          "React / Vite"],
        ["API Docs",    "http://localhost:8000/docs",     "Swagger UI (interactive)"],
        ["API JSON",    "http://localhost:8000/openapi.json", "OpenAPI 3.0 Schema"],
        ["Blockchain",  "http://127.0.0.1:8545",         "Hardhat local Ethereum node"],
        ["MongoDB",     "mongodb://localhost:27017",      "MongoDB 8.2"],
    ], [4.5*cm, 6*cm, 5.5*cm]),
    sp(4), PageBreak(),
]

# ── TABLE OF CONTENTS ──────────────────────────────────────────────────────────
toc_data = [
    ["#", "Section", "Page"],
    ["1",  "Backend API Overview",                "3"],
    ["2",  "POST /api/logs — Ingest Event",       "3"],
    ["3",  "GET /api/logs — List Logs",           "4"],
    ["4",  "GET /api/logs/stream — SSE Stream",   "5"],
    ["5",  "GET /api/logs/analytics — Charts",    "5"],
    ["6",  "GET /api/logs/{id} — Single Log",     "6"],
    ["6b", "GET /api/logs/{id}/explain — [NEW] AI Explain", "6"],
    ["7",  "GET /api/verify/{id} — Verify",       "7"],
    ["8",  "GET /api/profile/users — List Users", "7"],
    ["9",  "GET /api/profile/{id} — User Profile","8"],
    ["9b", "GET /api/settings — [NEW] Get Settings",  "8"],
    ["9c", "POST /api/settings — [NEW] Save Settings", "9"],
    ["9d", "GET /api/alerts/history — [NEW] Alert History", "9"],
    ["10", "GET /health — Health Check",          "10"],
    ["11", "GET / — Root",                        "10"],
    ["12", "Frontend API Client (api/client.js)", "11"],
    ["13", "Smart Contract Interface",            "12"],
    ["14", "Data Models Reference",               "13"],
    ["15", "Error Codes",                         "14"],
]
story += [h1("Table of Contents"), hr(), big_table(toc_data, [1.2*cm, 12*cm, 2.8*cm]), sp(), PageBreak()]

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1 — BACKEND OVERVIEW
# ═════════════════════════════════════════════════════════════════════════════
story += [h1("1. Backend API Overview"), hr()]
story += [
    p("The backend is a <b>FastAPI</b> application running at <b>http://localhost:8000</b>. "
      "It exposes REST endpoints for log ingestion, querying, blockchain verification, "
      "behavioral profiling, LLM threat explanation, and alert configuration."),
    sp(0.5),
    p("<b>Interactive Explorer:</b>"),
    url("http://localhost:8000/docs"),
    p("Open this in your browser to try any endpoint live with a built-in UI."),
    sp(0.5),
    p("<b>OpenAPI JSON Schema:</b>"),
    url("http://localhost:8000/openapi.json"),
    sp(),
    big_table([
        ["Method", "Endpoint",               "Summary"],
        ["POST",   "/api/logs",              "Ingest event — runs full ML pipeline + alert engine"],
        ["GET",    "/api/logs",              "List logs with optional filters and pagination"],
        ["GET",    "/api/logs/stream",       "Server-Sent Events — real-time log stream"],
        ["GET",    "/api/logs/analytics",    "Aggregated analytics data for charts"],
        ["GET",    "/api/logs/{log_id}",     "Fetch a single log by MongoDB ObjectID"],
        ["GET",    "/api/logs/{id}/explain", "[NEW] LLM threat explanation with MITRE ATT&CK"],
        ["GET",    "/api/verify/{log_id}",   "Verify log integrity vs blockchain hash"],
        ["GET",    "/api/profile/users",     "List all user IDs with behavioral profiles"],
        ["GET",    "/api/profile/{user_id}", "Get behavioral profile for a specific user"],
        ["GET",    "/api/settings",          "[NEW] Get current alert configuration"],
        ["POST",   "/api/settings",          "[NEW] Save alert configuration"],
        ["GET",    "/api/alerts/history",    "[NEW] Alert history — last 20 fired alerts"],
        ["GET",    "/health",                "Backend health check including blockchain status"],
        ["GET",    "/",                      "Root — returns service name, version, docs link"],
    ], [2*cm, 5.5*cm, 8.5*cm]),
    sp(), PageBreak(),
]

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2 — POST /api/logs
# ═════════════════════════════════════════════════════════════════════════════
story += [h1("2. Ingest Security Event"), hr()]
story += endpoint_block(
    method="POST", path="/api/logs", base_url=BACKEND,
    title="Ingest a new cybersecurity event",
    description=(
        "Core ingestion endpoint. Receives a security event and runs the full AI pipeline: "
        "anomaly detection (Isolation Forest) → threat classification (Random Forest) → "
        "risk scoring → behavioral profiling → MongoDB storage → blockchain hash storage → "
        "SSE broadcast to all connected dashboards."
    ),
    body="""{
  "user_id":    "alice.smith",          // required — username or account ID
  "source_ip":  "192.168.1.42",         // required — source IP address
  "event_type": "brute_force",          // required — see Event Types below
  "description":"Brute force: 500 attempts from 192.168.1.42",  // required
  "hour":       23,                     // optional — 0-23, defaults to current UTC hour
  "features":   [0.5, 500, 100, ...],   // optional — 20 ML features, auto-computed if omitted
  "metadata":   { "key": "value" }      // optional — any extra data
}""",
    response="""{
  "success":      true,
  "log_id":       "67f3a2c8e4b0123456789abc",   // MongoDB ObjectID — use for verification
  "risk_score":   73,                            // 0-100 danger score
  "severity":     "HIGH",                        // INFO | LOW | MEDIUM | HIGH | CRITICAL
  "threat_label": "Probe",                       // Normal | Probe | DoS | R2L | U2R
  "is_anomaly":   true                           // Isolation Forest anomaly flag
}""",
    frontend_fn="import { ingestLog } from './api/client'\n\nconst result = await ingestLog({\n  user_id: 'alice.smith',\n  source_ip: '192.168.1.42',\n  event_type: 'brute_force',\n  description: 'Brute force attack detected'\n})\n// result.data = { success, log_id, risk_score, severity, threat_label, is_anomaly }",
    notes=[
        "Event types: normal_login, failed_login, brute_force, port_scan, privilege_escalation, dos_attack, "
        "data_exfiltration, unauthorized_access, file_access, config_change, lateral_movement, "
        "sql_injection, xss_attempt, command_injection, service_started, service_stopped",
        "The 20 ML features are auto-generated from event_type if not provided — safe to omit",
        "The log_id returned is the MongoDB ObjectID — save it to use with the verify endpoint",
        "ML pipeline adds ~5-20ms of processing time per event",
    ]
)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3 — GET /api/logs
# ═════════════════════════════════════════════════════════════════════════════
story += [h1("3. List Security Logs"), hr()]
story += endpoint_block(
    method="GET", path="/api/logs", base_url=BACKEND,
    title="Retrieve logs with optional filters and pagination",
    description="Returns a paginated list of security logs from MongoDB. Supports filtering by severity level, threat label, and user ID. Results are ordered newest-first.",
    params=[
        ["skip",         "integer", "No",  "Number of records to skip for pagination. Default: 0"],
        ["limit",        "integer", "No",  "Maximum records to return (1–200). Default: 50"],
        ["severity",     "string",  "No",  "Filter by: INFO | LOW | MEDIUM | HIGH | CRITICAL"],
        ["threat_label", "string",  "No",  "Filter by: Normal | Probe | DoS | R2L | U2R"],
        ["user_id",      "string",  "No",  "Filter by exact username e.g. alice.smith"],
    ],
    response="""{
  "logs": [
    {
      "_id":            "67f3a2c8e4b0123456789abc",
      "user_id":        "alice.smith",
      "source_ip":      "192.168.1.42",
      "event_type":     "brute_force",
      "description":    "Brute force attack: 500 attempts...",
      "hour":           23,
      "threat_label":   "Probe",
      "threat_confidence": 0.84,
      "threat_probabilities": { "Normal": 0.05, "Probe": 0.84, "DoS": 0.11 },
      "is_anomaly":     true,
      "anomaly_score":  0.72,
      "risk_score":     73,
      "severity":       "HIGH",
      "behavioral_deviation": 0.65,
      "behavioral_flags": ["New IP address detected", "Unusual activity time: 23:00"],
      "metadata":       { "simulated": true },
      "tx_hash":        "0xabc123...",      // null if blockchain unavailable
      "block_number":   12,                 // null if blockchain unavailable
      "created_at":     "2026-03-19T17:24:43.961330"
    }
  ],
  "total": 220,      // total matching records (ignores pagination)
  "skip":  0,
  "limit": 50
}""",
    frontend_fn='import { getLogs } from "./api/client"\n\n// Get first 50 newest logs\nconst res = await getLogs({ limit: 50 })\nconst logs = res.data.logs\n\n// Get HIGH severity Probe attacks only\nconst threats = await getLogs({ severity: "HIGH", threat_label: "Probe", limit: 100 })\n\n// Get all logs for a specific user\nconst userLogs = await getLogs({ user_id: "alice.smith" })',
    notes=[
        "Use skip + limit for pagination: skip=50, limit=50 fetches page 2",
        "The total field always returns the full count even when paginated",
    ]
)

story.append(PageBreak())

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4 — GET /api/logs/stream
# ═════════════════════════════════════════════════════════════════════════════
story += [h1("4. Real-Time Event Stream (SSE)"), hr()]
story += endpoint_block(
    method="STREAM", path="/api/logs/stream", base_url=BACKEND,
    title="Server-Sent Events — Real-time log stream",
    description=(
        "Keep an open HTTP connection to receive logs in real time as they are ingested. "
        "Uses the Server-Sent Events (SSE) protocol — the browser/client receives data "
        "automatically without polling. On connect, sends the last 10 stored logs immediately, "
        "then streams new events as they arrive. Sends a heartbeat every 30 seconds to keep alive."
    ),
    response="""// Each event is a 'data:' line with JSON payload
data: {
  "_id":          "67f3a2c8e4b0123456789abc",
  "user_id":      "bob.jones",
  "event_type":   "port_scan",
  "severity":     "MEDIUM",
  "risk_score":   56,
  "threat_label": "Probe",
  "is_anomaly":   true,
  ...full log object...
}

// Heartbeat (keep-alive) every 30 seconds:
: heartbeat""",
    frontend_fn='// Used in Dashboard.jsx — starts automatically on page load\nconst es = new EventSource("/api/logs/stream")\n\nes.onmessage = (event) => {\n  const log = JSON.parse(event.data)\n  setLogs(prev => [log, ...prev].slice(0, 100))\n}\n\nes.onerror = () => {\n  es.close()  // reconnect logic here if needed\n}\n\n// Always close when component unmounts:\nreturn () => es.close()',
    notes=[
        "Client connects once — server pushes data automatically (no repeated requests)",
        "The /api proxy in vite.config.js forwards requests to localhost:8000",
        "Compatible with all modern browsers natively via EventSource API",
        "Each SSE subscriber gets their own asyncio.Queue on the server — messages are never lost",
    ]
)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 5 — GET /api/logs/analytics
# ═════════════════════════════════════════════════════════════════════════════
story += [h1("5. Analytics Data"), hr()]
story += endpoint_block(
    method="GET", path="/api/logs/analytics", base_url=BACKEND,
    title="Aggregated analytics for dashboard charts",
    description="Returns pre-aggregated data used to power the AI Analytics page charts. Includes threat distribution, severity distribution, risk timeline, top risky IPs, top risky users, and hourly activity heatmap.",
    response="""{
  "threat_distribution": [
    { "label": "Normal", "count": 95 },
    { "label": "Probe",  "count": 45 },
    { "label": "DoS",    "count": 28 },
    { "label": "R2L",    "count": 37 },
    { "label": "U2R",    "count": 15 }
  ],
  "severity_distribution": [
    { "label": "INFO",     "count": 12 },
    { "label": "LOW",      "count": 85 },
    { "label": "MEDIUM",   "count": 70 },
    { "label": "HIGH",     "count": 40 },
    { "label": "CRITICAL", "count": 13 }
  ],
  "risk_over_time": [
    { "risk": 29, "time": "2026-03-19T17:24:40" },
    { "risk": 63, "time": "2026-03-19T17:24:41" }
  ],
  "top_ips": [
    { "ip": "185.220.101.42", "avg_risk": 71.3, "count": 18 }
  ],
  "top_users": [
    { "user": "alice.smith", "avg_risk": 58.4, "count": 22 }
  ],
  "hourly_heatmap": []
}""",
    frontend_fn='import { getAnalytics } from "./api/client"\n\nconst res = await getAnalytics()\nconst { threat_distribution, risk_over_time, top_ips } = res.data',
)

story.append(PageBreak())

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 6 — GET /api/logs/{log_id}
# ═════════════════════════════════════════════════════════════════════════════
story += [h1("6. Get Single Log"), hr()]
story += endpoint_block(
    method="GET", path="/api/logs/{log_id}", base_url=BACKEND,
    title="Fetch a single log document by its MongoDB ObjectID",
    description="Returns the full log document for a given ID. The log_id is the MongoDB ObjectID returned when the event was ingested (also visible in the Forensics table).",
    params=[["log_id", "string", "Yes", "MongoDB ObjectID e.g. 67f3a2c8e4b0123456789abc"]],
    example_response="""{
  "_id":          "67f3a2c8e4b0123456789abc",
  "user_id":      "diana.patel",
  "source_ip":    "103.235.46.39",
  "event_type":   "unauthorized_access",
  "description":  "Unauthorized resource access by diana.patel from 103.235.46.39",
  "risk_score":   69,
  "severity":     "HIGH",
  "threat_label": "R2L",
  "is_anomaly":   true,
  "tx_hash":      null,
  "created_at":   "2026-03-19T17:24:43.961330"
}""",
    alt_response=[("404 — Log not found", '{ "detail": "Log not found" }')],
    frontend_fn='// No dedicated function — use axios directly:\nconst res = await api.get(`/logs/${logId}`)\nconst log = res.data',
)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 6b — GET /api/logs/{id}/explain  [NEW]
# ═════════════════════════════════════════════════════════════════════════════
story += [h1("6b. [NEW] AI Threat Explanation"), hr()]
story += endpoint_block(
    method="GET", path="/api/logs/{log_id}/explain", base_url=BACKEND,
    title="Generate AI-powered MITRE ATT&CK explanation for a security event",
    description=(
        "Returns a comprehensive cybersecurity analysis for a log entry. "
        "Tries Claude (Anthropic) first if ANTHROPIC_API_KEY is configured. "
        "Falls back to a built-in rule-based local analysis engine that uses the log's own data fields. "
        "Results are cached in MongoDB after the first call — second request for same log_id returns instantly. "
        "Only HIGH and CRITICAL severity logs show the Explain button in the UI."
    ),
    params=[["log_id", "string", "Yes", "MongoDB ObjectID of the log to explain"]],
    response="""{
  "log_id":               "67f3a2c8e4b0123456789abc",
  "cached":               false,         // true on subsequent calls
  "used_claude":          false,         // true if Anthropic API responded
  "summary":              "A high-severity brute_force event was detected from user \'alice.smith\' at IP 185.220.101.42, classified as a Probe threat with risk score 73/100. The Isolation Forest flagged this as statistically anomalous. Immediate investigation is strongly recommended.",
  "why_flagged":          "Risk score of 73/100 exceeds HIGH threshold; Isolation Forest flagged as anomaly (score 0.721); behavioral deviation of 0.65 indicates departure from baseline.",
  "attack_pattern":       "Automated credential stuffing — attacker cycles through password combinations at high rate to gain unauthorized access without triggering lockout.",
  "mitre_technique":      "T1110.001 — Brute Force: Password Guessing",
  "recommended_action":   "1. Block source IP at firewall.\\n2. Enforce account lockout after 5 failed attempts.\\n3. Enable MFA on targeted account.",
  "confidence_reasoning": "Random Forest classifier assigned Probe label with 84% confidence. Risk score 73 computed from severity HIGH, known-bad IP, behavioral deviation 0.65."
}""",
    frontend_fn='import { explainLog } from "./api/client"\n\nconst res = await explainLog("67f3a2c8e4b0123456789abc")\nconst {\n  summary, why_flagged, attack_pattern,\n  mitre_technique, recommended_action, confidence_reasoning\n} = res.data',
    notes=[
        "Works WITHOUT an API key — local engine generates analysis from log data fields",
        "Add ANTHROPIC_API_KEY to backend/.env to use Claude claude-opus-4-5 model",
        "Explain button only appears on HIGH and CRITICAL severity events in the UI",
        "Cached results served instantly from MongoDB — no repeated API calls",
        "Returns 404 if log_id is invalid or the log no longer exists",
    ]
)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 7 — GET /api/verify/{log_id}
# ═════════════════════════════════════════════════════════════════════════════
story += [h1("7. Blockchain Verification"), hr()]
story += endpoint_block(
    method="GET", path="/api/verify/{log_id}", base_url=BACKEND,
    title="Verify log integrity against the blockchain",
    description=(
        "Core tamper-detection endpoint. Fetches the log from MongoDB, "
        "recomputes its SHA-256 hash, then compares against the hash stored in the Ethereum smart contract. "
        "Returns VERIFIED if the hashes match, TAMPERED if they don't, "
        "or UNAVAILABLE if the blockchain node is not reachable."
    ),
    params=[["log_id", "string", "Yes", "MongoDB ObjectID of the log to verify"]],
    alt_response=[
        ("✅ VERIFIED — log is authentic", """{
  "status":          "VERIFIED",
  "log_id":          "67f3a2c8e4b0123456789abc",
  "recomputed_hash": "0xa1b2c3d4...",    // SHA-256 of current MongoDB document
  "stored_hash":     "0xa1b2c3d4...",    // hash from Ethereum smart contract
  "hashes_match":    true,
  "tx_hash":         "0xdeadbeef...",    // Ethereum transaction
  "block_number":    5,
  "risk_score":      73,
  "threat_label":    "Probe",
  "event_type":      "brute_force",
  "user_id":         "alice.smith"
}"""),
        ("❌ TAMPERED — log was modified", """{
  "status":          "TAMPERED",
  "hashes_match":    false,
  "recomputed_hash": "0xDIFFERENT...",   // does NOT match stored_hash
  "stored_hash":     "0xORIGINAL..."
}"""),
        ("⚠ UNAVAILABLE — blockchain not reachable", """{
  "status":          "UNAVAILABLE",
  "message":         "Blockchain node not reachable",
  "recomputed_hash": "0x...",            // hash still computed from current doc
  "stored_hash":     null
}"""),
        ("NOT_ON_CHAIN — log ingested before blockchain was connected", """{
  "status":          "NOT_ON_CHAIN",
  "message":         "This log was not stored on-chain"
}"""),
    ],
    frontend_fn='import { verifyLog } from "./api/client"\n\nconst res = await verifyLog("67f3a2c8e4b0123456789abc")\nconst { status, hashes_match, recomputed_hash, stored_hash } = res.data\n\nif (status === "VERIFIED")   console.log("Log is authentic!")\nif (status === "TAMPERED")   console.log("Log was modified!")\nif (status === "UNAVAILABLE") console.log("Start Hardhat node first")',
    notes=[
        "Requires Hardhat node to be running for VERIFIED/TAMPERED results",
        "Without blockchain: returns UNAVAILABLE but still shows recomputed_hash",
        "The SHA-256 is computed from the entire log document JSON",
    ]
)

story.append(PageBreak())

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 8 — GET /api/profile/users
# ═════════════════════════════════════════════════════════════════════════════
story += [h1("8. List Profiled Users"), hr()]
story += endpoint_block(
    method="GET", path="/api/profile/users", base_url=BACKEND,
    title="Return all user IDs that have behavioral profiles",
    description="Returns the list of user IDs for which the behavioral profiler has collected activity data. Only users who have had at least one event ingested through POST /api/logs will appear here.",
    response='{\n  "users": ["alice.smith", "bob.jones", "charlie.wu", "diana.patel"],\n  "count": 4\n}',
    frontend_fn='import { getUsers } from "./api/client"\n\nconst res = await getUsers()\nconst users = res.data.users  // ["alice.smith", "bob.jones", ...]',
)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 9 — GET /api/profile/{user_id}
# ═════════════════════════════════════════════════════════════════════════════
story += [h1("9. User Behavioral Profile"), hr()]
story += endpoint_block(
    method="GET", path="/api/profile/{user_id}", base_url=BACKEND,
    title="Get full behavioral analysis profile for a specific user",
    description="Returns the behavioral profiler's complete analysis for a user: their activity statistics, known IPs, typical working hours, event type frequencies, risk timeline, deviation score, and current behavioral flags.",
    params=[["user_id", "string", "Yes", "Username e.g. alice.smith"]],
    example_response="""{
  "user_id":          "alice.smith",
  "total_events":     22,
  "avg_risk_score":   45.3,
  "deviation_score":  0.68,               // 0.0 = normal, 1.0 = maximum deviation
  "known_ips":        ["192.168.1.10", "45.33.32.156"],
  "typical_hours":    [9, 10, 11, 14, 15, 16],
  "event_counts":     { "normal_login": 8, "failed_login": 6, "brute_force": 4 },
  "risk_timeline":    [29, 45, 73, 56, 29, 63, 18],
  "current_flags": [
    "New IP address detected: 185.220.101.42",
    "Unusual activity time: 23:00 (typical: 10:00)",
    "High-risk event type: brute_force"
  ]
}""",
    alt_response=[("404 — No activity recorded for user", '{ "detail": "No activity found for user: alice.smith" }')],
    frontend_fn='import { getProfile } from "./api/client"\n\nconst res = await getProfile("alice.smith")\nconst { deviation_score, current_flags, risk_timeline } = res.data',
)

story.append(PageBreak())

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 9b — GET /api/settings  [NEW]
# ═════════════════════════════════════════════════════════════════════════════
story += [h1("9b. [NEW] Get Alert Settings"), hr()]
story += endpoint_block(
    method="GET", path="/api/settings", base_url=BACKEND,
    title="Retrieve the current alert configuration",
    description="Returns the persisted alert configuration including severity threshold, risk score threshold, enabled notification channels, and which trigger rules are active. If no settings have been saved yet, returns the system defaults.",
    response="""{
  "min_severity":      "HIGH",      // INFO|LOW|MEDIUM|HIGH|CRITICAL
  "risk_threshold":    75,           // 0-100 — alerts fire above this score
  "email_enabled":     false,
  "email_to":          "",
  "slack_enabled":     false,
  "slack_webhook":     "",
  "rules": {
    "severity_rule":   true,         // fire on severity >= min_severity
    "risk_rule":       true,         // fire on risk_score > risk_threshold
    "anomaly_rule":    true,         // fire on is_anomaly=true + MEDIUM+
    "ip_rate_rule":    true,         // fire on 5+ events from same IP in 60s
    "user_rate_rule":  true          // fire on 3+ HIGH events same user in 5min
  }
}""",
    frontend_fn='import { getSettings } from "./api/client"\n\nconst res = await getSettings()\nconst settings = res.data\n// settings.email_enabled, settings.min_severity, settings.rules, etc.',
)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 9c — POST /api/settings  [NEW]
# ═════════════════════════════════════════════════════════════════════════════
story += [h1("9c. [NEW] Save Alert Settings"), hr()]
story += endpoint_block(
    method="POST", path="/api/settings", base_url=BACKEND,
    title="Persist alert configuration",
    description="Saves the alert configuration to MongoDB. Settings are applied immediately to the alert engine — the next ingested event will use the new thresholds. Can also be configured via the Settings page UI at http://localhost:5173/settings.",
    body="""{
  "min_severity":   "HIGH",        // required — minimum severity that triggers alerts
  "risk_threshold": 75,            // required — risk score threshold (0-100)
  "email_enabled":  true,          // optional — default false
  "email_to":       "sec@co.com",  // required if email_enabled=true
  "slack_enabled":  true,          // optional — default false
  "slack_webhook":  "https://hooks.slack.com/services/...",  // required if slack_enabled
  "rules": {                       // optional — all default true
    "severity_rule":  true,
    "risk_rule":      true,
    "anomaly_rule":   true,
    "ip_rate_rule":   true,
    "user_rate_rule": true
  }
}""",
    response='{\n  "success": true,\n  "message": "Settings saved"\n}',
    frontend_fn='import { saveSettings } from "./api/client"\n\nawait saveSettings({\n  min_severity: "HIGH",\n  risk_threshold: 75,\n  email_enabled: true,\n  email_to: "security@company.com",\n  slack_enabled: false,\n  rules: { severity_rule: true, risk_rule: true, anomaly_rule: true,\n           ip_rate_rule: true, user_rate_rule: true }\n})',
    notes=[
        "SMTP credentials (SMTP_USER, SMTP_PASSWORD) must be set in backend/.env separately",
        "Slack webhook URL can be set here OR in backend/.env as SLACK_WEBHOOK_URL",
        "Alert cooldown is fixed at 10 minutes per (IP + event_type) combination",
    ]
)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 9d — GET /api/alerts/history  [NEW]
# ═════════════════════════════════════════════════════════════════════════════
story += [h1("9d. [NEW] Alert History"), hr()]
story += endpoint_block(
    method="GET", path="/api/alerts/history", base_url=BACKEND,
    title="Retrieve the last 20 fired alerts",
    description="Returns the most recent alerts that were actually sent (not suppressed by cooldown). Each entry records which rule triggered it, what channels were notified, and a summary of the log that caused it.",
    response="""[
  {
    "timestamp":    "2026-03-19T17:31:22.541",
    "rule":         "severity_rule",          // which trigger rule fired
    "severity":     "CRITICAL",
    "risk_score":   87,
    "event_type":   "privilege_escalation",
    "user_id":      "frank.garcia",
    "source_ip":    "185.220.101.42",
    "channels":     ["email", "slack"],        // which channels were notified
    "log_id":       "67f3a2c8e4b0123456789abc"
  },
  ...
]""",
    frontend_fn='import { getAlertHistory } from "./api/client"\n\nconst res = await getAlertHistory()\nconst history = res.data   // array of alert records, newest first',
    notes=[
        "Returns empty array [] if no alerts have been fired yet",
        "Only includes alerts that passed the 10-minute cooldown and were actually sent",
        "Suppressed (cooldown) alerts are not recorded",
    ]
)

story.append(PageBreak())

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 10 — Health + Root
# ═════════════════════════════════════════════════════════════════════════════
story += [h1("10. System Endpoints"), hr()]
story += endpoint_block(
    method="GET", path="/health", base_url=BACKEND,
    title="Backend health check",
    description="Returns the operational status of the backend and whether the blockchain node is reachable. Use this to quickly verify the system is up.",
    response='{\n  "status":     "ok",\n  "blockchain": false    // true if Hardhat node is running on port 8545\n}',
    frontend_fn='// Quick health check\nconst res = await fetch("http://localhost:8000/health")\nconst { status, blockchain } = await res.json()',
)
story += endpoint_block(
    method="GET", path="/", base_url=BACKEND,
    title="Root — service information",
    description="Returns basic service metadata. Useful for confirming the API is running.",
    response='{\n  "service": "AI Blockchain Audit Log System",\n  "version": "1.0.0",\n  "docs":    "/docs"\n}',
    frontend_fn='const res = await fetch("http://localhost:8000/")\nconst info = await res.json()',
)

story.append(PageBreak())

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 12 — FRONTEND API CLIENT
# ═════════════════════════════════════════════════════════════════════════════
story += [h1("12. Frontend API Client"), hr()]
story += [
    p("Located at: <b>frontend/src/api/client.js</b>"),
    sp(0.3),
    p("All API calls go through an <b>Axios instance</b> with base URL <b>/api</b> (proxied by Vite to "
      "http://localhost:8000). A 15-second timeout is set on all requests."),
    sp(0.5),
    cod("""import axios from 'axios'

// Base Axios instance
const api = axios.create({
  baseURL: '/api',        // Vite proxies this → http://localhost:8000
  timeout: 15000,         // 15 second timeout
})

// -- Log endpoints --
export const getLogs      = (params = {}) => api.get('/logs', { params })
export const ingestLog    = (data)        => api.post('/logs', data)
export const getAnalytics = ()            => api.get('/logs/analytics')
export const explainLog   = (logId)       => api.get(`/logs/${logId}/explain`)  // [NEW]

// -- Verification --
export const verifyLog    = (logId)       => api.get(`/verify/${logId}`)

// -- Behavioral Profiles --
export const getUsers     = ()            => api.get('/profile/users')
export const getProfile   = (userId)     => api.get(`/profile/${userId}`)

// -- Alert Settings [NEW] --
export const getSettings     = ()       => api.get('/settings')
export const saveSettings    = (data)   => api.post('/settings', data)
export const getAlertHistory = ()       => api.get('/alerts/history')

export default api"""),
    sp(),
    h3("Usage Pattern (all pages)"),
    cod("""import { getLogs, getAnalytics, verifyLog, getProfile } from '../api/client'

// In a React component:
useEffect(() => {
  const fetchData = async () => {
    try {
      const res = await getLogs({ limit: 50, severity: 'HIGH' })
      setLogs(res.data.logs)   // res.data is the JSON response body
    } catch (err) {
      console.error(err)       // AxiosError if network/timeout
    }
  }
  fetchData()
}, [])"""),
    sp(),
    h3("Vite Proxy Configuration (vite.config.js)"),
    p("All /api/* requests from the frontend are automatically forwarded to the backend. "
      "This eliminates CORS issues and means you never hardcode localhost:8000 in the frontend."),
    cod("""// frontend/vite.config.js
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',  // Backend
        changeOrigin: true,
      },
    },
  },
})"""),
    sp(), PageBreak(),
]

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 13 — SMART CONTRACT
# ═════════════════════════════════════════════════════════════════════════════
story += [h1("13. Smart Contract Interface"), hr()]
story += [
    p("Contract: <b>AuditLog.sol</b>"),
    p("Network: <b>Hardhat Local (Chain ID 31337)</b>"),
    p("RPC URL: <b>http://127.0.0.1:8545</b>"),
    p("Address: <b>0x5FbDB2315678afecb367f032d93F642f64180aa3</b>"),
    sp(0.5),
    h3("Solidity Functions"),
    cod("""// Store a log hash on-chain (called by backend after ingestion)
function storeLog(
  string memory logId,        // MongoDB ObjectID as string
  bytes32 logHash,            // SHA-256 hash of the log document
  uint256 riskScore,          // 0-100
  string memory threatLabel,  // "Normal" | "Probe" | "DoS" | "R2L" | "U2R"
  string memory eventType,    // e.g. "brute_force"
  string memory userId        // e.g. "alice.smith"
) external

// Retrieve a stored log hash by its index (called by verify endpoint)
function getLog(uint256 index) external view returns (
  string memory logId,
  bytes32 logHash,
  uint256 riskScore,
  string memory threatLabel,
  string memory eventType,
  string memory userId,
  uint256 timestamp
)

// Get total number of stored logs
function getLogCount() external view returns (uint256)"""),
    sp(),
    h3("Python Web3 Client (backend/blockchain/web3_client.py)"),
    cod("""from blockchain.web3_client import (
  is_blockchain_available,   # bool — True if Hardhat is running
  compute_log_hash,          # dict → "0x<sha256hex>" string
  store_log_on_chain,        # dict → { tx_hash, block_number, block_timestamp }
  get_log_from_chain,        # index → { log_id, log_hash, risk_score, ... }
)"""),
    sp(),
    h3("Frontend Ethers.js Usage"),
    cod("""// Connect MetaMask
const provider = new ethers.BrowserProvider(window.ethereum)
const signer   = await provider.getSigner()

// Read from contract (no gas)
const contract = new ethers.Contract(CONTRACT_ADDRESS, ABI, provider)
const count    = await contract.getLogCount()
const log      = await contract.getLog(0)"""),
    sp(), PageBreak(),
]

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 14 — DATA MODELS
# ═════════════════════════════════════════════════════════════════════════════
story += [h1("14. Data Models Reference"), hr()]

story += [h3("Log Document (MongoDB)")]
fields = [
    ["Field",                 "Type",   "Description"],
    ["_id",                   "string", "MongoDB ObjectID — unique identifier for this log"],
    ["user_id",               "string", "Username or account ID that triggered the event"],
    ["source_ip",             "string", "IP address originating the event"],
    ["event_type",            "string", "Category: brute_force, port_scan, normal_login, etc."],
    ["description",           "string", "Human-readable description of the event"],
    ["hour",                  "int",    "Hour of day (0–23) when event occurred"],
    ["threat_label",          "string", "AI classification: Normal | Probe | DoS | R2L | U2R"],
    ["threat_confidence",     "float",  "ML confidence score for the threat label (0.0–1.0)"],
    ["threat_probabilities",  "object", "Per-class probabilities {Normal: 0.05, Probe: 0.84, ...}"],
    ["is_anomaly",            "bool",   "True if Isolation Forest classified as anomaly"],
    ["anomaly_score",         "float",  "Anomaly severity score (0.0–1.0, higher = more anomalous)"],
    ["risk_score",            "int",    "Combined risk score 0–100"],
    ["severity",              "string", "INFO | LOW | MEDIUM | HIGH | CRITICAL"],
    ["behavioral_deviation",  "float",  "How far this user's behavior deviates from baseline (0.0–1.0)"],
    ["behavioral_flags",      "array",  "List of specific anomaly flags triggered"],
    ["metadata",              "object", "Arbitrary extra key-value data"],
    ["tx_hash",               "string", "Ethereum transaction hash (null if blockchain unavailable)"],
    ["block_number",          "int",    "Ethereum block number (null if blockchain unavailable)"],
    ["created_at",            "string", "ISO 8601 timestamp when log was stored"],
]
story.append(big_table(fields, [4.5*cm, 2.5*cm, 9*cm]))
story.append(sp())

story += [h3("Severity Levels")]
sev = [
    ["Level",    "Score Range", "Color",  "Meaning"],
    ["INFO",     "0–15",        "Blue",   "Normal activity, no concern"],
    ["LOW",      "16–35",       "Green",  "Slightly unusual, log for records"],
    ["MEDIUM",   "36–59",       "Yellow", "Suspicious, investigate within 24h"],
    ["HIGH",     "60–79",       "Orange", "Likely attack, respond within 1h"],
    ["CRITICAL", "80–100",      "Red",    "Active breach, immediate action required"],
]
story.append(big_table(sev, [2.5*cm, 3*cm, 2.5*cm, 8*cm]))
story.append(sp())

story += [h3("Threat Labels (Random Forest Classes)")]
labels = [
    ["Label",  "Full Name",               "Attack Examples"],
    ["Normal", "Normal Traffic",           "Successful logins, file reads, service starts"],
    ["Probe",  "Network Reconnaissance",   "Port scans, ping sweeps, service version detection"],
    ["DoS",    "Denial of Service",        "SYN flood, UDP flood, HTTP request flood"],
    ["R2L",    "Remote-to-Local",          "Brute force, password spray, unauthorized access"],
    ["U2R",    "User-to-Root Escalation",  "Sudo exploits, SUID abuse, kernel exploits"],
]
story.append(big_table(labels, [2.5*cm, 5*cm, 8.5*cm]))
story.append(sp())
story.append(PageBreak())

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 15 — ERROR CODES
# ═════════════════════════════════════════════════════════════════════════════
story += [h1("15. Error Codes"), hr()]
errors = [
    ["HTTP Status", "When it occurs",                                        "Response body"],
    ["200 OK",      "Request succeeded",                                     '{ ...data... }'],
    ["404 Not Found","Log ID / user ID doesn\'t exist in the database",       '{ "detail": "Log not found in database" }'],
    ["422 Unprocessable","Request body missing required fields or wrong type",'{ "detail": [{ "loc": [...], "msg": "..." }] }'],
    ["500 Internal Error","Unhandled server exception",                      '{ "detail": "Internal server error" }'],
    ["303 See Other", "Happens when backend isn\'t running (Vite serves UI)", "HTML page — restart backend!"],
]
story.append(big_table(errors, [3*cm, 6.5*cm, 6.5*cm]))
story.append(sp())

story += [h3("Frontend Axios Error Handling")]
story.append(cod("""try {
  const res = await getLogs({ limit: 50 })
  setLogs(res.data.logs)
} catch (err) {
  if (err.code === 'ECONNREFUSED')       alert('Backend not running on port 8000')
  if (err.code === 'ERR_NETWORK')        alert('Cannot reach backend')
  if (err.response?.status === 404)      alert('Resource not found')
  if (err.response?.status === 422)      alert('Invalid request: ' + err.response.data.detail)
  if (err.message.includes('timeout'))   alert('Backend too slow — check MongoDB is running')
}"""))

story += [sp(), hr(),
    Paragraph("CyberAudit API Documentation  |  Generated March 2026  |  http://localhost:8000/docs",
              s("ft", fontSize=8, textColor=GREY, alignment=TA_CENTER))
]

# ─── Page background ──────────────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(DARK)
    canvas.rect(0, 0, A4[0], A4[1], fill=1, stroke=0)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GREY)
    canvas.drawCentredString(A4[0]/2, 1.2*cm, f"Page {doc.page}  —  CyberAudit API Docs")
    canvas.restoreState()

doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print(f"PDF generated: {os.path.abspath(OUTPUT)}")

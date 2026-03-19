# CyberAudit — AI-Powered Blockchain Audit Log System

> **Enterprise-grade, tamper-proof cybersecurity event logging with real AI threat detection, blockchain integrity, LLM-powered explanations, real-time alerts, and Docker support.**

---

## What Is This Project?

CyberAudit is a full-stack cybersecurity platform that does five things:

1. **Captures** real-time cybersecurity events (logins, attacks, scans, etc.)
2. **Analyzes** them with ML models — anomaly detection, threat classification, risk scoring
3. **Stores** a tamper-proof SHA-256 fingerprint of every event on a blockchain
4. **Explains** high-severity events with AI-generated MITRE ATT&CK analysis
5. **Alerts** your team via Email and Slack when critical events occur

> Think of it as a CCTV system for your entire network — every event is analyzed by AI, locked on a blockchain, and can be explained in plain English.

---

## New Features (v2.0)

| Feature | Description |
|---------|-------------|
| 🤖 **LLM Threat Explanation** | Click "Explain" on any HIGH/CRITICAL event → AI generates MITRE ATT&CK analysis, attack pattern, and recommended actions |
| 🔔 **Real-time Alert System** | Email + Slack alerts for critical events based on 5 configurable trigger rules |
| 🐳 **Docker Support** | Full containerization — run everything with `docker-compose up --build` |
| ⚙️ **Settings Page** | Configure alert thresholds, email, Slack from the dashboard UI |

---

## How the System Works (Data Flow)

```
Cybersecurity Event (POST /api/logs)
       │
       ▼
  FastAPI Backend
  ┌─────────────────────────────────────────────────┐
  │  1. Isolation Forest    → Anomaly? (score 0–1)  │
  │  2. Random Forest       → Threat Label          │
  │  3. Risk Scorer         → Score 0–100           │
  │  4. Behavioral Profiler → User deviation        │
  │  5. Alert Engine        → Email / Slack notify  │
  └─────────────────────────────────────────────────┘
       │                    │
       ▼                    ▼
  MongoDB               Hardhat Ethereum
  (full log)            (SHA-256 hash only)
       │
       ▼
  React Frontend (SSE real-time stream)
       │
       ▼  [on HIGH/CRITICAL click]
  LLM Explain (Claude / Local fallback → MITRE analysis)
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Smart Contract | Solidity + Hardhat | Immutable hash storage on local Ethereum |
| Backend | Python FastAPI | Async API, ML pipeline, alert engine |
| AI/ML | Scikit-learn | Isolation Forest + Random Forest |
| LLM | Anthropic Claude / Local fallback | Threat explanation + MITRE mapping |
| Database | MongoDB + Motor | Full log storage off-chain |
| Frontend | React + Vite | SPA with SSE real-time stream |
| Styling | Tailwind CSS + Framer Motion | Dark cyber theme + animations |
| Alerts | Gmail SMTP + Slack Webhooks | Real-time security notifications |
| Container | Docker + Docker Compose | One-command deployment |

---

## Dashboard Pages

| Page | URL | What It Shows |
|------|-----|--------------|
| **Live Threat Feed** | `/` | Real-time event stream. Stats: total, high severity, anomalies, avg risk. 🤖 Explain button on HIGH/CRITICAL |
| **AI Analytics** | `/analytics` | Threat distribution pie, risk timeline, activity heatmap, top IPs/users |
| **Blockchain Verifier** | `/verify` | Enter Log ID → VERIFIED or TAMPERED comparison |
| **Behavioral Profiler** | `/profile` | Per-user risk timeline, known IPs, behavioral flags |
| **Forensic Report** | `/forensics` | Filter by severity/threat/user → Export PDF |
| **Settings** | `/settings` | Configure alerts — email, Slack, thresholds, alert history |

---

## How to Start (CMD — Recommended)

Open **3 CMD windows**:

### Terminal 1 — Backend
```cmd
cd "e:\Blockchain project\backend"
uvicorn main:app --reload --port 8000
```
Wait for: `Application startup complete.`

### Terminal 2 — Frontend
```cmd
cd "e:\Blockchain project\frontend"
npm run dev
```
Wait for: `Local: http://localhost:5173/`

### Terminal 3 — Seed Data (first time only)
```cmd
cd "e:\Blockchain project\backend"
python simulate_events.py
```
Wait for: `Done: 220 succeeded`

### Open browser:
```
http://localhost:5173
```

> **MongoDB** runs as a Windows service automatically — no separate command needed.

---

## Run with Docker (One Command)

```bash
# From project root — builds and starts everything:
docker-compose up --build

# Open: http://localhost:80
```

Create a `.env` file in the **project root** with your API keys:
```env
ANTHROPIC_API_KEY=sk-ant-...
SMTP_USER=your@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
```

---

## LLM Threat Explanation (Feature 2)

Click **🤖 Explain** on any HIGH or CRITICAL event card.

The system generates:
- **Summary** — what happened and why it matters
- **Why Flagged** — ML model reasoning
- **Attack Pattern** — TTP description
- **MITRE ATT&CK** — technique ID and name
- **Recommended Action** — step-by-step response
- **Confidence Reasoning** — model score explanation

**Setup (optional — local fallback works without it):**
```env
# backend/.env
ANTHROPIC_API_KEY=sk-ant-...   # from console.anthropic.com
```
> Without a key or with the free evaluation plan, the built-in local analysis engine generates the same output using the log's actual data fields.

---

## Alert System (Feature 3)

### Trigger Rules
| Rule | Condition |
|------|-----------|
| Severity | `severity ≥ MIN_SEVERITY` |
| Risk Score | `risk_score > RISK_THRESHOLD` |
| AI Anomaly | `is_anomaly=true` + MEDIUM+ severity |
| IP Rate | 5+ events from same IP in 60 seconds |
| User Rate | 3+ HIGH events from same user in 5 minutes |
| Cooldown | 10-minute cooldown per (IP + event_type) |

### Setup Email (Gmail)
1. Google Account → Security → 2-Step Verification → **App passwords**
2. Select app: **Mail** → Generate → copy 16-character password

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
```

### Setup Slack
1. [api.slack.com/apps](https://api.slack.com/apps) → Create App → Incoming Webhooks → Add to Slack
2. Copy Webhook URL

```env
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../...
```

---

## Environment Variables (`backend/.env`)

```env
# Core
HARDHAT_RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0x5FbDB2315678afecb367f032d93F642f64180aa3
MONGO_URI=mongodb://localhost:27017
MONGO_DB=audit_log_db
BACKEND_PORT=8000

# LLM (optional)
ANTHROPIC_API_KEY=your_key_here

# Email Alerts (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx

# Slack Alerts (optional)
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...

# Alert Thresholds
ALERT_MIN_SEVERITY=HIGH
ALERT_RISK_THRESHOLD=75
```

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/logs` | Ingest security event (runs full ML pipeline) |
| `GET` | `/api/logs` | List logs with filters |
| `GET` | `/api/logs/stream` | SSE real-time event stream |
| `GET` | `/api/logs/analytics` | Aggregated analytics for charts |
| `GET` | `/api/logs/{id}/explain` | **[NEW]** LLM threat explanation with MITRE mapping |
| `GET` | `/api/verify/{log_id}` | Verify log integrity vs blockchain hash |
| `GET` | `/api/profile` | List all user behavioral profiles |
| `GET` | `/api/profile/{user_id}` | Get user's behavioral analysis |
| `GET` | `/api/settings` | **[NEW]** Get alert configuration |
| `POST` | `/api/settings` | **[NEW]** Save alert configuration |
| `GET` | `/api/alerts/history` | **[NEW]** Alert history (last 20) |
| `GET` | `/health` | Backend health check |
| `GET` | `/docs` | Interactive Swagger API explorer |

---

## Project Structure

```
Blockchain project/
├── docker-compose.yml        # [NEW] One-command Docker deployment
├── backend/
│   ├── Dockerfile            # [NEW] Python 3.11-slim container
│   ├── docker-entrypoint.sh  # [NEW] Auto-trains ML models on start
│   ├── main.py               # FastAPI app entry point
│   ├── simulate_events.py    # Sends 220 events through ML pipeline
│   ├── clear_db.py           # Clear MongoDB logs
│   ├── .env                  # Environment variables
│   ├── alerts/               # [NEW]
│   │   ├── alert_engine.py   # 5 trigger rules + 10-min cooldown
│   │   ├── email_notifier.py # HTML email via Gmail SMTP
│   │   └── slack_notifier.py # Slack Block Kit messages
│   ├── models/               # ML model inference
│   ├── routes/
│   │   ├── logs.py           # POST/GET /api/logs + alert hook
│   │   ├── explain.py        # [NEW] GET /api/logs/{id}/explain
│   │   ├── settings.py       # [NEW] GET/POST /api/settings
│   │   ├── verify.py         # Blockchain integrity check
│   │   └── profile.py        # Behavioral profiler endpoints
│   └── db/mongo_client.py    # MongoDB client
├── frontend/
│   ├── Dockerfile            # [NEW] Multi-stage React → Nginx
│   ├── nginx.conf            # [NEW] SPA + /api proxy config
│   └── src/
│       ├── pages/
│       │   ├── Dashboard.jsx     # [UPDATED] Explain button
│       │   ├── Settings.jsx      # [NEW] Alert config + history
│       │   └── ForensicReport.jsx# [UPDATED] Explain button
│       └── components/
│           └── ExplainModal.jsx  # [NEW] AI analysis modal
├── contracts/AuditLog.sol    # Ethereum smart contract
└── hardhat/Dockerfile        # [NEW] Local blockchain container
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `&&` not working in PowerShell | Use `;` instead: `python clear_db.py ; python simulate_events.py` |
| Port 8000 already in use | `netstat -ano \| findstr :8000` → `taskkill /f /pid <PID>` |
| 5000+ duplicate events | `python clear_db.py` then `python simulate_events.py` |
| Explain shows "Log not found" | Refresh dashboard first — stale log IDs from old DB |
| Explain shows 401 error | Invalid API key — check `ANTHROPIC_API_KEY` in `.env` |
| Explain shows 400 error | No credits — local fallback runs automatically |
| MongoDB "Access denied" | MongoDB is already running as a Windows service |

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
| ✅ **Blockchain Verifier Fixed** | End-to-end VERIFIED status — every ingested log gets a real `tx_hash` and `block_number` stored on-chain |

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
  │  6. Blockchain Writer   → tx_hash + block saved │
  └─────────────────────────────────────────────────┘
       │                    │
       ▼                    ▼
  MongoDB               Hardhat Ethereum
  (full log + tx_hash)  (SHA-256 canonical hash)
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
| Web3 | web3.py v7.x | Ethereum interaction (Python 3.12 compatible) |

---

## Dashboard Pages

| Page | URL | What It Shows |
|------|-----|--------------| 
| **Live Threat Feed** | `/` | Real-time event stream. Stats: total, high severity, anomalies, avg risk. 🤖 Explain button on HIGH/CRITICAL |
| **AI Analytics** | `/analytics` | Threat distribution pie, risk timeline, activity heatmap, top IPs/users |
| **Blockchain Verifier** | `/verify` | Enter Log ID → ✅ VERIFIED or ⚠️ TAMPERED comparison |
| **Behavioral Profiler** | `/profile` | Per-user risk timeline, known IPs, behavioral flags |
| **Forensic Report** | `/forensics` | Filter by severity/threat/user → Export PDF |
| **Settings** | `/settings` | Configure alerts — email, Slack, thresholds, alert history |

---

## How to Start (CMD — Recommended)

Open **3 CMD windows**:

### Terminal 1 — Hardhat Blockchain Node
```cmd
cd "e:\Blockchain project"
npx hardhat node
```
Wait for: `Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545/`

### Terminal 2 — Deploy Smart Contract (first time only)
```cmd
cd "e:\Blockchain project"
npx hardhat run scripts/deploy.js --network localhost
```
Wait for: `AuditLog deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3`

### Terminal 3 — Backend
```cmd
cd "e:\Blockchain project\backend"
python -m uvicorn main:app --port 8001
```
Wait for: `[OK] Blockchain node connected` and `Application startup complete.`

### Terminal 4 — Frontend
```cmd
cd "e:\Blockchain project\frontend"
npm run dev
```
Wait for: `Local: http://localhost:5173/`

### Terminal 5 — Seed Data (first time only)
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
> 
> ⚠️ **Port Note:** The backend runs on **port 8001** (port 8000 is reserved by Windows Hyper-V on some machines). The Vite frontend proxy is already configured to target `http://localhost:8001`.

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

## Blockchain Verifier

Every log ingested through `/api/logs` automatically:
1. Gets its SHA-256 hash computed from **canonical core fields** (user_id, source_ip, event_type, description, hour, threat_label, threat_confidence, is_anomaly, anomaly_score, risk_score, severity)
2. Stores the hash on-chain via `storeLog(logId, logHash, ...)` — the MongoDB ObjectId is used as the on-chain key
3. Updates the MongoDB document with the real `tx_hash` and `block_number`

**To verify a log:**
1. Go to **Forensic Report** page → copy any Log ObjectId
2. Go to **Blockchain Verifier** → paste the ID → click Verify
3. The system re-hashes the current MongoDB data and compares against the on-chain hash → ✅ **VERIFIED**

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
BACKEND_PORT=8001

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
| `POST` | `/api/logs` | Ingest security event (runs full ML pipeline + blockchain write) |
| `GET` | `/api/logs` | List logs with filters |
| `GET` | `/api/logs/stream` | SSE real-time event stream |
| `GET` | `/api/logs/analytics` | Aggregated analytics for charts |
| `GET` | `/api/logs/{id}/explain` | LLM threat explanation with MITRE mapping |
| `GET` | `/api/verify/{log_id}` | Verify log integrity vs blockchain hash → VERIFIED/TAMPERED |
| `GET` | `/api/profile` | List all user behavioral profiles |
| `GET` | `/api/profile/{user_id}` | Get user's behavioral analysis |
| `GET` | `/api/settings` | Get alert configuration |
| `POST` | `/api/settings` | Save alert configuration |
| `GET` | `/api/alerts/history` | Alert history (last 20) |
| `GET` | `/health` | Backend health check |
| `GET` | `/docs` | Interactive Swagger API explorer |

---

## Project Structure

```
Blockchain project/
├── docker-compose.yml        # One-command Docker deployment
├── README.md                 # This file
├── backend/
│   ├── Dockerfile            # Python 3.12-slim container
│   ├── docker-entrypoint.sh  # Auto-trains ML models on start
│   ├── main.py               # FastAPI app entry point
│   ├── simulate_events.py    # Sends 220 events through ML pipeline
│   ├── clear_db.py           # Clear MongoDB logs
│   ├── .env                  # Environment variables (BACKEND_PORT=8001)
│   ├── deployment.json       # Auto-generated after deploy script
│   ├── alerts/
│   │   ├── alert_engine.py   # 5 trigger rules + 10-min cooldown
│   │   ├── email_notifier.py # HTML email via Gmail SMTP
│   │   └── slack_notifier.py # Slack Block Kit messages
│   ├── blockchain/
│   │   └── web3_client.py    # web3.py v7 client — store/verify on Hardhat
│   ├── models/               # ML model inference
│   ├── routes/
│   │   ├── logs.py           # POST/GET /api/logs + blockchain + alert hook
│   │   ├── explain.py        # GET /api/logs/{id}/explain
│   │   ├── settings.py       # GET/POST /api/settings
│   │   ├── verify.py         # Blockchain integrity check (VERIFIED/TAMPERED)
│   │   └── profile.py        # Behavioral profiler endpoints
│   └── db/mongo_client.py    # MongoDB async client (Motor)
├── frontend/
│   ├── Dockerfile            # Multi-stage React → Nginx
│   ├── nginx.conf            # SPA + /api proxy config
│   ├── vite.config.js        # Proxy → http://localhost:8001
│   └── src/
│       ├── pages/
│       │   ├── Dashboard.jsx
│       │   ├── Analytics.jsx
│       │   ├── BlockchainVerifier.jsx
│       │   ├── BehavioralProfiler.jsx
│       │   ├── ForensicReport.jsx
│       │   └── Settings.jsx
│       └── components/
│           └── ExplainModal.jsx
├── contracts/AuditLog.sol    # Ethereum smart contract
│   └── storeLog(logId, logHash, riskScore, threatLabel, eventType, userId)
└── artifacts/                # Auto-generated by Hardhat compile
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `&&` not working in PowerShell | Use `;` instead: `python clear_db.py ; python simulate_events.py` |
| Port 8001 already in use | `Get-NetTCPConnection -LocalPort 8001 \| Select OwningProcess` → `Stop-Process -Id <PID>` |
| Port 8000 can't bind (error 10048/13) | Windows Hyper-V reserves port 8000 — use port 8001 (already configured) |
| `web3` import fails (`pkg_resources`) | Run: `pip install "web3>=6.0.0" --upgrade` |
| Blockchain shows UNAVAILABLE | Start Hardhat: `npx hardhat node` then deploy: `npx hardhat run scripts/deploy.js --network localhost` |
| Blockchain shows NOT_FOUND_ON_CHAIN | Old data pre-dates the fix — run `python clear_db.py` then `python simulate_events.py` |
| tx_hash is null in MongoDB | Restart backend after Hardhat starts — it caches blockchain connection at startup |
| `Assertion failed` after deploy | Harmless Node.js v25 / libuv bug on Windows — deploy still works |
| 5000+ duplicate events | `python clear_db.py` then `python simulate_events.py` |
| Explain shows "Log not found" | Refresh dashboard first — stale log IDs from old DB |
| Explain shows 401 error | Invalid API key — check `ANTHROPIC_API_KEY` in `.env` |
| Explain shows 400 error | No credits — local fallback runs automatically |
| MongoDB "Access denied" | MongoDB is already running as a Windows service |

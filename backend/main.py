"""
FastAPI Main Application -- AI-Powered Blockchain Audit Log System
"""

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routes.logs import router as logs_router
from routes.verify import router as verify_router
from routes.profile import router as profile_router
from routes.explain import router as explain_router
from routes.settings import router as settings_router

load_dotenv()

# Force UTF-8 stdout to avoid cp1252 errors on Windows
if sys.stdout.encoding != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

app = FastAPI(
    title="AI Blockchain Audit Log System",
    description="Tamper-proof cybersecurity audit log with ML threat detection",
    version="2.0.0",
)

# -- CORS ----------------------------------------------------------------------
app.add_middleware(  # type: ignore[arg-type]
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:80"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -- Routers -------------------------------------------------------------------
app.include_router(logs_router)
app.include_router(verify_router)
app.include_router(profile_router)
app.include_router(explain_router)
app.include_router(settings_router)


@app.on_event("startup")
async def startup_event():
    """Warm up ML models on startup and capture event loop for background tasks."""
    import asyncio
    print("[*] AI Blockchain Audit Log System starting...")

    # Capture main loop so background threads in routes.logs can submit coroutines
    import routes.logs as _logs_module
    _logs_module._main_loop = asyncio.get_event_loop()  # type: ignore[attr-defined]

    try:
        from models.anomaly_detector import detect_anomaly
        from models.threat_classifier import classify_threat
        test_features = [2.0, 1500.0, 2000.0, 8, 6, 0.05, 0.04, 0.03, 0.85, 0.15,
                         12, 10, 0.82, 0.18, 0.04, 10, 0, 0, 1, 3]
        detect_anomaly(test_features)
        classify_threat(test_features)
        print("[OK] ML models loaded successfully")
    except FileNotFoundError:
        print("[!] ML models not found -- run: python models/train_models.py")
    except Exception as e:
        print(f"[!] ML warmup error: {e}")

    from blockchain.web3_client import is_blockchain_available
    if is_blockchain_available():
        print("[OK] Blockchain node connected")
    else:
        print("[!] Blockchain node not reachable -- logs stored to MongoDB only")


@app.get("/")
async def root():
    return {
        "service": "AI Blockchain Audit Log System",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    from blockchain.web3_client import is_blockchain_available
    return {
        "status": "ok",
        "blockchain": is_blockchain_available(),
    }

"""
Logs Router — Core log ingestion, query, SSE stream, and analytics endpoints
"""

import json
import asyncio
from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Query, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from models.anomaly_detector import detect_anomaly
from models.threat_classifier import classify_threat
from models.risk_scorer import compute_risk_score, score_to_severity
from models.behavioral_profiler import update_profile
from db.mongo_client import insert_log, get_logs, get_analytics

router = APIRouter(prefix="/api/logs", tags=["logs"])

_sse_subscribers: List[asyncio.Queue] = []


class LogIngestionRequest(BaseModel):
    user_id: str
    source_ip: str
    event_type: str
    description: str
    hour: Optional[int] = None
    features: Optional[List[float]] = None
    metadata: Optional[dict] = {}


def _auto_features(req: LogIngestionRequest) -> List[float]:
    import random
    hour = req.hour if req.hour is not None else datetime.utcnow().hour
    sigs = {
        "brute_force":          [0.5, 500, 100, 200, 180, 0.7, 0.7, 0.3, 0.9, 0.1, 50, 45, 0.9, 0.1, 0.6, hour, 15, 0, 0, 2],
        "port_scan":            [0.1, 200, 50, 450, 400, 0.6, 0.6, 0.4, 0.1, 0.9, 240, 10, 0.1, 0.9, 0.6, hour, 2, 0, 0, 1],
        "privilege_escalation": [10, 5000, 2000, 5, 3, 0.0, 0.0, 0.0, 0.8, 0.2, 10, 8, 0.8, 0.2, 0.0, hour, 0, 1, 30, 40],
        "dos_attack":           [0.05, 50000, 10, 510, 510, 0.9, 0.9, 0.7, 0.95, 0.05, 255, 255, 0.95, 0.05, 0.9, hour, 1, 0, 0, 0],
        "data_exfiltration":    [120, 10000, 1000, 3, 2, 0.0, 0.0, 0.0, 0.7, 0.3, 5, 4, 0.7, 0.3, 0.0, hour, 0, 1, 5, 80],
        "normal_login":         [2, 1500, 3000, 5, 4, 0.02, 0.01, 0.01, 0.9, 0.1, 8, 6, 0.85, 0.15, 0.01, hour, 0, 0, 1, 2],
        "failed_login":         [1, 300, 100, 20, 18, 0.1, 0.1, 0.3, 0.85, 0.15, 15, 12, 0.8, 0.2, 0.1, hour, 5, 0, 0, 1],
        "unauthorized_access":  [5, 2000, 500, 10, 8, 0.05, 0.05, 0.1, 0.7, 0.3, 20, 15, 0.7, 0.3, 0.1, hour, 3, 0, 2, 15],
        "lateral_movement":     [8, 3000, 700, 15, 12, 0.1, 0.1, 0.2, 0.75, 0.25, 30, 20, 0.75, 0.25, 0.2, hour, 4, 1, 5, 25],
        "sql_injection":        [3, 800, 200, 30, 25, 0.3, 0.3, 0.5, 0.8, 0.2, 25, 18, 0.8, 0.2, 0.4, hour, 8, 0, 1, 10],
    }
    base = sigs.get(req.event_type, [2.0, 1500.0, 2000.0, 8, 6, 0.05, 0.04, 0.03, 0.85, 0.15, 12, 10, 0.82, 0.18, 0.04, hour, 0, 0, 1, 3])
    return [v * (1 + random.gauss(0, 0.05)) for v in base]


@router.post("")
async def ingest_log(req: LogIngestionRequest, background_tasks: BackgroundTasks):
    hour = req.hour if req.hour is not None else datetime.utcnow().hour
    features = req.features or _auto_features(req)

    # ML Pipeline
    try:
        anomaly_result = detect_anomaly(features)
        threat_result = classify_threat(features)
    except FileNotFoundError:
        anomaly_result = {"is_anomaly": False, "normalized_score": 0.1, "raw_score": 0.4}
        threat_result = {"label": "Normal", "label_id": 0, "confidence": 0.9, "probabilities": {"Normal": 0.9}}

    risk_score = compute_risk_score(
        event_type=req.event_type,
        anomaly_normalized=anomaly_result["normalized_score"],
        threat_label=threat_result["label"],
        frequency_count=5,
        hour=hour,
    )
    severity = score_to_severity(risk_score)

    behavioral = update_profile(
        user_id=req.user_id,
        ip=req.source_ip,
        hour=hour,
        event_type=req.event_type,
        risk_score=risk_score,
    )

    log_doc = {
        "user_id": req.user_id,
        "source_ip": req.source_ip,
        "event_type": req.event_type,
        "description": req.description,
        "hour": hour,
        "threat_label": threat_result["label"],
        "threat_confidence": threat_result["confidence"],
        "threat_probabilities": threat_result["probabilities"],
        "is_anomaly": anomaly_result["is_anomaly"],
        "anomaly_score": anomaly_result["normalized_score"],
        "risk_score": risk_score,
        "severity": severity,
        "behavioral_deviation": behavioral["deviation_score"],
        "behavioral_flags": behavioral["flags"],
        "metadata": req.metadata or {},
        "tx_hash": None,
        "block_number": None,
    }

    log_id = await insert_log(log_doc)
    log_doc["_id"] = log_id

    # Fire alerts in background (non-blocking)
    background_tasks.add_task(_run_alert, dict(log_doc))

    # Broadcast to SSE
    broadcast = {k: v for k, v in log_doc.items()}
    for q in _sse_subscribers:
        try:
            q.put_nowait(broadcast)
        except asyncio.QueueFull:
            pass

    return {
        "success": True, "log_id": log_id,
        "risk_score": risk_score, "severity": severity,
        "threat_label": threat_result["label"],
        "is_anomaly": anomaly_result["is_anomaly"],
    }


def _run_alert(log_doc: dict):
    """Schedule alert processing on uvicorn's running event loop (non-blocking)."""
    import asyncio
    try:
        from alerts.alert_engine import process_alert
        loop = asyncio.get_running_loop()
        loop.create_task(process_alert(log_doc))
    except RuntimeError:
        pass  # No running loop — safe to ignore in test contexts
    except Exception:
        pass  # Never let alert errors affect the API


@router.get("/stream")
async def stream_logs():
    queue: asyncio.Queue = asyncio.Queue(maxsize=100)
    _sse_subscribers.append(queue)

    async def event_generator():
        try:
            logs, _ = await get_logs(limit=10)
            for log in reversed(logs):
                yield f"data: {json.dumps(log, default=str)}\n\n"
            while True:
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=30)
                    yield f"data: {json.dumps(data, default=str)}\n\n"
                except asyncio.TimeoutError:
                    yield ": heartbeat\n\n"
        finally:
            if queue in _sse_subscribers:
                _sse_subscribers.remove(queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/analytics")
async def analytics_endpoint():
    return await get_analytics()


@router.get("")
async def list_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    severity: Optional[str] = None,
    threat_label: Optional[str] = None,
    user_id: Optional[str] = None,
):
    logs, total = await get_logs(skip=skip, limit=limit, severity=severity,
                                  threat_label=threat_label, user_id=user_id)
    return {"logs": logs, "total": total, "skip": skip, "limit": limit}


@router.get("/{log_id}")
async def get_single_log(log_id: str):
    from db.mongo_client import get_log_by_id
    from fastapi import HTTPException
    log = await get_log_by_id(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    return log

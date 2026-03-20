"""
MongoDB Client — with automatic in-memory fallback.
If MongoDB is not running, all data is stored in memory (lost on restart).
This lets the app run fully without a MongoDB installation.
"""

import logging
from datetime import datetime
from typing import Optional, Any
from bson import ObjectId  # type: ignore[import]

logger = logging.getLogger(__name__)

# ── Try connecting to real MongoDB ─────────────────────────────────────────────
_real_db: Any = None
try:
    import motor.motor_asyncio as _motor
    from dotenv import load_dotenv
    import os
    load_dotenv()
    _MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    _MONGO_DB  = os.getenv("MONGO_DB", "audit_log_db")
    _client    = _motor.AsyncIOMotorClient(_MONGO_URI, serverSelectionTimeoutMS=2000)
    _real_db   = _client[_MONGO_DB]
    logger.info("Motor MongoDB client created for %s", _MONGO_URI)
except Exception as e:
    logger.warning("MongoDB client init failed: %s — using in-memory store", e)

# ── In-memory store (fallback) ─────────────────────────────────────────────────
_mem_logs: list = []   # list of log dicts
_mongo_ok: Optional[bool] = None   # cached ping result


async def _is_mongo_up() -> bool:
    global _mongo_ok, _real_db
    if _real_db is None:
        return False
    if _mongo_ok is not None:
        return _mongo_ok
    try:
        await _real_db.client.admin.command("ping")
        _mongo_ok = True
    except Exception:
        _mongo_ok = False
        logger.warning("MongoDB unreachable — using in-memory store for all operations")
    return _mongo_ok


# ── Public API (same interface regardless of backend) ─────────────────────────

async def insert_log(log_data: dict) -> str:
    """Insert a log document. Returns the inserted ID as a string."""
    doc = {**log_data, "created_at": datetime.utcnow().isoformat()}
    if await _is_mongo_up():
        result = await _real_db.logs.insert_one(doc)  # type: ignore[union-attr]
        return str(result.inserted_id)
    else:
        id_str = str(ObjectId())
        doc["_id"] = id_str
        _mem_logs.append(doc)
        return id_str


async def get_logs(limit: int = 50, skip: int = 0,
                   severity: Optional[str] = None, threat_label: Optional[str] = None,
                   user_id: Optional[str] = None) -> tuple[list, int]:
    """Return (logs, total_count) with optional filters."""
    if await _is_mongo_up():
        query = {}
        if severity:     query["severity"]     = severity
        if threat_label: query["threat_label"] = threat_label
        if user_id:      query["user_id"]       = user_id
        total  = await _real_db.logs.count_documents(query)  # type: ignore[union-attr]
        cursor = _real_db.logs.find(query).sort("created_at", -1).skip(skip).limit(limit)  # type: ignore[union-attr]
        logs   = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            logs.append(doc)
        return logs, total
    else:
        logs = list(reversed(_mem_logs))
        if severity:     logs = [l for l in logs if l.get("severity") == severity]
        if threat_label: logs = [l for l in logs if l.get("threat_label") == threat_label]
        if user_id:      logs = [l for l in logs if l.get("user_id") == user_id]
        total = len(logs)
        return logs[skip: skip + limit], total  # type: ignore[index]


async def get_log_by_id(log_id: str) -> Optional[dict]:
    """Fetch a single log by its string ID."""
    if await _is_mongo_up():
        try:
            doc = await _real_db.logs.find_one({"_id": ObjectId(log_id)})  # type: ignore[union-attr]
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        except Exception:
            return None
    else:
        return next((l for l in _mem_logs if l.get("_id") == log_id), None)


async def update_log(log_id: str, fields: dict) -> None:
    """Patch an existing log document with new fields (e.g. tx_hash, block_number)."""
    if await _is_mongo_up():
        try:
            await _real_db.logs.update_one(  # type: ignore[union-attr]
                {"_id": ObjectId(log_id)},
                {"$set": fields},
            )
        except Exception as e:
            logger.warning("update_log failed for %s: %s", log_id, e)
    else:
        for log in _mem_logs:
            if log.get("_id") == log_id:
                log.update(fields)
                break


async def get_analytics() -> dict:
    """Return aggregated analytics data."""
    if await _is_mongo_up():
        threat_dist = []
        async for doc in _real_db.logs.aggregate([  # type: ignore[union-attr]
            {"$group": {"_id": "$threat_label", "count": {"$sum": 1}}},
            {"$project": {"label": "$_id", "count": 1, "_id": 0}},
        ]):
            threat_dist.append(doc)

        severity_dist = []
        async for doc in _real_db.logs.aggregate([  # type: ignore[union-attr]
            {"$group": {"_id": "$severity", "count": {"$sum": 1}}},
            {"$project": {"label": "$_id", "count": 1, "_id": 0}},
        ]):
            severity_dist.append(doc)

        risk_over_time = []
        async for doc in _real_db.logs.find({}, {"risk_score": 1, "created_at": 1, "_id": 0}).sort("created_at", -1).limit(100):  # type: ignore[union-attr]
            risk_over_time.append({"risk": doc.get("risk_score", 0), "time": doc.get("created_at")})

        top_ips = []
        async for doc in _real_db.logs.aggregate([  # type: ignore[union-attr]
            {"$group": {"_id": "$source_ip", "avg_risk": {"$avg": "$risk_score"}, "count": {"$sum": 1}}},
            {"$sort": {"avg_risk": -1}},
            {"$limit": 8},
            {"$project": {"ip": "$_id", "avg_risk": {"$round": ["$avg_risk", 1]}, "count": 1, "_id": 0}},
        ]):
            top_ips.append(doc)

        top_users = []
        async for doc in _real_db.logs.aggregate([  # type: ignore[union-attr]
            {"$group": {"_id": "$user_id", "avg_risk": {"$avg": "$risk_score"}, "count": {"$sum": 1}}},
            {"$sort": {"avg_risk": -1}},
            {"$limit": 8},
            {"$project": {"user": "$_id", "avg_risk": {"$round": ["$avg_risk", 1]}, "count": 1, "_id": 0}},
        ]):
            top_users.append(doc)

        return {
            "threat_distribution": threat_dist,
            "severity_distribution": severity_dist,
            "risk_over_time": list(reversed(risk_over_time)),
            "top_ips": top_ips,
            "top_users": top_users,
            "hourly_heatmap": [],
        }
    else:
        # In-memory analytics
        from collections import Counter
        logs = _mem_logs
        threat_dist   = [{"label": k, "count": v} for k, v in Counter(l.get("threat_label", "Normal") for l in logs).items()]
        severity_dist = [{"label": k, "count": v} for k, v in Counter(l.get("severity", "INFO")       for l in logs).items()]
        risk_over_time = [{"risk": l.get("risk_score", 0), "time": l.get("created_at")} for l in logs[-100:]]  # type: ignore[index]
        from collections import defaultdict
        ip_risk: dict = defaultdict(list)
        user_risk: dict = defaultdict(list)
        for l in logs:
            ip_risk[l.get("source_ip", "?")].append(l.get("risk_score", 0))
            user_risk[l.get("user_id", "?")].append(l.get("risk_score", 0))
        top_ips   = sorted([{"ip": k,   "avg_risk": round(float(sum(v)/len(v)), 1)} for k, v in ip_risk.items()],   key=lambda x: -x["avg_risk"])[:8]  # type: ignore[call-overload,index]
        top_users = sorted([{"user": k, "avg_risk": round(float(sum(v)/len(v)), 1)} for k, v in user_risk.items()], key=lambda x: -x["avg_risk"])[:8]  # type: ignore[call-overload,index]
        return {
            "threat_distribution": threat_dist,
            "severity_distribution": severity_dist,
            "risk_over_time": risk_over_time,
            "top_ips": top_ips,
            "top_users": top_users,
            "hourly_heatmap": [],
        }


# ── Explanation cache (Feature 2 — LLM) ───────────────────────────────────────

async def save_explanation(log_id: str, explanation: dict) -> None:
    """Cache LLM explanation on the log document itself."""
    if await _is_mongo_up():
        try:
            await _real_db.logs.update_one(  # type: ignore[union-attr]
                {"_id": ObjectId(log_id)},
                {"$set": {"explanation": explanation}}
            )
        except Exception as e:
            logger.warning("save_explanation failed: %s", e)
    else:
        for log in _mem_logs:
            if log.get("_id") == log_id:
                log["explanation"] = explanation
                break


async def get_explanation(log_id: str) -> Optional[dict]:
    """Return cached explanation dict, or None if not yet generated."""
    if await _is_mongo_up():
        try:
            doc = await _real_db.logs.find_one(  # type: ignore[union-attr]
                {"_id": ObjectId(log_id)},
                {"explanation": 1}
            )
            return doc.get("explanation") if doc else None  # type: ignore[return-value]
        except Exception:
            return None
    else:
        log = next((l for l in _mem_logs if l.get("_id") == log_id), None)
        return log.get("explanation") if log else None


# ── Settings (Feature 3 — Alerts) ─────────────────────────────────────────────

_mem_settings: dict = {}      # in-memory fallback for settings
_mem_alerts:   list = []      # in-memory fallback for alert history

_DEFAULT_SETTINGS = {
    "email_enabled": False,
    "slack_enabled": False,
    "smtp_user": "",
    "slack_webhook_url": "",
    "min_severity": "HIGH",
    "risk_threshold": 75,
}


async def get_settings() -> dict:
    if await _is_mongo_up():
        doc = await _real_db.settings.find_one({"_id": "global"})  # type: ignore[union-attr]
        if doc:
            doc.pop("_id", None)
            return doc
        return dict(_DEFAULT_SETTINGS)
    return dict(_mem_settings) or dict(_DEFAULT_SETTINGS)


async def save_settings(data: dict) -> None:
    if await _is_mongo_up():
        await _real_db.settings.update_one(  # type: ignore[union-attr]
            {"_id": "global"},
            {"$set": data},
            upsert=True
        )
    else:
        _mem_settings.update(data)


async def save_alert(alert_doc: dict) -> None:
    """Persist a fired alert to the alerts collection."""
    doc = {**alert_doc, "fired_at": datetime.utcnow().isoformat()}
    if await _is_mongo_up():
        await _real_db.alerts.insert_one(doc)  # type: ignore[union-attr]
    else:
        _mem_alerts.append(doc)
        if len(_mem_alerts) > 200:
            _mem_alerts.pop(0)


async def get_alert_history(limit: int = 20) -> list:
    """Return last N fired alerts, newest first."""
    if await _is_mongo_up():
        cursor = _real_db.alerts.find({}).sort("fired_at", -1).limit(limit)  # type: ignore[union-attr]
        docs = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            docs.append(doc)
        return docs
    else:
        alerts_reversed = list(reversed(_mem_alerts))
        return alerts_reversed[:limit]  # type: ignore[index]

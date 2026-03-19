"""
Settings & Alert History Routes
GET  /api/settings         — fetch current alert config
POST /api/settings         — save alert config
GET  /api/alerts/history   — last 20 fired alerts
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from db.mongo_client import get_settings, save_settings, get_alert_history

router = APIRouter(tags=["settings"])


class SettingsPayload(BaseModel):
    email_enabled:      Optional[bool]  = None
    slack_enabled:      Optional[bool]  = None
    smtp_user:          Optional[str]   = None
    slack_webhook_url:  Optional[str]   = None
    min_severity:       Optional[str]   = None   # INFO|LOW|MEDIUM|HIGH|CRITICAL
    risk_threshold:     Optional[int]   = None   # 0-100


@router.get("/api/settings")
async def get_alert_settings():
    """Return current alert configuration."""
    return await get_settings()


@router.post("/api/settings")
async def update_alert_settings(payload: SettingsPayload):
    """Save alert configuration to MongoDB."""
    data = {k: v for k, v in payload.model_dump().items() if v is not None}
    if not data:
        return {"message": "No changes provided"}
    await save_settings(data)
    return {"message": "Settings saved", "updated": data}


@router.get("/api/alerts/history")
async def alert_history(limit: int = 20):
    """Return the last N security alerts that were fired."""
    alerts = await get_alert_history(limit=min(limit, 100))
    return {"alerts": alerts, "count": len(alerts)}

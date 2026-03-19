"""
Alert Engine — evaluates every ingested log against trigger rules
and fires email/Slack notifications when conditions are met.

Trigger rules (checked in order):
  1. severity in [CRITICAL, HIGH]
  2. risk_score > threshold (default 75)
  3. is_anomaly AND severity >= MEDIUM
  4. Same IP fires 5+ events in 60 seconds  -> rate alert
  5. Same user fires 3+ HIGH events in 5 mins -> user alert

A 10-minute cooldown per (source_ip, event_type) prevents spam.
Settings are read live from MongoDB so changes take effect immediately.
"""

import asyncio
import logging
from collections import defaultdict, deque
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# ── In-process rate tracking (resets on restart) ───────────────────────────────
_ip_timestamps:   dict = defaultdict(lambda: deque(maxlen=20))   # ip  -> [datetime, ...]
_user_high_times: dict = defaultdict(lambda: deque(maxlen=10))   # user -> [datetime, ...]
_cooldowns:       dict = {}   # (ip, event_type) -> datetime of last alert

SEVERITY_ORDER = {"INFO": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
COOLDOWN_MINUTES = 10


def _severity_gte(a: str, b: str) -> bool:
    return SEVERITY_ORDER.get(a, 0) >= SEVERITY_ORDER.get(b, 0)


def _check_cooldown(ip: str, event_type: str) -> bool:
    """Returns True if we are NOT in cooldown (alert is allowed)."""
    key = (ip, event_type)
    last = _cooldowns.get(key)
    if last and datetime.utcnow() - last < timedelta(minutes=COOLDOWN_MINUTES):
        return False
    _cooldowns[key] = datetime.utcnow()
    return True


async def process_alert(log: dict) -> None:
    """
    Called after ML pipeline in POST /api/logs.
    Evaluates trigger rules asynchronously — never blocks the HTTP response.
    """
    from db.mongo_client import get_settings, save_alert
    from alerts.email_notifier import send_email_alert
    from alerts.slack_notifier import send_slack_alert

    try:
        settings = await get_settings()
        email_on  = settings.get("email_enabled", False)
        slack_on  = settings.get("slack_enabled", False)
        threshold = int(settings.get("risk_threshold", 75))
        min_sev   = settings.get("min_severity", "HIGH")

        if not email_on and not slack_on:
            return  # nothing to do

        severity   = log.get("severity", "INFO")
        risk       = log.get("risk_score", 0)
        is_anomaly = log.get("is_anomaly", False)
        ip         = log.get("source_ip", "")
        user       = log.get("user_id", "")
        event_type = log.get("event_type", "")
        now        = datetime.utcnow()

        # Track timestamps for rate checks
        _ip_timestamps[ip].append(now)
        if severity in ("HIGH", "CRITICAL"):
            _user_high_times[user].append(now)

        # ── Evaluate triggers ────────────────────────────────────────────────
        reasons = []

        if _severity_gte(severity, min_sev):
            reasons.append(f"Severity {severity} meets threshold {min_sev}")

        if risk > threshold:
            reasons.append(f"Risk score {risk} exceeds threshold {threshold}")

        if is_anomaly and _severity_gte(severity, "MEDIUM"):
            reasons.append("AI anomaly detected with medium+ severity")

        # Rate alert: same IP 5+ events in 60 seconds
        recent_ip = [t for t in _ip_timestamps[ip] if now - t < timedelta(seconds=60)]
        if len(recent_ip) >= 5:
            reasons.append(f"IP {ip} triggered {len(recent_ip)} events in 60 seconds")

        # User alert: 3+ HIGH events in 5 minutes
        recent_high = [t for t in _user_high_times[user] if now - t < timedelta(minutes=5)]
        if len(recent_high) >= 3:
            reasons.append(f"User {user} triggered {len(recent_high)} HIGH events in 5 minutes")

        if not reasons:
            return

        # ── Cooldown check ───────────────────────────────────────────────────
        if not _check_cooldown(ip, event_type):
            logger.debug("Alert suppressed by cooldown for %s / %s", ip, event_type)
            return

        # ── Build alert payload ──────────────────────────────────────────────
        alert_doc = {
            "log_id":      log.get("_id", ""),
            "event_type":  event_type,
            "user_id":     user,
            "source_ip":   ip,
            "severity":    severity,
            "risk_score":  risk,
            "threat_label":log.get("threat_label", ""),
            "is_anomaly":  is_anomaly,
            "reasons":     reasons,
            "channels":    [],
        }

        # ── Fire alerts ──────────────────────────────────────────────────────
        tasks = []
        if email_on:
            tasks.append(_fire_email(log, reasons, settings, alert_doc, send_email_alert))
        if slack_on:
            tasks.append(_fire_slack(log, reasons, settings, alert_doc, send_slack_alert))

        await asyncio.gather(*tasks, return_exceptions=True)
        await save_alert(alert_doc)

    except Exception as e:
        logger.error("Alert engine error: %s", e)


async def _fire_email(log, reasons, settings, alert_doc, send_fn):
    try:
        await asyncio.to_thread(send_fn, log, reasons, settings)
        alert_doc["channels"].append("email")
        logger.info("Email alert sent for %s", log.get("_id"))
    except Exception as e:
        logger.warning("Email alert failed: %s", e)


async def _fire_slack(log, reasons, settings, alert_doc, send_fn):
    try:
        await asyncio.to_thread(send_fn, log, reasons, settings)
        alert_doc["channels"].append("slack")
        logger.info("Slack alert sent for %s", log.get("_id"))
    except Exception as e:
        logger.warning("Slack alert failed: %s", e)

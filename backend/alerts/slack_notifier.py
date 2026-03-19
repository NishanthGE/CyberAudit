"""
Slack Alert Notifier — sends rich Block Kit messages via Incoming Webhook.
"""

import os
import json
import logging
import httpx

logger = logging.getLogger(__name__)

_SEVERITY_COLORS = {
    "CRITICAL": "#ff003c",
    "HIGH":     "#ff6b00",
    "MEDIUM":   "#ffd700",
    "LOW":      "#00ff87",
    "INFO":     "#60a5fa",
}

_SEVERITY_EMOJI = {
    "CRITICAL": ":rotating_light:",
    "HIGH":     ":warning:",
    "MEDIUM":   ":large_yellow_circle:",
    "LOW":      ":large_green_circle:",
    "INFO":     ":information_source:",
}


def send_slack_alert(log: dict, reasons: list, settings: dict) -> None:
    """
    Send a Slack Block Kit alert to the configured webhook URL.
    Reads SLACK_WEBHOOK_URL from environment (or settings override).
    """
    webhook_url = settings.get("slack_webhook_url") or os.getenv("SLACK_WEBHOOK_URL", "")
    if not webhook_url:
        raise ValueError("SLACK_WEBHOOK_URL not set in .env or settings")

    severity   = log.get("severity", "INFO")
    color      = _SEVERITY_COLORS.get(severity, "#60a5fa")
    emoji      = _SEVERITY_EMOJI.get(severity, ":information_source:")
    event_type = log.get("event_type", "").replace("_", " ").title()
    risk       = log.get("risk_score", 0)
    user       = log.get("user_id", "unknown")
    ip         = log.get("source_ip", "unknown")
    threat     = log.get("threat_label", "Unknown")
    anomaly    = "Yes :red_circle:" if log.get("is_anomaly") else "No :green_circle:"

    reasons_text = "\n".join(f"• {r}" for r in reasons)
    flags = log.get("behavioral_flags") or []
    flags_text = "\n".join(f"• {f}" for f in flags) if flags else "None"

    payload = {
        "attachments": [
            {
                "color": color,
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"{emoji} CyberAudit Security Alert — {severity}",
                            "emoji": True,
                        },
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*Event Type*\n`{event_type}`"},
                            {"type": "mrkdwn", "text": f"*Risk Score*\n`{risk}/100`"},
                            {"type": "mrkdwn", "text": f"*User ID*\n`{user}`"},
                            {"type": "mrkdwn", "text": f"*Source IP*\n`{ip}`"},
                            {"type": "mrkdwn", "text": f"*Threat Label*\n`{threat}`"},
                            {"type": "mrkdwn", "text": f"*Anomaly*\n{anomaly}"},
                        ],
                    },
                    {"type": "divider"},
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*:memo: Description*\n{log.get('description', '')}",
                        },
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*:triangular_flag_on_post: Alert Triggered Because*\n{reasons_text}",
                        },
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*:eyes: Behavioral Flags*\n{flags_text}",
                        },
                    },
                    {"type": "divider"},
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": ":bar_chart: Open Dashboard", "emoji": True},
                                "url": "http://localhost:5173",
                                "style": "danger" if severity in ("CRITICAL", "HIGH") else "primary",
                            },
                            {
                                "type": "button",
                                "text": {"type": "plain_text", "text": ":mag: Forensic Report", "emoji": True},
                                "url": "http://localhost:5173/forensics",
                            },
                        ],
                    },
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": f"Log ID: `{log.get('_id', '')}` | CyberAudit AI Blockchain Audit System",
                            }
                        ],
                    },
                ],
            }
        ]
    }

    response = httpx.post(
        webhook_url,
        content=json.dumps(payload),
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    response.raise_for_status()
    logger.info("Slack alert sent (status %s)", response.status_code)

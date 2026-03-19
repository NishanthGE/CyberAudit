"""
Email Alert Notifier — sends HTML security alerts via Gmail SMTP.
Reads SMTP credentials from environment variables.
"""

import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

_SEVERITY_COLORS = {
    "CRITICAL": "#ff003c",
    "HIGH":     "#ff6b00",
    "MEDIUM":   "#ffd700",
    "LOW":      "#00ff87",
    "INFO":     "#60a5fa",
}


def _build_html(log: dict, reasons: list) -> str:
    severity = log.get("severity", "INFO")
    color    = _SEVERITY_COLORS.get(severity, "#60a5fa")
    flags    = log.get("behavioral_flags") or []
    flag_html = "".join(f"<li>{f}</li>" for f in flags) if flags else "<li>None</li>"

    return f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#0d0d18;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0d0d18;padding:24px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0"
             style="background:#111128;border-radius:12px;border:1px solid {color}40;overflow:hidden;">

        <!-- Header -->
        <tr><td style="background:{color}18;padding:24px 32px;border-bottom:1px solid {color}40;">
          <h1 style="margin:0;color:{color};font-size:22px;">
            &#9888; CyberAudit Security Alert
          </h1>
          <p style="margin:6px 0 0;color:#64748b;font-size:13px;">
            Severity: <strong style="color:{color}">{severity}</strong> &nbsp;|&nbsp;
            Risk Score: <strong style="color:#ffd700">{log.get('risk_score', 0)}/100</strong>
          </p>
        </td></tr>

        <!-- Body -->
        <tr><td style="padding:24px 32px;">

          <h2 style="color:#00f5ff;font-size:14px;margin:0 0 12px;text-transform:uppercase;
                     letter-spacing:1px;">Event Details</h2>
          <table width="100%" cellpadding="6" cellspacing="0"
                 style="background:#0d0d18;border-radius:8px;border:1px solid #1e293b;">
            <tr>
              <td style="color:#64748b;font-size:12px;width:130px;">Event Type</td>
              <td style="color:#e2e8f0;font-size:12px;font-family:monospace;">
                {log.get('event_type','').replace('_',' ').upper()}</td>
            </tr>
            <tr style="background:#111128;">
              <td style="color:#64748b;font-size:12px;">User ID</td>
              <td style="color:#e2e8f0;font-size:12px;font-family:monospace;">{log.get('user_id','')}</td>
            </tr>
            <tr>
              <td style="color:#64748b;font-size:12px;">Source IP</td>
              <td style="color:#e2e8f0;font-size:12px;font-family:monospace;">{log.get('source_ip','')}</td>
            </tr>
            <tr style="background:#111128;">
              <td style="color:#64748b;font-size:12px;">Threat Label</td>
              <td style="color:#e2e8f0;font-size:12px;font-family:monospace;">{log.get('threat_label','')}</td>
            </tr>
            <tr>
              <td style="color:#64748b;font-size:12px;">Anomaly</td>
              <td style="color:{'#ff003c' if log.get('is_anomaly') else '#00ff87'};
                         font-size:12px;font-family:monospace;font-weight:bold;">
                {'YES' if log.get('is_anomaly') else 'No'}</td>
            </tr>
            <tr style="background:#111128;">
              <td style="color:#64748b;font-size:12px;">Description</td>
              <td style="color:#e2e8f0;font-size:12px;">{log.get('description','')}</td>
            </tr>
          </table>

          <h2 style="color:#00f5ff;font-size:14px;margin:20px 0 10px;text-transform:uppercase;
                     letter-spacing:1px;">Alert Triggered Because</h2>
          <ul style="color:#94a3b8;font-size:12px;margin:0;padding-left:20px;line-height:1.8;">
            {"".join(f"<li>{r}</li>" for r in reasons)}
          </ul>

          <h2 style="color:#00f5ff;font-size:14px;margin:20px 0 10px;text-transform:uppercase;
                     letter-spacing:1px;">Behavioral Flags</h2>
          <ul style="color:#94a3b8;font-size:12px;margin:0;padding-left:20px;line-height:1.8;">
            {flag_html}
          </ul>

          <!-- CTA -->
          <div style="margin-top:24px;text-align:center;">
            <a href="http://localhost:5173"
               style="display:inline-block;background:{color};color:white;padding:12px 28px;
                      border-radius:8px;font-weight:bold;font-size:13px;text-decoration:none;">
              Open CyberAudit Dashboard
            </a>
          </div>

        </td></tr>

        <!-- Footer -->
        <tr><td style="padding:16px 32px;border-top:1px solid #1e293b;">
          <p style="margin:0;color:#334155;font-size:11px;text-align:center;">
            CyberAudit AI Blockchain Audit Log System &nbsp;|&nbsp;
            Log ID: {log.get('_id','')}
          </p>
        </td></tr>

      </table>
    </td></tr>
  </table>
</body>
</html>"""


def send_email_alert(log: dict, reasons: list, settings: dict) -> None:
    """
    Send HTML security alert email via Gmail SMTP.
    Reads SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD from environment.
    settings dict may override SMTP_USER as recipient.
    """
    host     = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port     = int(os.getenv("SMTP_PORT", "587"))
    user     = os.getenv("SMTP_USER", "")
    password = os.getenv("SMTP_PASSWORD", "")
    to_addr  = settings.get("smtp_user") or user

    if not user or not password:
        raise ValueError("SMTP_USER and SMTP_PASSWORD must be set in .env")

    severity = log.get("severity", "INFO")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"[CyberAudit] {severity} Alert — {log.get('event_type','').replace('_',' ').title()}"
    msg["From"]    = f"CyberAudit <{user}>"
    msg["To"]      = to_addr

    msg.attach(MIMEText(_build_html(log, reasons), "html"))

    with smtplib.SMTP(host, port) as server:
        server.ehlo()
        server.starttls()
        server.login(user, password)
        server.sendmail(user, to_addr, msg.as_string())

    logger.info("Email alert sent to %s", to_addr)

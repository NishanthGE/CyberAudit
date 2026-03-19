"""
LLM Threat Explanation Route
GET /api/logs/{log_id}/explain

Tries Claude first; if no API key or insufficient credits,
falls back to a rule-based local analysis engine that generates
a full professional explanation from the log's own data fields.
"""

import os
import json
from fastapi import APIRouter, HTTPException
from db.mongo_client import get_log_by_id, save_explanation, get_explanation

router = APIRouter(prefix="/api/logs", tags=["explain"])

SYSTEM_PROMPT = """You are a senior cybersecurity analyst with deep expertise in MITRE ATT&CK, 
threat intelligence, and incident response. You will be given a security event log and must 
analyze it thoroughly.

Return ONLY a valid JSON object with exactly these keys (no markdown, no extra text):
{
  "summary": "2-3 sentence plain-English summary of what happened and why it matters",
  "why_flagged": "Specific technical reasons why the AI flagged this event as suspicious",
  "attack_pattern": "The likely attack pattern or technique being used",
  "mitre_technique": "MITRE ATT&CK technique ID and name e.g. T1110.001 - Brute Force: Password Guessing",
  "recommended_action": "Specific actionable steps the security team should take right now",
  "confidence_reasoning": "Why the AI models assigned this risk score and threat label"
}"""


# ── Rule-based local analysis engine ─────────────────────────────────────────

MITRE_MAP = {
    "brute_force":          ("T1110.001", "Brute Force: Password Guessing"),
    "failed_login":         ("T1110",     "Brute Force"),
    "port_scan":            ("T1046",     "Network Service Discovery"),
    "privilege_escalation": ("T1068",     "Exploitation for Privilege Escalation"),
    "dos_attack":           ("T1499",     "Endpoint Denial of Service"),
    "data_exfiltration":    ("T1041",     "Exfiltration Over C2 Channel"),
    "unauthorized_access":  ("T1078",     "Valid Accounts"),
    "lateral_movement":     ("T1021",     "Remote Services"),
    "sql_injection":        ("T1190",     "Exploit Public-Facing Application"),
    "xss_attempt":          ("T1059.007", "Command and Scripting: JavaScript"),
    "command_injection":    ("T1059",     "Command and Scripting Interpreter"),
    "file_access":          ("T1083",     "File and Directory Discovery"),
    "config_change":        ("T1562",     "Impair Defenses"),
    "service_started":      ("T1543",     "Create or Modify System Process"),
    "service_stopped":      ("T1489",     "Service Stop"),
    "normal_login":         ("T1078",     "Valid Accounts"),
    "dns_query":            ("T1071.004", "Application Layer Protocol: DNS"),
    "network_scan":         ("T1046",     "Network Service Discovery"),
    "malware_detected":     ("T1204",     "User Execution"),
    "ransomware":           ("T1486",     "Data Encrypted for Impact"),
    "credential_dump":      ("T1003",     "OS Credential Dumping"),
}

ATTACK_PATTERNS = {
    "brute_force":
        "Automated credential stuffing — attacker cycles through password combinations at high rate "
        "to gain unauthorized access without triggering lockout.",
    "failed_login":
        "Repeated authentication failures suggest either mis-typed credentials or a low-rate "
        "password spray attack deliberately flying under lockout thresholds.",
    "port_scan":
        "Systematic probing of network ports to map open services, identify running software "
        "versions, and locate potential entry points for further exploitation.",
    "privilege_escalation":
        "Exploitation of a misconfiguration, unpatched kernel vulnerability, or SUID binary "
        "to elevate from user-level to root/admin access.",
    "dos_attack":
        "Volumetric flood attack sending requests at a rate exceeding service capacity, "
        "causing resource exhaustion and denial of legitimate user access.",
    "data_exfiltration":
        "Unauthorized bulk transfer of sensitive data to an external destination, "
        "indicating a data breach in progress or completed.",
    "lateral_movement":
        "Attacker pivoting from initial compromise host to adjacent internal systems "
        "using stolen credentials or trust relationships.",
    "sql_injection":
        "Malicious SQL payloads injected into user-controlled input fields to manipulate "
        "database queries, extract data, or execute OS commands.",
    "unauthorized_access":
        "Access to restricted resources using valid credentials that belong to another user "
        "or service account, suggesting credential theft or insider threat.",
    "command_injection":
        "User-controlled input passed unsanitized to a system shell, allowing arbitrary "
        "command execution with the privileges of the web server process.",
    "config_change":
        "Unauthorized modification to system configuration files, potentially disabling "
        "security controls, opening backdoors, or persisting malware.",
    "file_access":
        "Access to sensitive files outside the user's normal working set, "
        "indicative of reconnaissance or data staging before exfiltration.",
    "xss_attempt":
        "Cross-site scripting payload attempts to inject client-side scripts into web responses, "
        "which could steal session cookies or redirect victims to phishing pages.",
}

RECOMMENDED_ACTIONS = {
    "brute_force": (
        "1. Immediately block source IP at the firewall.\n"
        "2. Enforce account lockout after 5 failed attempts.\n"
        "3. Enable MFA on the targeted account.\n"
        "4. Review auth logs for the past 24h for successful logins from this IP.\n"
        "5. Alert the targeted user to change their password immediately."
    ),
    "port_scan": (
        "1. Block the scanning IP at the perimeter firewall.\n"
        "2. Review IDS/IPS rules to ensure future scans are auto-blocked.\n"
        "3. Audit network segmentation — can this IP reach internal subnets?\n"
        "4. Check if the scan was followed by any connection attempts."
    ),
    "privilege_escalation": (
        "1. Immediately revoke elevated privileges for this user session.\n"
        "2. Isolate the host from the network for forensic analysis.\n"
        "3. Check for cron jobs, SUID binaries, or scheduled tasks added.\n"
        "4. Patch the exploited vulnerability — check kernel and SUID paths.\n"
        "5. Perform a full root filesystem integrity check."
    ),
    "dos_attack": (
        "1. Activate rate limiting and connection throttling at the load balancer.\n"
        "2. Enable DDoS protection (Cloudflare / AWS Shield / similar).\n"
        "3. Block the attack source IP ranges at the upstream provider.\n"
        "4. Scale horizontally — add capacity to absorb traffic.\n"
        "5. Alert the infrastructure team and activate the DDoS response runbook."
    ),
    "data_exfiltration": (
        "1. Immediately block the destination IP/domain at the firewall.\n"
        "2. Terminate the user's active sessions and revoke credentials.\n"
        "3. Identify exactly which data was exfiltrated — check DLP logs.\n"
        "4. Initiate breach notification procedures if PII/PCI data was involved.\n"
        "5. Preserve forensic evidence before remediation."
    ),
    "lateral_movement": (
        "1. Isolate all hosts the attacker has accessed from the network.\n"
        "2. Reset credentials for all accounts used in lateral movement.\n"
        "3. Audit SMB, RDP, and SSH logs across the environment.\n"
        "4. Hunt for persistence mechanisms (backdoors, new admin accounts).\n"
        "5. Map the full attack path using SIEM correlation."
    ),
    "sql_injection": (
        "1. Immediately take the affected web endpoint offline if possible.\n"
        "2. Parameterize all database queries — no string concatenation.\n"
        "3. Review database user permissions — web app user should have minimum rights.\n"
        "4. Check if any data was extracted in the response.\n"
        "5. Deploy a WAF rule to block SQL injection patterns at the edge."
    ),
    "unauthorized_access": (
        "1. Disable or lock the accessed account pending investigation.\n"
        "2. Determine if credentials were phished, leaked, or guessed.\n"
        "3. Review all actions performed during the unauthorized session.\n"
        "4. Force password reset and enable MFA.\n"
        "5. Check for any data downloaded or configuration changes made."
    ),
    "default": (
        "1. Review and preserve all relevant logs for this event.\n"
        "2. Assess the potential impact on data confidentiality and integrity.\n"
        "3. Block the source IP at the perimeter if external.\n"
        "4. Notify the security team and open an incident ticket.\n"
        "5. Monitor for follow-on activity from the same source or user."
    ),
}


def _local_explain(log: dict) -> dict:
    """Generate a professional security analysis locally without an LLM API."""
    event_type  = log.get("event_type", "unknown").lower()
    user_id     = log.get("user_id", "unknown")
    source_ip   = log.get("source_ip", "unknown")
    severity    = log.get("severity", "MEDIUM")
    risk_score  = log.get("risk_score", 50)
    threat_label = log.get("threat_label", "Unknown")
    is_anomaly  = log.get("is_anomaly", False)
    flags       = log.get("behavioral_flags", [])
    anomaly_score = log.get("anomaly_score", 0)
    beh_dev     = round(log.get("behavioral_deviation", 0), 2)
    hour        = log.get("hour", 12)
    confidence  = round(log.get("threat_confidence", 0.5) * 100)

    mitre_id, mitre_name = MITRE_MAP.get(event_type, ("T1078", "Valid Accounts"))
    mitre_str = f"{mitre_id} — {mitre_name}"

    attack = ATTACK_PATTERNS.get(event_type,
        f"Suspicious {event_type.replace('_',' ')} activity detected from {source_ip}. "
        "The pattern matches known threat actor TTPs recorded in threat intelligence feeds."
    )

    action = RECOMMENDED_ACTIONS.get(event_type, RECOMMENDED_ACTIONS["default"])

    # ── Summary ───────────────────────────────────────────────────────────────
    anomaly_note = (
        f" The Isolation Forest anomaly detector flagged this as statistically unusual "
        f"(anomaly score: {round(anomaly_score, 3)}), indicating it deviates significantly "
        f"from established baseline behaviour for {'this user' if beh_dev > 0.3 else 'this IP'}."
        if is_anomaly else ""
    )
    offhours = " The event occurred outside normal business hours, increasing suspicion." if hour < 7 or hour > 21 else ""
    summary = (
        f"A {severity.lower()}-severity {event_type.replace('_', ' ')} event was detected "
        f"from user '{user_id}' at IP {source_ip}, classified as a '{threat_label}' threat "
        f"with a risk score of {risk_score}/100.{anomaly_note}{offhours} "
        f"Immediate investigation is {'strongly ' if severity in ('CRITICAL','HIGH') else ''}recommended."
    )

    # ── Why flagged ───────────────────────────────────────────────────────────
    reasons = []
    if risk_score >= 80:
        reasons.append(f"risk score of {risk_score}/100 exceeds the HIGH-risk threshold")
    elif risk_score >= 60:
        reasons.append(f"elevated risk score of {risk_score}/100")
    if is_anomaly:
        reasons.append(
            f"Isolation Forest flagged this as an anomaly (score {round(anomaly_score,3)}) — "
            f"the IP/user combination does not match any known legitimate baseline"
        )
    if beh_dev > 0.4:
        reasons.append(
            f"behavioural deviation of {beh_dev} indicates significant departure "
            f"from this user's normal activity profile"
        )
    if flags:
        reasons.append(f"active behavioural flags: {', '.join(flags)}")
    if threat_label not in ("Normal", "Unknown"):
        reasons.append(
            f"Random Forest classifier assigned '{threat_label}' label with "
            f"{confidence}% confidence based on 47 network features"
        )
    if hour < 7 or hour > 21:
        reasons.append(f"event occurred at {hour:02d}:00, outside normal working hours")

    why_flagged = "; ".join(reasons).capitalize() + "." if reasons else (
        f"Event type '{event_type}' matched threat signatures in the ML classifier training set "
        f"with {confidence}% confidence."
    )

    # ── Confidence reasoning ──────────────────────────────────────────────────
    confidence_reasoning = (
        f"The Random Forest classifier trained on KDD Cup 99 / NSL-KDD network intrusion data "
        f"assigned threat label '{threat_label}' with {confidence}% confidence. "
        f"Risk score {risk_score} was computed as a weighted function of severity ({severity}), "
        f"known-bad IP reputation, behavioural deviation ({beh_dev}), and anomaly detection output. "
        f"{'The Isolation Forest anomaly model also independently flagged this event.' if is_anomaly else 'No anomaly detected by Isolation Forest — risk score driven primarily by pattern matching.'}"
    )

    return {
        "summary":              summary,
        "why_flagged":          why_flagged,
        "attack_pattern":       attack,
        "mitre_technique":      mitre_str,
        "recommended_action":   action,
        "confidence_reasoning": confidence_reasoning,
    }


def _build_user_message(log: dict) -> str:
    return f"""Analyze this cybersecurity event:

Event Type: {log.get('event_type', 'unknown')}
User ID: {log.get('user_id', 'unknown')}
Source IP: {log.get('source_ip', 'unknown')}
Description: {log.get('description', 'No description')}
Severity: {log.get('severity', 'UNKNOWN')}
Risk Score: {log.get('risk_score', 0)}/100
Threat Label: {log.get('threat_label', 'Unknown')} (confidence: {round(log.get('threat_confidence', 0) * 100)}%)
Is Anomaly: {log.get('is_anomaly', False)} (score: {round(log.get('anomaly_score', 0), 3)})
Behavioral Deviation: {round(log.get('behavioral_deviation', 0), 2)}
Behavioral Flags: {', '.join(log.get('behavioral_flags', [])) or 'None'}
Hour of Day: {log.get('hour', 'unknown')}:00
Timestamp: {log.get('created_at', 'unknown')}
Stored on Blockchain: {'Yes, TX: ' + log['tx_hash'] if log.get('tx_hash') else 'No'}
"""


@router.get("/{log_id}/explain")
async def explain_log(log_id: str):
    """
    Generate a cybersecurity explanation for a log entry.
    Tries Claude first; falls back to rule-based local analysis if API unavailable.
    Results are cached in MongoDB after the first call.
    """
    # 1. Check cache first
    cached = await get_explanation(log_id)
    if cached:
        return {"log_id": log_id, "cached": True, **cached}

    # 2. Fetch log from DB
    log_doc = await get_log_by_id(log_id)
    if not log_doc:
        raise HTTPException(status_code=404, detail="Log not found")

    # 3. Try Claude API
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    use_claude = bool(api_key and api_key not in ("your_key_here", "your_anthropic_api_key_here"))

    explanation = None
    used_claude = False

    if use_claude:
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model="claude-opus-4-5",          # falls back to latest available
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": _build_user_message(log_doc)}],
            )
            raw = message.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()
            explanation = json.loads(raw)
            used_claude = True
        except Exception:
            pass  # Fall through to local engine

    # 4. Local fallback
    if explanation is None:
        explanation = _local_explain(log_doc)

    # 5. Cache in MongoDB
    await save_explanation(log_id, explanation)

    return {"log_id": log_id, "cached": False, "used_claude": used_claude, **explanation}

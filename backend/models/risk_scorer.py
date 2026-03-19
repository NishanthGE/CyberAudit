"""
Risk Scoring Engine
Computes a 0–100 risk score from multiple weighted signals.
"""

from typing import Literal

# Event type base weights (0-40)
EVENT_WEIGHTS = {
    "normal_login":          2,
    "failed_login":          15,
    "brute_force":           38,
    "port_scan":             30,
    "privilege_escalation":  40,
    "dos_attack":            40,
    "file_access":           10,
    "data_exfiltration":     40,
    "lateral_movement":      35,
    "command_injection":     40,
    "sql_injection":         38,
    "xss_attempt":           20,
    "unauthorized_access":   35,
    "config_change":         12,
    "service_started":        3,
    "service_stopped":       10,
}

# Threat label multipliers
THREAT_MULTIPLIERS = {
    "Normal": 0.0,
    "Probe":  0.3,
    "DoS":    0.6,
    "R2L":    0.5,
    "U2R":    0.7,
}

# Off-hours risk bonus (midnight–6am = highest risk)
def _time_score(hour: int) -> float:
    """Return 0.0–10.0 based on hour of day (off-hours = higher)."""
    if 0 <= hour <= 5:
        return 10.0
    elif 6 <= hour <= 7 or 22 <= hour <= 23:
        return 6.0
    elif 8 <= hour <= 18:
        return 0.0
    else:
        return 3.0


def compute_risk_score(
    event_type: str,
    anomaly_normalized: float,   # 0.0–1.0 from Isolation Forest
    threat_label: str,
    frequency_count: int,        # how many events from this source in last 5 min
    hour: int,                   # 0–23
    failed_logins: int = 0,
) -> int:
    """
    Compute a 0–100 integer risk score.

    Weighting:
      - Event base weight:    40%  (0–40 pts)
      - Anomaly signal:       25%  (0–25 pts)
      - Threat label boost:   20%  (0–20 pts)
      - Frequency signal:      5%  (0–5 pts)
      - Time-of-day bonus:    10%  (0–10 pts)
    """
    # 1. Event base (40 pts max)
    event_base = EVENT_WEIGHTS.get(event_type, 10)

    # 2. Anomaly contribution (25 pts max)
    anomaly_pts = anomaly_normalized * 25.0

    # 3. Threat label contribution (20 pts max)
    threat_pts = THREAT_MULTIPLIERS.get(threat_label, 0.0) * (100 / 0.7) * 0.20

    # 4. Frequency signal (5 pts max — caps at 50+ events/5min)
    freq_pts = min(frequency_count / 10.0, 5.0)

    # 5. Time-of-day (10 pts max)
    time_pts = _time_score(hour)

    # 6. Failed login bonus
    failed_login_bonus = min(failed_logins * 1.5, 10.0)

    raw = event_base + anomaly_pts + threat_pts + freq_pts + time_pts + failed_login_bonus
    score = int(min(max(raw, 0), 100))
    return score


def score_to_severity(score: int) -> str:
    """Convert numeric risk score to severity label."""
    if score >= 85:
        return "CRITICAL"
    elif score >= 65:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    elif score >= 15:
        return "LOW"
    else:
        return "INFO"

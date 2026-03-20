"""
Behavioral Profiler — Per-user baseline and deviation detection.
Uses explicit typed data structures (no defaultdict with ambiguous lambdas).
"""

import numpy as np
from datetime import datetime
from collections import deque
from typing import Dict, List

# Explicit per-user profile store
_user_profiles: Dict[str, dict] = {}


def _new_profile() -> dict:
    return {
        "typical_hours": [],       # List[int]
        "known_ips": set(),        # Set[str]
        "event_history": deque(maxlen=500),  # deque of dicts
        "total_events": 0,         # int
        "avg_risk_score": 0.0,     # float
        "flags": [],               # List[dict]
    }


def _get_or_create(user_id: str) -> dict:
    if user_id not in _user_profiles:
        _user_profiles[user_id] = _new_profile()
    return _user_profiles[user_id]


def update_profile(user_id: str, ip: str, hour: int, event_type: str, risk_score: int) -> dict:
    """
    Update the per-user behavioral baseline and return deviation analysis.
    Returns: deviation_score (0.0–1.0), flags (list[str]), is_flagged (bool)
    """
    profile = _get_or_create(user_id)
    flags: List[str] = []
    deviation_score = 0.0

    # 1. New IP deviation
    if len(profile["known_ips"]) > 0 and ip not in profile["known_ips"]:
        flags.append(f"New IP address detected: {ip}")
        deviation_score += 0.3

    # 2. Unusual hour
    hours: List[int] = profile["typical_hours"]
    if len(hours) >= 10:
        hour_arr = np.array(hours, dtype=float)
        mean_hour = float(np.mean(hour_arr))  # type: ignore[call-overload]
        std_hour = max(float(np.std(hour_arr)), 1.0)  # type: ignore[call-overload]
        z_score = abs(hour - mean_hour) / std_hour
        if z_score > 2.5:
            flags.append(f"Unusual activity time: {hour:02d}:00 (typical: {int(mean_hour):02d}:00)")
            deviation_score += min(z_score * 0.1, 0.3)

    # 3. High-risk event type
    high_risk_events = {
        "privilege_escalation", "data_exfiltration", "lateral_movement",
        "brute_force", "dos_attack", "command_injection",
    }
    if event_type in high_risk_events:
        flags.append(f"High-risk event type: {event_type}")
        deviation_score += 0.25

    # 4. Frequency spike for same event type
    history: deque = profile["event_history"]
    same_type_count = sum(1 for e in history if e.get("event_type") == event_type)
    if same_type_count > 5:
        flags.append(f"High frequency of '{event_type}': {same_type_count} recent occurrences")
        deviation_score += 0.15

    # 5. Risk score spike vs user average
    total: int = profile["total_events"]
    avg: float = profile["avg_risk_score"]
    if total > 5 and risk_score > (avg * 1.5 + 20):
        flags.append(f"Risk score spike: {risk_score} vs avg {avg:.0f}")
        deviation_score += 0.2

    # ── Update profile ───────────────────────────────────────────────────────
    profile["known_ips"].add(ip)
    profile["typical_hours"].append(hour)
    if len(profile["typical_hours"]) > 200:
        profile["typical_hours"] = profile["typical_hours"][-200:]

    profile["event_history"].append({
        "event_type": event_type,
        "ip": ip,
        "hour": hour,
        "risk_score": risk_score,
        "timestamp": datetime.utcnow().isoformat(),
    })

    # Rolling average risk score
    n: int = profile["total_events"]
    profile["avg_risk_score"] = (avg * n + risk_score) / (n + 1)
    profile["total_events"] = n + 1

    deviation_score = min(deviation_score, 1.0)

    # Store flags (keep last 50)
    if flags:
        profile["flags"].extend([
            {"flag": f, "timestamp": datetime.utcnow().isoformat()} for f in flags
        ])
    profile["flags"] = profile["flags"][-50:]

    return {
        "deviation_score": round(float(deviation_score), 3),  # type: ignore[call-overload]
        "flags": flags,
        "is_flagged": bool(flags),
        "known_ips_count": len(profile["known_ips"]),
        "total_events": profile["total_events"],
        "avg_risk_score": round(float(profile["avg_risk_score"]), 1),  # type: ignore[call-overload]
    }


def get_user_profile(user_id: str) -> dict:
    """Return the full behavioral profile for a user."""
    profile = _user_profiles.get(user_id, _new_profile())
    return {
        "user_id": user_id,
        "total_events": int(profile["total_events"]),
        "avg_risk_score": round(float(profile["avg_risk_score"]), 1),  # type: ignore[call-overload]
        "known_ips": list(profile["known_ips"]),
        "recent_events": list(profile["event_history"])[-20:],  # type: ignore[index]
        "recent_flags": list(profile["flags"])[-20:],  # type: ignore[index]
        "typical_hours": list(profile["typical_hours"])[-50:],  # type: ignore[index]
    }


def get_all_user_ids() -> List[str]:
    """Return all user IDs that have been profiled."""
    return list(_user_profiles.keys())

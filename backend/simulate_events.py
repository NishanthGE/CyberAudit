"""
Event Simulation Script
Generates and ingests 200+ realistic cybersecurity events via the FastAPI backend.
Run: python simulate_events.py  (while backend is running on port 8000)
"""

import sys
import httpx
import random
import asyncio
from datetime import datetime

# Force UTF-8 to avoid Windows cp1252 issues
if sys.stdout.encoding.lower() != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

API_URL = "http://localhost:8001/api/logs"

USERS = [
    "alice.smith", "bob.jones", "charlie.wu", "diana.patel",
    "eve.taylor", "frank.garcia", "grace.kim", "hank.roberts",
    "iris.chen", "jack.mason",
]

INTERNAL_IPS = [f"192.168.1.{i}" for i in range(10, 50)]
EXTERNAL_IPS = [
    "45.33.32.156", "198.20.69.74", "89.248.167.131", "103.235.46.39",
    "185.220.101.42", "94.102.49.193", "77.247.181.162", "71.6.135.131",
    "216.58.200.46", "104.26.13.74", "52.84.12.204", "172.217.14.238",
    "104.16.98.52", "185.156.73.54", "5.188.206.18", "193.32.161.9",
]

EVENT_TEMPLATES = [
    ("normal_login",         "User {u} logged in successfully from {ip}",                       15),
    ("failed_login",         "Failed login attempt for user {u} from {ip}",                     12),
    ("brute_force",          "Brute force attack: {n} attempts from {ip} targeting {u}",         8),
    ("port_scan",            "Port scan from {ip}: swept {n} ports in {t}s",                     8),
    ("privilege_escalation", "User {u} attempted privilege escalation to root from {ip}",        6),
    ("dos_attack",           "DoS flood from {ip}: {n} req/sec targeting internal service",      5),
    ("data_exfiltration",    "Data exfil by {u}: {n}MB sent to external IP {ip}",               5),
    ("unauthorized_access",  "Unauthorized resource access by {u} from {ip}",                   8),
    ("file_access",          "Sensitive file accessed by {u} from {ip}",                        7),
    ("config_change",        "System config modified by {u} from {ip}",                         5),
    ("lateral_movement",     "Lateral movement: {u} pivoting via {ip}",                         4),
    ("sql_injection",        "SQL injection attempt from {ip} on web endpoint",                  3),
    ("xss_attempt",          "XSS payload from {ip}: {u} targeted",                             3),
    ("command_injection",    "Command injection attempt from {ip} on API",                       3),
    ("service_started",      "Service started by {u} on host {ip}",                             5),
    ("service_stopped",      "Service unexpectedly stopped -- user: {u}, host: {ip}",           3),
]

WEIGHTS = [t[2] for t in EVENT_TEMPLATES]

SEVERITY_SYMBOLS = {
    "CRITICAL": "[CRIT]",
    "HIGH":     "[HIGH]",
    "MEDIUM":   "[MED] ",
    "LOW":      "[LOW] ",
    "INFO":     "[INFO]",
}


def pick_event() -> dict:
    template = random.choices(EVENT_TEMPLATES, weights=WEIGHTS, k=1)[0]
    user = random.choice(USERS)
    ip = random.choice(EXTERNAL_IPS if random.random() < 0.35 else INTERNAL_IPS)
    n = random.randint(10, 5000)
    t = random.randint(1, 60)
    hour = random.choices(range(24), weights=[
        5, 4, 4, 3, 3, 3, 4, 6, 8, 9, 10, 10,
        10, 10, 10, 9, 8, 7, 7, 6, 6, 5, 5, 5,
    ], k=1)[0]
    return {
        "user_id":    user,
        "source_ip":  ip,
        "event_type": template[0],
        "description": template[1].format(u=user, ip=ip, n=n, t=t),
        "hour":        hour,
        "metadata": {
            "simulated": True,
            "simulated_at": datetime.utcnow().isoformat(),
        },
    }


async def run_simulation(total_events: int = 220, delay_ms: int = 150):
    print("=" * 60)
    print("  Cybersecurity Event Simulator")
    print(f"  Events: {total_events}  |  Delay: {delay_ms}ms")
    print("=" * 60)

    success: int = 0
    failed: int = 0

    async with httpx.AsyncClient(timeout=30.0) as client:
        for i in range(1, total_events + 1):
            payload = pick_event()
            try:
                resp = await client.post(API_URL, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    sev   = data.get("severity", "?")
                    risk  = data.get("risk_score", 0)
                    label = data.get("threat_label", "?")
                    flag  = " ANOMALY!" if data.get("is_anomaly") else ""
                    sym   = SEVERITY_SYMBOLS.get(sev, "[?]   ")
                    print(f"[{i:3d}/{total_events}] {sym} Risk:{risk:3d} | {label:8s} | "
                          f"{payload['event_type']:25s}{flag}")
                    success += 1  # type: ignore[misc]
                else:
                    print(f"[{i:3d}/{total_events}] [ERR] HTTP {resp.status_code}: {str(resp.text)[:60]}")  # type: ignore[index]
                    failed += 1  # type: ignore[misc]
            except Exception as e:
                print(f"[{i:3d}/{total_events}] [ERR] {e}")
                failed += 1  # type: ignore[misc]

            if delay_ms > 0:
                await asyncio.sleep(delay_ms / 1000.0)

    print("=" * 60)
    print(f"  Done: {success} succeeded, {failed} failed")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(run_simulation(total_events=220, delay_ms=150))

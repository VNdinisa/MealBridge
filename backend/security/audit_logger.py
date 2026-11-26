import json
from datetime import datetime, timezone
from pathlib import Path

AUDIT_FILE = Path(__file__).resolve().parent.parent / "logs" / "audit.jsonl"

def log_audit_event(user_id: str, role: str, action: str, resource_id: str, outcome: str = "ALLOW"):
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "role": role,
        "action": action,
        "resource_id": resource_id,
        "outcome": outcome,
    }
    with AUDIT_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

#!/usr/bin/env bash
set -euo pipefail

mkdir -p backend/security backend/logs

echo "1. Creating backend/security/rbac.py..."
cat << 'PY' > backend/security/rbac.py
from functools import wraps
from fastapi import Header, HTTPException, status

ALLOWED_ROLES = {"dispatcher", "volunteer", "admin"}

def verify_role(required_roles: list[str], x_user_role: str | None = Header(default=None)):
    if not x_user_role or x_user_role.lower() not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid role header"
        )
    if x_user_role.lower() not in [r.lower() for r in required_roles]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Role '{x_user_role}' is not permitted for this action"
        )
    return x_user_role.lower()
PY

echo "2. Creating backend/security/privacy_guard.py..."
cat << 'PY' > backend/security/privacy_guard.py
import re
from pydantic import BaseModel, field_validator

# Enforce synthetic/pretend data rules (e.g., 555 test numbers or "Pretend" prefix)
REAL_PHONE_PATTERN = re.compile(r"^(?!.*555)\+?\d[\d\s\-]{7,14}$")

class DeliveryStopPayload(BaseModel):
    stop_id: str
    neighbor_alias: str
    pretend_address: str
    pretend_phone: str
    is_pretend_data: bool = True

    @field_validator("is_pretend_data")
    @classmethod
    def must_be_pretend(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Privacy Policy Violation: Only pretend datasets are permitted.")
        return v

    @field_validator("pretend_phone")
    @classmethod
    def reject_real_phone(cls, v: str) -> str:
        if REAL_PHONE_PATTERN.match(v.strip()):
            raise ValueError("PII Guardrail: Use synthetic 555 test phone numbers only.")
        return v
PY

echo "3. Creating backend/security/audit_logger.py..."
cat << 'PY' > backend/security/audit_logger.py
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
PY

echo "4. Ensuring audit logs are gitignored..."
grep -qxF 'backend/logs/' .gitignore || echo 'backend/logs/' >> .gitignore
grep -qxF '.env' .gitignore || echo '.env' >> .gitignore

echo "Security modules created in backend/security/:"
ls -la backend/security/

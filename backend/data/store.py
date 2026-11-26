import json
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DATA_FILE = Path(__file__).resolve().parent / "mealbridge_state.json"
_LOCK = threading.Lock()


def _build_initial_seed() -> dict:
    volunteers = [
        {
            "volunteer_id": f"VOL-{i:02d}",
            "name": f"Pretend Volunteer {i:02d}",
            "pretend_phone": f"555-01{i:02d}",
            "zone": f"Zone {((i - 1) % 4) + 1}",
            "active": True,
            "is_pretend_data": True,
        }
        for i in range(1, 11)
    ]

    dietary_tags = ["Standard", "Low-Sodium", "Diabetic-Friendly", "Vegetarian"]
    statuses = ["pending", "in_transit", "delivered"]

    stops = [
        {
            "stop_id": f"STOP-{i:02d}",
            "neighbor_alias": f"Pretend Neighbor {i:02d}",
            "pretend_address": f"{100 + i} Pretend Wellness Ave, Unit {i}",
            "pretend_phone": f"555-02{i:02d}",
            "dietary_note": dietary_tags[(i - 1) % len(dietary_tags)],
            "assigned_volunteer_id": f"VOL-{((i - 1) % 10) + 1:02d}",
            "status": statuses[0] if i > 6 else ("in_transit" if i > 3 else "delivered"),
            "is_pretend_data": True,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        for i in range(1, 21)
    ]

    return {
        "volunteers": volunteers,
        "stops": stops,
    }


def _read_state() -> dict:
    if not DATA_FILE.exists():
        state = _build_initial_seed()
        DATA_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")
        return state
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def _write_state(state: dict) -> None:
    DATA_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def list_volunteers() -> list[dict]:
    with _LOCK:
        return _read_state()["volunteers"]


def list_stops(volunteer_id: Optional[str] = None) -> list[dict]:
    with _LOCK:
        stops = _read_state()["stops"]
        if volunteer_id:
            return [s for s in stops if s.get("assigned_volunteer_id") == volunteer_id]
        return stops


def get_stop(stop_id: str) -> Optional[dict]:
    with _LOCK:
        for stop in _read_state()["stops"]:
            if stop["stop_id"] == stop_id:
                return stop
        return None


def upsert_stop(stop_payload: dict) -> dict:
    with _LOCK:
        state = _read_state()
        now = datetime.now(timezone.utc).isoformat()
        record = {
            **stop_payload,
            "status": stop_payload.get("status", "pending"),
            "assigned_volunteer_id": stop_payload.get("assigned_volunteer_id", "VOL-01"),
            "updated_at": now,
        }
        for idx, existing in enumerate(state["stops"]):
            if existing["stop_id"] == record["stop_id"]:
                state["stops"][idx] = {**existing, **record}
                _write_state(state)
                return state["stops"][idx]

        state["stops"].append(record)
        _write_state(state)
        return record


def update_stop_status(stop_id: str, new_status: str) -> Optional[dict]:
    with _LOCK:
        state = _read_state()
        for stop in state["stops"]:
            if stop["stop_id"] == stop_id:
                stop["status"] = new_status
                stop["updated_at"] = datetime.now(timezone.utc).isoformat()
                _write_state(state)
                return stop
        return None


def reset_seed_data() -> dict:
    with _LOCK:
        state = _build_initial_seed()
        _write_state(state)
        return state


def register_onboarded_user(
    name: str,
    role: str,
    pretend_phone: str,
    zone: str = "Zone 1",
) -> dict:
    """
    Registers a pretend volunteer or dispatcher into mealbridge_state.json
    and returns a session payload for the Expo client.
    """
    with _LOCK:
        state = _read_state()
        state.setdefault("dispatchers", [])
        now = datetime.now(timezone.utc).isoformat()
        clean_role = role.lower().strip()

        if clean_role == "dispatcher":
            next_num = len(state["dispatchers"]) + 1
            user_id = f"DISP-{next_num:02d}"
            user_record = {
                "dispatcher_id": user_id,
                "name": name,
                "pretend_phone": pretend_phone,
                "role": "dispatcher",
                "active": True,
                "is_pretend_data": True,
                "created_at": now,
            }
            state["dispatchers"].append(user_record)
        else:
            next_num = len(state["volunteers"]) + 1
            user_id = f"VOL-{next_num:02d}"
            user_record = {
                "volunteer_id": user_id,
                "name": name,
                "pretend_phone": pretend_phone,
                "zone": zone,
                "role": "volunteer",
                "active": True,
                "is_pretend_data": True,
                "created_at": now,
            }
            state["volunteers"].append(user_record)

        _write_state(state)

        return {
            "user_id": user_id,
            "name": name,
            "role": clean_role,
            "zone": zone if clean_role == "volunteer" else "ALL",
            "token": f"mb-pretend-{clean_role}-{user_id.lower()}",
            "is_pretend_data": True,
        }


def verify_session_token(token: str) -> Optional[dict]:
    """
    Validates a pretend Bearer token ('mb-pretend-<role>-<user_id>')
    against active volunteers, dispatchers, or admin accounts in state.
    """
    if not token or not token.startswith("mb-pretend-"):
        return None

    parts = token.split("-", 3)
    if len(parts) != 4:
        return None

    _, _, token_role, raw_user_id = parts
    role = token_role.lower().strip()
    user_id = raw_user_id.upper().strip()

    with _LOCK:
        state = _read_state()

        if role == "volunteer":
            for v in state.get("volunteers", []):
                if v.get("volunteer_id", "").upper() == user_id and v.get("active", True):
                    return {"user_id": v["volunteer_id"], "role": "volunteer"}

        elif role == "dispatcher":
            for d in state.get("dispatchers", []):
                if d.get("dispatcher_id", "").upper() == user_id and d.get("active", True):
                    return {"user_id": d["dispatcher_id"], "role": "dispatcher"}

        elif role == "admin" and user_id == "ADMIN-01":
            return {"user_id": "ADMIN-01", "role": "admin"}

    return None

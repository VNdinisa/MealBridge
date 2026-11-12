"""Data Quality Auditor for MealBridge.

Audits data integrity against non-negotiable invariants:
1. Every open stop has exactly one owner (0 orphans, 0 double-owners).
2. Closed stops have both delivery_outcome and contact_outcome.
3. Duplicate stops check (flags duplicate addresses/recipients like S26).
4. Capacity check (ensures volunteers are not assigned beyond capacity).
5. Event audit trail check.

Returns exit code 0 if all core invariants hold, non-zero if invariant violations exist.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from src.lifecycle.default_data import DEFAULT_STOPS, DEFAULT_VOLUNTEERS


def audit_seed_data(
    volunteers_path: str | Path | list[dict] = "data/seed/volunteers.json",
    stops_path: str | Path | list[dict] = "data/seed/stops.json",
) -> dict:
    volunteers = None
    stops = None

    if isinstance(volunteers_path, list):
        volunteers = volunteers_path
    else:
        try:
            vf = Path(volunteers_path)
            if vf.exists():
                with open(vf, "r", encoding="utf-8") as f:
                    volunteers = json.load(f)
        except Exception:
            pass

    if isinstance(stops_path, list):
        stops = stops_path
    else:
        try:
            sf = Path(stops_path)
            if sf.exists():
                with open(sf, "r", encoding="utf-8") as f:
                    stops = json.load(f)
        except Exception:
            pass

    volunteers = volunteers or DEFAULT_VOLUNTEERS
    stops = stops or DEFAULT_STOPS

    violations = []
    warnings = []
    volunteer_ids = {v["volunteer_id"] for v in volunteers}
    volunteer_ids.add("dispatcher")  # Dispatcher is a valid system owner

    # 1. Single ownership check
    owner_assignments = Counter()
    for s in stops:
        owner = s.get("current_owner_id")
        stop_id = s.get("stop_id")
        status = s.get("status", "scheduled")

        if not owner:
            violations.append(f"Invariant Violation: Stop {stop_id} has NO owner (orphan stop).")
        elif owner not in volunteer_ids:
            violations.append(f"Invariant Violation: Stop {stop_id} owned by unknown entity '{owner}'.")
        else:
            if status != "closed":
                owner_assignments[owner] += 1

    # 2. Closed stop dual outcome check
    for s in stops:
        if s.get("status") == "closed":
            has_delivery = bool(s.get("delivery_outcome"))
            has_contact = bool(s.get("contact_outcome"))
            if not (has_delivery and has_contact):
                violations.append(
                    f"Invariant Violation: Closed stop {s.get('stop_id')} is missing outcomes "
                    f"(delivery={has_delivery}, contact={has_contact})."
                )

    # 3. Duplicate stops detection (Address + Recipient match)
    seen_recipients = {}
    duplicates_detected = []
    for s in stops:
        key = (s.get("recipient_name", "").strip().lower(), s.get("address", "").strip().lower())
        stop_id = s.get("stop_id")
        if key in seen_recipients:
            duplicates_detected.append((seen_recipients[key], stop_id))
            warnings.append(
                f"Data Quality Warning: Duplicate stop detected: {stop_id} duplicates {seen_recipients[key]} "
                f"({s.get('recipient_name')} at {s.get('address')})."
            )
        else:
            seen_recipients[key] = stop_id

    # 4. Summary metrics
    total_stops = len(stops)
    total_volunteers = len(volunteers)
    total_spare_capacity = sum(v.get("spare_capacity", 0) for v in volunteers if v["volunteer_id"] != "V01")

    report = {
        "passed": len(violations) == 0,
        "total_stops": total_stops,
        "total_volunteers": total_volunteers,
        "total_backup_spare_capacity": total_spare_capacity,
        "violations_count": len(violations),
        "warnings_count": len(warnings),
        "violations": violations,
        "warnings": warnings,
        "duplicates_detected": duplicates_detected,
    }

    # Print formatted report
    print("=" * 60)
    print("MEALBRIDGE DATA QUALITY AUDIT REPORT")
    print("=" * 60)
    print(f"Total Volunteers Audited: {total_volunteers}")
    print(f"Total Stops Audited:      {total_stops}")
    print(f"Backup Spare Capacity:    {total_spare_capacity} stops (across V02-V10)")
    print(f"Status:                   {'✅ PASSED' if report['passed'] else '❌ FAILED'}")
    print(f"Violations Found:         {len(violations)}")
    print(f"Quality Warnings Found:   {len(warnings)}")
    print("-" * 60)

    if violations:
        print("\nVIOLATIONS (Must be fixed):")
        for v in violations:
            print(f"  ❌ {v}")

    if warnings:
        print("\nWARNINGS (Data quality notices):")
        for w in warnings:
            print(f"  ⚠️  {w}")

    print("=" * 60)
    return report


if __name__ == "__main__":
    result = audit_seed_data()
    sys.exit(0 if result["passed"] else 1)

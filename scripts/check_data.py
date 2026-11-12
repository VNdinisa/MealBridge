"""Data Quality Auditor CLI for MealBridge."""

import sys
from pathlib import Path

# Add project root to sys.path if run directly
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.lifecycle.auditor import audit_seed_data

if __name__ == "__main__":
    v_path = ROOT_DIR / "data" / "seed" / "volunteers.json"
    s_path = ROOT_DIR / "data" / "seed" / "stops.json"

    print("Running Adenibiya's Data Quality Audit...")
    report = audit_seed_data(v_path, s_path)

    print(f"Stops audited: {report['total_stops_audited']}")
    print(f"Volunteers audited: {report['total_volunteers_audited']}")
    print(f"Violations: {report['violations_count']}")
    print(f"Warnings: {report['warnings_count']}")

    if report["warnings"]:
        print("\nWarnings:")
        for w in report["warnings"]:
            print(f"  [WARN] {w}")

    if report["violations"]:
        print("\nViolations:")
        for v in report["violations"]:
            print(f"  [FAIL] {v}")
        sys.exit(1)
    else:
        print("\nAll non-negotiable invariants PASSED.")
        sys.exit(0)

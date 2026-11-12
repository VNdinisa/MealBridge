---
name: data-quality-check
description: Audit MealBridge data integrity and compute workflow metrics (orphan stops, double owners, missing outcomes, time to reassign, contact completion). Use before demos, after migrations, after workflow changes, or whenever someone asks whether the data is right or how well the workflow is performing.
---
# Data quality check

Write `scripts/check_data.py` (read-only) that prints a report and exits non-zero on invariant violations.

## Integrity checks
- Open stops with zero or multiple owners.
- Closed stops missing delivery or contact outcome.
- Events out of order, missing actor, or referencing unknown stops/volunteers.
- Stops stuck in `at_risk` or `reassign_proposed` longer than a threshold.
- Duplicate stops, impossible time windows, volunteers over capacity.

## Metrics
- Median and p90 time from voice update to confirmed reassignment.
- % affected stops with confirmed contact; % closed with both outcomes.
- % parses needing human confirmation; % confirmations that changed the parse.
- Open stops by owner and by age.

Report counts with example ids. Recommend fixes, never mutate data.

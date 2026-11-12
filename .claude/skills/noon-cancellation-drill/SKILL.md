---
name: noon-cancellation-drill
description: Run the end-to-end MealBridge proof: one voice update, one change, one confirmed contact. Use to verify the core reassignment path, before demos, and as the Week 1 gate, or when the user says run the drill, test the main flow, or noon scenario.
---
# Noon cancellation drill

Scenario: it is 12:00. Volunteer V3 uploads "I can't make my stops today, my car broke down." V3 owns S07, S08, S09.

Steps to execute and assert:
1. Load seed data; assert 20 stops, one owner each.
2. Submit audio (sidecar transcript) -> parsed `cancel`, speaker V3, stops S07-S09, confidence >= 0.8.
3. Stops move to `at_risk`; board shows them first.
4. Reassignment proposals generated; dispatcher approves (simulated).
5. Owners updated; events logged; contact script drafted for each recipient.
6. Simulate contact on S07: reached. Delivery recorded. Stop closed with both outcomes.
7. Run the data-quality check: zero invariant violations. No stop ownerless at any step.

Print a timeline with elapsed times. The drill passes only if every assertion holds.

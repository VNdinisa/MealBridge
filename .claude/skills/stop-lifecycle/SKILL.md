---
name: stop-lifecycle
description: Defines and enforces the MealBridge stop state machine, ownership invariant, and append-only event log. Use whenever code touches stop status, ownership, contact status, closure, or events, or when designing any change that could affect who owns a stop.
---
# Stop lifecycle

## States
`scheduled` -> `at_risk` (volunteer cancelled / schedule changed) -> `reassign_proposed` -> `reassigned` (new owner accepted) -> `out_for_delivery` -> `delivered` -> `closed`.
Side paths: `unable_to_deliver`, `recipient_declined`, `needs_escalation` (no eligible volunteer; dispatcher owns it).

## Contact status (separate field)
`not_attempted` -> `attempted_no_answer` (count, last time) -> `reached` | `wrong_number` | `unreachable_escalated`.

## Invariants (enforce in code and tests)
1. Every non-closed stop has exactly one owner (volunteer id or `dispatcher`).
2. Closing requires a delivery outcome AND a contact outcome.
3. Every transition writes an immutable event: id, stop id, from, to, actor (user/agent/system), reason, source update id, timestamp.
4. Transitions are validated against an allowed-transition table; illegal ones raise.
5. Ownership changes only via a transition that also logs an event.

## Build checklist
- Transition table as data, with unit tests for every legal and illegal edge.
- A query `open_stops_by_owner()` that powers the board and proves invariant 1.
- Property-style test: random sequences of events never produce zero or two owners.

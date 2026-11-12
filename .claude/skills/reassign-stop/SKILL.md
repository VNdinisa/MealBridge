---
name: reassign-stop
description: Find affected stops and propose a new owner when a volunteer cancels or availability changes in MealBridge. Use for reassignment logic, volunteer ranking, escalation to the dispatcher, or explaining why a volunteer was suggested.
---
# Reassign stop

## Steps
1. Affected stops = open stops owned by the volunteer in the update window.
2. Mark them `at_risk`; ownership stays with the original volunteer until a proposal is approved, but the dispatcher is shown them first.
3. Filter eligible volunteers: available in the stop's window, capacity left, not the cancelling volunteer.
4. Rank deterministically: window fit, zone familiarity / proximity, current load, prior familiarity with the recipient, fewer total changes to the route.
5. Propose the top choice per stop (or a batch to one volunteer when it is cheaper), with 1-2 alternates and a plain-language reason (LLM may phrase the reason, never choose).
6. Dispatcher approves, edits, or rejects. On approval: transition to `reassigned`, update owner, log event, queue the contact script.
7. No eligible volunteer: dispatcher becomes owner, state `needs_escalation`, show at top of the board.

## Rules
- Never leave a stop ownerless. Never auto-assign without dispatcher approval in the MVP.
- Also notify the receiving volunteer and ask for acceptance; unaccepted proposals time out back to the dispatcher.
- Unit-test: cancel one volunteer with 3 stops; cancel with zero eligible; two cancellations at once.

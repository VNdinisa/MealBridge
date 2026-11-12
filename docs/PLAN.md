# Four-week plan

## Week 1: Prove the reassignment path
- Seed program: 26 stops (S01-S20 for V01, S21-S25 background, S26 duplicate row), 10 volunteers (V01 cancels, spare capacity covers 18 stops, 2 escalate to dispatcher).
- Stop lifecycle state machine, single ownership invariant, and append-only event log (`stop-lifecycle`).
- Voice update via transcript sidecar -> structured update with confidence scoring (`voice-update-parse`).
- Deterministic reassignment engine with NVIDIA NIM safety/protocol check and Gemini explanation (`reassign-stop`).
- Dispatcher approval flow, older-adult contact script drafting, and confirmed contact + delivery closure.
- Gate: `/noon-drill` passes end to end with zero invariant violations.

## Week 2: Real voice and availability
- Audio upload + real STT provider behind `Transcriber`.
- Volunteer availability changes (cancel, delay, window change, swap).
- Confirmation queue for low-confidence parses.
- Gate: 10 recorded or scripted updates parse with >= agreed accuracy (see `grounded-eval`).

## Week 3: Contact and closure
- Contact attempts, outcomes, retry and escalation rules (`contact-and-closure`).
- Contact scripts and closure notes drafted by the comms agent, dispatcher edits and approves.
- Open-stops-by-owner board with aging and "who still needs a call".
- Gate: no stop can reach closed without delivery + contact outcomes.

## Week 4: Evaluate, secure, demo
- Data checks and metrics (`data-quality-check`).
- Permission tests and abuse cases (`access-control-review`).
- Older-adult perspective review of scripts and UI.
- Grounded evaluation report and demo script.

## Roles and agents
| Person | Lane | Agents / skills they lean on |
|---|---|---|
| Sadiq | Build, requirements, eval | dispatch-architect, voice-intake-engineer, reassignment-engineer, eval-runner |
| Vuyolwetu | Lead, data protection | security-access-tester, dispatcher-lens, `access-control-review` |
| Adenibiya | Data checks, measures | data-quality-auditor, `data-quality-check`, `grounded-eval` |
| Omotayo | Permissions, older-adult view | security-access-tester, comms-writer, `contact-and-closure` |

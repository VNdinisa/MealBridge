# MealBridge

Voice updates in, dispatch actions out, and a clear record of who was reached. Nobody gets forgotten.

Built for the UN SDG 3 challenge (Good Health and Well-Being). One fictional program, 20 stops, four-week MVP.

## The one-sentence test
At noon a volunteer cancels. The dispatcher uploads a voice note. Within seconds they see which stops are affected, who now owns each one, and what to do next. Every design choice is judged against that moment.

## Team lanes
- Sadiq: builds the workflow (implementation, requirements, grounded evaluation).
- Vuyolwetu: leads, coordinates, owns data protection.
- Adenibiya: checks the data and measures.
- Omotayo: tests permissions, brings the older-adult perspective.

## Stack (default, change only via docs/DECISIONS.md)
- Python 3.11, FastAPI, SQLite (single file DB), pytest.
- Minimal web UI (server-rendered or small React) with: open-stops-by-owner board, voice upload, reassignment review.
- Speech-to-text behind a `Transcriber` interface. Providers: real STT, plus a `sidecar` provider that reads a `.txt` transcript next to the audio file so tests and demos never depend on a network.
- LLM calls behind a `Parser` interface returning schema-validated JSON. Always keep a rules-based fallback.

## Non-negotiable invariants
1. Every open stop has exactly one owner at all times (a volunteer or the dispatcher). No orphans, no double owners.
2. Every state change writes an append-only event (who, what, when, why, source update id).
3. A stop closes only with BOTH a delivery outcome and a contact outcome recorded.
4. Low-confidence or ambiguous voice parses never change data silently. They create a "needs dispatcher confirmation" item and the affected stops stay with their current owner, flagged.
5. If no eligible volunteer exists, the dispatcher becomes owner and the stop is flagged "needs escalation". Never leave it unassigned.
6. All data is fictional. Names are invented, phone numbers use reserved fake ranges, addresses are invented. Still treat it like real personal data: minimal fields, role-based access, no PII in logs.

## Definition of done for the first proof (Week 1)
One voice update -> one structured change -> one reassignment -> one confirmed contact, with the event trail and a passing `/noon-drill`.

## Working agreements
- Specs before code: update docs/ before changing behavior.
- Small commits, tests with every behavior change.
- Use the subagents in `.claude/agents/` and skills in `.claude/skills/`. See docs/PLAN.md for who does what.
- Plain language in all UI text and contact scripts (older-adult reading level, short sentences).

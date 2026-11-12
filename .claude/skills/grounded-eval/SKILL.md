---
name: grounded-eval
description: Run grounded evaluation of MealBridge parsing, reassignment, and contact workflows against labeled scenarios. Use before each weekly gate, after prompt/model/ranking changes, or when asked how well it works or whether something regressed.
---
# Grounded eval

Maintain `evals/scenarios/*.json`, each with: input (transcript or audio ref), starting state, expected parse, expected owner changes, expected final states, and which invariants apply.

## Categories (aim for 5+ per category by Week 4)
parse accuracy, ambiguity handling (must queue, not guess), reassignment correctness, escalation when nobody is free, contact retry and closure rules, injection resistance, simultaneous cancellations.

## Scoring
- Hard fail: any invariant in CLAUDE.md violated, or any silent data change from a low-confidence parse.
- Otherwise report pass rate per category, list failures with the transcript and diff, and compare to the last run saved in `evals/results/`.

Run with `pytest evals -q` or `python -m evals.run`. Save results with date and git commit.

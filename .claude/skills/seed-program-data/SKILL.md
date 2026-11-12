---
name: seed-program-data
description: Generate the fictional MealBridge program dataset (20 stops, volunteers, availability windows, routes). Use whenever the user needs seed data, fixtures, demo data, or test data for stops, volunteers, or recipients, even if they just say "add sample data".
---
# Seed program data

Create deterministic fictional data (fixed random seed) so tests and demos are repeatable.

## Contents
- Program: one fictional meal program with one delivery day, noon-to-3pm window.
- 20 stops: id (S01-S20), first name and initial only, invented street address, area/zone (3 zones), time window, dietary note (non-medical, e.g. "soft food"), preferred contact method, fake phone in a reserved fictional range, mobility note (e.g. "slow to answer door").
- 8 volunteers: id (V1-V8), first name, zone familiarity, vehicle capacity, availability windows, fake phone.
- Initial assignment: each stop has exactly one owner volunteer, 2-4 stops each, with some overlap risk.
- Include edge cases: one stop nobody else is available for, one volunteer with a partial window, one recipient who rarely answers the phone, two stops with similar names (to test ambiguity).

## Rules
- No real people, addresses, or phone numbers. Use invented names; phone numbers like +000-555-01xx.
- Output as `data/seed/*.json` plus a loader script and a test asserting 20 stops and exactly one owner per stop.

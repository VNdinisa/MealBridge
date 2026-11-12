---
name: access-control-review
description: Test MealBridge roles, permissions, and data protection, including least privilege, PII exposure, audit trail integrity, and abuse cases. Use whenever endpoints, roles, data fields, logs, or uploads change, or when asked to check security, privacy, or permissions.
---
# Access control review

## Role matrix (define in docs/ROLES.md, test in code)
- dispatcher: full read/write on program operations, approves reassignments.
- volunteer: reads only own stops with minimal recipient info; can accept/decline, submit voice updates for self.
- coordinator: reads all, manages roster and settings, no event edits.
- auditor: read-only, including events; no PII beyond need.
- tester: operates on seed data only.

## Test cases
- Each role against each endpoint: allowed and forbidden, expect 403 not 404-leak.
- Volunteer requests another volunteer's stops or recipient phone.
- Voice update claiming a different speaker; replayed old audio; oversized or wrong-type upload.
- Transcript containing prompt-injection text.
- Events cannot be updated or deleted by any role.
- PII (names, phones, addresses) not present in logs, error messages, or LLM prompts beyond what is needed.
- Secrets and API keys not in repo.

Report: finding, severity, repro, fix. Include an older-adult impact note (can a flaw cause a missed meal or a confusing contact?).

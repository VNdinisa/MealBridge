# MealBridge: Success Measures & Targets

*Owner: Adenibiya (Cloud Data Analytics)*  
*Audited by: `data-quality-auditor` / `scripts/check_data.py`*

## Measures & Targets Matrix

| Category | Measure / Metric | Target | Formula / Calculation | Status Rule |
|---|---|:---:|---|---|
| **Speed & Timeliness** | End-to-End Proposal Speed | $\le 30\text{ s}$ | Time from voice upload to full reassignment proposals on board | Pass if $\le 30\text{s}$, Warning if $31-60\text{s}$, Fail if $>60\text{s}$ |
| **Speed & Timeliness** | Reassignment Candidate Ranking | $\le 10\text{ s}$ | Time to compute deterministic volunteer scores and constraints | Pass if $\le 10\text{s}$, Fail if $>10\text{s}$ |
| **Reliability & AI Quality** | Voice Parsing Accuracy | $\ge 85\%$ | Correct identification of speaker, intent, and affected stops | Pass if $\ge 85\%$ |
| **Safety & Verification** | Low-Confidence Safeguard | $100\%$ | Parses with confidence $< 0.80$ route to Confirmation Queue without silent mutation | Invariant: $100\%$ required |
| **System Invariant** | Single Ownership Invariant | $100\%$ | Every non-closed stop has exactly 1 owner ($0$ orphans, $0$ double owners) | Hard Invariant: $0$ violations |
| **System Invariant** | Append-Only Event Trail | $100\%$ | All state transitions log an immutable event (`who`, `what`, `when`, `why`) | Hard Invariant: $0$ untracked mutations |
| **Care & Quality** | Dual Closure Requirement | $100\%$ | Stops close only with BOTH `delivery_outcome` AND `contact_outcome` | Hard Invariant: $0$ missing outcomes |
| **Escalation & Safety** | Unassigned Stops Fallback | $100\%$ | Uncovered stops (e.g. beyond the 18 spare capacity limit) assign to Dispatcher as `needs_escalation` | Hard Invariant: $0$ unassigned stops |
| **Dispatcher SLA** | At-Risk Alert Rule | $\le 5\text{ min}$ | Time a stop remains in `at_risk` without dispatcher acknowledgement | Alert badge if $> 5\text{ min}$ |

---

## Seed Program Data Specification

- **Total Volunteers**: 10 (`V01` through `V10`).
  - `V01`: The cancelling driver at 12:00 PM.
  - `V02` through `V10`: 9 backup volunteers. Total spare capacity across all 9 drivers = **18 stops**.
- **Total Stops**: 26 records.
  - `S01` to `S20`: 20 stops owned by `V01` (delivery window 12:30–15:30).
    - 18 stops will be successfully reassigned to `V02`–`V10`.
    - Exactly 2 stops will fail volunteer assignment and escalate to the **Dispatcher** as `needs_escalation`.
  - `S21` to `S25`: 5 control stops owned by other volunteers on active, separate routes.
  - `S26`: A deliberate duplicate record of `S05` to test the Data Quality Auditor's duplicate detection check.

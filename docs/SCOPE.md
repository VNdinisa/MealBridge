# MealBridge Project Plan — Phase 0: Scope & Information Handling

## 1. One-Page Scope Document
- **Project Name**: MealBridge
- **Objective**: Build a streamlined dispatch coordination prototype to connect volunteers and manage stop distribution efficiently during unexpected disruptions.
- **Assigned UN SDG**: Goal 3 (Good Health and Well-Being).

### In Scope (What we are doing)
- Defining core roles (Dispatch, Field Operations, Data/Security, Older-Adult Care).
- Building functional mock workflows using pretend data (10 volunteers, 26 delivery stops).
- Establishing clear information security rules and role-based access control.
- Voice-to-dispatch pipeline with Google Gemini 2.5 Flash and NVIDIA NIM.
- Deterministic reassignment engine with human-in-the-loop dispatcher approval.
- Compassionate, older-adult-friendly contact scripts and double-outcome stop closure.

### Out of Scope (What we are NOT doing)
- Integrating live production databases or real user personally identifiable information (PII).
- Automated live-GPS vehicle tracking for this initial prototype phase.
- Autonomous AI reassignment without dispatcher approval.

---

## 2. Shared Task List (Phase 0: Agree)

| Status | Task Description | Assignee | Target Date | Notes |
|:---:|---|:---:|:---:|---|
| ✅ | Lead kickoff & confirm scope | Vuyolwetu | Tue 10 Nov | Completed |
| ✅ | Set up shared task list | Vuyolwetu | Tue 10 Nov | Completed |
| ✅ | Sort information (Public / Internal / Private) | Vuyolwetu | Wed 11 Nov | Defined below |
| ✅ | Write info handling rules (Pretend data only) | Vuyolwetu | Wed 11 Nov | Documented in Section 3 |
| ✅ | Determine success metrics and targets | Adenibiya | Wed 11 Nov | Documented in measures sheet |
| ✅ | Describe pretend data (10 volunteers, 26 stops) | Adenibiya | Wed 11 Nov | Seed specs finalized |
| 🔲 | Write dispatcher scenario (Current vs. Proposed) | Omotayo | Tue 10 Nov | Under review |
| 🔲 | Write plan for reaching older neighbors | Omotayo | Wed 11 Nov | Comms rules drafted |

---

## 3. Information Sheet & Handling Rules

### Data Classification Buckets
- **Public**: General project descriptions, non-sensitive summary metrics, and presentation overviews.
- **Internal**: Team notes, task assignments, architecture drafts, internal schedules, and evaluation reports.
- **Private**: Restricted mock credentials, API keys, and server-side secrets.

### Core Handling Rules (Phase 0–2)
1. **Pretend Data Only**: Absolutely no real names, real phone numbers, or live user personal information may be used in code repositories, testing, or mock datasets. All records must use fictional/mock placeholders (e.g., `+1-555-01xx` numbers, invented street names).
2. **Secret Management**: Google Cloud and NVIDIA API keys must reside in server-side environment variables (`.env`, never committed to Git).
3. **No PII in Logs**: System logs, terminal scrollback, and telemetry must never output personal names or phone numbers unmasked.

# Two-sprint plan

SmartExpense has two sprints on [Jira board 36](https://sathvikgullipalli.atlassian.net/jira/software/projects/SEB/boards/36/backlog). All 27 SRS requirements have [GitHub issue mappings](github-issues.json). The application implements the 17 functional requirements; local automated verification does not complete the remaining manual and deployment acceptance.

## Jira allocation

| Sprint | ID | Issues | Scope |
|---|---|---|---|
| SEB Sprint 1 — Foundation | 70 | SEB-2–5, SEB-12–17 | Accounts, isolation, categories, budgets, and dashboard; 10 issues |
| SEB Sprint 2 — Integration | 103 | SEB-6–11, SEB-18–28 | Transactions, CSV, quality checks, and security acceptance; 17 issues |

Both sprints are in the future state and have no start or end dates recorded. The board has two sprints; there is no third QA sprint.

| Epic | Requirements | Issues | Responsibility |
|---|---|---|---|
| [SEB-1](https://sathvikgullipalli.atlassian.net/browse/SEB-1) — Foundation | SEB-F-001–004, SEB-F-011–016 | SEB-2–5, SEB-12–17 | Sathvik: foundation implementation |
| [SEB-29](https://sathvikgullipalli.atlassian.net/browse/SEB-29) — Transactions | SEB-F-005–010 | SEB-6–11 | Sahana: transaction implementation |
| [SEB-30](https://sathvikgullipalli.atlassian.net/browse/SEB-30) — Reporting and quality | SEB-F-017, SEB-NF-001–005 | SEB-18–23 | Arya: acceptance cases and tests; Sathvik: CSV integration |
| [SEB-31](https://sathvikgullipalli.atlassian.net/browse/SEB-31) — Security | SEB-SR-001–005 | SEB-24–28 | Arya: acceptance cases and tests; Sathvik: integration fixes |

As of 31 October 2026, the 10 Foundation issues are Done. Integration has four Done issues (SEB-6–9) and 13 In Progress issues (SEB-10–11, SEB-18–28). Jira workflow status and test evidence answer different questions: a passing local test does not establish deployed or manual acceptance.

## Delivered work

Arya's [PR #3](https://github.com/gsathvik73-afk/se-project/pull/3) supplied detailed cases and automated checks for CSV, nonfunctional requirements, and security. Sahana's [PR #4](https://github.com/gsathvik73-afk/se-project/pull/4) supplied transaction management. Integration connected those flows to the existing account, category, budget, and dashboard foundation, and added CSV export, login lockout, safe errors, pagination, and local startup support.

## Acceptance still open

| GitHub issue | Requirement / case | Evidence needed |
|---|---|---|
| [#25](https://github.com/gsathvik73-afk/se-project/issues/25) | SEB-NF-004 / TC-UX-01 | Five first-time users complete the entry and error-correction exercise. Record each result; a single browser smoke check is partial evidence. |
| [#26](https://github.com/gsathvik73-afk/se-project/issues/26) | SEB-NF-005 / TC-PORT-01 | Complete the action matrix in Chrome, Firefox, and Edge, including mobile width. |
| [#27](https://github.com/gsathvik73-afk/se-project/issues/27) | SEB-SR-001 / TC-SEC-01 | Verify a public HTTPS deployment, HTTP redirect, valid certificate, and supported TLS version. No public deployment has been verified. |

## Run and review

```sh
./run.sh
# In another terminal:
.venv/bin/python -m pytest -q
```

Open http://127.0.0.1:5050. Register, log in, add income and an expense, edit, cancel a deletion, apply filters, export CSV, set budgets, and inspect Dashboard. Local data and the secret are stored under ignored `instance/` and survive a restart.

[Verification](verification.md) records the test evidence and its limits. The [SRS](SRS_Team14_SmartExpense.pdf), [SAD](SAD_Team14_SmartExpense_Simple.pdf), and [Test Plan](Test_Plan_Team14_SmartExpense.pdf) provide the requirements and acceptance procedures. This page retains its existing `sprint-1.md` path so older links continue to work.

# Sprint 1 integration

All 27 requirements are mapped to [GitHub issues](github-issues.json). The local app includes all 17 functional requirements and the locally verifiable quality/security work. Three acceptance items remain open; the sprint is not claimed fully accepted.

## Contributions and review

- Arya's [PR #3](https://github.com/gsathvik73-afk/se-project/pull/3) was already merged. Reviewed the detailed cases and automated tests. They correctly identified missing CSV, lockout, error handling and responsive UI work; completed checks now run normally instead of xfail.
- Sahana's [PR #4](https://github.com/gsathvik73-afk/se-project/pull/4) was reviewed, fixed in focused follow-up commits, approved and merged after CI passed. Transaction CRUD, field validation, confirmation, sorting and filtering now integrate with budgets, dashboard and owner checks.
- Sathvik's existing foundation is retained. Integration adds CSV, persistent five-failure/five-minute login lockout, safe failure messages/logging, security headers, pagination and one-command startup.

Contributor identities and original commit timestamps are preserved. No shared history was rewritten or backdated. Follow-up commits describe actual work performed during this integration.

## Acceptance left open

| GitHub issue | Requirement / case | Remaining evidence |
|---|---|---|
| [#25](https://github.com/gsathvik73-afk/se-project/issues/25) | SEB-NF-004 / TC-UX-01 | Five first-time users perform the entry/error-correction exercise. Add Expense and field errors are implemented; one browser smoke check is insufficient. |
| [#26](https://github.com/gsathvik73-afk/se-project/issues/26) | SEB-NF-005 / TC-PORT-01 | Run the complete Chrome, Firefox and Edge matrix. In-app browser and 360px checks are partial evidence only. |
| [#27](https://github.com/gsathvik73-afk/se-project/issues/27) | SEB-SR-001 / TC-SEC-01 | Public HTTPS, HTTP redirect and valid TLS certificate. User confirmed the local app is sufficient for this handoff. |

## Run and test

```sh
./run.sh
# In another terminal:
.venv/bin/python -m pytest -q
```

Open http://127.0.0.1:5050. Register, log in, add income/expense, edit, cancel a deletion, apply filters, export CSV, set budgets and inspect the dashboard. Database and local key are under ignored `instance/`; restart preserves data.

[Verification](verification.md) records the actual result and limits. Source SRS, SAD and Test Plan remain in this directory.

## Original Jira allocation

The original Epic is [SEB-1](https://sathvikgullipalli.atlassian.net/browse/SEB-1), board 36, sprint 70. Sathvik owns SEB-2–5 and SEB-12–17; Sahana's transaction allocation is SEB-6–11. Arya contributed test cases for SEB-18–28. GitHub issue status is the current integration tracker. The `jira_status` values in the JSON/CSV are a historical Jira snapshot, not a claim that Jira was updated during this handoff.

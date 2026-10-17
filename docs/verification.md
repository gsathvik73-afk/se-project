# Sprint 1 local verification — 29 October 2026

The integrated application is ready for local use. **105 passed, 2 skipped, no expected failures** in 110.82 seconds, Python 3.11 / SQLite:

```sh
.venv/bin/python -m pytest -q -s --junitxml=/tmp/sprint1-final-results.xml
```

The two skips are the deployed HTTP-to-HTTPS redirect and TLS certificate tests: no public deployment URL was configured. The user confirmed local operation is sufficient for this handoff. This is local acceptance evidence; it does not close all manual/deployed requirements.

## What passed

- TC-AUTH-01–04: normalized unique registration, input boundaries, successful/failed login, logout/session replay rejection and user isolation including CSV.
- TC-EXP-01–06: expense/income creation, amount/date/required-field validation, custom-category selection, persisted edits, confirmation/cancel behaviour, deletion, filter validation, sort, pagination and complete filtered totals. Mutations update dashboard/budget reads; over-budget warnings permit further entries.
- TC-CAT-01, TC-BUD-01–03 and TC-DSH-01–02: defaults/custom categories, rename, saved monthly/category budgets, exact spending/remaining/percentage, 80%/100% boundaries, monthly totals, category breakdown, six-month empty months and year rollover.
- TC-RPT-01: eight CSV checks including headers, UTF-8/escaping, matched filters/order, foreign-user exclusion, formula neutralization, empty results and export beyond the first 50 rows.
- TC-PERF-01: 5,000 stored expenses; 100/100 dashboard and 100/100 transaction loads under three seconds. Dashboard p90 **26.2 ms**, maximum **28.8 ms**; transactions p90 **10.6 ms**, maximum **12.4 ms**. Flask test-client measurements, not a deployed network/load benchmark. Dashboard total was INR 50,000; each page showed 50 transactions.
- TC-PERF-02: **20 concurrent users, 260 successful actions**, including login, page reads, category saves and income saves. Each user saw only their own records and totals. The first run exposed SQLite contention while checking passwords; moving password verification before acquiring the write lock fixed it, and the targeted and full runs then passed.
- TC-REL-01: data survives application restart; forced failures after flush leave no partial record, allow retry and return a safe message. Failure logging omits exception details/SQL parameters.
- TC-SEC-02–05: distinct salted bcrypt hashes, no stored/logged plaintext passwords, owner protection on transaction mutations and categories/budgets, SQL/XSS payload checks, CSRF, password boundary, five-failure/five-minute lockout, Retry-After and restart/expiry/reset checks.
- Local parts of TC-SEC-01/TC-UX-01/TC-PORT-01: Secure-cookie configuration, CSP/HSTS headers, local resources, readable errors/input retention, Add Expense action, responsive CSS/table wrappers and chart script.

## Browser smoke evidence

In-app browser, synthetic local demo account: registration, login, expense save, explicit delete-confirmation page, cancellation preserving the record, monthly budget save and dashboard figures verified. INR 250 Food spending against an INR 500 monthly budget showed INR 250 remaining and 50%. The local server was restarted after the final route changes, and the session/data persisted. At 360px the dashboard had no document overflow; the transaction form/table was also inspected at that width. Screenshots are local QA artifacts outside the source repository.

The browser smoke check covers one tester and one embedded browser engine. It is partial evidence for usability and portability.

## Still open

| Requirement | GitHub issue | Remaining acceptance |
|---|---|---|
| SEB-NF-004 | [#25](https://github.com/gsathvik73-afk/se-project/issues/25) | Five first-time users and their three-click entry/error-correction results. |
| SEB-NF-005 | [#26](https://github.com/gsathvik73-afk/se-project/issues/26) | Complete Chrome, Firefox and Edge action matrix including mobile width. |
| SEB-SR-001 | [#27](https://github.com/gsathvik73-afk/se-project/issues/27) | Public valid HTTPS, HTTP redirect and TLS 1.2+ certificate validation; deferred for local-only handoff. |

## Review and build

Arya PR #3 was already merged and reviewed retrospectively. Sahana PR #4 was approved and merged after both CI jobs passed at `893c9da575f541c61a8927271a26f5e14e831b1e`; merge `a569aa5216cac7b0ebfbbf80011fe789fc05346f`. Original contributor commits remain intact. Follow-up integration code is split into task-based commits. Final PR CI provides the reproducible clean-run result.

Original foundation-only/reverted-build notes are superseded by this integrated-build result. Jira status fields in the traceability files remain the historical Jira snapshot; GitHub tracks this handoff.

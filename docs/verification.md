# Integrated Sprint 1 verification — 8 October 2026

Build: integrated `sprint-1/epic-1-foundation`; automated tester: Codex. Environment: Python 3.11, Flask, SQLite. Result: **62 passed in 48.24s** (`python -m pytest -q`). No failing automated tests or known Critical/Major code defect in this run.

Covered: TC-AUTH-01–04, TC-EXP-01–06, TC-CAT-01, TC-BUD-01–03, TC-DSH-01–02, TC-RPT-01; owner checks on read/edit/delete/category/budget/CSV; salted distinct bcrypt hashes and no plaintext in log capture; stored XSS escaping, injection login/filter inputs, minimum password length and five-failure/five-minute lockout; failed-save flush followed by rollback and successful retry; reopening the same database; HTTPS redirect, Secure/HttpOnly session flags and HSTS in configured test mode.

The real local HTTP workload uses gunicorn 2 workers with 12 threads each and isolated synthetic data. TC-PERF-01: 5,000 transactions, 100 dashboard loads and 100 transaction-list loads, all under three seconds. TC-PERF-02: 20 logged-in users, 400 concurrent-workload requests, no errors or mixed owner records. Exact timings and actual process-restart persistence result are saved in load-results.json. This evidence establishes local server response performance, not deployed browser end-to-end speed.

Browser smoke: authenticated dashboard, charts/totals, saved expense with default date/category/payment, recalculated totals, and 360px transaction/expense layouts in Codex in-app browser. The expense amount field receives automatic focus; Add expense → type amount → Save uses two clicks. This is one automated smoke check, not a five-participant study.

Pending acceptance: TC-UX-01 five real first-time participants; TC-PORT-01 current Chrome, Firefox and Edge matrix; TC-SEC-01 real public HTTPS certificate/TLS and redirect checks; deployed performance and persistent PostgreSQL smoke after provisioning. Vercel project is created; Neon requires account-holder marketplace terms acceptance before the free database can be provisioned. No live URL is claimed yet.

Design decisions: server-side revocable sessions expire after 8 hours. Canvas charts retain readable numerical tables. Vercel requires persistent PostgreSQL; deployment refuses ephemeral SQLite. Transaction amount/date validation, pagination, owner filters, CSV safety, CSRF and password lockout are integrated.

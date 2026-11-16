# Current local verification

November 2026 recovery of SmartExpense. Command: `python scripts/quality.py` with Python 3.11 and temporary SQLite databases. The complete local run executed 299 cases: **297 passed, 0 failed, 2 skipped**. The independent unit selection passed 37 cases; those unit cases are also included in the full-suite count. There are 136 distinct integration/system scenarios, eight for each of the 17 functional requirements.

The latest measured source has 543 executable statements, of which 515 ran: **94.84% statement coverage**. Of 172 branch exits, 154 ran: **89.53% branch coverage**. Combined measurement: **93.57%**. No source lines were excluded from coverage. Missing lines and exits remain in coverage JSON/XML and the HTML report.

The test run preceded only a narrowly targeted Bandit false-positive annotation on the existing password-guidance line and evidence-serialization improvements; application behavior was unchanged. The summary records the tested base revision and dirty-tree status. Fresh CI artifacts identify the exact pushed revision and should be used for final evaluation.

## Functional and boundary evidence

Account normalization/uniqueness, password constraints, login/logout/replay, owner isolation, expense/income CRUD, field validation, retained corrections, confirmation/cancel, date/category/amount filters, sorting, pagination and complete CSV all passed. Categories, monthly/category budget upsert, exact 80/100 boundaries, correct read-time totals, empty months and six-month year rollover passed.

Recovery regressions cover category booleans/fractions/huge IDs, filter amounts that could overflow SQLite, early-calendar trend underflow and JSON error consistency. CSV tests cover UTF-8, commas, quotes, embedded newlines, empty output, formulas, owner isolation and more than one page.

## Nonfunctional and security evidence

5000 stored transactions: all 100 dashboard and all 100 transaction requests were under 3 seconds. Latest measured local p90 was 55.0 ms for dashboard and 43.5 ms for list; these are Flask test-client timings under local workload, not deployed network benchmarks. The 20-user run completed 260 successful actions and reconciled each user's saved data. Restart durability and forced failure after flush verified rollback and retry.

Hash salts, plaintext/log absence, owner authorization, CSRF, SQL/XSS payloads, lockout persistence/expiry/reset, no-store/CSP/cookie configuration and safe failure handling passed. pyflakes emitted no application findings. Bandit uses one explicit B105 false-positive annotation for a public validation message; no blanket checks are disabled. See security-review.md.

## Browser and video evidence

Isolated headless Chromium used synthetic accounts and actual HTML form submission to register/login, create income and expenses, save a category and budget, edit, open/cancel deletion, apply filters, download/parse CSV and inspect dashboard figures. A 360px dashboard check had no document overflow. Screenshots and recording metadata are in reports/browser. Exact 60-second and 120-second WebM videos are in videos. These are current-build retrospective demonstrations, not historical sprint recordings.

## Open acceptance

Two deployment tests skip because no SEB_DEPLOYED_URL was configured. No public HTTPS certificate, redirect or TLS acceptance is claimed. Five-first-time-user observation and the full latest-browser matrix remain open. See issues 25-27 and evaluation-checklist.md. No human review, manual test or instructor sign-off is inferred from passing automation.

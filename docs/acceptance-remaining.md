# Remaining acceptance and how to finish it

These are evidence requirements, not unresolved claims of a known broken core feature. Never mark them complete solely to make the issue list empty.

## Issue 25 three click entry and errors

Code exists: Dashboard Add Expense in smartexpense/templates/dashboard.html, entry fields in templates/transactions.html and validate_transaction in routes.py. Automated tests check the link, useful field errors and retained values. The SRS separately requires **five actual first-time users**.

Have five people who have not used the app begin from Dashboard in synthetic accounts. Agree beforehand whether field-selection clicks count; record the convention rather than changing it after results. Ask each to add INR 250 Food/UPI today, then correct a deliberately invalid amount. Record anonymous participant ID, date, browser/version, clicks, outcome, correction result and observer. Use usability-participants.csv; empty cells mean not observed. If any person fails the criterion, record the failure, improve the flow and repeat honestly. Attach results to issue 25 before closing it.

## Issue 26 browser and mobile compatibility

scripts/browser_acceptance.py runs fifteen real UI checks twice, at 1280px and 360px, for stable Chrome, Edge and Firefox. It covers register/login, category create/rename, income/expense entry, budgets, dashboard/charts, edits, delete confirmation/cancel/confirm, filters, CSV download/formula safety and logout. It records actual versions, viewport widths, screenshots and failures. Browser acceptance Actions uploads separate artifacts for all three browsers. The matrix has now passed all 90 checkpoints, with stable versions and screenshots recorded in docs/reports/browser-acceptance; issue 26 is closed. Run it again after relevant UI changes.

## Issue 27 public HTTPS and TLS

A local HTTP demo and Secure-cookie unit test do not establish public HTTPS. Use a chosen host with persistent database storage and a strong SECRET_KEY, run the prepared Docker/Gunicorn package, configure a valid domain certificate and HTTP-to-HTTPS redirect, require TLS 1.2+, and set COOKIE_SECURE=1. See maintenance.md. The user confirmed no public test URL is currently available.

Run `SEB_DEPLOYED_URL=https://your-real-host .venv/bin/python -m pytest tests/test_security.py -k 'deployed' -q` against that actual host. Record hostname, date, certificate/redirect results and an authenticated Secure/HttpOnly cookie. Close issue 27 only after these pass. The two deployment tests currently skip without a URL.

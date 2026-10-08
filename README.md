# SmartExpense — Team 14

A Flask web application for personal expenses, categories, monthly budgets and spending reports. Sprint 1 is tracked under [Epic 1 / SEB-1](https://sathvikgullipalli.atlassian.net/browse/SEB-1).

## Run locally

Python 3.11+:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-lock.txt
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
flask --app smartexpense init-db
flask --app smartexpense run --port 5050
```

Open http://127.0.0.1:5050 and register an account. The SQLite database lives in ignored `instance/`; no passwords, secrets or live data belong in Git. Use `DATABASE_URL` for another SQLAlchemy database URI; install its driver separately. Set `COOKIE_SECURE=1` for HTTPS environments. Deployment, TLS and load validation belong to the team's security/quality work.

```sh
python -m pytest -q
```

## Sprint 1 scope

| Owner | Requirements | Test plan |
|---|---|---|
| Sai Sathvik Gullipalli | SEB-F-001–004; SEB-F-011–016 | TC-AUTH-01–04; TC-CAT-01; TC-BUD-01–03; TC-DSH-01–02 |
| Sahana Shivakumar — Transaction Management | SEB-F-005–010 | TC-EXP-01–06 |
| Teammates — individual allocation pending | SEB-F-017; SEB-NF-001–005; SEB-SR-001–005 | TC-RPT-01; TC-PERF-01–02; TC-REL-01; TC-UX-01; TC-PORT-01; TC-SEC-01–05 |

Sathvik's account, session, category, budget, dashboard and chart implementation is on `main`. The transaction screen is a read-only integration view. Expense/income entry, transaction edits/deletes/filtering, CSV export, login lockout and deployed performance/security acceptance are awaiting teammates. Shared hashing, CSRF, ownership checks and transaction schema are foundation dependencies; they do not mark the taken test suites complete.

See [Sprint 1 handoff](docs/sprint-1.md), [API contract](docs/api-contract.md), [requirement/Jira traceability](docs/traceability.csv), [verification](docs/verification.md), and the source SRS, test plan and simplified SAD in `docs/`.

The earlier full-project integration has been reverted to match Sathvik’s ten assigned requirements. Jira now records ten own-scope stories Done and 17 teammate stories To Do. Role allocation and later member assignment are in docs/sprint-1.md. Deployment and Neon provisioning are handed to the Security / deployment role.

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

Open http://127.0.0.1:5050 and register an account. The SQLite database lives in ignored `instance/`; no passwords, secrets or live data belong in Git. Use `DATABASE_URL` for persistent PostgreSQL (psycopg is included). Vercel automatically enforces HTTPS and secure cookies; local SQLite is rejected on Vercel. Schema initialization supports the additive login-lockout migration.

```sh
python -m pytest -q
```

## Sprint 1 scope

| Owner | Requirements | Test plan |
|---|---|---|
| Sai Sathvik Gullipalli | SEB-F-001–004; SEB-F-011–016 | TC-AUTH-01–04; TC-CAT-01; TC-BUD-01–03; TC-DSH-01–02 |
| Teammates — individual allocation pending | SEB-F-005–010 | TC-EXP-01–06 |
| Teammates — individual allocation pending | SEB-F-017; SEB-NF-001–005; SEB-SR-001–005 | TC-RPT-01; TC-PERF-01–02; TC-REL-01; TC-UX-01; TC-PORT-01; TC-SEC-01–05 |

The integrated build on `sprint-1/epic-1-foundation` implements all functional requirements, including transaction CRUD/filtering, CSV, budgets, charts, account isolation and login lockout. The allocation above preserves the original agreed work split. See the [eight-minute demo guide](docs/demo-guide.md). Automated checks pass 62 tests. The local HTTP workload check passes 5,000 transactions and 20 concurrent users. Deployment, five-person usability acceptance and the complete three-browser matrix remain pending; these are not claimed as passed.

See [Sprint 1 handoff](docs/sprint-1.md), [API contract](docs/api-contract.md), [requirement/Jira traceability](docs/traceability.csv), [verification](docs/verification.md), and the source SRS, test plan and simplified SAD in `docs/`.

## Vercel deployment

Project: `smartexpense-team14` in `sath-raes-projects`. Entrypoint `app.py`, static assets `public/static`, Singapore function region. `python bootstrap.py` initializes the persistent database during build.

The account holder must accept Neon marketplace terms before provisioning its free database. Connect the database to this Vercel project, provide `DATABASE_URL` (PostgreSQL with TLS) and a randomly generated `SECRET_KEY` as private production environment variables, then run `npx vercel@63.1.0 --prod`. Never commit `.env*` or credentials. Verify `/health`, registration/login, HTTPS redirects, cookie flags, and data persistence after redeployment before calling deployment accepted.

Reproduce the isolated HTTP load and process-restart check:

```sh
PYTHONPATH=. python scripts/load_check.py
```

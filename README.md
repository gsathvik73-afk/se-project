# SmartExpense — Team 14

A small Flask app for personal expenses, income, categories, monthly/category budgets, dashboard charts and filtered CSV exports. Uses Python 3.11+ and SQLite locally.

## Start locally

```sh
./run.sh
```

Open [SmartExpense](http://127.0.0.1:5050), register, then log in. The launcher creates the virtual environment if needed, installs the pinned dependencies, prepares the database, and keeps a private local secret in ignored `instance/`. Existing accounts and data are preserved. Stop with Ctrl+C; rerun the same command to restart. Set `PORT=5051 ./run.sh` if port 5050 is in use.

From Dashboard, choose **Add Expense**. Transactions supports expenses/income, editing, a separate delete confirmation, date/category/amount filters, sorting and 50-row pages. **Export filtered CSV** downloads every matching owned record across all pages. Dashboard totals and budget alerts recalculate from saved transactions. Warnings begin at 80%; spending above 100% never blocks new entries.

## Verify

```sh
.venv/bin/python -m pytest -q
```

Tests cover the integrated functional flows, 5,000-record page performance, 20 concurrent users, persistence/rollback, and local security. The two deployed TLS tests require `SEB_DEPLOYED_URL`. Five first-time users and the full Chrome/Firefox/Edge matrix still need manual acceptance; see [verification](docs/verification.md).

## Sprint 1 and contributions

[GitHub issues](https://github.com/gsathvik73-afk/se-project/issues?q=is%3Aissue) track all 27 SRS requirements; [Sprint 1](docs/sprint-1.md) links the remaining acceptance checks. Original [Jira Epic SEB-1](https://sathvikgullipalli.atlassian.net/browse/SEB-1) references remain in the traceability files.

- Sathvik: account/session, category, budget and dashboard foundation; integration fixes.
- Sahana: transaction management, [PR #4](https://github.com/gsathvik73-afk/se-project/pull/4).
- Arya: detailed acceptance cases and automated CSV/nonfunctional/security tests, [PR #3](https://github.com/gsathvik73-afk/se-project/pull/3).

Original contributor commits remain intact. New integration work is split into focused commits for transaction review, tests, CSV, lockout, concurrency, UI/errors, startup and handoff.

[API contract](docs/api-contract.md) · [Requirement traceability](docs/traceability.csv) · [GitHub requirement mapping](docs/github-issues.json)

## Configuration

`SECRET_KEY` overrides the local key. `DATABASE_URL` overrides SQLite (install another database's driver separately). Run `.venv/bin/python -m flask --app smartexpense init-db` with the same environment after updating an existing installation; it creates the login guard table without replacing data. The launcher does this automatically.

Keep `instance/`, `.env` and credentials out of Git. For a future HTTPS host, supply a strong `SECRET_KEY`, persistent database storage and `COOKIE_SECURE=1`, then use Gunicorn behind TLS. Public deployment is deferred; local HTTP does not establish the deployed HTTPS requirement.

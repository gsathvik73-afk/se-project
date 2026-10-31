# SmartExpense — Team 14

SmartExpense is a Flask app for tracking personal expenses and income. It includes categories, monthly and category budgets, dashboard charts, and filtered CSV exports. Local development uses Python 3.11+ and SQLite.

Project requirements: [SRS (Word)](docs/SRS_Team14_SmartExpense.docx) · [SRS (PDF)](docs/SRS_Team14_SmartExpense.pdf).

## Start locally

```sh
./run.sh
```

Open [SmartExpense](http://127.0.0.1:5050), register, then log in. The launcher creates the virtual environment, installs the pinned dependencies, prepares the database, and stores a private local secret in ignored `instance/`. Existing accounts and transactions survive a restart. Stop with Ctrl+C and run the same command again. Use `PORT=5051 ./run.sh` if port 5050 is occupied.

Choose **Add Expense** from Dashboard to create a transaction. Transactions supports income and expenses, edits, a separate delete confirmation, date/category/amount filters, sorting, and 50-row pages. **Export filtered CSV** includes all matching records, including records beyond the current page. Dashboard totals and budget alerts reflect saved transactions. Warnings start at 80%; spending above a budget does not block new entries.

## Verification

```sh
.venv/bin/python -m pytest -q
```

The recorded local run passed 105 tests, with two deployment checks skipped. Tests cover the functional flows, 5,000-record page performance, 20 concurrent users, persistence, rollback, and local security. The deployed TLS tests need `SEB_DEPLOYED_URL`. Five first-time user trials, the Chrome/Firefox/Edge matrix, and public HTTPS acceptance remain open. See [verification](docs/verification.md) for dates, measurements, and limits.

## Planning and contributions

The project has **two sprints** on [Jira board 36](https://sathvikgullipalli.atlassian.net/jira/software/projects/SEB/boards/36/backlog): Foundation and Integration. Four epics group foundation, transactions, reporting and quality, and security. The [sprint plan](docs/sprint-1.md) lists the allocation and remaining acceptance checks.

[GitHub issues](https://github.com/gsathvik73-afk/se-project/issues?q=is%3Aissue) map all 27 SRS requirements. Their descriptions record the original Jira creation date separately from the GitHub migration date.

- Sathvik: accounts and sessions, categories, budgets, dashboard, and integration fixes including CSV export.
- Sahana: transaction management, delivered in [PR #4](https://github.com/gsathvik73-afk/se-project/pull/4).
- Arya: detailed acceptance cases and automated CSV, nonfunctional, and security tests, delivered in [PR #3](https://github.com/gsathvik73-afk/se-project/pull/3).

[API contract](docs/api-contract.md) · [Requirement traceability](docs/traceability.csv) · [GitHub requirement mapping](docs/github-issues.json)

## Configuration

`SECRET_KEY` overrides the local key. `DATABASE_URL` overrides SQLite; another database needs its own driver. After updating an existing installation, run `.venv/bin/python -m flask --app smartexpense init-db` with the same environment. It creates missing tables and seeds categories without replacing stored data. The launcher runs this step automatically.

Keep `instance/`, `.env`, and credentials out of Git. An HTTPS deployment needs a strong `SECRET_KEY`, persistent storage, `COOKIE_SECURE=1`, and Gunicorn behind TLS. Local HTTP does not establish the deployed HTTPS requirement.

# SmartExpense - Team 14

Personal INR expense and income tracking with private categories, monthly/category budgets, dashboard charts and complete filtered CSV exports. Current team: **Sathik, Arya and Sahana**. Flask, SQLite, Jinja and local Canvas charts; no bank connection.

## Run

```sh
./run.sh
```

Open http://127.0.0.1:5050, register a synthetic account and log in. Python 3.11+ is required. The launcher creates `.venv`, installs exact dependencies, initializes missing tables and stores a private local secret under ignored `instance/`. Existing accounts and data survive restart. Use `PORT=5051 ./run.sh` for another port.

The dashboard's **Add Expense** action opens transaction entry. Save expenses/income, edit records, cancel or confirm deletion, filter/sort records, and export all matching rows across every page. Budget warnings start at 80%; strictly above 100% shows an over-budget alert and still permits entry. All private queries and mutations use the authenticated owner.

## Verify and inspect evidence

```sh
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/quality.py
```

The last full local run passed **297 tests, with 2 deployed-HTTPS skips**. It includes **37 isolated unit tests** and **136 functional scenarios**, eight per functional requirement. Statement coverage: **94.84%**; branch coverage: **89.53%**; combined: **93.57%**. These have different denominators. See [verification](docs/verification.md), [all four required reports](docs/reports/README.md) and [machine-readable summary](docs/reports/summary.json). Actions regenerates fresh reports and builds a deployable container for the pushed revision.

## Submission documents

- [SRS](docs/SRS.pdf), [SAD](docs/SAD.pdf), [Test Plan](docs/Test_Plan.pdf).
- [Project plan with WBS, effort and schedule](docs/Team14_Project_Plan.pdf), [combined project report and synopsis](docs/Project_Report.pdf).
- [Requirements and owners](docs/requirements.json), [traceability](docs/traceability.csv), [136 executed case records](docs/test-cases.csv), [API contract](docs/api-contract.md).
- [One-minute and two-minute retrospective videos](docs/videos/README.md), [demo rehearsal](docs/demo-rehearsal.md), [design changes](docs/deviations.md), [maintenance](docs/maintenance.md), [LLM use](docs/ai-use.md).
- **Twelve-page viva guides:** [Sathik](docs/viva/Sathik_Viva_Guide.pdf), [Arya](docs/viva/Arya_Viva_Guide.pdf), [Sahana](docs/viva/Sahana_Viva_Guide.pdf).

## GitHub and contributions

[GitHub backlog](https://github.com/gsathvik73-afk/se-project/issues) has all 27 requirement issues assigned to the three verified collaborators, with story-point labels and Sprint 1/2 milestones. [Contribution responsibilities and genuine PR evidence](docs/contributions.md) distinguish current ownership from actual authorship. Original member commits and PRs are preserved. November recovery work is AI-assisted under the repository-owner account, with real dates and focused commits.

Sathik owns accounts, budgets and dashboard responsibility; Sahana owns the transaction lifecycle; Arya owns reporting/export and quality/security responsibility. New member changes and reviews must be made from their own accounts. No Jira work is needed for this handoff.

## Acceptance still required

The [evaluation checklist](docs/evaluation-checklist.md) maps every teacher criterion to evidence and remaining work. Five first-time users, a complete current Chrome/Firefox/Edge matrix and valid public HTTPS still need their required evidence. Issues #25-27 stay open. The GitHub token lacks Projects scope; [board setup](docs/github-project-status.md) is prepared, and the issue backlog already works. Genuine member PR/review actions cannot be replaced by generated authorship. New videos are explicitly retrospective, not claimed as October recordings.

## Configuration and deployment

`SECRET_KEY` supplies the application key; `DATABASE_URL` overrides local SQLite; `COOKIE_SECURE=1` enables Secure cookies on HTTPS. `init-db` adds missing tables/defaults and preserves records; schema-column changes need reviewed migrations. CI uploads a non-root Docker/Gunicorn package. A public host still needs persistent storage, a valid certificate, HTTP redirect and TLS 1.2+. See the maintenance plan.

Never commit `instance/`, databases, `.env` files, credentials or personal financial data. Run tests against temporary synthetic databases. This repository is a release candidate with explicit acceptance gaps, not a claim that unobserved manual checks passed.

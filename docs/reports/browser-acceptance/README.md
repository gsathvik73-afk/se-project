# Stable browser acceptance report

SEB-NF-005 / TC-PORT-01: **PASS**. Fifteen full-flow checkpoints in each of three stable browsers at both 1280px and 360px: **90 passed**.

CI evidence: https://github.com/gsathvik73-afk/se-project/actions/runs/43796420904

| Browser | Actual version | Desktop | 360px |
|---|---|---:|---:|
| chrome | 157.0.8103.78 | 15 PASS | 15 PASS |
| edge | 157.0.4341.60 | 15 PASS | 15 PASS |
| firefox | 160.0 | 15 PASS | 15 PASS |

Full cases: register/login, category create/rename, income/expense entry, saved budgets, dashboard totals/charts, persisted edits, deletion confirmation/cancel/confirm, date/amount filters, CSV download/formula safety and logout protection. Each screenshot checkpoint also checks document overflow.

Raw results preserve the actual browser capabilities, CSS viewport width, source checkout, timestamp and any error. Screenshots are in the browser-specific directories. Browsers are isolated headless instances on Ubuntu, selected from the stable vendor channel with Selenium Manager. This verifies the browser requirement; it is not evidence from five real first-time users or a public HTTPS host.

Reproduce: install requirements-browser.txt, then run python scripts/browser_acceptance.py --browser chrome (or edge/firefox). Browser downloads need network access. Avoid reusing a personal browser profile.

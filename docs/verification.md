# Foundation verification — 8 October 2026

Local automated result: **34 passed** (`python -m pytest -q`, Python 3.11, SQLite; 22.35 seconds).

Verified: valid registration, duplicate email normalization, invalid account inputs, login success/failure, logout with rejected replay of old session; anonymous guards; CSRF on writes; default/custom categories, rename and default protection; foreign category/transaction rejection and owner-only totals; monthly/category budget persistence and upsert; INR 1800 spent / 3200 remaining / 36%, Food 500 / 500 / 50%; alert values below 80%, at 80%, at 100%, above 100%; monthly totals 10000/1800/8200; category breakdown; six-month zeros and year rollover; invalid budgets/months; escaped display of user text.

These are foundation tests, not the final complete STP run. Transaction entry, export and editing remain teammate work. TC-AUTH-04's CSV check, TC-CAT-01's expense-form selector, and TC-BUD-03's integrated new-entry check are pending team integration. Performance, concurrency, restart/rollback fault injection, five-user three-click usability, full three-browser/mobile compatibility, deployed HTTPS, and full security-suite execution have not passed merely because core tests passed. The ten own-scope implementation stories are Done; their teammate integration dependencies remain explicitly pending.

Design decisions: server-side sessions have an 8-hour absolute lifetime in this build (SRS does not specify a lifetime); Canvas charts replace the SAD's suggested Chart.js while retaining numerical tables. HTTPS-only cookie mode is enabled with COOKIE_SECURE=1 in deployment. Login lockout is pending SEB-SR-005.

Browser smoke check: synthetic sample login, dashboard totals/charts, budget form save and default category choices verified in the in-app browser. This does not establish the complete TC-PORT-01 browser matrix.

## Scope correction

The whole-project additions and 62-test/load acceptance claims were reverted from the current build at Sathvik’s request. This build retains only his account, category, budget, dashboard and chart scope plus shared foundations. The 17 teammate requirements are To Do with delivery-role labels. Earlier integrated-build evidence remains historical in Git/Jira and is not acceptance evidence for the current reverted build.

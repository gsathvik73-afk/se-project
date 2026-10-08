# Sprint 1 demo guide

Your authored requirement scope is SEB-F-001–004 and SEB-F-011–016, traced to SEB-2–5 and SEB-12–17 under Epic 1. Transaction and quality work originally allocated to teammates is now integrated into this build for a complete demonstration; do not attribute teammates’ work to yourself in an assessment.

## Eight-minute demonstration

1. Register your own account and log in. Show the default eight categories.
2. Add income: source Demo salary, amount 10000, current date.
3. From Dashboard click Add expense, type 500 in the autofocus amount field, then Save expense. Date, Food category and Cash payment are prefilled. Add Travel 300 and Rent 1000.
4. Set this month’s overall budget to 5000 and Food budget to 1000. Dashboard now shows income 10000, expenses 1800, balance 8200; overall 36%, Food 50%.
5. Add another Food expense of 300: Food reaches 80% and displays its warning. Add 250: Food exceeds 100%, displays its over-budget message, and still allows entry.
6. Add a custom Books category, rename it Study, and show it in the expense selector. Rename keeps historical transaction links intact.
7. Select another month, then the current month. Explain category pie, six-month trend and accessible numerical tables.
8. Show transaction filters, matching totals, edit, delete confirmation/cancel and filtered CSV. Open a second account to show private records stay isolated; log out and show protected-page login redirect.
9. Show automated evidence in docs/verification.md and local workload results in docs/load-results.json. Avoid claiming production performance, a five-person usability study or a three-browser matrix before those checks actually occur.

## Real-user acceptance still required

Ask five people who have not used the app to add an expense from Dashboard. Record participant code (no private names needed), click count, success/failure, error usefulness, browser/version, date and build. The intended flow uses two clicks; typing and automatic focus add no clicks. Each person must succeed within three clicks to pass TC-UX-01.

Run registration/login/expense/filter/export/budget/dashboard/logout on current Chrome, Firefox and Edge, recording actual versions and results. Recheck expense entry at 360px. The in-app browser and 360px smoke checks alone are not the full TC-PORT-01 matrix.

The Vercel deployment needs the account holder to accept the Neon marketplace terms. After acceptance, provision the free database, connect DATABASE_URL, set SECRET_KEY privately, deploy and verify HTTPS and durable storage. Local demo is available immediately with the README commands.

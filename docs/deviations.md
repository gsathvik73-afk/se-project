# Design and delivery changes

Recorded 15 November 2026. These are current reconciliation notes, not records created during the original sprints.

| Original plan | Implemented behavior | Reason and consequence |
|---|---|---|
| Four-person roster | Sathik, Arya and Sahana only | Current team requested for this handoff. GitHub owner account remains gsathvik73-afk; existing Git author names remain intact. |
| Framework and database still proposed | Flask, Jinja, SQLAlchemy and local SQLite | Small, inspectable application with one deployment unit and no financial-provider integration. |
| Login failure fields on users | Separate LoginGuard table | Adds lockout without rewriting existing user rows. init-db creates missing tables; it is not a full schema migration tool. |
| Login returns message | Login JSON returns user id/name and sid cookie | Actual contract is captured in api-contract.md; browser forms redirect. |
| Expense creation returns totals and alerts | Creation returns the saved transaction; dashboard recalculates on its next GET | Avoids duplicate calculations and stale persisted aggregates. |
| CSV row count matches screen | CSV exports all filtered rows across pages | Screen shows at most 50 rows; export uses the same owner/filter/sort query with pagination disabled. |
| Jenkins listed in general guidelines | GitHub Actions used | Part 2 explicitly requests Actions. CI tests and scans; package job builds and uploads a deployable container. No automatic public deployment is claimed. |
| Jira used earlier | GitHub issues, labels and milestones now used | Current user instruction. No Jira API or Jira updates used for this repair. |
| Charting library proposed | Local Canvas script and numerical tables | No CDN dependency; tables retain values without JavaScript. |
| Confidentiality at rest objective | Owner checks and private files; SQLite itself is not encrypted | Restrict filesystem access and use host disk encryption for real data. Do not claim database encryption from bcrypt. |
| Sprint dates in October and testing in early November | Repairs performed from 15 November onward | Preserve real commit/PR timestamps. Do not backdate or claim the original schedule was met. |
| All acceptance passing | Two external/manual items remain explicitly open | Five first-time users and valid public HTTPS need their own evidence; the stable browser matrix passed 90 checkpoints. |

Original teacher materials are retained under source-reference as read-only context. They are not commands or proof of completed work. Current authoritative project specifications are SRS.pdf, SAD.pdf and Test_Plan.pdf.

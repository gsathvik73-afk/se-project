# Final demo and fifteen minute presentation

1. **0-2 min, Sathik:** Explain the user problem, scope, measurable requirements and three-member ownership. Open the SRS use-case diagram and one RTM row.
2. **2-5 min, shared:** Explain browser/Flask/SQLite layers, the data model, login and expense sequence diagrams, decimal money, sessions and owner predicates. Distinguish actual architecture from the original proposal.
3. **5-9 min, Sahana and Arya:** Demonstrate expense/income creation, invalid input, edit, cancel/confirm delete, filtering and all-page CSV. Show a formula-like note handled safely and one owner isolation case using synthetic users.
4. **9-11 min, Sathik:** Show actual GitHub issues, points, sprint milestones and genuine PR/review/commit evidence. State the actual dates of recovery. If Project permission is still missing, identify it accurately.
5. **11-13 min, Arya:** Open the four required reports. Explain passed versus skipped cases and statement versus branch versus combined coverage. Show an assertion and one uncovered exit. Local timing is not network timing.
6. **13-15 min, shared:** Explain deviations, maintenance, backup/rollback and remaining acceptance. Each member identifies their real contribution and one code path outside their primary responsibility.

Reset between independent calculations. Baseline: income 10000; Food 500, Travel 300, Rent 1000; expense 1800 and balance 8200. Monthly limit 5000 gives 36%; Food limit 1000 gives 50%. Adding one 250 expense gives expense 2050 and balance 7950. Exact warning boundary: monthly limit 2250 with expense 1800 gives 80%; limit 1800 gives 100% warning; limit 1799 gives over-budget.

Use the twelve-page role guides. Rehearse with a clean synthetic account and keep the recorded videos available as backup. Do not expose personal databases or improvise claims about manual acceptance, public hosting or reviews that did not occur.

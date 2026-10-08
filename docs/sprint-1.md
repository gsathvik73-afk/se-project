# Epic 1 / Sprint 1 handoff

- Project: SmartExpense — Team 14 (`SEB`).
- Epic 1: [SEB-1](https://sathvikgullipalli.atlassian.net/browse/SEB-1).
- Board: [SEB backlog](https://sathvikgullipalli.atlassian.net/jira/software/projects/SEB/boards/36/backlog).
- Sprint: **SEB Sprint 1**, ID 70. Planned, not started. Dates must reflect the team's current schedule; the September dates in the old test plan are historical and were not copied.
- All 27 requirement stories are children of SEB-1 and in Sprint 1, created in requirement order.
- Sathvik's tickets: SEB-2–5 and SEB-12–17. Teammate tickets: SEB-6–11 and SEB-18–28.
- Arya and Sahana are the requested collaborators. Their exact Jira accounts and which taken bundle belongs to each have not been supplied; taken stories remain unassigned. The SRS lists four members; it does not establish these new allocations.

## Add Arya and Sahana to Jira

Jira calls projects “spaces” in this site's current UI. Open SmartExpense, then **Space settings → Access → Add people**. If the person is already on the site, select their verified account. This site currently uses the Free plan: its Access screen says **Everyone’s an admin** and offers only the Administrator role. Granular Member permissions require a plan upgrade; no upgrade was made. Sathvik remains the space owner, and ticket assignees track who does the work. If they are not on the site, an administrator must first invite their email through **Atlassian Administration → Directory → Users → Invite users**, granting Jira access, then add them to this space. After acceptance, set each ticket's **Assignee** to the correct person. No email address has been guessed or invitation sent.

Project access plus an Assignee is how they work on your project. Jira's Epic→Story hierarchy describes work, not a manager→employee reporting hierarchy. Keep the work in SEB-1 / SEB Sprint 1 and use the owner labels until allocations are confirmed.

## GitHub collaboration

Sahana's existing collaborator account is `SahanaShivakumarBadiger`; no duplicate invitation is needed. Arya's GitHub username is still needed. In **Repository Settings → Collaborators → Add people**, search the verified username and invite with Write access; each teammate accepts their invitation.

Clone and check out the shared starting point:

```sh
git clone https://github.com/gsathvik73-afk/se-project.git
cd se-project
git fetch origin
git switch main
# Example after SEB-6 is assigned to you:
git switch -c SEB-6-add-expense
```

Use Jira keys in branch names, commits and PR titles, e.g. `SEB-6 Add expense`. In each PR include exact SEB-F/NF/SR requirements, TC IDs, evidence and integration dependencies. Select Sathvik as reviewer. The foundation is on main. Base teammate branches and pull requests on main, using the matching Jira key.

## Work in dependency order

1. Integrate account/session foundation and default/custom categories.
2. Teammate adds transaction CRUD and filters using the shared model/API contract.
3. Integrate budgets/alerts and dashboard/charts; totals query stored transactions and recalculate on each read.
4. Teammate adds CSV with the same filters and owner scope as the list.
5. Team executes all mapped functional tests, then performance, rollback, usability, browser and security acceptance tests on the integrated build.

Definition of done: reviewed code; mapped test evidence (build, tester, date, actual result, status, defect); RTM updated; no Critical/Major open defect. Creating tickets or passing foundation tests alone does not complete Sprint 1.

## Corrected scope and role allocation

Sathvik’s scope is only SEB-F-001–004 and SEB-F-011–016 (SEB-2–5, SEB-12–17). Those ten implementation stories remain Done. The 17 teammate stories are To Do and unassigned, under the same Epic 1 / Sprint 1. Whole-project completion claims from the earlier integration attempt are superseded.

| Delivery role | Jira stories | Requirements | Tests |
|---|---|---|---|
| Transaction developer | SEB-6–11 | SEB-F-005–010 | TC-EXP-01–06 |
| Reporting developer | SEB-18 | SEB-F-017 | TC-RPT-01 |
| QA / performance tester | SEB-19–23 | SEB-NF-001–005 | TC-PERF-01–02, TC-REL-01, TC-UX-01, TC-PORT-01 |
| Security / deployment engineer | SEB-24–28 | SEB-SR-001–005 | TC-SEC-01–05 |

Roles are delivery responsibilities in issue descriptions and `role-*` labels, not invented Jira user accounts or permission roles. A member can hold more than one bundle. After adding Arya and Sahana, set each bundle’s Assignee to the verified member. Their exact allocation remains your choice.

Basic password hashing, CSRF, owner checks and the transaction model remain necessary dependencies of Sathvik’s account/data-isolation/budget/dashboard work. Their presence does not complete the teammates’ security acceptance suite.

Your demo: register/login/logout; category defaults/add/rename; monthly/category budgets; usage figures and thresholds; selected-month totals, category pie and six-month trend. Use synthetic stored transactions for figures while the transaction developer builds CRUD. CSV isolation, custom-category selection in the expense form and adding a new expense after budget warnings require later teammate integration and must be rechecked then.

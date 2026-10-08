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
git switch --track origin/sprint-1/epic-1-foundation
# Example after SEB-6 is assigned to you:
git switch -c SEB-6-add-expense
```

Use Jira keys in branch names, commits and PR titles, e.g. `SEB-6 Add expense`. In each PR include exact SEB-F/NF/SR requirements, TC IDs, evidence and integration dependencies. Select Sathvik as reviewer. The foundation PR must be reviewed/merged before PRs built on it are merged to main. If working before that merge, target the foundation branch to keep the diff focused, then retarget to main after it merges.

## Work in dependency order

1. Integrate account/session foundation and default/custom categories.
2. Teammate adds transaction CRUD and filters using the shared model/API contract.
3. Integrate budgets/alerts and dashboard/charts; totals query stored transactions and recalculate on each read.
4. Teammate adds CSV with the same filters and owner scope as the list.
5. Team executes all mapped functional tests, then performance, rollback, usability, browser and security acceptance tests on the integrated build.

Definition of done: reviewed code; mapped test evidence (build, tester, date, actual result, status, defect); RTM updated; no Critical/Major open defect. Creating tickets or passing foundation tests alone does not complete Sprint 1.

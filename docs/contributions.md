# Contributor responsibilities and evidence

| Member | Verified GitHub collaborator | Current full feature responsibility | Genuine original evidence |
|---|---|---|---|
| Sathik | gsathvik73-afk | Accounts, budgets, dashboard and integration | Foundation PRs #1/#2 and integration PR #32 |
| Arya | arya7sai | Filtered CSV reporting plus quality/security verification | Test development PR #3; current reporting ownership is not retroactive code authorship |
| Sahana | SahanaShivakumarBadiger | Expense/income transaction lifecycle and filtering | Transaction PR #4 |

November recovery work is AI-assisted under the repository-owner account. Its actual author/committer and timestamps are retained. It is divided into meaningful quality, documentation and learning-material changes, rather than artificial empty commits or teammate impersonation.

For new work, each member uses their own authenticated account, branch and PR. The repository owner reviews a teammate's PR; another contributor reviews an owner-authored change. Review the real diff, reproduce the requirement, verify CI, and record actual findings. A review request is not a completed review. An assignee label is not evidence of authorship.

## Concrete review sequence

1. Sathik reviews authentication, budget and dashboard behavior against the revised SRS and checks startup and persistence.
2. Sahana reviews malformed category-ID protection, transaction validation, editing, delete confirmation and filters against the scenarios.
3. Arya checks filtered CSV completeness/escaping/formula safety, regenerates reports and reconciles statement/branch metrics.
4. Each member records genuine findings in their own PR or review and fixes any observed issue. Never manufacture a defect, date or approval solely to increase counts.
5. After the owner resolves findings and CI is green, freeze the actual reviewed revision. Keep manual/hosting acceptance items open until observed.

Read the corresponding twelve-page PDF in viva before rehearsing. Every member should also trace one requirement outside their own area.

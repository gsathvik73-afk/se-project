# Evaluation evidence and acceptance gaps

Current reconciliation: November 2026. Follow-up corrects milestone counters/deadlines, adds verified member/source guide pages and completes stable-browser acceptance. Teacher materials in source-reference are source requirements, not evidence that the work was completed on their original dates. No Jira work was performed for this repair. GitHub is the project tracker.

| Teacher criterion | Current evidence | State |
|---|---|---|
| Synopsis with team, description, functional features and ownership | Project_Report.pdf section 1; Team14_Project_Plan.pdf | Present; three people only |
| IEEE-style SRS with introductory/descriptive sections and measurable FR/NFR | SRS.pdf; 17 FR, 5 NFR, 5 security requirements | Present |
| At least one UML use-case diagram | SRS.pdf and diagrams/use-cases.svg | Present |
| At least two security objectives and two security requirements | SRS.pdf section 5.1 | Present; deployment acceptance still open |
| IEEE-style Test Plan sections 3, 4 and 5 complete | Test_Plan.pdf | Present |
| Test Plan section 5.1 dedicated to security | Test_Plan.pdf section 5.1 | Present |
| SRS traceability and at least 7-10 cases | traceability.csv, requirements.json, test-cases.csv | 27 mapped requirements; 136 executed functional scenarios |
| Original guideline: 8-10 cases for each implemented functional use case | Eight independently executed scenarios for each of 17 functional requirements | Automated results present; separate human manual execution is not claimed |
| SAD component diagram, descriptions, pattern and security architecture | SAD.pdf; diagrams/components.svg | Present |
| At least two UML sequences, API design, error handling | SAD.pdf; login-sequence.svg; expense-sequence.svg; api-contract.md | Present |
| Lifecycle justification, tools, build/reuse decisions, WBS, person-month estimate and Gantt | Team14_Project_Plan.pdf | Present; estimates labelled planning assumptions |
| GitHub Project linked to repo | scripts/setup_project.py and github-project-status.md | Blocked by token missing project scope; issue backlog is available |
| Backlog derived from FR/NFR and security requirements | 27 existing GitHub issues; github-backlog.json | Updated and verified through GitHub API |
| Story points, individual owners and two sprints | GitHub points labels, assignees, Sprint 1/2 milestones; backlog.csv | Present; current reconciliation is not historical authorship proof |
| GitHub Actions for pushes and PRs | .github/workflows/tests.yml | Configured; see current PR checks for exact revision |
| CI/CD and containerization | Quality job plus container package job; Dockerfile and maintenance.md | CI and deployable package; public CD endpoint not configured |
| Static code analysis | pyflakes and Bandit results under reports | Present; one narrowly documented B105 validation-text false positive |
| Code follows updated SRS/SAD/Test Plan | Actual APIs documented; 297 passing checks in local full suite | Locally verified; limits below |
| Assigned member raises PR and owner formally reviews | Original Arya PR 3 and Sahana PR 4; GitHub history | Genuine historical PRs retained. Current recovery PRs are owner-account AI-assisted work; no independent human review is invented |
| Every member completes a functional feature | Current vertical responsibilities in project plan and contributions.md | Sathik accounts/budgets/dashboard; Sahana transactions; Arya reporting/export. Actual authorship must be demonstrated with real member PRs, not only assignment |
| One-minute Sprint 1 video in repository | videos/Sprint1_demo.webm and videos/README.md | Present; clearly labelled retrospective current-build recording |
| Two-minute Sprint 2 video in repository | videos/Sprint2_demo.webm and videos/README.md | Present; clearly labelled retrospective current-build recording |
| Deviations explained and documents finalized | deviations.md and updated PDFs | Present |
| Development freeze | release-candidate.md and actual Git release-candidate tag | Candidate freeze only; pending acceptance is not hidden |
| Unit Test Report | reports/unit-test-report.md and XML | 37 isolated unit tests passed |
| System Validation Report | reports/system-validation-report.md and XML | Complete local regression: 297 passed, 2 deployed checks skipped |
| Code Coverage Report | reports/code-coverage-report.md, coverage.json/XML/HTML | Measured statement coverage, with misses retained |
| Branch Coverage Report | reports/branch-coverage-report.md | Measured branch coverage, with misses retained |
| Maintenance plan | maintenance.md | Present |
| Working final demo and 15-minute presentation | Project_Report.pdf; demo-rehearsal.md; application and videos | Rehearsal ready; live human delivery still required |
| LLM prompts, understanding and originality explanation | ai-use.md; three 12-page viva guides | Present; members must learn and explain the code |

## Acceptance that cannot be replaced by generated evidence

1. **Five first-time users** must perform TC-UX-01 and record actual click counts and error correction. GitHub issue #25 remains open. A browser script is not five people.
2. **Current stable Chrome, Edge and Firefox** completed fifteen full-flow checkpoints at each of 1280px and 360px: 90 total, with actual versions and screenshots in reports/browser-acceptance. Issue #26 is closed.
3. **Valid public HTTPS** needs a chosen host/domain, certificate, HTTP redirect and successful deployed tests. Issue #27 remains open; two tests skip without SEB_DEPLOYED_URL.
4. **GitHub Projects permission** must be available to create/link the required Project board. All 27 issue records already have assignees, points and sprint milestones. Run setup_project.py after the repository owner grants project scope.
5. **Real member actions and reviews** remain real-person evidence: original PRs are retained; current AI-assisted repairs are not relabelled as three different people. Each member should review their area and raise any new PR from their own account. The owner cannot independently approve their own PR.

Original October sprint deadlines and early-November testing dates have already passed. New recordings, point estimates, repairs and documents are not represented as if they existed on those dates. No instructor signature or manual test result is fabricated.

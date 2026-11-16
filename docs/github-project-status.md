# GitHub Project access

GitHub's direct GraphQL response rejected Projects fields with INSUFFICIENT_SCOPES. The authenticated owner token has repo/workflow access but lacks read:project/project. This was verified directly, not inferred from a CLI warning. Repository updates and the issue backlog work normally.

The GitHub issue backlog now has 27 requirements, the three collaborator assignees, point labels and Sprint 1/2 milestones. This is useful project tracking, but it does not itself satisfy the separate linked GitHub Project criterion.

Repository owner can enable the required scope with:

```sh
gh auth refresh -h github.com -s project
python scripts/setup_project.py
```

The script creates or reuses `SmartExpense Team 14 SDLC`, links it to this repo, adds numeric Story Points and Sprint fields, adds the existing issues and sets the actual acceptance state. It never creates fake member accounts or rewrites Git history. It writes github-project.json only after successful setup.

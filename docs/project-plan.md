# Project planning index

The complete plan is Team14_Project_Plan.pdf, with lifecycle rationale, tool choices, build/reuse analysis, WBS, rough effort and Gantt view. Requirements.json and backlog.csv hold all 27 requirement estimates and current owners. GitHub issues have matching assignees, point labels and Sprint 1/2 milestones.

Teacher baseline: backlog by October 12, dry run October 12-16, Sprint 1 October 19-23, Sprint 2 October 26-30 and testing November 2-6. November recovery is recorded as recovery. The estimates are planning assumptions, not measured time sheets or retroactive proof of completion.

The GitHub Project board setup is prepared separately in scripts/setup_project.py because Projects needs additional token scope. See github-project-status.md. Current tracker is GitHub only.

Milestone counter verification now compares GitHub's displayed open/closed counts with actual linked issue states. A stale counter is refreshed by detaching and restoring one existing association, without reopening completed issues. Sprint 1 is closed when all ten foundation requirements are closed. Sprint 2 stays open while its acceptance requirements remain. Planned due dates are restored to October 23 and October 30; these dates are historical baseline deadlines, not fabricated completion dates. The actual snapshot is docs/milestones.json.

# Release candidate freeze

The November recovery and member-guide follow-up are frozen as a candidate after successful repository CI and packaging. The exact candidate is identified by the Git tag `v2.0.0-rc.2`; resolve it with `git rev-parse v2.0.0-rc.1` and inspect its merged PRs. The tag date is its actual creation date.

The prior rc.1 tag remains unchanged. The rc.2 follow-up corrects milestone counters and planned dates, adds verified member-specific PR/source walkthroughs, and records the passing 90-check stable-browser matrix.

The candidate contains the repaired application, 136 functional scenarios, isolated unit/security/nonfunctional tests, required reports, revised three-member specifications, backlog ownership/points/sprints, two retrospective videos, maintenance material and three twelve-page viva guides.

This freeze does not claim unobserved five-real-user acceptance, public HTTPS, Projects access or independent human review. The acceptance conditions remain visible in evaluation-checklist.md. Any subsequent behavior change needs a focused issue/PR, appropriate regression verification, documentation updates and a new candidate tag. Preserve the current tag and history rather than rewriting the evidence.

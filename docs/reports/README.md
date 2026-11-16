# Required test reports

| Teacher deliverable | Human-readable report | Raw evidence |
|---|---|---|
| Unit Test Report | unit-test-report.md | unit-test-report.xml; unit-test-log.txt |
| System Validation Report | system-validation-report.md | system-validation-report.xml; system-test-log.txt |
| Code Coverage Report | code-coverage-report.md | coverage.json; coverage.xml; coverage-html/index.html |
| Branch Coverage Report | branch-coverage-report.md | coverage.json; coverage.xml; coverage-html/index.html |

Run `python scripts/quality.py` after installing requirements-dev.txt. It creates fresh evidence, fails on failed tests or checks and requires at least 80% combined coverage. This is a project gate, not an evaluator-prescribed threshold. Statement and branch percentages are reported separately. The full-suite system report includes the unit cases; do not add those totals together.

The XML includes per-case names, outcomes and times. Coverage HTML may be generated locally; CI uploads the complete reports directory as its quality-reports artifact. The committed summary records local provenance, and CI artifacts are tied to the pushed revision. security-review.md explains the one reviewed scanner false positive.

Browser screenshots and synthetic recording metadata are in browser. They are partial browser acceptance evidence, not results from five real participants or an untested public TLS target.

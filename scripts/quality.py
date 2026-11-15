#!/usr/bin/env python3
"""Produce fresh, auditable unit, system, statement and branch reports."""
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'reports'


def run(*args, output=None, accepted=(0,)):
    result = subprocess.run([sys.executable, *args], cwd=ROOT, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    if output:
        (OUT / output).write_text(result.stdout)
    print(result.stdout, end='')
    if result.returncode not in accepted:
        raise SystemExit(result.returncode)
    return result.returncode


def report_xml(path, title):
    root = ET.parse(path).getroot()
    cases = root.findall('.//testcase')
    failures = sum(c.find('failure') is not None or c.find('error') is not None for c in cases)
    skipped = sum(c.find('skipped') is not None for c in cases)
    rows = [f'# {title}', '', f'Executed at {datetime.now(timezone.utc).isoformat()}.', '',
            f'{len(cases)-skipped-failures} passed; {failures} failed; {skipped} skipped.', '',
            'Full case identifiers, durations and captured output are in the adjacent JUnit XML.', '',
            '| Test | Result | Seconds |', '|---|---|---:|']
    for c in cases:
        state = 'SKIP' if c.find('skipped') is not None else 'FAIL' if c.find('failure') is not None or c.find('error') is not None else 'PASS'
        rows.append(f"| {c.get('classname')}.{c.get('name')} | {state} | {c.get('time')} |")
    (OUT / (path.stem+'.md')).write_text('\n'.join(rows)+'\n')
    return dict(total=len(cases), passed=len(cases)-skipped-failures, failed=failures, skipped=skipped)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    run('-m', 'pytest', '-q', '-m', 'unit', '--junitxml=docs/reports/unit-test-report.xml', output='unit-test-log.txt')
    unit = report_xml(OUT/'unit-test-report.xml', 'Unit Test Report')
    run('-m', 'coverage', 'erase')
    run('-m', 'coverage', 'run', '-m', 'pytest', '-q', '-s', '--junitxml=docs/reports/system-validation-report.xml', output='system-test-log.txt')
    system = report_xml(OUT/'system-validation-report.xml', 'System Validation Report')
    run('-m', 'coverage', 'json', '-o', 'docs/reports/coverage.json')
    run('-m', 'coverage', 'xml', '-o', 'docs/reports/coverage.xml')
    run('-m', 'coverage', 'html')
    run('-m', 'coverage', 'report', '-m', output='coverage-summary.txt')
    data = json.loads((OUT/'coverage.json').read_text())
    for kind, covered, total in [('Code', 'covered_lines', 'num_statements'), ('Branch', 'covered_branches', 'num_branches')]:
        lines = [f'# {kind} Coverage Report', '',
                 'Measured from the complete suite using coverage.py with branch measurement enabled.', '',
                 '| Module | Covered | Total | Percent |', '|---|---:|---:|---:|']
        for name, item in list(data['files'].items())+[('TOTAL', {'summary': data['totals']})]:
            s=item['summary']; numerator=s[covered]; denominator=s[total]
            lines.append(f'| {name} | {numerator} | {denominator} | {100*numerator/denominator if denominator else 100:.2f}% |')
        lines.extend(['', 'Missing line numbers and branch destinations are in coverage.json and the HTML report.',
            'These percentages measure executed Python statements and branch exits, not complete requirements acceptance.',
            'Browser JavaScript coverage, first-time-user acceptance and public HTTPS are separate checks.'])
        (OUT/(kind.lower()+'-coverage-report.md')).write_text('\n'.join(lines)+'\n')
    run('-m', 'pyflakes', 'smartexpense', output='static-analysis.txt')
    run('-m', 'bandit', '-r', 'smartexpense', '-f', 'json', output='security-scan.json')
    revision=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    (OUT/'summary.json').write_text(json.dumps({'executed_at':datetime.now(timezone.utc).isoformat(),
        'base_revision':revision, 'working_tree_changes_included':bool(subprocess.check_output(['git','status','--porcelain'],cwd=ROOT)),
        'python':sys.version, 'unit':unit,'suite':system,'coverage':data['totals']}, indent=2)+'\n')


if __name__ == '__main__':
    main()

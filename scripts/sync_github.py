#!/usr/bin/env python3
"""Idempotently reconcile GitHub issues from the reviewed local requirements.

Dry-run by default. --apply updates existing issues, assignees, milestones and
point labels. Does not alter Git history or create contributor identities.
"""
import argparse
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
REPO='gsathvik73-afk/se-project'


def gh(*args, data=None):
    command=['gh','api',*args]
    if data is not None:command+=['--input','-']
    p=subprocess.run(command,input=json.dumps(data) if data is not None else None,
                     capture_output=True,text=True,check=True)
    return json.loads(p.stdout) if p.stdout.strip() else None


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    requirements=json.loads((ROOT/'docs/requirements.json').read_text())
    if not args.apply:
        for r in requirements:print(r['requirement'],r['github_assignee'],r['sprint'],r['story_points'])
        return
    milestones=gh(f'repos/{REPO}/milestones?state=all&per_page=100')
    ms={m['title']:m['number'] for m in milestones}
    for title in ['Sprint 1','Sprint 2']:
        if title not in ms:
            data=gh(f'repos/{REPO}/milestones',data={'title':title,'description':'Historical planned sprint allocation reconciled in November 2026; dates and completion evidence are documented in docs/project-plan.md.'})
            ms[title]=data['number']
    labels=gh(f'repos/{REPO}/labels?per_page=100');known={x['name'] for x in labels}
    for name,color in [('sprint-1','1d76db'),('sprint-2','5319e7')]+[(f'points:{n}','bfd4f2') for n in [1,2,3,5,8]]:
        if name not in known:gh(f'repos/{REPO}/labels',data={'name':name,'color':color})
    evidence=[]
    for r in requirements:
        n=int(r['github_issue'].rsplit('/',1)[1]); old=gh(f'repos/{REPO}/issues/{n}')
        labels=[x['name'] for x in old['labels'] if not x['name'].startswith(('points:','sprint-'))]
        labels += [r['sprint'].lower().replace(' ','-'),f"points:{r['story_points']}"]
        body=f"""## User story
As an account owner, I need {r['title'].lower()} so I can manage my finances safely.

## Acceptance and traceability
- Requirement: {r['requirement']}
- Acceptance: {r['expected']}
- Verification: {r['test_case']}
- Steps: {r['steps']}
- Responsibility: {r['owner']} (@{r['github_assignee']})
- Estimate: **{r['story_points']} story points**
- Planned sprint: **{r['sprint']}**
- Acceptance status: {r['acceptance_status']}
- Current evidence: `{r['evidence']}`; see `docs/evaluation-checklist.md` for limits.
- Evidence link: {r.get('evidence_url', 'docs/acceptance-remaining.md for external acceptance steps')}

Allocation reconciled in November 2026. Assignment is a current delivery/review responsibility and does not establish historical code authorship. Genuine original PRs remain available in repository history. Manual and deployment checks stay open until evidence exists.
"""
        result=gh(f'repos/{REPO}/issues/{n}', '-X','PATCH',data={'body':body,'assignees':[r['github_assignee']], 'milestone':ms[r['sprint']],'labels':labels})
        evidence.append({'requirement':r['requirement'],'number':n,'url':result['html_url'],'assignees':[a['login'] for a in result['assignees']], 'milestone':result['milestone']['title'],'labels':[a['name'] for a in result['labels']],'state':result['state']})
    # GitHub may retain stale milestone counters despite correct issue links.
    # Verify counters as well as the issue's milestone property, and refresh one
    # existing association only when needed. Never reopen/close issues to fix UI.
    snapshots=[]
    for title in ['Sprint 1','Sprint 2']:
        number=ms[title]; items=[e for e in evidence if e['milestone']==title]
        expected_open=sum(e['state']=='open' for e in items)
        expected_closed=sum(e['state']=='closed' for e in items)
        points=sum(r['story_points'] for r in requirements if r['sprint']==title)
        current=gh(f'repos/{REPO}/milestones/{number}')
        if (current['open_issues'],current['closed_issues']) != (expected_open,expected_closed):
            issue=gh(f"repos/{REPO}/issues/{items[0]['number']}")
            query='mutation($input:UpdateIssueInput!){updateIssue(input:$input){issue{number}}}'
            for target in [None,current['node_id']]:
                gh('graphql',data={'query':query,'variables':{'input':{'id':issue['node_id'],'milestoneId':target}}})
        deadline='2026-10-23T00:00:00Z' if title=='Sprint 1' else '2026-10-30T00:00:00Z'
        current=gh(f'repos/{REPO}/milestones/{number}','-X','PATCH',data={
            'due_on':deadline,'state':'closed' if expected_open==0 else 'open',
            'description':f"Goal: {'accounts, categories, budgets and dashboard' if title=='Sprint 1' else 'transactions, reporting and quality/security acceptance'}. {len(items)} requirement issues; {points} planned story points. Teacher baseline deadline; November reconciliation does not claim historical on-time completion. See docs/project-plan.md, docs/requirements.json and docs/evaluation-checklist.md."})
        assert (current['open_issues'],current['closed_issues'])==(expected_open,expected_closed), current
        snapshots.append({k:current[k] for k in ['number','title','html_url','state','due_on','open_issues','closed_issues','description']})
    (ROOT/'docs/milestones.json').write_text(json.dumps(snapshots,indent=2)+'\n')
    (ROOT/'docs/github-backlog.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(f'Updated {len(evidence)} existing issues; no duplicate requirements created.')

if __name__=='__main__':main()

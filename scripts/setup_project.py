#!/usr/bin/env python3
"""Create/link the evaluator's GitHub Project after gh has project scope.

Run: gh auth refresh -h github.com -s project
Then: python scripts/setup_project.py
No credentials are stored in this script or repository.
"""
import json
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parents[1]
OWNER='gsathvik73-afk';REPO=OWNER+'/se-project';TITLE='SmartExpense Team 14 SDLC'


def gh(*args):
    p=subprocess.run(['gh',*args],capture_output=True,text=True)
    if p.returncode:raise RuntimeError(p.stderr.strip())
    return json.loads(p.stdout) if p.stdout.strip() else None


def main():
    projects=gh('project','list','--owner',OWNER,'--format','json')['projects']
    project=next((p for p in projects if p['title']==TITLE),None)
    if project is None:project=gh('project','create','--owner',OWNER,'--title',TITLE,'--format','json')
    number=str(project['number']);pid=project['id']
    gh('project','link',number,'--owner',OWNER,'--repo',REPO)
    fields=gh('project','field-list',number,'--owner',OWNER,'--format','json')['fields']
    byname={f['name']:f for f in fields}
    if 'Story Points' not in byname:byname['Story Points']=gh('project','field-create',number,'--owner',OWNER,'--name','Story Points','--data-type','NUMBER','--format','json')
    if 'Sprint' not in byname:byname['Sprint']=gh('project','field-create',number,'--owner',OWNER,'--name','Sprint','--data-type','SINGLE_SELECT','--single-select-options','Sprint 1,Sprint 2','--format','json')
    fields=gh('project','field-list',number,'--owner',OWNER,'--format','json')['fields'];byname={f['name']:f for f in fields}
    options={o['name']:o['id'] for o in byname['Sprint']['options']}
    states={o['name']:o['id'] for o in byname['Status']['options']}
    for r in json.loads((ROOT/'docs/requirements.json').read_text()):
        item=gh('project','item-add',number,'--owner',OWNER,'--url',r['github_issue'],'--format','json')
        gh('project','item-edit','--id',item['id'],'--project-id',pid,'--field-id',byname['Story Points']['id'],'--number',str(r['story_points']))
        gh('project','item-edit','--id',item['id'],'--project-id',pid,'--field-id',byname['Sprint']['id'],'--single-select-option-id',options[r['sprint']])
        state='Todo' if 'Pending' in r['acceptance_status'] else 'Done'
        gh('project','item-edit','--id',item['id'],'--project-id',pid,'--field-id',byname['Status']['id'],'--single-select-option-id',states[state])
    (ROOT/'docs/github-project.json').write_text(json.dumps(project,indent=2)+'\n')
    print(project['url'])

if __name__=='__main__':main()

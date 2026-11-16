#!/usr/bin/env python3
"""Collect inspectable code locations and original PR contribution metadata."""
import ast
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1];REPO='gsathvik73-afk/se-project'


def api(path):
    return json.loads(subprocess.check_output(['gh','api',path],text=True))


def main():
    revision=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    symbols={}
    paths=['smartexpense/routes.py','smartexpense/models.py','smartexpense/__init__.py','scripts/quality.py','scripts/browser_acceptance.py','tests/support.py']
    paths += [str(p.relative_to(ROOT)) for p in sorted((ROOT/'tests').glob('test_*.py'))]
    for path in paths:
        text=(ROOT/path).read_text();lines=text.splitlines()
        for node in ast.parse(text).body:
            if isinstance(node,(ast.FunctionDef,ast.ClassDef)):
                key=path+':'+node.name
                symbols[key]={'file':path,'symbol':node.name,'line':node.lineno,'end_line':node.end_lineno,
                    'url':f'https://github.com/{REPO}/blob/{revision}/{path}#L{node.lineno}-L{node.end_lineno}',
                    'excerpt':'\n'.join(lines[node.lineno-1:min(node.end_lineno,node.lineno+11)])}
    people={}
    for person,login,prs in [('Sathik','gsathvik73-afk',[1,2,32,41,42]),('Arya','arya7sai',[3]),('Sahana','SahanaShivakumarBadiger',[4])]:
        evidence=[]
        for number in prs:
            pr=api(f'repos/{REPO}/pulls/{number}')
            commits=api(f'repos/{REPO}/pulls/{number}/commits?per_page=100')
            files=api(f'repos/{REPO}/pulls/{number}/files?per_page=100')
            evidence.append({'number':number,'title':pr['title'],'author_login':pr['user']['login'],'url':pr['html_url'],'merged_at':pr['merged_at'],'merge_commit':pr['merge_commit_sha'],
                'commits':[{'sha':c['sha'],'author':c['commit']['author']['name'],'subject':c['commit']['message'].splitlines()[0],'url':c['html_url']} for c in commits],
                'changed_files':[f['filename'] for f in files]})
        people[person]={'github_login':login,'pull_requests':evidence}
    (ROOT/'docs/repository-evidence.json').write_text(json.dumps({'source_revision':revision,'symbols':symbols,'members':people},indent=2)+'\n')
    print('Collected code anchors and actual PR/commit metadata for all three members.')

if __name__=='__main__':main()

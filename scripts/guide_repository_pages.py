"""Repository-specific pages inserted into each twelve-page viva guide.

All authorship records and source anchors come from repository-evidence.json.
The remaining pages preserve the shared foundations and role walkthroughs.
"""
from xml.sax.saxutils import escape


def page(person,number,ctx):
    p=ctx['p'];table=ctx['table'];S=ctx['S'];e=ctx['evidence']
    from reportlab.platypus import Paragraph
    def link(label,url):
        return Paragraph('<link href="'+escape(url,{'"':'&quot;'})+'"><u>'+escape(label)+'</u></link>',S['SmallBody'])
    def head(text):return p(text,'GuideH')
    def source(symbol):return e['symbols'][symbol]
    def source_link(key):
        s=source(key);return link(f"Open {s['file']} lines {s['line']}-{s['end_line']} - {s['symbol']}",s['url'])
    prs=e['members'][person]['pull_requests']
    if number==1:
        title=f'{person} SmartExpense Viva Guide'
        st=[p(title,'GuideTitle'),head('01 Your verified contributions and learning path')]
        intro={
        'Sathik':'Your account is gsathvik73-afk. The repository records your account/budget/dashboard foundation, integration, CSV and login-security work. The later recovery PRs are explicitly AI-assisted work under your account. The table below identifies the actual records to open during the viva.',
        'Arya':'Your account is arya7sai. Original PR 3 records detailed acceptance cases, reusable test helpers and automated CSV, nonfunctional and security checks. Your current reporting responsibility includes understanding the export implementation, but assignment is not proof that you originally wrote that implementation.',
        'Sahana':'Your account is SahanaShivakumarBadiger; your original Git author name is sahana2704. Original PR 4 records transaction implementation and the 50-row list limit. That PR also contains later integration fixes by Sathik; the separate author names below matter.'}[person]
        st.append(p(intro))
        rows={
        'Sathik':[['94a175d','Account, budget and dashboard foundation','smartexpense/__init__.py; models.py; routes.py'],['f6e177f','Owner-scoped filtered CSV export','routes.py transaction_export'],['4bbbd3e; 6eebc15','Persistent login guard; reduced SQLite lock contention','routes.py login; models.py LoginGuard'],['PRs 41 and 42','AI-assisted boundary fixes, reports and submission repair','tests; scripts; docs; Actions']],
        'Arya':[['0dc89d7','Detailed CSV/NFR/security test cases','Original DOCX in Git history; current Test_Plan.pdf and test-cases.csv supersede it'],['ae19df4','Automated acceptance checks and shared fixtures','tests/support.py; test_csv_export.py; test_nonfunctional.py; test_security.py']],
        'Sahana':[['b9f6600','Expense/income transaction management','routes.py; transaction_form.html; transactions.html'],['a10a986','Limit list results to 50 rows','routes.py transaction list'],['b0fcdcd; 893c9da','Later fixes/tests authored by Sathik, not Sahana','Validation/API/pagination integration and tests/test_transactions.py']] }[person]
        st.append(table(['Record','What it contributes','Where to find the result'],rows,[84,192,227]))
        for pr in prs:st.append(link(f"PR {pr['number']} by {pr['author_login']} - {pr['title']}",pr['url']))
        st+= [head('What to learn and demonstrate'),p({
        'Sathik':'Read create_app, register/login/logout, LoginGuard, budget_list and dashboard_data. Show account isolation, logout replay rejection and an exact budget boundary. Trace one requirement through SRS, source, test and CI evidence. Demonstrate the actual PR rather than treating an assignee label as authorship.',
        'Arya':'Read the four test/helper files above, then transaction_rows and transaction_export. Demonstrate an all-page filtered export, CSV quoting/formula safety, restart rollback and the difference between statement and branch coverage. Show the two original commit diffs with git show 0dc89d7 and git show ae19df4.',
        'Sahana':'Read transaction_record, owned_transaction, validate_transaction and CRUD routes. Demonstrate a rejected value, a saved edit, cancellation preserving a record, confirmed deletion and a filtered list. Open git show b9f6600 and git show a10a986, then distinguish later review fixes.'}[person]),
        head('How to verify the evidence'),p('docs/repository-evidence.json stores the original PR author, commit SHA, changed-file list and current source links. docs/contributions.md summarizes responsibility. A short SHA can be opened with git show SHA; a PR shows its author, commits, review and merge. Existing history is preserved. Pages 2, 4, 5 and 10 map the repository and your feature to exact files.')]
        return st
    if number==2:
        st=[p('02 Find your way around the repository','GuideTitle'),p('The repository root is the folder containing README.md and run.sh. Paths below are relative to that root. A browser request reaches a Flask route, which validates input, checks its owner and uses the models to read or commit SQLite data. Templates render HTML; static files style and draw it.')]
        rows=[['README.md; run.sh; run.py','Start here. Setup, launcher, private local key, database preparation and local server.'],['smartexpense/__init__.py','create_app builds Flask, CSRF, database, headers and safe error handling.'],['smartexpense/models.py','User, LoginSession, LoginGuard, Category, Transaction and Budget; fields, constraints and indexes.'],['smartexpense/routes.py','Authentication, protected owner checks, money/date validation, CRUD, budgets, dashboard and CSV.'],['smartexpense/templates/','base.html navigation; auth.html account forms; transactions.html list/entry; transaction_form.html edit; transaction_delete.html confirmation; budgets.html; categories.html; dashboard.html.'],['smartexpense/static/','style.css handles layout and responsive rules; charts.js draws the local Canvas charts.'],['tests/','Unit, transaction, CSV, security and nonfunctional assertions; support.py fixtures and conftest.py evidence markers.'],['scripts/quality.py; scripts/browser_acceptance.py','Generate required reports; run current-stable browser journeys with screenshots and actual versions.'],['.github/workflows/','tests.yml runs quality and container packaging; browser-acceptance.yml runs Chrome, Edge and Firefox.'],['docs/requirements.json; traceability.csv','All 27 SRS items, owners, points, sprint, source, case and issue links.'],['docs/reports/; docs/videos/; docs/viva/','Execution/coverage/scans and browser evidence; retrospective demos; these learning guides.'],['Dockerfile; requirements*.txt; .gitignore','Deployable image, exact package inputs and exclusions for private/generated files.']]
        st.append(table(['Location','What it is and why it exists'],rows,[187,316]))
        st+=[head('Your first files to open'),p({'Sathik':'__init__.py -> models.py -> routes.py load_user/login -> budget_list/dashboard_data -> templates/dashboard.html -> tests/test_core.py.','Arya':'tests/support.py -> test_csv_export.py -> test_nonfunctional.py -> test_security.py -> routes.py transaction_export -> scripts/quality.py -> docs/reports.','Sahana':'models.py Transaction -> routes.py owned_transaction/validate_transaction -> CRUD routes -> templates/transactions.html -> transaction_form.html -> transaction_delete.html -> tests/test_transactions.py.'}[person]),head('Private runtime data'),p('instance/ and .venv/ are local and ignored. instance contains the personal database and local key after startup; they are not submission files. Never add them to Git. GET reads, POST creates/actions, PUT updates and DELETE removes. Status 201 means created, 422 means invalid input and 404 means unavailable/foreign record.')]
        return st
    if number==10:
        st=[p('10 Read the actual GitHub project evidence','GuideTitle'),p('Git stores commits and branches; GitHub adds issues, milestones, PR review and Actions. Open the repository and follow the items below. A closed issue means its acceptance is met; a label alone cannot prove that. A milestone groups stories into an increment, while a PR proposes a concrete branch diff.')]
        st.append(table(['GitHub item','What to inspect and where the repository explains it'],[
        ['Issues 5-31','The 27 requirement stories. Body: SRS ID, acceptance, owner, points, sprint and test. docs/github-backlog.json mirrors their actual state.'],['Milestone 1 Sprint 1','Foundation issues 5-8 and 15-20. Teacher planned due October 23. docs/milestones.json records actual counts and state.'],['Milestone 2 Sprint 2','Transactions/reporting/NFR/security issues 9-14 and 21-31. Teacher planned due October 30. It stays open while acceptance issues remain.'],['points and sprint labels','Relative effort and sprint selection. Read requirements.json; points are not hours, marks or proof of work.'],['Pull requests','Open your original member PR, changed files and commit authors; read subsequent owner integration separately. Current issue assignment does not change past authorship.'],['Actions','Quality jobs run tests/scans; package builds Docker; browser matrix records stable versions and screenshots. Open the exact head revision and artifact, not just a green badge.'],['Tag v2.0.0-rc.1 and newer candidates','Immutable checkpoints. docs/release-candidate.md states acceptance limits; do not move old tags to conceal a change.'],['Project board','Different from a milestone. scripts/setup_project.py prepares Story Points and Sprint fields; Projects scope is required. docs/github-project-status.md records access.']], [155,348]))
        st+= [head('Your contribution and review evidence')]
        for pr in prs:st.append(link(f"Inspect PR {pr['number']} - {pr['title']}",pr['url']))
        st+= [head('Check the diff and history yourself'),p('git log --graph --oneline --decorate --all\ngit show COMMIT_SHA\ngit diff origin/main...your-branch\ngh issue view ISSUE_NUMBER\ngh pr view PR_NUMBER --web','CodeText'),p('For new work: update main, make a focused branch, implement and test, inspect/stage intended files, commit, push and open your own PR. The reviewer checks the actual diff and evidence; a review request or automated check is not an independent human approval. Owner-authored AI repairs keep their real account and dates.')]
        return st
    return None


def code_block(person,number,ctx):
    """Small real source excerpt attached to the two role walkthrough pages."""
    keys={('Sathik',4):'smartexpense/routes.py:load_user',('Sathik',5):'smartexpense/routes.py:money',
          ('Sahana',4):'smartexpense/routes.py:owned_transaction',('Sahana',5):'smartexpense/routes.py:transaction_record',
          ('Arya',4):'smartexpense/routes.py:transaction_export',('Arya',5):'scripts/quality.py:report_xml'}
    key=keys[(person,number)];s=ctx['evidence']['symbols'][key]
    from reportlab.platypus import Paragraph
    style=ctx['S']['SmallBody']
    location=Paragraph('<link href="'+escape(s['url'],{'"':'&quot;'})+'"><u>'+escape(f"Repository excerpt: {s['file']}:{s['line']} - {s['symbol']}")+'</u></link>',style)
    lines=[]
    for n,line in enumerate(s['excerpt'].splitlines()[:8],s['line']):
        short=line if len(line)<=88 else line[:84]+' ...'
        lines.append(f'{n:3} '+short)
    return [ctx['p']('Read the submitted code','GuideH'),location,ctx['p']('\n'.join(lines),'CodeText'),ctx['p']('This is an abbreviated excerpt; open the linked file for the complete function. The explanation above describes how it participates in the full feature.','SmallBody')]

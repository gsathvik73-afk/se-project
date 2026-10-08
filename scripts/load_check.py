"""Real HTTP acceptance check against isolated synthetic SQLite data."""
import concurrent.futures as futures
import http.cookiejar
import json
import os
from pathlib import Path
import re
import statistics
import subprocess
import sys
import tempfile
import time
import urllib.request
from datetime import date
from decimal import Decimal
import bcrypt
from smartexpense import create_app
from smartexpense.database import initialize_database
from smartexpense.models import db, User, Category, Transaction

with tempfile.TemporaryDirectory() as temporary:
    uri = 'sqlite:///' + temporary + '/load.db'
    app = create_app({'SECRET_KEY':'isolated-load-check', 'SQLALCHEMY_DATABASE_URI':uri})
    with app.app_context():
        initialize_database()
        category = db.session.scalar(db.select(Category).where(Category.name=='Food')).id
        for i in range(20):
            user = User(name=f'Load {i}', email=f'load{i}@example.test', password_hash=bcrypt.hashpw(b'LoadTest123',bcrypt.gensalt(rounds=4)))
            db.session.add(user); db.session.flush()
            for n in range(5000 if i==0 else i+1):
                db.session.add(Transaction(user_id=user.id,type='expense',amount=Decimal('1.00'),txn_date=date.today(),category_id=category,payment_mode='Cash',note=f'owner-{i}'))
        db.session.commit()
    env=dict(os.environ, SECRET_KEY='isolated-load-check', DATABASE_URL=uri)
    process = subprocess.Popen([sys.executable,'-m','gunicorn','--workers','2','--threads','12','--bind','127.0.0.1:5060','app:app'],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    base='http://127.0.0.1:5060'
    try:
        for _ in range(100):
            try:
                urllib.request.urlopen(base+'/health',timeout=1).close();break
            except Exception: time.sleep(.1)
        def logged_in(i):
            opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
            page=opener.open(base+'/login').read().decode()
            token=re.search(r'name="csrf_token" value="([^"]+)"',page)[1]
            request=urllib.request.Request(base+'/login',data=json.dumps({'email':f'load{i}@example.test','password':'LoadTest123'}).encode(),headers={'Content-Type':'application/json','X-CSRFToken':token})
            assert opener.open(request).status==200
            return opener
        clients=[logged_in(i) for i in range(20)]
        timings={}
        for route in ('/dashboard','/transactions'):
            samples=[]
            for _ in range(100):
                start=time.perf_counter()
                response=clients[0].open(base+route);assert response.status==200;response.read()
                samples.append(time.perf_counter()-start)
            timings[route]={'loads':100,'under_3s':sum(t<=3 for t in samples),'p90_seconds':round(sorted(samples)[89],4),'max_seconds':round(max(samples),4)}
            assert timings[route]['under_3s']>=90
        def concurrent_check(i):
            for _ in range(10):
                request=urllib.request.Request(base+'/transactions',headers={'Accept':'application/json'})
                result=json.load(clients[i].open(request))
                assert result['count']==(5000 if i==0 else i+1)
                assert all(row['note']==f'owner-{i}' for row in result['transactions'])
                result=json.load(clients[i].open(base+'/api/dashboard'))
                assert result['expense']==f"{5000 if i==0 else i+1}.00"
            return i
        with futures.ThreadPoolExecutor(max_workers=20) as pool:
            completed=list(pool.map(concurrent_check,range(20)))
        process.terminate();process.wait(timeout=10)
        process = subprocess.Popen([sys.executable,'-m','gunicorn','--workers','2','--threads','12','--bind','127.0.0.1:5060','app:app'],env=env,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        for _ in range(100):
            try:
                urllib.request.urlopen(base+'/health',timeout=1).close();break
            except Exception: time.sleep(.1)
        persisted=json.load(clients[0].open(urllib.request.Request(base+'/transactions',headers={'Accept':'application/json'})))
        assert persisted['count']==5000
        evidence={'restart_persistence':'passed after actual gunicorn process restart','environment' :'Local HTTP, gunicorn 2 workers / 12 threads each, SQLite WAL; not deployed performance','performance':timings,'concurrency':{'logged_in_users':len(completed),'requests':400,'errors':0,'owner_isolation':'passed'}}
        Path('docs/load-results.json').write_text(json.dumps(evidence,indent=2)+'\n')
        print(json.dumps(evidence,indent=2))
    finally:
        process.terminate();process.wait(timeout=10)

"""Eight independently executed scenarios for each of the seventeen functional requirements.

The catalog is shared with the submission case exporter. Hash cost is reduced only
inside this suite; the existing security/concurrency tests retain production cost.
"""
from datetime import date, timedelta
from decimal import Decimal
import csv
from io import StringIO
import bcrypt
import pytest
from smartexpense.models import db, User, Category, Transaction
from support import make_app, write, csrf

SCENARIOS = {
1: ['unique account', 'normalized duplicate', 'empty name', 'malformed email', 'short password', 'eight character boundary', 'long name', 'multibyte password bound'],
2: ['correct credentials', 'wrong password', 'unknown email', 'normalized email', 'missing password', 'nonstring password', 'lock after five failures', 'session cookie flags'],
3: ['logout success', 'old cookie replay', 'anonymous dashboard', 'anonymous transactions', 'anonymous categories', 'anonymous budgets', 'anonymous API', 'logout requires CSRF'],
4: ['list excludes foreign row', 'detail blocks foreign row', 'update blocks foreign row', 'delete blocks foreign row', 'dashboard excludes foreign income', 'CSV excludes foreign note', 'private categories hidden', 'foreign budget scope blocked'],
5: ['smallest amount', 'integer amount', 'decimal amount', 'optional note', 'note retained', 'payment mode retained', 'today date', 'maximum amount'],
6: ['income saved', 'source retained', 'balance updated', 'no category required', 'no payment required', 'smallest income', 'past date accepted', 'empty source rejected'],
7: ['zero rejected', 'negative rejected', 'text rejected', 'blank rejected', 'future rejected', 'third decimal rejected', 'infinity rejected', 'positive boundary accepted'],
8: ['amount updated', 'note updated', 'date updated', 'payment updated', 'category updated', 'income source updated', 'invalid edit rolled back', 'dashboard recalculated'],
9: ['confirmation page', 'cancel preserves', 'confirmed form delete', 'JSON delete', 'deleted detail absent', 'dashboard recalculated', 'foreign delete blocked', 'missing id safe'],
10: ['inclusive date range', 'category filter', 'minimum amount', 'maximum amount', 'ascending amount', 'descending amount', 'empty results', 'invalid range rejected'],
11: ['eight defaults', 'add custom', 'rename custom', 'default immutable', 'duplicate rejected', 'case duplicate rejected', 'blank rejected', 'select custom in expense'],
12: ['overall saved', 'category saved', 'upsert overall', 'upsert category', 'separate month', 'zero rejected', 'negative rejected', 'foreign category blocked'],
13: ['spent exact', 'remaining exact', 'percentage exact', 'category spending', 'income excluded', 'negative remaining', 'no budget empty', 'zero spending'],
14: ['below 80', 'at 80', 'above 80', 'at 100', 'above 100', 'entry allowed over budget', 'category alert', 'month isolation'],
15: ['income total', 'expense total', 'net balance', 'empty month', 'month isolation', 'after expense create', 'after income create', 'invalid month'],
16: ['category sum', 'three categories', 'six months', 'zero months', 'selected month included', 'year rollover', 'empty category list', 'underflow rejected'],
17: ['CSV header', 'owner isolation', 'date filter', 'amount sorting', 'empty export', 'CSV escaping', 'formula neutralization', 'all pages exported'],
}
CASES = [(r,i,s) for r,items in SCENARIOS.items() for i,s in enumerate(items)]


@pytest.fixture
def environment(tmp_path, monkeypatch):
    original=bcrypt.gensalt
    monkeypatch.setattr(bcrypt,'gensalt',lambda:original(rounds=4))
    app=make_app(tmp_path)
    c=app.test_client()
    write(c,'/register',{'name':'A','email':'a@example.com','password':'password123'})
    write(c,'/login',{'email':'a@example.com','password':'password123'})
    with app.app_context():
        user=db.session.scalar(db.select(User));uid=user.id
        cats={c.name:c.id for c in db.session.scalars(db.select(Category))}
        for name,amount in [('Food','500'),('Travel','300'),('Rent','1000')]:
            db.session.add(Transaction(user_id=uid,type='expense',amount=Decimal(amount),txn_date=date(2026,10,8),category_id=cats[name],payment_mode='UPI',note=name))
        db.session.add(Transaction(user_id=uid,type='income',amount=10000,txn_date=date(2026,10,8),source='Salary'))
        db.session.commit()
        tid=db.session.scalar(db.select(Transaction.id).where(Transaction.type=='expense',Transaction.category_id==cats['Food']))
    return app,c,cats,tid


def expense(c,cats,**extra):
    body={'type':'expense','amount':'250','date':'2026-10-08','category_id':cats['Food'],'payment_mode':'UPI'}
    body.update(extra)
    return write(c,'/transactions',body)


def dashboard(c,month='2026-10'):
    return c.get('/api/dashboard?month='+month).json


def foreign(app,c):
    b=app.test_client()
    write(b,'/register',{'name':'B','email':'b@example.com','password':'password123'})
    write(b,'/login',{'email':'b@example.com','password':'password123'})
    cat=write(b,'/categories',{'name':'Private B'}).json['category']['id']
    tx=write(b,'/transactions',{'type':'income','amount':'999','date':'2026-10-08','source':'B','note':'FOREIGNSECRET'}).json['transaction']['id']
    return b,cat,tx


@pytest.mark.parametrize('r,i,label', CASES, ids=[f'SEB-F-{r:03}-{i+1:02}-{s}' for r,i,s in CASES])
def test_functional_scenario(environment,r,i,label,record_property):
    record_property('requirement',f'SEB-F-{r:03}')
    record_property('case_id',f'IT-F{r:03}-{i+1:02}')
    app,c,cats,tid=environment
    if r==1:
        fresh=app.test_client();body={'name':'New','email':'new@example.com','password':'password123'}
        edits=[{}, {'email':'A@EXAMPLE.COM'}, {'name':''}, {'email':'bad'}, {'password':'1234567'}, {'password':'12345678'}, {'name':'a'*101}, {'password':'😀'*30}]
        body.update(edits[i]);resp=write(fresh,'/register',body)
        assert resp.status_code==([201,422,422,422,422,201,422,422][i])
    elif r==2:
        body={'email':'a@example.com','password':'password123'}
        if i==1:body['password']='wrong'
        if i==2:body['email']='nobody@example.com'
        if i==3:body['email']=' A@EXAMPLE.COM '
        if i==4:body.pop('password')
        if i==5:body['password']=['bad']
        if i==6:
            for _ in range(5):assert write(c,'/login',{'email':'a@example.com','password':'wrong'}).status_code==401
            assert write(c,'/login',body).status_code==429
        else:
            resp=write(c,'/login',body);assert resp.status_code==(401 if i in (1,2,4,5) else 200)
            if i==7:assert 'HttpOnly' in resp.headers['Set-Cookie'] and 'SameSite=Lax' in resp.headers['Set-Cookie']
    elif r==3:
        if i==7:assert c.post('/logout',json={}).status_code==400
        else:
            token=c.get_cookie('sid').value
            assert write(c,'/logout',{}).status_code==200
            if i==1:c.set_cookie('sid',token);assert c.get('/api/dashboard').status_code==401
            if 2<=i<=5:assert c.get(['/dashboard','/transactions','/categories','/budgets'][i-2]).status_code==302
            if i==6:assert c.get('/api/dashboard').status_code==401
    elif r==4:
        b,cat,tx=foreign(app,c)
        if i==0:assert 'FOREIGNSECRET' not in c.get('/transactions').text
        if i==1:assert c.get(f'/transactions/{tx}').status_code==404
        if i==2:assert write(c,f'/transactions/{tx}',{'amount':'1'},'put').status_code==404
        if i==3:assert write(c,f'/transactions/{tx}',{},'delete').status_code==404
        if i==4:assert dashboard(c)['income']=='10000.00'
        if i==5:assert 'FOREIGNSECRET' not in c.get('/transactions/export.csv').text
        if i==6:assert 'Private B' not in c.get('/categories').text
        if i==7:assert write(c,'/budgets',{'month':'2026-10','limit':'100','category_id':cat},'put').status_code==404
    elif r==5:
        edits=[{'amount':'0.01'},{'amount':'1'},{'amount':'250.50'},{},{'note':'Lunch'},{'payment_mode':'Cash'},{'date':date.today().isoformat()},{'amount':'9999999999.99'}]
        resp=expense(c,cats,**edits[i]);assert resp.status_code==201
        for key,value in edits[i].items():
            assert resp.json['transaction'][key]==(f'{Decimal(value):.2f}' if key=='amount' else value)
    elif r==6:
        body={'type':'income','amount':'2000','date':'2026-10-08','source':'Freelance'}
        if i==5:body['amount']='0.01'
        if i==6:body['date']='2026-01-01'
        if i==7:body['source']=''
        resp=write(c,'/transactions',body);assert resp.status_code==(422 if i==7 else 201)
        if i==1:assert resp.json['transaction']['source']=='Freelance'
        if i==2:assert dashboard(c)['balance']=='10200.00'
        if i in (3,4):assert resp.json['transaction']['category_id'] is None and resp.json['transaction']['payment_mode'] is None
    elif r==7:
        edits=[{'amount':'0'},{'amount':'-1'},{'amount':'text'},{'amount':''},{'date':(date.today()+timedelta(days=2)).isoformat()},{'amount':'0.001'},{'amount':'Infinity'},{'amount':'0.01'}]
        assert expense(c,cats,**edits[i]).status_code==(201 if i==7 else 422)
        if i<7:assert dashboard(c)['expense']=='1800.00'
    elif r==8:
        changes=[{'amount':'600'},{'note':'Changed'},{'date':'2026-09-01'},{'payment_mode':'Cash'},{'category_id':cats['Travel']},{'type':'income','source':'Gift'},{'amount':'-1'},{'amount':'600'}]
        resp=write(c,f'/transactions/{tid}',changes[i],'put');assert resp.status_code==(422 if i==6 else 200)
        stored=c.get(f'/transactions/{tid}').json['transaction']
        if i==6:assert stored['amount']=='500.00'
        elif i==7:assert dashboard(c)['expense']=='1900.00'
        else:
            for key,val in changes[i].items():assert stored[key]==(f'{Decimal(val):.2f}' if key=='amount' else val)
    elif r==9:
        path=f'/transactions/{tid}'
        if i==0:assert c.get(path+'/delete').status_code==200;assert c.get(path).status_code==200
        if i==1:
            assert c.post(path+'/delete',data={'csrf_token':csrf(c),'confirm':'no'}).status_code==200
            assert c.get(path).status_code==200
        if i==2:assert c.post(path+'/delete',data={'csrf_token':csrf(c),'confirm':'yes'}).status_code==302
        if 3<=i<=5:
            assert write(c,path,{},'delete').status_code==200
            if i==4:assert c.get(path).status_code==404
            if i==5:assert dashboard(c)['expense']=='1300.00'
        if i==6:
            _,_,tx=foreign(app,c);assert write(c,f'/transactions/{tx}',{},'delete').status_code==404
        if i==7:assert write(c,'/transactions/999999',{},'delete').status_code==404
    elif r==10:
        queries=[{'start':'2026-10-08','end':'2026-10-08'},{'category_id':cats['Food']},{'min_amount':'500'},{'max_amount':'500'},{'sort':'amount_asc'},{'sort':'amount_desc'},{'start':'2026-11-01'},{'start':'2026-11-01','end':'2026-10-01'}]
        resp=c.get('/transactions',query_string=queries[i],headers={'Accept':'application/json'})
        assert resp.status_code==(422 if i==7 else 200)
        if i<7:
            rows=resp.json['transactions']; assert len(rows)==[4,1,3,2,4,4,0][i]
            if i in (4,5):assert [Decimal(t['amount']) for t in rows]==sorted([Decimal(t['amount']) for t in rows],reverse=i==5)
    elif r==11:
        if i==0:assert len(c.get('/categories',headers={'Accept':'application/json'}).json['categories'])==8
        if i in (1,2,7):
            cat=write(c,'/categories',{'name':'Books'}).json['category']['id']
            if i==2:assert write(c,f'/categories/{cat}',{'name':'Study'},'put').json['category']['name']=='Study'
            if i==7:assert expense(c,cats,category_id=cat).status_code==201
        if i==3:assert write(c,f"/categories/{cats['Food']}",{'name':'Change'},'put').status_code==403
        if i in (4,5,6):assert write(c,'/categories',{'name':['Food','food',''][i-4]}).status_code==422
    elif r==12:
        body={'month':'2026-10','limit':'5000'}
        if i in (1,3):body['category_id']=cats['Food']
        if i==4:body['month']='2026-09'
        if i==5:body['limit']='0'
        if i==6:body['limit']='-1'
        if i==7:_,body['category_id'],_=foreign(app,c)
        resp=write(c,'/budgets',body,'put');assert resp.status_code==(422 if i in (5,6) else 404 if i==7 else 200)
        if i in (2,3):
            body['limit']='6000';assert write(c,'/budgets',body,'put').status_code==200
            assert len(dashboard(c)['budgets'])==1 and dashboard(c)['budgets'][0]['limit']=='6000.00'
        if i==4:assert dashboard(c)['budgets']==[] and len(dashboard(c,'2026-09')['budgets'])==1
    elif r==13:
        if i!=6:
            body={'month':'2026-09' if i==7 else '2026-10','limit':'1000' if i==5 else '5000'}
            if i==3:body.update(category_id=cats['Food'],limit='1000')
            write(c,'/budgets',body,'put')
        data=dashboard(c,'2026-09' if i==7 else '2026-10')
        if i==6:assert data['budgets']==[]
        else:
            b=data['budgets'][0]
            assert [b['spent'],b['remaining'],b['percent_used']]==(['500.00','500.00','50.00'] if i==3 else ['1800.00','-800.00','180.00'] if i==5 else ['0.00','5000.00','0.00'] if i==7 else ['1800.00','3200.00','36.00'])
            if i==4:assert data['income']=='10000.00' and b['spent']=='1800.00'
    elif r==14:
        limits=['2500','2250','2000','1800','1799','100','625','100']
        body={'month':'2026-09' if i==7 else '2026-10','limit':limits[i]}
        if i==6:body['category_id']=cats['Food']
        write(c,'/budgets',body,'put')
        if i==7:assert dashboard(c)['budgets']==[]
        else:
            assert dashboard(c)['budgets'][0]['alert']==['none','warning','warning','warning','over','over','warning'][i]
            if i==5:assert expense(c,cats).status_code==201
    elif r==15:
        if i==5:expense(c,cats)
        if i==6:write(c,'/transactions',{'type':'income','amount':'2000','date':'2026-10-08','source':'Gift'})
        if i==7:assert c.get('/api/dashboard?month=bad').status_code==422
        else:
            d=dashboard(c,'2026-09' if i in (3,4) else '2026-10')
            expected=('0.00','0.00','0.00') if i in (3,4) else ('10000.00','2050.00','7950.00') if i==5 else ('12000.00','1800.00','10200.00') if i==6 else ('10000.00','1800.00','8200.00')
            assert (d['income'],d['expense'],d['balance'])==expected
    elif r==16:
        d=dashboard(c,'2026-01' if i==5 else '2026-09' if i==6 else '2026-10')
        if i==0:assert sum(Decimal(x['total']) for x in d['categories'])==Decimal('1800')
        if i==1:assert len(d['categories'])==3
        if i==2:assert len(d['trend'])==6
        if i==3:assert [x['expense'] for x in d['trend'][:5]]==['0.00']*5
        if i==4:assert d['trend'][-1]['month']=='2026-10'
        if i==5:assert d['trend'][0]['month']=='2025-08'
        if i==6:assert d['categories']==[]
        if i==7:assert c.get('/api/dashboard?month=0001-01').status_code==422
    elif r==17:
        if i==1:foreign(app,c)
        if i==5:expense(c,cats,note='comma, quote " and\nnewline')
        if i==6:expense(c,cats,note='=SUM(A1:A2)')
        if i==7:
            with app.app_context():
                uid=db.session.scalar(db.select(User.id).where(User.email=='a@example.com'))
                db.session.add_all(Transaction(user_id=uid,type='income',amount=1,txn_date=date(2026,10,8),source='Gift') for _ in range(55));db.session.commit()
        query={'start':'2026-10-08','end':'2026-10-08'} if i==2 else {'sort':'amount_asc'} if i==3 else {'start':'2026-11-01'} if i==4 else {}
        resp=c.get('/transactions/export.csv',query_string=query);assert resp.status_code==200
        rows=list(csv.reader(StringIO(resp.text)))
        assert rows[0]==['date','type','category','amount','payment_mode','source','note']
        if i==1:assert 'FOREIGNSECRET' not in resp.text
        if i==2:assert len(rows)==5
        if i==3:assert [Decimal(row[3]) for row in rows[1:]]==sorted(Decimal(row[3]) for row in rows[1:])
        if i==4:assert len(rows)==1
        if i==5:assert any(row[-1]=='comma, quote " and\nnewline' for row in rows[1:])
        if i==6:assert any(row[-1]=="'=SUM(A1:A2)" for row in rows[1:])
        if i==7:assert len(rows)==60

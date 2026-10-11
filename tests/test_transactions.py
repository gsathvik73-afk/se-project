import csv
import io
from datetime import date, timedelta, datetime, timezone
from decimal import Decimal
from sqlalchemy.exc import OperationalError
import pytest
from smartexpense.models import db, User, Transaction, Category, Budget
from test_core import app, client, account, write, seed, csrf


def expense(client, category, amount='250', **kwargs):
    body=dict(type='expense',amount=amount,date=date.today().isoformat(),category_id=category,payment_mode='UPI',note='Lunch')
    body.update(kwargs)
    return write(client,'/transactions',body)


def test_TC_EXP_01_02(client,app):
    account(client);cats=seed(app)
    response=expense(client,cats['Food'],date='2026-10-08')
    assert response.status_code==201 and response.json['transaction']['note']=='Lunch'
    assert client.get('/api/dashboard?month=2026-10').json['expense']=='2050.00'
    assert expense(client,cats['Food'],note='',date='2026-10-08').status_code==201
    income=write(client,'/transactions',dict(type='income',amount='2000',date='2026-10-08',source='Freelance'))
    assert income.status_code==201
    report=client.get('/api/dashboard?month=2026-10').json
    assert report['income']=='12000.00' and report['balance']=='9700.00'

@pytest.mark.parametrize('value',['0','-1','','text','NaN','0.001'])
def test_TC_EXP_03_invalid_amount(client,app,value):
    account(client);cats=seed(app)
    assert expense(client,cats['Food'],amount=value).status_code==422
    assert client.get('/transactions',headers={'Accept':'application/json'}).json['count']==4

def test_TC_EXP_03_date_and_small_amount(client,app):
    account(client);cats=seed(app)
    assert expense(client,cats['Food'],date=(date.today()+timedelta(days=1)).isoformat()).status_code==422
    assert expense(client,cats['Food'],amount='0.01').status_code==201

def test_TC_EXP_04_edit_totals(client,app):
    account(client);seed(app)
    listing=client.get('/transactions',headers={'Accept':'application/json'}).json['transactions']
    target=next(t for t in listing if t['amount']=='500.00')
    assert write(client,f"/transactions/{target['id']}",{'amount':'600'},'put').status_code==200
    assert client.get('/api/dashboard?month=2026-10').json['expense']=='1900.00'
    income=next(t for t in listing if t['type']=='income')
    assert write(client,f"/transactions/{income['id']}",{'amount':'11000'},'put').status_code==200
    assert client.get('/api/dashboard?month=2026-10').json['balance']=='9100.00'

def test_TC_EXP_05_cancel_confirm(client,app):
    account(client);seed(app)
    target=next(t for t in client.get('/transactions',headers={'Accept':'application/json'}).json['transactions'] if t['amount']=='300.00')
    assert client.get(f"/transactions/{target['id']}/delete").status_code==200
    assert write(client,f"/transactions/{target['id']}",{'confirm':False},'delete').status_code==422
    assert client.get(f"/transactions/{target['id']}").status_code==200
    assert write(client,f"/transactions/{target['id']}",{'confirm':True},'delete').status_code==200
    assert client.get('/api/dashboard?month=2026-10').json['expense']=='1500.00'

def test_TC_EXP_06_RPT_01_filters_and_export(client,app):
    account(client);cats=seed(app)
    query={'from':'2026-10-01','to':'2026-10-31','category_id':cats['Food'],'min':'100','max':'600','sort':'amount','order':'asc'}
    result=client.get('/transactions',query_string=query,headers={'Accept':'application/json'}).json
    assert result['count']==1 and result['total']=='500.00'
    exported=client.get('/transactions/export.csv',query_string=query)
    assert exported.mimetype=='text/csv'
    data=list(csv.DictReader(io.StringIO(exported.text)))
    assert len(data)==result['count'] and data[0]['amount']=='500.00'
    for order in ['asc','desc']:
        rows=client.get('/transactions',query_string={'sort':'amount','order':order},headers={'Accept':'application/json'}).json['transactions']
        values=[Decimal(r['amount']) for r in rows]
        assert values==sorted(values,reverse=order=='desc')
    none=client.get('/transactions',query_string={'min':'999999'},headers={'Accept':'application/json'}).json
    assert none['count']==0 and none['total']=='0.00'

@pytest.mark.parametrize('query',[{'from':'2026-10-31','to':'2026-10-01'},{'min':'500','max':'10'},{'sort':'amount; DROP TABLE user'},{'order':'bad'},{'min':'NaN'},{'page':'0'},{'from':'2026-99-01'}])
def test_bad_filters(client,query):
    account(client);assert client.get('/transactions',query_string=query).status_code==422

def test_export_every_page_and_csv_escaping(client,app):
    account(client)
    with app.app_context():
        owner=db.session.scalar(db.select(User));cat=db.session.scalar(db.select(Category).where(Category.name=='Food'))
        db.session.add_all([Transaction(user_id=owner.id,type='expense',amount=1,txn_date=date(2026,10,8),category_id=cat.id,payment_mode='Cash',note='=SUM(1,2)\n"quoted"') for _ in range(55)])
        db.session.commit()
    result=client.get('/transactions',headers={'Accept':'application/json'}).json
    assert len(result['transactions'])==50 and result['count']==55 and result['total']=='55.00'
    assert len(client.get('/transactions?page=2',headers={'Accept':'application/json'}).json['transactions'])==5
    data=list(csv.DictReader(io.StringIO(client.get('/transactions/export.csv').text)))
    assert len(data)==55 and data[0]['note']=="'=SUM(1,2)\n\"quoted\""

def test_TC_AUTH_04_SEC_03_all_foreign_operations(client,app):
    account(client);cats=seed(app)
    other=app.test_client();account(other,'b@example.com','B')
    txn=expense(other,cats['Food']).json['transaction']['id']
    category=write(other,'/categories',{'name':'Private'}).json['category']['id']
    write(other,'/budgets',{'month':'2026-10','limit':'8888'})
    assert client.get(f'/transactions/{txn}').status_code==404
    assert client.get(f'/transactions/{txn}/edit').status_code==404
    assert write(client,f'/transactions/{txn}',{'amount':'1'},'put').status_code==404
    assert write(client,f'/transactions/{txn}',{'confirm':True},'delete').status_code==404
    assert write(client,f'/categories/{category}',{'name':'Stolen'},'put').status_code==404
    assert expense(client,category).status_code==404
    assert write(client,'/budgets',{'month':'2026-10','category_id':category,'limit':'1'}).status_code==404
    assert '8888' not in client.get('/budgets?month=2026-10').text
    assert len(list(csv.DictReader(io.StringIO(client.get('/transactions/export.csv').text))))==4
    assert other.get(f'/transactions/{txn}').json['transaction']['amount']=='250.00'

def test_TC_CAT_01_expense_selector_and_rename(client,app):
    account(client)
    cat=write(client,'/categories',{'name':'Books'}).json['category']['id']
    assert 'Books' in client.get('/transactions/new').text
    assert expense(client,cat).status_code==201
    assert write(client,f'/categories/{cat}',{'name':'Study'},'put').status_code==200
    assert 'Study' in client.get('/transactions').text

def test_TC_BUD_03_never_blocks_entries(client,app):
    account(client);cats=seed(app)
    write(client,'/budgets',{'month':'2026-10','limit':'1800'})
    result=expense(client,cats['Food'],date='2026-10-08')
    assert result.status_code==201 and result.json['alerts'][0]['alert']=='over'

def test_TC_SEC_02_password_storage(client,app,caplog):
    account(client);other=app.test_client();account(other,'b@example.com')
    with app.app_context():
        users=db.session.scalars(db.select(User)).all()
        assert users[0].password_hash!=users[1].password_hash
        assert all(u.password_hash.startswith(b'$2') and b'password123' not in u.password_hash for u in users)
    assert 'password123' not in caplog.text

def test_TC_SEC_04_sql_and_stored_xss(client,app):
    account(client);cats=seed(app)
    assert write(client,'/login',{'email':"' OR 1=1 --",'password':'anything'}).status_code==401
    payload='<script>alert(document.cookie)</script>'
    txn=expense(client,cats['Food'],note=payload).json['transaction']
    page=client.get('/transactions').text
    assert payload not in page and '&lt;script&gt;' in page
    assert client.get(f"/transactions/{txn['id']}").json['transaction']['note']==payload

def test_TC_SEC_05_length_and_lockout(client,app):
    assert write(client,'/register',{'name':'A','email':'a@example.com','password':'1234567'}).status_code==422
    assert write(client,'/register',{'name':'A','email':'a@example.com','password':'12345678'}).status_code==201
    for _ in range(5):
        assert write(client,'/login',{'email':'a@example.com','password':'wrong'}).status_code==401
    blocked=write(client,'/login',{'email':'a@example.com','password':'12345678'})
    assert blocked.status_code==429 and 1<=int(blocked.headers['Retry-After'])<=300
    with app.app_context():
        user=db.session.scalar(db.select(User));user.locked_until=datetime.now(timezone.utc)-timedelta(seconds=1);db.session.commit()
    assert write(client,'/login',{'email':'a@example.com','password':'12345678'}).status_code==200
    with app.app_context():
        user=db.session.scalar(db.select(User));assert user.failed_attempts==0 and user.locked_until is None

def test_TC_REL_01_commit_failure_rolls_back(client,app,monkeypatch):
    account(client);cats=seed(app)
    original=db.session.commit
    def fail_commit():
        db.session.flush()
        raise OperationalError('test failure',{},Exception('injected'))
    monkeypatch.setattr(db.session,'commit',fail_commit)
    result=expense(client,cats['Food'])
    assert result.status_code==500 and result.json['error']=='SAVE_FAILED'
    monkeypatch.setattr(db.session,'commit',original)
    assert client.get('/transactions',headers={'Accept':'application/json'}).json['count']==4
    assert expense(client,cats['Food']).status_code==201

def test_TC_REL_01_restart_persistence(client,app):
    account(client);cats=seed(app);expense(client,cats['Food'])
    # A new factory/engine simulates process reopening the same persistent file.
    from smartexpense import create_app
    reopened=create_app(dict(TESTING=True,SECRET_KEY='test-only-secret',SQLALCHEMY_DATABASE_URI=app.config['SQLALCHEMY_DATABASE_URI']))
    fresh=reopened.test_client()
    write(fresh,'/login',{'email':'a@example.com','password':'password123'})
    assert fresh.get('/transactions',headers={'Accept':'application/json'}).json['count']==5

def test_https_redirect_and_secure_cookie(app):
    app.config.update(ENFORCE_HTTPS=True,SESSION_COOKIE_SECURE=True)
    client=app.test_client()
    response=client.get('/login',base_url='http://localhost')
    assert response.status_code==308 and response.location.startswith('https://')
    page=client.get('/login',base_url='https://localhost')
    import re
    token=re.search(r'name="csrf_token" value="([^"]+)"',page.text)[1]
    assert client.post('/register',base_url='https://localhost',json={'name':'A','email':'a@example.com','password':'password123'},headers={'X-CSRFToken':token,'Referer':'https://localhost/login'}).status_code==201
    response=client.post('/login',base_url='https://localhost',json={'email':'a@example.com','password':'password123'},headers={'X-CSRFToken':token,'Referer':'https://localhost/login'})
    sid=next(h for h in response.headers.getlist('Set-Cookie') if h.startswith('sid='))
    assert 'Secure' in sid and 'HttpOnly' in sid
    assert 'max-age=31536000' in response.headers['Strict-Transport-Security']

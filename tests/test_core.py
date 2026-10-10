import re
from datetime import date
from decimal import Decimal
import pytest
from smartexpense import create_app
from smartexpense.models import db, User, Category, Transaction, Budget

@pytest.fixture
def app(tmp_path):
    app=create_app({'TESTING':True,'SECRET_KEY':'test-only-secret','SQLALCHEMY_DATABASE_URI':f'sqlite:///{tmp_path}/test.db'})
    with app.app_context():
        app.test_cli_runner().invoke(args=['init-db'])
    yield app

@pytest.fixture
def client(app):
    return app.test_client()

def csrf(client):
    page=client.get('/login').text
    return re.search(r'name="csrf_token" value="([^"]+)"',page)[1]

def write(client,path,body,method='post'):
    return getattr(client,method)(path,json=body,headers={'X-CSRFToken':csrf(client)})

def account(client,email='a@example.com',name='A'):
    assert write(client,'/register',{'name':name,'email':email,'password':'password123'}).status_code==201
    assert write(client,'/login',{'email':email,'password':'password123'}).status_code==200

def seed(app):
    with app.app_context():
        a=db.session.scalar(db.select(User).where(User.email=='a@example.com'))
        cats={c.name:c.id for c in db.session.scalars(db.select(Category))}
        for name,amount in [('Food','500'),('Travel','300'),('Rent','1000')]:
            db.session.add(Transaction(user_id=a.id,type='expense',amount=Decimal(amount),txn_date=date(2026,10,8),category_id=cats[name],payment_mode='UPI'))
        db.session.add(Transaction(user_id=a.id,type='income',amount=Decimal('10000'),txn_date=date(2026,10,8),source='Salary'))
        db.session.commit()
        return cats

def test_registration_duplicate_and_login(client):
    account(client)
    assert write(client,'/register',{'name':'Other','email':'A@EXAMPLE.COM','password':'password123'}).status_code==422
    assert write(client,'/login',{'email':'a@example.com','password':'wrong'}).status_code==401
    assert client.get('/dashboard').status_code==200

@pytest.mark.parametrize('body',[{'name':'','email':'a@b.com','password':'password123'},{'name':'A','email':'bad','password':'password123'},{'name':'A','email':'a@b.com','password':'short'},{'name':'A','email':'a@b.com','password':'😀'*30}])
def test_registration_validation(client,body):
    assert write(client,'/register',body).status_code==422

def test_logout_revokes_replayed_cookie(client):
    account(client);cookie=client.get_cookie('sid').value
    assert write(client,'/logout',{}).status_code==200
    client.set_cookie('sid',cookie)
    assert client.get('/api/dashboard').status_code==401
    assert client.get('/dashboard').status_code==302

def test_csrf_required(client):
    assert client.post('/register',json={'name':'A','email':'a@example.com','password':'password123'}).status_code==400

def test_categories_add_rename_and_defaults(client,app):
    account(client)
    defaults=client.get('/categories',headers={'Accept':'application/json'}).json['categories']
    assert len(defaults)==8 and all(c['is_default'] for c in defaults)
    added=write(client,'/categories',{'name':'Books'}).json['category']
    assert write(client,f"/categories/{added['id']}",{'name':'Study'},'put').status_code==200
    assert 'Study' in client.get('/categories').text
    assert write(client,'/categories',{'name':'food'}).status_code==422
    with app.app_context(): food=db.session.scalar(db.select(Category).where(Category.name=='Food')).id
    assert write(client,f'/categories/{food}',{'name':'Changed'},'put').status_code==403

def test_foreign_category_budget_and_transaction_isolation(client,app):
    account(client);seed(app)
    b=app.test_client();account(b,'b@example.com','B')
    foreign_cat=write(b,'/categories',{'name':'Private'}).json['category']['id']
    assert write(client,f'/categories/{foreign_cat}',{'name':'Stolen'},'put').status_code==404
    assert write(client,'/budgets',{'month':'2026-10','limit':'5000','category_id':foreign_cat},'put').status_code==404
    with app.app_context():
        owner=db.session.scalar(db.select(User).where(User.email=='b@example.com'))
        txn=Transaction(user_id=owner.id,type='income',amount=99999,txn_date=date(2026,10,8),source='B private');db.session.add(txn);db.session.commit();tid=txn.id
    assert client.get(f'/transactions/{tid}').status_code==404
    assert 'B private' not in client.get('/transactions').text
    assert client.get('/api/dashboard?month=2026-10').json['income']=='10000.00'
    assert b.get('/api/dashboard?month=2026-10').json['expense']=='0.00'

def test_budget_persistence_upsert_and_totals(client,app):
    account(client);cats=seed(app)
    for category,limit in [(None,'5000'),(cats['Food'],'1000')]:
        assert write(client,'/budgets',{'month':'2026-10','limit':limit,'category_id':category},'put').status_code==200
    data=client.get('/api/dashboard?month=2026-10').json
    assert (data['income'],data['expense'],data['balance'])==('10000.00','1800.00','8200.00')
    assert [(b['spent'],b['remaining'],b['percent_used']) for b in data['budgets']]==[('1800.00','3200.00','36.00'),('500.00','500.00','50.00')]
    write(client,'/budgets',{'month':'2026-10','limit':'6000'},'put')
    with app.app_context(): assert db.session.scalar(db.select(db.func.count()).select_from(Budget))==2
    new=app.test_client();write(new,'/login',{'email':'a@example.com','password':'password123'})
    assert new.get('/api/dashboard?month=2026-10').json['budgets'][0]['limit']=='6000.00'

@pytest.mark.parametrize('limit,expected',[('2500','none'),('2250','warning'),('1800','warning'),('1799','over')])
def test_alert_thresholds(client,app,limit,expected):
    account(client);seed(app);write(client,'/budgets',{'month':'2026-10','limit':limit},'put')
    assert client.get('/api/dashboard?month=2026-10').json['budgets'][0]['alert']==expected
    # Alerts are computed at read time and never reject transaction writes.

def test_chart_breakdown_six_months_and_empty_state(client,app):
    account(client);seed(app)
    with app.app_context():
        user=db.session.scalar(db.select(User));food=db.session.scalar(db.select(Category).where(Category.name=='Food'))
        db.session.add(Transaction(user_id=user.id,type='expense',amount=100,txn_date=date(2026,5,1),category_id=food.id,payment_mode='Cash'));db.session.commit()
    data=client.get('/api/dashboard?month=2026-10').json
    assert data['categories']==[{'name':'Food','total':'500.00'},{'name':'Rent','total':'1000.00'},{'name':'Travel','total':'300.00'}]
    assert [t['month'] for t in data['trend']]==['2026-05','2026-06','2026-07','2026-08','2026-09','2026-10']
    assert [t['expense'] for t in data['trend']]==['100.00','0.00','0.00','0.00','0.00','1800.00']
    empty=client.get('/api/dashboard?month=2026-11').json
    assert empty['income']==empty['expense']==empty['balance']=='0.00'
    assert client.get('/dashboard?month=2026-10').status_code==200

@pytest.mark.parametrize('limit',['0','-1','NaN','Infinity','0.001','10000000000','abc'])
def test_invalid_budgets_not_saved(client,app,limit):
    account(client)
    assert write(client,'/budgets',{'month':'2026-10','limit':limit},'put').status_code==422
    with app.app_context(): assert db.session.scalar(db.select(db.func.count()).select_from(Budget))==0

@pytest.mark.parametrize('month',['2026-13','2026-1','0000-01','bad'])
def test_invalid_month(client,month):
    account(client);assert client.get('/api/dashboard',query_string={'month':month}).status_code==422

def test_year_rollover_trend(client):
    account(client)
    assert [t['month'] for t in client.get('/api/dashboard?month=2026-01').json['trend']]==['2025-08','2025-09','2025-10','2025-11','2025-12','2026-01']

def test_user_text_escaped(client):
    account(client,name='<script>alert(1)</script>')
    page=client.get('/dashboard').text
    assert '<script>alert(1)</script>' not in page
    assert '&lt;script&gt;' in page

@pytest.mark.parametrize('path',['/categories','/budgets','/transactions','/dashboard'])
def test_anonymous_pages_redirect(client,path):
    assert client.get(path).status_code==302


def test_invalid_json_payload(client):
    assert client.post('/register',json=['invalid'],headers={'X-CSRFToken':csrf(client)}).status_code==422

def test_budget_and_category_html_forms(client):
    account(client)
    assert client.post('/categories',data={'csrf_token':csrf(client),'name':'Books'}).status_code==302
    assert 'Books' in client.get('/categories').text
    assert client.post('/budgets',data={'csrf_token':csrf(client),'month':'2026-10','limit':'5000','category_id':''}).status_code==302
    assert '5000.00' in client.get('/budgets?month=2026-10').text

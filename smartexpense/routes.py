from calendar import monthrange
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from functools import wraps
from secrets import token_urlsafe
from zoneinfo import ZoneInfo
import re
import bcrypt
from flask import Blueprint, abort, current_app, flash, g, jsonify, redirect, render_template, request, url_for
from sqlalchemy import func, or_
from sqlalchemy.exc import IntegrityError
from .models import db, User, LoginSession, Category, Transaction, Budget

bp = Blueprint('web', __name__)
IST = ZoneInfo('Asia/Kolkata')

def today():
    return datetime.now(IST).date()

def payload():
    if request.is_json:
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            abort(422)
        return data
    return request.form

def json_request():
    return request.is_json or request.path.startswith('/api/') or request.accept_mimetypes.best == 'application/json'

def error(fields, template=None, **context):
    if json_request() or not template:
        return jsonify(error='VALIDATION_ERROR', fields=fields), 422
    return render_template(template, errors=fields, **context), 422

@bp.before_request
def load_user():
    g.user = None
    g.login_session = None
    token = request.cookies.get('sid')
    if token:
        login = db.session.get(LoginSession, token)
        if login:
            expires = login.expires_at.replace(tzinfo=timezone.utc)
            if expires > datetime.now(timezone.utc):
                g.user = db.session.get(User, login.user_id)
                g.login_session = login

def protected(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not g.user:
            if json_request():
                return jsonify(error='NOT_AUTHENTICATED'), 401
            return redirect(url_for('web.login'))
        return view(*args, **kwargs)
    return wrapped

def categories():
    return db.session.scalars(db.select(Category).where(or_(Category.user_id.is_(None), Category.user_id == g.user.id)).order_by(Category.name)).all()

def visible_category(value):
    try:
        cat = db.session.get(Category, int(value))
    except (TypeError, ValueError):
        abort(404)
    if not cat or cat.user_id not in (None, g.user.id):
        abort(404)
    return cat

def parse_month(value):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}', value):
        raise ValueError('Choose a month in YYYY-MM format.')
    first = date.fromisoformat(value + '-01')
    return first, date(first.year, first.month, monthrange(first.year, first.month)[1])

def money(value):
    try:
        result = Decimal(str(value))
        if not result.is_finite() or result <= 0 or result > Decimal('9999999999.99') or result != result.quantize(Decimal('.01')):
            raise ValueError()
        return result.quantize(Decimal('.01'))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError('Enter a positive amount with at most two decimal places.')

def fmt(value):
    return f'{Decimal(value or 0):.2f}'

def expense_sum(first, last, category_id=None):
    stmt = db.select(func.coalesce(func.sum(Transaction.amount), 0)).where(Transaction.user_id == g.user.id, Transaction.type == 'expense', Transaction.txn_date.between(first, last))
    if category_id is not None:
        stmt = stmt.where(Transaction.category_id == category_id)
    return Decimal(db.session.scalar(stmt))

def dashboard_data(month):
    first, last = parse_month(month)
    income = Decimal(db.session.scalar(db.select(func.coalesce(func.sum(Transaction.amount), 0)).where(Transaction.user_id == g.user.id, Transaction.type == 'income', Transaction.txn_date.between(first, last))))
    spent = expense_sum(first, last)
    breakdown = db.session.execute(db.select(Category.name, func.sum(Transaction.amount)).join(Transaction, Transaction.category_id == Category.id).where(Transaction.user_id == g.user.id, Transaction.type == 'expense', Transaction.txn_date.between(first, last)).group_by(Category.id, Category.name).order_by(Category.name)).all()
    budgets = []
    for b in db.session.scalars(db.select(Budget).where(Budget.user_id == g.user.id, Budget.month == month).order_by(Budget.id)):
        used = spent if b.category_id is None else expense_sum(first, last, b.category_id)
        percent = used * 100 / b.limit
        budgets.append(dict(id=b.id, category_id=b.category_id, name='Monthly budget' if b.category_id is None else db.session.get(Category, b.category_id).name, limit=fmt(b.limit), spent=fmt(used), remaining=fmt(b.limit-used), percent_used=fmt(percent), alert='over' if percent > 100 else 'warning' if percent >= 80 else 'none'))
    trend=[]
    serial = first.year*12 + first.month-1
    for offset in range(5, -1, -1):
        y,m=divmod(serial-offset,12)
        start,end=parse_month(f'{y:04d}-{m+1:02d}')
        trend.append(dict(month=start.strftime('%Y-%m'), expense=fmt(expense_sum(start,end))))
    return dict(month=month, income=fmt(income), expense=fmt(spent), balance=fmt(income-spent), budgets=budgets, categories=[dict(name=n,total=fmt(v)) for n,v in breakdown], trend=trend)

@bp.route('/')
def index():
    return redirect(url_for('web.dashboard' if g.user else 'web.login'))

@bp.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('auth.html', mode='register', errors={})
    data=payload(); name=str(data.get('name','')).strip(); email=str(data.get('email','')).strip().lower(); password=data.get('password','')
    fields={}
    if not name or len(name)>100: fields['name']='Enter a name of 1 to 100 characters.'
    if len(email)>254 or not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+',email): fields['email']='Enter a valid email address.'
    if not isinstance(password,str) or len(password)<8 or len(password.encode('utf-8'))>72: fields['password']='Use at least 8 characters and no more than 72 UTF-8 bytes.'
    if fields: return error(fields,'auth.html',mode='register')
    user=User(name=name,email=email,password_hash=bcrypt.hashpw(password.encode(),bcrypt.gensalt()))
    db.session.add(user)
    try: db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error({'email':'This email already has an account.'},'auth.html',mode='register')
    if json_request(): return jsonify(user={'id':user.id,'name':user.name}),201
    flash('Account created. Please log in.')
    return redirect(url_for('web.login'))

@bp.route('/login', methods=['GET','POST'])
def login():
    if request.method=='GET': return render_template('auth.html',mode='login',errors={})
    data=payload(); email=str(data.get('email','')).strip().lower(); password=data.get('password','')
    user=db.session.scalar(db.select(User).where(User.email==email))
    valid=isinstance(password,str) and len(password.encode('utf-8'))<=72 and user and bcrypt.checkpw(password.encode(),user.password_hash)
    if not valid:
        if json_request(): return jsonify(error='INVALID_CREDENTIALS'),401
        return render_template('auth.html',mode='login',errors={'password':'Invalid email or password.'}),401
    if g.login_session: db.session.delete(g.login_session)
    token=token_urlsafe(32)
    db.session.add(LoginSession(token=token,user_id=user.id,expires_at=datetime.now(timezone.utc)+timedelta(hours=8)))
    db.session.commit()
    response=jsonify(user={'id':user.id,'name':user.name}) if json_request() else redirect(url_for('web.dashboard'))
    response.set_cookie('sid',token,max_age=8*3600,httponly=True,secure=current_app.config['SESSION_COOKIE_SECURE'],samesite='Lax')
    return response

@bp.post('/logout')
@protected
def logout():
    db.session.delete(g.login_session);db.session.commit()
    response=jsonify(ok=True) if json_request() else redirect(url_for('web.login'))
    response.delete_cookie('sid',secure=current_app.config['SESSION_COOKIE_SECURE'],httponly=True,samesite='Lax')
    return response

@bp.get('/dashboard')
@protected
def dashboard():
    try: data=dashboard_data(request.args.get('month',today().strftime('%Y-%m')))
    except ValueError as exc: return error({'month':str(exc)},'message.html',title='Invalid month')
    return render_template('dashboard.html',data=data)

@bp.get('/api/dashboard')
@protected
def dashboard_api():
    try: return jsonify(dashboard_data(request.args.get('month',today().strftime('%Y-%m'))))
    except ValueError as exc: return error({'month':str(exc)})

@bp.route('/categories',methods=['GET','POST'])
@protected
def category_list():
    if request.method=='GET':
        cats=categories()
        if json_request(): return jsonify(categories=[dict(id=c.id,name=c.name,is_default=c.user_id is None) for c in cats])
        return render_template('categories.html',cats=cats,errors={})
    name=str(payload().get('name','')).strip()
    if not name or len(name)>80: return error({'name':'Enter a category name of 1 to 80 characters.'},'categories.html',cats=categories())
    if any(c.name.casefold()==name.casefold() for c in categories()): return error({'name':'Choose a category name that is not already listed.'},'categories.html',cats=categories())
    cat=Category(user_id=g.user.id,name=name);db.session.add(cat)
    try: db.session.commit()
    except IntegrityError:
        db.session.rollback();return error({'name':'This category already exists.'},'categories.html',cats=categories())
    if json_request(): return jsonify(category={'id':cat.id,'name':cat.name}),201
    return redirect(url_for('web.category_list'))

@bp.route('/categories/<int:category_id>',methods=['PUT','POST'])
@protected
def rename_category(category_id):
    cat=visible_category(category_id)
    if cat.user_id is None: abort(403)
    name=str(payload().get('name','')).strip()
    if not name or len(name)>80 or any(c.id!=cat.id and c.name.casefold()==name.casefold() for c in categories()):
        return error({'name':'Use a unique category name of 1 to 80 characters.'},'categories.html',cats=categories())
    cat.name=name
    try: db.session.commit()
    except IntegrityError:
        db.session.rollback();return error({'name':'This category already exists.'},'categories.html',cats=categories())
    if json_request(): return jsonify(category={'id':cat.id,'name':cat.name})
    return redirect(url_for('web.category_list'))

@bp.route('/budgets',methods=['GET','PUT','POST'])
@protected
def budget_list():
    if request.method=='GET':
        month=request.args.get('month',today().strftime('%Y-%m'))
        try: data=dashboard_data(month)
        except ValueError as exc: return error({'month':str(exc)},'message.html',title='Invalid month')
        if json_request(): return jsonify(month=month,budgets=data['budgets'])
        return render_template('budgets.html',data=data,cats=categories(),errors={})
    data=payload();fields={};month=data.get('month','')
    try: parse_month(month)
    except (ValueError,TypeError): fields['month']='Choose a valid month.'
    try: limit=money(data.get('limit'))
    except ValueError as exc: fields['limit']=str(exc)
    raw_category=data.get('category_id');category_id=None
    if raw_category not in (None,''): category_id=visible_category(raw_category).id
    if fields:
        safe_month=today().strftime('%Y-%m')
        return error(fields,'budgets.html',data=dashboard_data(safe_month),cats=categories())
    budget=db.session.scalar(db.select(Budget).where(Budget.user_id==g.user.id,Budget.month==month,Budget.category_id==category_id))
    if budget: budget.limit=limit
    else:
        budget=Budget(user_id=g.user.id,month=month,category_id=category_id,limit=limit);db.session.add(budget)
    try: db.session.commit()
    except IntegrityError:
        db.session.rollback();return error({'limit':'The budget changed in another request. Please retry.'})
    if json_request(): return jsonify(budget=dict(id=budget.id,month=month,category_id=category_id,limit=fmt(limit)))
    return redirect(url_for('web.budget_list',month=month))

@bp.get('/transactions')
@protected
def transaction_list():
    # Read-only integration view. Teammate adds CRUD, filters and sorting (F-005–010).
    rows=db.session.scalars(db.select(Transaction).where(Transaction.user_id==g.user.id).order_by(Transaction.txn_date.desc(),Transaction.id.desc()).limit(50)).all()
    return render_template('transactions.html',rows=rows)

@bp.get('/transactions/<int:transaction_id>')
@protected
def transaction_detail(transaction_id):
    txn=db.session.scalar(db.select(Transaction).where(Transaction.id==transaction_id,Transaction.user_id==g.user.id))
    if not txn: abort(404)
    return jsonify(transaction=dict(id=txn.id,type=txn.type,amount=fmt(txn.amount),date=txn.txn_date.isoformat(),category_id=txn.category_id,payment_mode=txn.payment_mode,source=txn.source,note=txn.note))

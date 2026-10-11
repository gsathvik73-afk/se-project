from calendar import monthrange
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from functools import wraps
from secrets import token_urlsafe
from zoneinfo import ZoneInfo
import re
import csv
import io
import math
import bcrypt
from flask import Blueprint, abort, current_app, flash, g, jsonify, redirect, render_template, request, url_for, Response
from sqlalchemy import func, or_, update, case
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
    now = datetime.now(timezone.utc)
    if user and user.locked_until and user.locked_until.replace(tzinfo=timezone.utc) > now:
        remaining = math.ceil((user.locked_until.replace(tzinfo=timezone.utc) - now).total_seconds())
        response = jsonify(error='ACCOUNT_LOCKED', retry_after=remaining) if json_request() else render_template('auth.html', mode='login', errors={'password': f'Too many failed attempts. Try again in {remaining} seconds.'})
        return response, 429, {'Retry-After': str(remaining)}
    # After lockout expiry, start a new consecutive-failure window.
    if user and user.locked_until:
        user.failed_attempts = 0
        user.locked_until = None
        db.session.commit()
    valid = isinstance(password, str) and len(password.encode('utf-8')) <= 72 and user and bcrypt.checkpw(password.encode(), user.password_hash)
    if not valid:
        if user:
            # Atomic increment prevents simultaneous failures losing updates.
            db.session.execute(update(User).where(User.id == user.id).values(
                failed_attempts=User.failed_attempts + 1,
                locked_until=case((User.failed_attempts >= 4, now + timedelta(minutes=5)), else_=User.locked_until),
            ))
            db.session.commit()
        if json_request():
            return jsonify(error='INVALID_CREDENTIALS'), 401
        return render_template('auth.html', mode='login', errors={'password': 'Invalid email or password.'}), 401
    user.failed_attempts = 0
    user.locked_until = None
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


PAYMENT_MODES = ('Cash', 'UPI', 'Card', 'Net Banking', 'Other')

def owned_transaction(transaction_id):
    txn = db.session.scalar(db.select(Transaction).where(Transaction.id == transaction_id, Transaction.user_id == g.user.id))
    if not txn:
        abort(404)
    return txn

def transaction_json(txn):
    return dict(id=txn.id, type=txn.type, amount=fmt(txn.amount), date=txn.txn_date.isoformat(), category_id=txn.category_id, payment_mode=txn.payment_mode, source=txn.source, note=txn.note)

def transaction_fields(data, existing=None):
    fields = {}
    values = {}
    kind = data.get('type', existing.type if existing else 'expense')
    if kind not in ('expense', 'income'):
        fields['type'] = 'Choose expense or income.'
    values['type'] = kind
    try:
        values['amount'] = money(data.get('amount', existing.amount if existing else None))
    except ValueError as exc:
        fields['amount'] = str(exc)
    try:
        raw = data.get('date', existing.txn_date.isoformat() if existing else '')
        if not isinstance(raw, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', raw):
            raise ValueError()
        values['txn_date'] = date.fromisoformat(raw)
        if values['txn_date'] > today():
            raise ValueError()
    except (ValueError, TypeError):
        fields['date'] = 'Choose today or an earlier date.'
    note = data.get('note', existing.note if existing else '') or ''
    if not isinstance(note, str) or len(note) > 2000:
        fields['note'] = 'Use a note of at most 2,000 characters.'
    values['note'] = note
    values.update(category_id=None, payment_mode=None, source=None)
    if kind == 'expense':
        category_id = data.get('category_id', existing.category_id if existing else None)
        if category_id in (None, ''):
            fields['category_id'] = 'Choose a category.'
        else:
            values['category_id'] = visible_category(category_id).id
        mode = data.get('payment_mode', existing.payment_mode if existing else 'Cash')
        if mode not in PAYMENT_MODES:
            fields['payment_mode'] = 'Choose a listed payment mode.'
        values['payment_mode'] = mode
    if kind == 'income':
        source = data.get('source', existing.source if existing else '')
        if not isinstance(source, str) or not source.strip() or len(source.strip()) > 100:
            fields['source'] = 'Enter an income source of 1 to 100 characters.'
        else:
            values['source'] = source.strip()
    return values, fields

def form_context(txn=None, values=None):
    cats = categories()
    preferences = request.cookies
    default_category = next((c.id for c in cats if c.name == 'Food'), cats[0].id if cats else '')
    # Preferences are UI defaults only, and are revalidated against ownership on save.
    try:
        previous = int(preferences.get('last_category', default_category))
        if previous in [c.id for c in cats]:
            default_category = previous
    except (TypeError, ValueError):
        pass
    defaults = transaction_json(txn) if txn else dict(type='expense', date=today().isoformat(), category_id=default_category, payment_mode=preferences.get('last_payment', 'Cash'), amount='', note='', source='')
    defaults.update(values or {})
    return dict(values=defaults, cats=cats, modes=PAYMENT_MODES, txn=txn)

@bp.get('/transactions/new')
@protected
def new_transaction():
    return render_template('transaction_form.html', errors={}, **form_context(values={'type': request.args.get('type', 'expense')}))

@bp.route('/transactions', methods=['GET', 'POST'])
@protected
def transaction_list():
    if request.method == 'POST':
        data = payload()
        values, fields = transaction_fields(data)
        if fields:
            return error(fields, 'transaction_form.html', **form_context(values=dict(data)))
        txn = Transaction(user_id=g.user.id, **values)
        db.session.add(txn)
        db.session.commit()
        if json_request():
            return jsonify(transaction=transaction_json(txn), alerts=dashboard_data(txn.txn_date.strftime('%Y-%m'))['budgets']), 201
        response = redirect(url_for('web.transaction_list'))
        if txn.type == 'expense':
            response.set_cookie('last_category', str(txn.category_id), samesite='Lax', secure=current_app.config['SESSION_COOKIE_SECURE'])
            response.set_cookie('last_payment', txn.payment_mode, samesite='Lax', secure=current_app.config['SESSION_COOKIE_SECURE'])
        flash('Transaction saved.')
        return response
    try:
        stmt, filters = filtered_transactions(request.args)
        page = int(request.args.get('page', '1'))
        if page < 1:
            raise ValueError('Choose a positive page number.')
    except (ValueError, TypeError) as exc:
        return error({'filters': str(exc)}, 'message.html', title='Check transaction filters')
    # Aggregate the filtered subquery rather than only the current page.
    sub = stmt.order_by(None).subquery()
    total, count = db.session.execute(db.select(func.coalesce(func.sum(sub.c.amount), 0), func.count()).select_from(sub)).one()
    rows = db.session.scalars(stmt.offset((page - 1) * 50).limit(50)).all()
    names = {c.id: c.name for c in categories()}
    if json_request():
        return jsonify(transactions=[transaction_json(t) for t in rows], total=fmt(total), count=count, page=page)
    return render_template('transactions.html', rows=rows, names=names, cats=categories(), filters=filters, total=fmt(total), count=count, page=page, pages=max(1, math.ceil(count / 50)))

def filtered_transactions(args):
    stmt = db.select(Transaction).where(Transaction.user_id == g.user.id)
    filters = {k: args.get(k, '') for k in ('from', 'to', 'category_id', 'min', 'max')}
    boundaries = {}
    for key in ('from', 'to'):
        if filters[key]:
            try:
                if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', filters[key]):
                    raise ValueError()
                boundaries[key] = date.fromisoformat(filters[key])
            except (ValueError, TypeError):
                raise ValueError('Use valid YYYY-MM-DD dates.')
    if 'from' in boundaries and 'to' in boundaries and boundaries['from'] > boundaries['to']:
        raise ValueError('The start date must be on or before the end date.')
    if 'from' in boundaries:
        stmt = stmt.where(Transaction.txn_date >= boundaries['from'])
    if 'to' in boundaries:
        stmt = stmt.where(Transaction.txn_date <= boundaries['to'])
    if filters['category_id']:
        stmt = stmt.where(Transaction.category_id == visible_category(filters['category_id']).id)
    amounts = {}
    for key in ('min', 'max'):
        if filters[key]:
            try:
                value = Decimal(filters[key])
                if not value.is_finite() or value < 0 or value > Decimal('9999999999.99') or value != value.quantize(Decimal('.01')):
                    raise ValueError()
                amounts[key] = value
            except (InvalidOperation, ValueError, TypeError):
                raise ValueError('Use nonnegative amounts with at most two decimal places.')
    if 'min' in amounts and 'max' in amounts and amounts['min'] > amounts['max']:
        raise ValueError('Minimum amount must not exceed maximum amount.')
    if 'min' in amounts:
        stmt = stmt.where(Transaction.amount >= amounts['min'])
    if 'max' in amounts:
        stmt = stmt.where(Transaction.amount <= amounts['max'])
    sort = args.get('sort', 'date')
    order = args.get('order', 'desc')
    if sort not in ('date', 'amount') or order not in ('asc', 'desc'):
        raise ValueError('Choose date or amount and ascending or descending order.')
    column = Transaction.txn_date if sort == 'date' else Transaction.amount
    stmt = stmt.order_by(column.asc() if order == 'asc' else column.desc(), Transaction.id.asc() if order == 'asc' else Transaction.id.desc())
    filters.update(sort=sort, order=order)
    return stmt, filters

@bp.get('/transactions/<int:transaction_id>')
@protected
def transaction_detail(transaction_id):
    return jsonify(transaction=transaction_json(owned_transaction(transaction_id)))

@bp.get('/transactions/<int:transaction_id>/edit')
@protected
def edit_transaction_form(transaction_id):
    return render_template('transaction_form.html', errors={}, **form_context(owned_transaction(transaction_id)))

@bp.route('/transactions/<int:transaction_id>', methods=['PUT', 'POST'])
@protected
def edit_transaction(transaction_id):
    txn = owned_transaction(transaction_id)
    data = payload()
    values, fields = transaction_fields(data, txn)
    if fields:
        return error(fields, 'transaction_form.html', **form_context(txn, dict(data)))
    for key, value in values.items():
        setattr(txn, key, value)
    db.session.commit()
    if json_request():
        return jsonify(transaction=transaction_json(txn))
    flash('Transaction updated.')
    return redirect(url_for('web.transaction_list'))

@bp.get('/transactions/<int:transaction_id>/delete')
@protected
def confirm_delete(transaction_id):
    return render_template('confirm_delete.html', txn=owned_transaction(transaction_id))

@bp.route('/transactions/<int:transaction_id>/delete', methods=['POST'])
@bp.route('/transactions/<int:transaction_id>', methods=['DELETE'])
@protected
def delete_transaction(transaction_id):
    txn = owned_transaction(transaction_id)
    if payload().get('confirm') not in (True, 'yes'):
        if json_request():
            return jsonify(error='CONFIRMATION_REQUIRED'), 422
        return redirect(url_for('web.transaction_list'))
    db.session.delete(txn)
    db.session.commit()
    if json_request():
        return jsonify(ok=True)
    flash('Transaction deleted.')
    return redirect(url_for('web.transaction_list'))

@bp.get('/transactions/export.csv')
@protected
def export_csv():
    try:
        stmt, _ = filtered_transactions(request.args)
    except (ValueError, TypeError) as exc:
        return error({'filters': str(exc)})
    # Same filters/order/owner scope as the list, across every matching page.
    names = {c.id: c.name for c in categories()}
    rows = db.session.scalars(stmt).all()
    output = io.StringIO(newline='')
    writer = csv.writer(output)
    writer.writerow(('date', 'type', 'category', 'amount', 'payment_mode', 'source', 'note'))
    def safe_cell(value):
        value = str(value or '')
        return "'" + value if value.lstrip().startswith(('=', '+', '-', '@')) or value.startswith(('\t', '\r', '\n')) else value
    for txn in rows:
        writer.writerow((txn.txn_date.isoformat(), txn.type, safe_cell(names.get(txn.category_id, '')), fmt(txn.amount), safe_cell(txn.payment_mode), safe_cell(txn.source), safe_cell(txn.note)))
    return Response(output.getvalue(), content_type='text/csv; charset=utf-8', headers={'Content-Disposition': 'attachment; filename="transactions.csv"'})

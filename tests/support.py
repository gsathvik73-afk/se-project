"""Shared helpers for the TC-RPT / TC-PERF / TC-REL / TC-UX / TC-PORT / TC-SEC tests."""
import re
from datetime import date
from decimal import Decimal

import pytest

from smartexpense import create_app
from smartexpense.models import db, User, Category, Transaction

PASSWORD = 'Zx9!unique-pass'


def make_app(tmp_path, **config):
    cfg = {
        'TESTING': True,
        'SECRET_KEY': 'test-only-secret',
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{tmp_path}/test.db',
    }
    cfg.update(config)
    app = create_app(cfg)
    with app.app_context():
        app.test_cli_runner().invoke(args=['init-db'])
    return app


@pytest.fixture
def app(tmp_path):
    return make_app(tmp_path)


@pytest.fixture
def client(app):
    return app.test_client()


def csrf(client):
    page = client.get('/login').text
    return re.search(r'name="csrf_token" value="([^"]+)"', page)[1]


def write(client, path, body, method='post'):
    return getattr(client, method)(path, json=body, headers={'X-CSRFToken': csrf(client)})


def account(client, email='a@example.com', name='A', password=PASSWORD):
    assert write(client, '/register', {'name': name, 'email': email, 'password': password}).status_code == 201
    assert write(client, '/login', {'email': email, 'password': password}).status_code == 200


def user_id(app, email):
    with app.app_context():
        return db.session.scalar(db.select(User).where(User.email == email)).id


def category_id(app, name):
    with app.app_context():
        return db.session.scalar(db.select(Category).where(Category.name == name, Category.user_id.is_(None))).id


def add_transaction(app, email, **fields):
    """Insert a transaction straight into the database (the add-transaction route is another teammate's work)."""
    uid = user_id(app, email)
    fields.setdefault('type', 'expense')
    fields.setdefault('amount', Decimal('100'))
    fields.setdefault('txn_date', date(2026, 10, 8))
    if fields['type'] == 'expense':
        fields.setdefault('category_id', category_id(app, 'Food'))
        fields.setdefault('payment_mode', 'UPI')
    else:
        fields.setdefault('source', 'Salary')
    with app.app_context():
        txn = Transaction(user_id=uid, **fields)
        db.session.add(txn)
        db.session.commit()
        return txn.id

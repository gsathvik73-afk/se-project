"""Security tests: TC-SEC-01 to TC-SEC-05 (SEB-SR-001 to SEB-SR-005).

Tests marked xfail check behaviour the SAD requires but the app does not have yet.
They turn into XPASS when the feature is added; remove the marker then.
"""
import http.client
import os
import re
import ssl
from pathlib import Path
from urllib.parse import urlparse

import pytest

from smartexpense.models import db, User, Category, Budget, Transaction
from support import (PASSWORD, account, add_transaction, app, category_id, client, csrf,  # noqa: F401
                     make_app, user_id, write)

SRC = Path(__file__).resolve().parent.parent / 'smartexpense'
DEPLOYED = os.environ.get('SEB_DEPLOYED_URL', '').rstrip('/')


# ---------------------------------------------------------------- TC-SEC-01
def test_sec01_session_cookie_flags(tmp_path):
    app = make_app(tmp_path, SESSION_COOKIE_SECURE=True)
    c = app.test_client()
    write(c, '/register', {'name': 'A', 'email': 'a@example.com', 'password': PASSWORD})
    cookies = write(c, '/login', {'email': 'a@example.com', 'password': PASSWORD}).headers.getlist('Set-Cookie')
    sid = next(x for x in cookies if x.startswith('sid='))
    assert 'HttpOnly' in sid and 'Secure' in sid and 'SameSite=Lax' in sid


def test_sec01_no_external_resources(client):
    """No page loads scripts, styles or images from another origin (no mixed content)."""
    account(client)
    for path in ('/login', '/register', '/dashboard', '/transactions', '/budgets', '/categories'):
        page = client.get(path).text
        assert not re.search(r'(?:src|href)="https?://', page), path


@pytest.mark.xfail(strict=False, reason='SAD 3.9 asks for HSTS and CSP headers; not added yet')
def test_sec01_security_headers(client):
    headers = client.get('/login').headers
    assert 'Strict-Transport-Security' in headers
    assert 'Content-Security-Policy' in headers


@pytest.mark.skipif(not DEPLOYED.startswith('https://'),
                    reason='set SEB_DEPLOYED_URL=https://your-host to run the deployed HTTPS checks')
def test_sec01_deployed_http_redirects_to_https():
    host = urlparse(DEPLOYED).hostname
    conn = http.client.HTTPConnection(host, timeout=10)
    conn.request('GET', '/login')
    resp = conn.getresponse()
    assert resp.status in (301, 302, 307, 308)
    assert resp.getheader('Location', '').startswith('https://')


@pytest.mark.skipif(not DEPLOYED.startswith('https://'),
                    reason='set SEB_DEPLOYED_URL=https://your-host to run the deployed HTTPS checks')
def test_sec01_deployed_tls12_ok_and_valid_certificate():
    host = urlparse(DEPLOYED).hostname
    ctx = ssl.create_default_context()          # verifies certificate and host name
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    with ctx.wrap_socket(__import__('socket').create_connection((host, 443), timeout=10), server_hostname=host) as s:
        assert s.version() in ('TLSv1.2', 'TLSv1.3')


# ---------------------------------------------------------------- TC-SEC-02
def test_sec02_hashes_are_salted_and_passwords_never_stored(app, tmp_path, caplog):
    caplog.set_level('DEBUG')
    a, b = app.test_client(), app.test_client()
    account(a, 'a@example.com', 'A')
    account(b, 'b@example.com', 'B')                      # same password as A
    write(a, '/login', {'email': 'a@example.com', 'password': 'wrong-password'})   # a failed login too
    with app.app_context():
        hashes = [u.password_hash for u in db.session.scalars(db.select(User).order_by(User.id))]
    assert len(hashes) == 2 and hashes[0] != hashes[1]
    assert all(h.startswith(b'$2b$') and len(h) == 60 for h in hashes)     # bcrypt, per-user salt
    assert all(PASSWORD.encode() not in h for h in hashes)
    assert PASSWORD.encode() not in (tmp_path / 'test.db').read_bytes()   # not anywhere in the database file
    for secret in (PASSWORD, 'wrong-password', hashes[0].decode()):
        assert secret not in caplog.text                                   # not in logs


def test_sec02_responses_never_contain_hash(client):
    account(client)
    for path in ('/dashboard', '/transactions', '/categories', '/budgets'):
        assert '$2b$' not in client.get(path).text


def test_sec02_correct_password_accepted_wrong_rejected(client):
    account(client)
    other = client.application.test_client()
    assert write(other, '/login', {'email': 'a@example.com', 'password': 'not-it-at-all'}).status_code == 401
    assert write(other, '/login', {'email': 'a@example.com', 'password': PASSWORD}).status_code == 200


# ---------------------------------------------------------------- TC-SEC-03
@pytest.fixture
def two_users(app):
    a, b = app.test_client(), app.test_client()
    account(a, 'a@example.com', 'A')
    account(b, 'b@example.com', 'B')
    b_cat = write(b, '/categories', {'name': 'B private'}).json['category']['id']
    b_txn = add_transaction(app, 'b@example.com', note='B secret note', category_id=b_cat)
    write(b, '/budgets', {'month': '2026-10', 'limit': '777', 'category_id': b_cat}, 'put')
    return app, a, b, b_cat, b_txn


def test_sec03_foreign_transaction_is_404_and_looks_like_missing(two_users):
    _, a, _, _, b_txn = two_users
    foreign = a.get(f'/transactions/{b_txn}')
    missing = a.get('/transactions/999999')
    assert foreign.status_code == missing.status_code == 404
    assert foreign.data == missing.data                      # IDs cannot be probed
    assert 'B secret note' not in a.get('/transactions').text


def test_sec03_foreign_category_cannot_be_renamed(two_users):
    app, a, b, b_cat, _ = two_users
    assert write(a, f'/categories/{b_cat}', {'name': 'Stolen'}, 'put').status_code == 404
    names = [c['name'] for c in b.get('/categories', headers={'Accept': 'application/json'}).json['categories']]
    assert 'B private' in names and 'Stolen' not in names


def test_sec03_default_category_cannot_be_renamed(two_users):
    app, a, *_ = two_users
    assert write(a, f"/categories/{category_id(app, 'Food')}", {'name': 'Changed'}, 'put').status_code in (403, 404)
    with app.app_context():
        assert db.session.scalar(db.select(Category).where(Category.name == 'Food')) is not None


def test_sec03_foreign_category_cannot_be_used_for_a_budget(two_users):
    app, a, _, b_cat, _ = two_users
    assert write(a, '/budgets', {'month': '2026-10', 'limit': '5000', 'category_id': b_cat}, 'put').status_code == 404
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(Budget).where(Budget.user_id == user_id(app, 'a@example.com'))) == 0
    assert a.get('/api/dashboard?month=2026-10').json['budgets'] == []     # B's 777 budget is not visible to A


def test_sec03_anonymous_gets_no_data(app, two_users):
    _, _, _, _, b_txn = two_users
    anon = app.test_client()
    resp = anon.get(f'/transactions/{b_txn}', headers={'Accept': 'application/json'})
    assert resp.status_code == 401 and b'B secret note' not in resp.data
    assert anon.get('/transactions').status_code == 302


@pytest.mark.xfail(strict=False, reason='transaction edit/delete/add routes (SEB-F-005, 008, 009) not implemented yet')
@pytest.mark.parametrize('method,body', [('put', {'amount': '1.00'}), ('delete', None)])
def test_sec03_foreign_transaction_cannot_be_changed(two_users, method, body):
    app, a, _, _, b_txn = two_users
    resp = write(a, f'/transactions/{b_txn}', body, method) if body else a.delete(f'/transactions/{b_txn}', headers={'X-CSRFToken': csrf(a)})
    assert resp.status_code == 404
    with app.app_context():
        assert db.session.get(Transaction, b_txn).amount == 100


@pytest.mark.xfail(strict=False, reason='POST /transactions (SEB-F-005) not implemented yet')
def test_sec03_foreign_category_cannot_be_used_on_new_expense(two_users):
    _, a, _, b_cat, _ = two_users
    body = {'type': 'expense', 'amount': '10.00', 'date': '2026-10-08', 'category_id': b_cat, 'payment_mode': 'UPI'}
    assert write(a, '/transactions', body).status_code == 404


# ---------------------------------------------------------------- TC-SEC-04
SQLI_EMAILS = ["' OR '1'='1' --", "admin'--", "a@example.com' OR '1'='1"]



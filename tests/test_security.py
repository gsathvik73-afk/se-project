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


@pytest.mark.parametrize('method,body', [('put', {'amount': '1.00'}), ('delete', None)])
def test_sec03_foreign_transaction_cannot_be_changed(two_users, method, body):
    app, a, _, _, b_txn = two_users
    resp = write(a, f'/transactions/{b_txn}', body, method) if body else a.delete(f'/transactions/{b_txn}', headers={'X-CSRFToken': csrf(a)})
    assert resp.status_code == 404
    with app.app_context():
        assert db.session.get(Transaction, b_txn).amount == 100


def test_sec03_foreign_category_cannot_be_used_on_new_expense(two_users):
    _, a, _, b_cat, _ = two_users
    body = {'type': 'expense', 'amount': '10.00', 'date': '2026-10-08', 'category_id': b_cat, 'payment_mode': 'UPI'}
    assert write(a, '/transactions', body).status_code == 404


# ---------------------------------------------------------------- TC-SEC-04
SQLI_EMAILS = ["' OR '1'='1' --", "admin'--", "a@example.com' OR '1'='1"]


@pytest.mark.parametrize('email', SQLI_EMAILS)
def test_sec04_sql_injection_cannot_bypass_login(client, email):
    account(client, 'victim@example.com', 'Victim')
    attacker = client.application.test_client()
    resp = write(attacker, '/login', {'email': email, 'password': "' OR '1'='1"})
    assert resp.status_code == 401
    assert attacker.get_cookie('sid') is None
    assert attacker.get('/dashboard').status_code == 302


def test_sec04_sql_text_is_stored_as_plain_text_and_tables_survive(client, app):
    account(client)
    evil = "Robert'); DROP TABLE category;--"
    assert write(client, '/categories', {'name': evil}).status_code == 201
    cats = client.get('/categories', headers={'Accept': 'application/json'}).json['categories']
    assert evil in [c['name'] for c in cats] and len(cats) == 9
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(Category)) == 9


def test_sec04_sql_in_ids_and_filters_is_rejected(client, app):
    account(client)
    other = app.test_client()
    account(other, 'b@example.com', 'B')
    add_transaction(app, 'b@example.com', note='B only')
    assert write(client, '/budgets', {'month': '2026-10', 'limit': '10', 'category_id': '1 OR 1=1'}, 'put').status_code == 404
    assert client.get('/api/dashboard', query_string={'month': "2026-10' OR '1'='1"}).status_code == 422
    assert client.get('/transactions/1 OR 1=1').status_code == 404
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(Budget)) == 0


XSS = ['<script>alert(\'xss\')</script>', '<img src=x onerror=alert(1)>']


@pytest.mark.parametrize('payload', XSS)
def test_sec04_stored_xss_is_escaped_everywhere(client, app, payload):
    account(client)
    cat = write(client, '/categories', {'name': payload}).json['category']['id']
    write(client, '/budgets', {'month': '2026-10', 'limit': '1000', 'category_id': cat}, 'put')
    add_transaction(app, 'a@example.com', note=payload, category_id=cat)
    for path in ('/categories', '/budgets?month=2026-10', '/dashboard?month=2026-10', '/transactions'):
        page = client.get(path).text
        assert payload not in page, path
        assert '&lt;' in page, path


def test_sec04_source_has_no_string_built_sql_or_unsafe_output():
    py = '\n'.join(p.read_text(encoding='utf-8') for p in SRC.glob('*.py'))
    assert not re.search(r'execute\(\s*f[\'"]', py)
    assert not re.search(r'execute\([^)]*(%|\+|\.format)', py)
    assert 'Markup(' not in py
    for template in (SRC / 'templates').glob('*.html'):
        assert '|safe' not in template.read_text(encoding='utf-8'), template.name


# ---------------------------------------------------------------- TC-SEC-05
def test_sec05_password_minimum_length_boundary(client):
    short = write(client, '/register', {'name': 'A', 'email': 'a@example.com', 'password': 'Abcd123'})   # 7
    assert short.status_code == 422 and 'at least 8' in short.json['fields']['password']
    assert write(client, '/register', {'name': 'A', 'email': 'a@example.com', 'password': 'Abcd1234'}).status_code == 201   # 8


def test_sec05_failure_counter_resets_after_success(client):
    account(client)
    c = client.application.test_client()
    for _ in range(4):
        assert write(c, '/login', {'email': 'a@example.com', 'password': 'wrong-password'}).status_code == 401
    assert write(c, '/login', {'email': 'a@example.com', 'password': PASSWORD}).status_code == 200


def test_sec05_unknown_email_and_wrong_password_look_the_same(client):
    account(client)
    c = client.application.test_client()
    wrong = write(c, '/login', {'email': 'a@example.com', 'password': 'wrong-password'})
    unknown = write(c, '/login', {'email': 'nobody@example.com', 'password': 'wrong-password'})
    assert wrong.status_code == unknown.status_code == 401 and wrong.json == unknown.json


def test_sec05_login_locked_after_five_failures(client):
    account(client)
    c = client.application.test_client()
    for _ in range(5):
        assert write(c, '/login', {'email': 'a@example.com', 'password': 'wrong-password'}).status_code == 401
    locked = write(c, '/login', {'email': 'a@example.com', 'password': PASSWORD})   # correct password, still blocked
    assert locked.status_code == 429 and 'Retry-After' in locked.headers
    # The 5-minute wait and unlock are checked by hand in TC-SEC-05 steps 6 and 7.


def test_sec05_lockout_survives_restart_and_expires(tmp_path, monkeypatch):
    from datetime import timedelta
    from smartexpense import routes
    from smartexpense.models import LoginGuard
    first = make_app(tmp_path)
    c = first.test_client()
    account(c)
    for _ in range(5):
        assert write(c, '/login', {'email': 'a@example.com', 'password': 'wrong'}).status_code == 401
    restarted = make_app(tmp_path)
    c2 = restarted.test_client()
    locked = write(c2, '/login', {'email': 'a@example.com', 'password': PASSWORD})
    assert locked.status_code == 429 and 0 < int(locked.headers['Retry-After']) <= 300
    after_lockout = routes.utcnow() + timedelta(seconds=301)
    monkeypatch.setattr(routes, 'utcnow', lambda: after_lockout)
    assert write(c2, '/login', {'email': 'a@example.com', 'password': PASSWORD}).status_code == 200
    with restarted.app_context():
        guard = db.session.get(LoginGuard, user_id(restarted, 'a@example.com'))
        assert guard.failures == 0 and guard.locked_until is None

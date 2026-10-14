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

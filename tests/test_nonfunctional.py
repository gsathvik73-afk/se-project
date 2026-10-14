"""Non-functional tests: TC-PERF-01/02 (SEB-NF-001/002), TC-REL-01 (SEB-NF-003),
TC-UX-01 (SEB-NF-004) and TC-PORT-01 (SEB-NF-005).

UX-01 (five first-time users, click counts) and the real-browser part of PORT-01
cannot be automated; these tests cover the parts that can.
"""
import re
import time
from collections import Counter
from datetime import date
from decimal import Decimal
from pathlib import Path
from threading import Barrier, Thread

import pytest

from smartexpense.models import db, Budget, Category, Transaction
from support import (PASSWORD, account, add_transaction, app, category_id, client, csrf,  # noqa: F401
                     make_app, user_id, write)

STATIC = Path(__file__).resolve().parent.parent / 'smartexpense' / 'static'


# ---------------------------------------------------------------- TC-PERF-01
def test_perf01_pages_load_within_3_seconds_with_5000_transactions(app, client):
    account(client)
    uid, food = user_id(app, 'a@example.com'), category_id(app, 'Food')
    rows = [dict(user_id=uid, type='expense', amount=Decimal('10.00'), txn_date=date(2026, 10, 1 + i % 28),
                 category_id=food, payment_mode='UPI', note=f'seed {i}') for i in range(5000)]
    with app.app_context():
        db.session.execute(db.insert(Transaction), rows)
        db.session.commit()
        assert db.session.scalar(db.select(db.func.count()).select_from(Transaction)) == 5000

    for path in ('/dashboard?month=2026-10', '/transactions'):
        client.get(path)                                           # warm-up, not counted
        times = []
        for _ in range(100):
            start = time.perf_counter()
            resp = client.get(path)
            times.append(time.perf_counter() - start)
            assert resp.status_code == 200
        fast = sum(t <= 3.0 for t in times)
        assert fast >= 90, f'{path}: only {fast}/100 loads within 3 s (slowest {max(times):.2f}s)'

    # A fast but wrong page must not pass: totals come from the database, the list is capped at 50 rows.
    assert client.get('/api/dashboard?month=2026-10').json['expense'] == '50000.00'
    assert client.get('/transactions').text.count('<tr>') == 51           # header row + 50 records


# ---------------------------------------------------------------- TC-PERF-02
def test_perf02_twenty_concurrent_users_no_errors_no_mixed_data(app):
    users, rounds = 20, 3
    gate = Barrier(users)
    statuses, failures = [], []

    def session(n):
        try:
            c = app.test_client()
            email = f'u{n:02d}@example.com'
            assert write(c, '/register', {'name': f'U{n:02d}', 'email': email, 'password': PASSWORD}).status_code == 201
            gate.wait(timeout=60)                                   # all 20 log in together
            statuses.append(write(c, '/login', {'email': email, 'password': PASSWORD}).status_code)
            for i in range(rounds):
                statuses.append(c.get('/dashboard').status_code)
                statuses.append(c.get('/transactions').status_code)
                statuses.append(write(c, '/categories', {'name': f'U{n:02d}-note-{i}'}).status_code)
        except Exception as exc:                                    # noqa: BLE001
            failures.append(f'user {n}: {exc!r}')

    threads = [Thread(target=session, args=(n,)) for n in range(users)]
    [t.start() for t in threads]
    [t.join(timeout=120) for t in threads]

    assert not failures, failures
    counts = Counter(statuses)
    assert not [s for s in counts if s >= 500], f'server errors: {counts}'
    assert counts[201] == users * rounds and counts[200] >= users * (1 + 2 * rounds)

    for n in range(users):                                          # every save present, nobody sees anyone else's
        c = app.test_client()
        write(c, '/login', {'email': f'u{n:02d}@example.com', 'password': PASSWORD})
        names = [x['name'] for x in c.get('/categories', headers={'Accept': 'application/json'}).json['categories']]
        mine = [x for x in names if re.match(r'U\d\d-note-', x)]
        assert sorted(mine) == [f'U{n:02d}-note-{i}' for i in range(rounds)]


# ---------------------------------------------------------------- TC-REL-01
def test_rel01_saved_data_survives_a_server_restart(tmp_path):
    first = make_app(tmp_path)
    c = first.test_client()
    account(c)
    cat = write(c, '/categories', {'name': 'Books'}).json['category']['id']
    write(c, '/budgets', {'month': '2026-10', 'limit': '5000'}, 'put')
    add_transaction(first, 'a@example.com', amount=Decimal('250'), note='Lunch')
    del first, c

    restarted = make_app(tmp_path)                                  # new app object on the same database file
    c2 = restarted.test_client()
    assert write(c2, '/login', {'email': 'a@example.com', 'password': PASSWORD}).status_code == 200
    data = c2.get('/api/dashboard?month=2026-10').json
    assert data['expense'] == '250.00' and data['budgets'][0]['limit'] == '5000.00'
    names = [x['name'] for x in c2.get('/categories', headers={'Accept': 'application/json'}).json['categories']]
    assert 'Books' in names


def test_rel01_failed_save_leaves_no_partial_record_and_can_be_retried(tmp_path, monkeypatch):
    app = make_app(tmp_path, PROPAGATE_EXCEPTIONS=False)            # return the 500 page instead of raising
    c = app.test_client()
    account(c)

    def fail_after_insert():
        db.session.flush()                                          # row is written inside the transaction ...
        raise RuntimeError('forced failure before commit')          # ... but never committed

    with monkeypatch.context() as m:
        m.setattr(db.session, 'commit', fail_after_insert)
        resp = write(c, '/budgets', {'month': '2026-10', 'limit': '5000'}, 'put')
    assert resp.status_code == 500
    assert 'Traceback' not in resp.text and 'forced failure' not in resp.text     # no stack trace shown

    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(Budget)) == 0   # nothing half-saved

    assert write(c, '/budgets', {'month': '2026-10', 'limit': '5000'}, 'put').status_code == 200   # retry works
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(Budget)) == 1


@pytest.mark.xfail(strict=False, reason='SAD 4.4 friendly 500 message and request reference not implemented yet')
def test_rel01_failed_save_shows_friendly_message(tmp_path, monkeypatch):
    app = make_app(tmp_path, PROPAGATE_EXCEPTIONS=False)
    c = app.test_client()
    account(c)
    monkeypatch.setattr(db.session, 'commit', lambda: (_ for _ in ()).throw(RuntimeError('boom')))
    resp = write(c, '/budgets', {'month': '2026-10', 'limit': '5000'}, 'put')
    assert 'Your data was not saved' in resp.text


# ---------------------------------------------------------------- TC-UX-01

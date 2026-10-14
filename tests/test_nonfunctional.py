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

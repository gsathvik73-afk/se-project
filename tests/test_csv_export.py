"""TC-RPT-01: filtered CSV export (SEB-F-017).

The export route does not exist yet (the reporting developer is building it), so every test here
is marked xfail. Once GET /transactions/export.csv is added they start to run for real:
an XPASS means the feature meets the SAD contract (section 4.3); remove the marker then.
Contract: same filters as the list (from, to, category_id, min, max, sort), owner only,
header row date,type,category,amount,payment_mode,source,note, UTF-8, formula cells neutralised.
"""
import csv
import io
from datetime import date
from decimal import Decimal

import pytest

from support import PASSWORD, account, add_transaction, app, category_id, client, write  # noqa: F401

pytestmark = pytest.mark.xfail(strict=False, reason='SEB-F-017 CSV export route is not implemented yet')

URL = '/transactions/export.csv'
HEADER = ['date', 'type', 'category', 'amount', 'payment_mode', 'source', 'note']


def parse(resp):
    return list(csv.reader(io.StringIO(resp.data.decode('utf-8'))))


@pytest.fixture
def data(app, client):
    account(client)
    other = app.test_client()
    account(other, 'b@example.com', 'B')
    food, travel = category_id(app, 'Food'), category_id(app, 'Travel')
    add_transaction(app, 'a@example.com', amount=Decimal('500'), txn_date=date(2026, 10, 8), category_id=food, note='Lunch')
    add_transaction(app, 'a@example.com', amount=Decimal('250'), txn_date=date(2026, 10, 9), category_id=food, note='Dinner, with "friends"')
    add_transaction(app, 'a@example.com', amount=Decimal('50'), txn_date=date(2026, 10, 10), category_id=food, note='Tea')       # below min
    add_transaction(app, 'a@example.com', amount=Decimal('300'), txn_date=date(2026, 10, 11), category_id=travel, note='Bus')    # other category
    add_transaction(app, 'a@example.com', amount=Decimal('400'), txn_date=date(2026, 9, 5), category_id=food, note='Old')        # other month
    add_transaction(app, 'a@example.com', amount=Decimal('120'), txn_date=date(2026, 10, 12), category_id=food, note='=SUM(1+1)')
    add_transaction(app, 'a@example.com', amount=Decimal('130'), txn_date=date(2026, 10, 13), category_id=food, note='caf\u00e9 \u20b9')
    add_transaction(app, 'b@example.com', amount=Decimal('999'), txn_date=date(2026, 10, 8), category_id=food, note='B private')
    return client


FILTER = {'from': '2026-10-01', 'to': '2026-10-31', 'category_id': None, 'min': '100', 'sort': 'amount_desc'}


def filtered(client, app_):
    return client.get(URL, query_string={**FILTER, 'category_id': category_id(app_, 'Food')})


def test_rpt01_download_headers(data, app):
    resp = filtered(data, app)
    assert resp.status_code == 200
    assert resp.headers['Content-Type'].lower().startswith('text/csv') and 'utf-8' in resp.headers['Content-Type'].lower()
    assert 'attachment' in resp.headers['Content-Disposition']


def test_rpt01_header_row_and_rows_match_the_filter(data, app):
    rows = parse(filtered(data, app))
    assert rows[0] == HEADER
    notes = [r[6] for r in rows[1:]]
    assert sorted(notes) == sorted(['Lunch', 'Dinner, with "friends"', "'=SUM(1+1)", 'caf\u00e9 \u20b9'])
    assert sum(Decimal(r[3]) for r in rows[1:]) == Decimal('1000.00')
    assert [Decimal(r[3]) for r in rows[1:]] == sorted((Decimal(r[3]) for r in rows[1:]), reverse=True)   # sorted as asked


def test_rpt01_other_users_rows_never_exported(data, app):
    resp = data.get(URL)
    assert resp.status_code == 200
    assert 'B private' not in resp.data.decode('utf-8')


def test_rpt01_formula_cells_are_neutralised(data, app):
    notes = [r[6] for r in parse(data.get(URL, query_string={'from': '2026-10-01', 'to': '2026-10-31'}))[1:]]
    assert "'=SUM(1+1)" in notes and '=SUM(1+1)' not in notes


def test_rpt01_no_matches_gives_header_only(data):
    rows = parse(data.get(URL, query_string={'from': '2030-01-01', 'to': '2030-01-31'}))
    assert rows == [HEADER]


def test_rpt01_from_after_to_is_rejected(data):
    assert data.get(URL, query_string={'from': '2026-10-31', 'to': '2026-10-01'}).status_code == 422


def test_rpt01_anonymous_cannot_export(app):
    assert app.test_client().get(URL, headers={'Accept': 'application/json'}).status_code in (401, 302)

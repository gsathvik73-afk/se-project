"""TC-EXP-01–06 and integrated category, budget and owner checks."""
from datetime import timedelta
from decimal import Decimal

import pytest

from smartexpense.routes import today
from smartexpense.models import db, Transaction
from support import account, app, category_id, client, csrf, write  # noqa: F401


def expense(app, **changes):
    return dict(type='expense', amount='250.00', date=today().isoformat(),
                category_id=category_id(app, 'Food'), payment_mode='UPI', **changes)


def test_expense_income_edits_deletion_recalculate_dashboard(app, client):
    account(client)
    month = today().strftime('%Y-%m')
    write(client, '/budgets', {'month': month, 'limit': '200'}, 'put')
    txn = write(client, '/transactions', expense(app)).json['transaction']
    income = write(client, '/transactions', {'type': 'income', 'amount': '2000',
                                          'date': today().isoformat(), 'source': 'Freelance'})
    assert income.status_code == 201
    data = client.get('/api/dashboard', query_string={'month': month}).json
    assert (data['income'], data['expense'], data['balance']) == ('2000.00', '250.00', '1750.00')
    assert data['budgets'][0]['alert'] == 'over'
    assert write(client, '/transactions', expense(app)).status_code == 201  # alerts permit writes
    assert write(client, f"/transactions/{txn['id']}", {'amount': '600'}, 'put').status_code == 200
    assert client.get('/api/dashboard', query_string={'month': month}).json['expense'] == '850.00'
    assert client.get(f"/transactions/{txn['id']}/edit").status_code == 200
    assert write(client, f"/transactions/{txn['id']}", {}, 'delete').status_code == 200
    assert client.get(f"/transactions/{txn['id']}").status_code == 404
    assert client.get('/api/dashboard', query_string={'month': month}).json['expense'] == '250.00'


@pytest.mark.parametrize('amount', ['0', '-1', '', 'abc', 'NaN', 'Infinity', '0.001', '10000000000'])
def test_invalid_amount_never_saves(app, client, amount):
    account(client)
    body = expense(app); body['amount'] = amount
    response = write(client, '/transactions', body)
    assert response.status_code == 422 and 'amount' in response.json['fields']
    with app.app_context():
        assert db.session.scalar(db.select(db.func.count()).select_from(Transaction)) == 0


def test_dates_required_fields_custom_category_and_html_retry(app, client):
    account(client)
    body = expense(app)
    body['date'] = (today() + timedelta(days=1)).isoformat()
    assert write(client, '/transactions', body).status_code == 422
    body['date'] = 'bad'
    assert write(client, '/transactions', body).status_code == 422
    body = expense(app); body['category_id'] = None
    assert write(client, '/transactions', body).status_code == 422
    body['category_id'] = write(client, '/categories', {'name': 'Books'}).json['category']['id']
    body['amount'] = '0.01'
    assert write(client, '/transactions', body).status_code == 201
    assert 'Books' in client.get('/transactions').text
    body['amount'] = 'abc'; body['note'] = 'keep my input'; body['csrf_token'] = csrf(client)
    response = client.post('/transactions', data=body)
    assert response.status_code == 422 and 'keep my input' in response.text
    assert 'positive amount' in response.text
    assert client.post('/transactions', json=expense(app)).status_code == 400
    assert '/delete' in client.get('/transactions').text


@pytest.mark.parametrize('filters', [{'start': 'bad'}, {'min': 'NaN'}, {'max': 'Infinity'},
    {'from': '2026-10-31', 'to': '2026-10-01'}, {'min': '20', 'max': '10'},
    {'category_id': 'abc'}, {'page': '0'}])
def test_invalid_filters_rejected(app, client, filters):
    account(client)
    assert client.get('/transactions', query_string=filters, headers={'Accept': 'application/json'}).status_code == 422


def test_filters_sort_pagination_and_total(app, client):
    account(client)
    body = expense(app)
    for i in range(51):
        body['amount'] = str(i + 1)
        assert write(client, '/transactions', body).status_code == 201
    headers = {'Accept': 'application/json'}
    page = client.get('/transactions?sort=amount_asc', headers=headers).json
    assert len(page['transactions']) == 50 and page['has_next'] and page['total'] == '1326.00'
    page2 = client.get('/transactions?sort=amount_asc&page=2', headers=headers).json
    assert len(page2['transactions']) == 1 and page2['transactions'][0]['amount'] == '51.00'
    assert not page2['has_next']
    filtered = client.get('/transactions?min=10&max=20&sort=amount_desc', headers=headers).json
    assert filtered['total'] == '165.00'
    assert [Decimal(t['amount']) for t in filtered['transactions']] == list(map(Decimal, range(20, 9, -1)))
    assert 'Next' in client.get('/transactions?sort=amount_asc').text
    assert client.get('/transactions?min=100', headers=headers).json['total'] == '0.00'


def test_html_delete_requires_confirmation_and_cancel_keeps_record(app, client):
    account(client)
    txn = write(client, '/transactions', expense(app)).json['transaction']
    path = f"/transactions/{txn['id']}/delete"
    confirm = client.get(path)
    assert confirm.status_code == 200 and 'Confirm delete' in confirm.text and 'Cancel' in confirm.text
    assert client.get('/transactions').status_code == 200
    assert client.get(f"/transactions/{txn['id']}").status_code == 200
    assert client.post(path, data={'csrf_token': csrf(client)}).status_code == 200
    assert client.get(f"/transactions/{txn['id']}").status_code == 200
    assert client.post(path, data={'csrf_token': csrf(client), 'confirm': 'yes'}).status_code == 302
    assert client.get(f"/transactions/{txn['id']}").status_code == 404

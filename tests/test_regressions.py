"""Security and boundary defects discovered in the November recovery audit."""
import pytest
from support import account, app, client, write  # noqa: F401


@pytest.mark.parametrize('category', [True, False, 1.9, '1.9', '9'*100, 9223372036854775808])
@pytest.mark.requirement('SEB-SR-003')
def test_category_ids_cannot_be_coerced_or_overflow(client, category):
    account(client)
    response = write(client, '/transactions', {'type': 'expense', 'amount': '1',
        'date': '2026-10-08', 'category_id': category, 'payment_mode': 'UPI'})
    assert response.status_code == 404
    assert response.json == {'error': 'NOT_FOUND'}
    assert client.get('/api/dashboard?month=2026-10').json['expense'] == '0.00'


@pytest.mark.parametrize('path', ['/api/dashboard', '/dashboard', '/budgets'])
@pytest.mark.requirement('SEB-F-016')
def test_six_month_trend_cannot_underflow_calendar(client, path):
    account(client)
    assert client.get(path+'?month=0001-01').status_code == 422


@pytest.mark.parametrize('key', ['min_amount', 'max_amount'])
@pytest.mark.parametrize('value', ['1e1000000', 'Infinity', '-1', '10000000000'])
@pytest.mark.requirement('SEB-F-010')
def test_filter_amounts_cannot_overflow_database(client, key, value):
    account(client)
    response = client.get('/transactions', query_string={key: value}, headers={'Accept': 'application/json'})
    assert response.status_code == 422
    assert key in response.json['fields']


@pytest.mark.parametrize('path, code', [('/missing', 404), ('/register', 400)])
@pytest.mark.requirement('SEB-SR-004')
def test_json_http_errors_never_leak_html_or_internal_details(client, path, code):
    response = client.post(path, json={})
    assert response.status_code == code
    assert response.is_json and 'error' in response.json

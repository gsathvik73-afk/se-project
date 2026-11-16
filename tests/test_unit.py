"""Isolated rules; no database, browser, password hashing or network."""
from datetime import date
from decimal import Decimal

import pytest

from smartexpense.routes import fmt, money, parse_month

pytestmark = pytest.mark.unit


@pytest.mark.parametrize('raw, expected', [('0.01', '0.01'), ('1', '1.00'),
    ('250.50', '250.50'), ('9999999999.99', '9999999999.99'), (10, '10.00')])
@pytest.mark.requirement('SEB-F-007')
def test_money_accepts_exact_positive_decimal(raw, expected):
    assert money(raw) == Decimal(expected)


@pytest.mark.parametrize('raw', ['0', '-1', '', None, True, 'abc', 'NaN', 'sNaN',
    'Infinity', '-Infinity', '0.001', '10000000000', '1e1000000'])
@pytest.mark.requirement('SEB-F-007')
def test_money_rejects_invalid_amounts(raw):
    with pytest.raises(ValueError):
        money(raw)


@pytest.mark.parametrize('month, last', [('2024-02', 29), ('2026-02', 28),
    ('2026-04', 30), ('2026-12', 31), ('0001-06', 30), ('9999-12', 31)])
@pytest.mark.requirement('SEB-F-015')
def test_month_bounds_include_leap_year(month, last):
    first, end = parse_month(month)
    assert first.day == 1 and end.day == last
    assert first.year == end.year and first.month == end.month


@pytest.mark.parametrize('month', ['2026-00', '2026-13', '2026-1', '0000-01',
    '0001-01', '0001-05', 'bad', None, 202611])
@pytest.mark.requirement('SEB-F-015')
def test_month_rejects_invalid_or_unrepresentable_trend(month):
    with pytest.raises(ValueError):
        parse_month(month)


@pytest.mark.parametrize('raw, expected', [(None, '0.00'), (0, '0.00'),
    (Decimal('250.5'), '250.50'), (Decimal('-10'), '-10.00')])
@pytest.mark.requirement('SEB-F-013')
def test_format_money_preserves_sign_and_two_decimal_places(raw, expected):
    assert fmt(raw) == expected

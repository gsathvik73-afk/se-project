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



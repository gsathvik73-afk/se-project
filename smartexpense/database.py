import sqlite3

from sqlalchemy import event, inspect, text
from sqlalchemy.engine import Engine

from .models import Category, DEFAULT_CATEGORIES, db


@event.listens_for(Engine, 'connect')
def sqlite_settings(connection, _):
    if isinstance(connection, sqlite3.Connection):
        cursor = connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.execute('PRAGMA busy_timeout=30000')
        cursor.close()


def initialize_database():
    """Create schema and migrate the additive Sprint 1 login fields."""
    db.create_all()
    columns = {column['name'] for column in inspect(db.engine).get_columns('user')}
    with db.engine.begin() as connection:
        if 'failed_attempts' not in columns:
            connection.execute(text('ALTER TABLE "user" ADD COLUMN failed_attempts INTEGER NOT NULL DEFAULT 0'))
        if 'locked_until' not in columns:
            connection.execute(text('ALTER TABLE "user" ADD COLUMN locked_until TIMESTAMP'))
        if db.engine.dialect.name == 'sqlite':
            connection.execute(text('PRAGMA journal_mode=WAL'))
    for name in DEFAULT_CATEGORIES:
        if not db.session.scalar(db.select(Category).where(Category.user_id.is_(None), Category.name == name)):
            db.session.add(Category(name=name))
    db.session.commit()

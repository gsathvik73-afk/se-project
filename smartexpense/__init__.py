import os
from pathlib import Path
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from .models import db, Category, DEFAULT_CATEGORIES

csrf = CSRFProtect()

def create_app(config=None):
    app = Flask(__name__, instance_relative_config=True)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL', 'sqlite:///smartexpense.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=os.environ.get('COOKIE_SECURE', '0') == '1',
        MAX_CONTENT_LENGTH=64*1024,
    )
    if config:
        app.config.update(config)
    if not app.config['SECRET_KEY']:
        raise RuntimeError('Set SECRET_KEY before starting SmartExpense.')
    db.init_app(app)
    csrf.init_app(app)
    from .routes import bp
    app.register_blueprint(bp)
    @app.cli.command('init-db')
    def init_db():
        """Create tables and the eight shared read-only categories."""
        db.create_all()
        for name in DEFAULT_CATEGORIES:
            if not db.session.scalar(db.select(Category).where(Category.user_id.is_(None), Category.name == name)):
                db.session.add(Category(name=name))
        db.session.commit()
        print('Database ready.')
    return app

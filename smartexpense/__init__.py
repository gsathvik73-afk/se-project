import os
from pathlib import Path
from flask import Flask, g, jsonify, render_template, request
from secrets import token_hex
from flask_wtf.csrf import CSRFProtect
from .models import db, Category, DEFAULT_CATEGORIES

class SmartExpenseFlask(Flask):
    def log_exception(self, exc_info):
        # Exception strings can contain SQL parameters; log only the failure type.
        self.logger.error('request=%s endpoint=%s failure=%s',
                          getattr(g, 'request_id', 'unavailable'), request.endpoint, exc_info[0].__name__)


csrf = CSRFProtect()

def create_app(config=None):
    app = SmartExpenseFlask(__name__, instance_relative_config=True)
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
    @app.before_request
    def request_reference():
        g.request_id = token_hex(6)

    @app.after_request
    def security_headers(response):
        response.headers['Content-Security-Policy'] = ("default-src 'self'; script-src 'self'; "
            "style-src 'self'; img-src 'self' data:; object-src 'none'; base-uri 'self'; "
            "frame-ancestors 'none'; form-action 'self'")
        response.headers['Strict-Transport-Security'] = 'max-age=31536000'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'same-origin'
        if request.endpoint != 'static':
            response.headers['Cache-Control'] = 'no-store'
        return response

    @app.errorhandler(500)
    def failed_save(error):
        db.session.rollback()
        message = 'Your data was not saved. Please retry.'
        if request.is_json or request.accept_mimetypes.best == 'application/json':
            return jsonify(error='SAVE_FAILED', message=message, request_id=g.request_id), 500
        return render_template('message.html', title='Please try again',
                               errors={'save': message, 'reference': g.request_id}), 500

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

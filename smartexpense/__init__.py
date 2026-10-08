import os
from pathlib import Path
from secrets import token_hex
from flask import Flask, g, jsonify, render_template, request
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.middleware.proxy_fix import ProxyFix
from .models import db

csrf = CSRFProtect()

def create_app(config=None):
    deployed = os.environ.get('VERCEL') == '1'
    instance = '/tmp/smartexpense' if deployed else None
    app = Flask(__name__, static_folder='../public/static', static_url_path='/static', instance_relative_config=True, **({'instance_path': instance} if instance else {}))
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    uri = os.environ.get('DATABASE_URL', 'sqlite:///smartexpense.db')
    if uri.startswith('postgres://'):
        uri = uri.replace('postgres://', 'postgresql+psycopg://', 1)
    elif uri.startswith('postgresql://'):
        uri = uri.replace('postgresql://', 'postgresql+psycopg://', 1)
    if deployed and uri.startswith('sqlite:'):
        raise RuntimeError('Vercel requires a persistent DATABASE_URL; local SQLite is not supported in deployment.')
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY'),
        SQLALCHEMY_DATABASE_URI=uri,
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={'pool_pre_ping': True},
        SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=deployed or os.environ.get('COOKIE_SECURE', '0') == '1',
        MAX_CONTENT_LENGTH=64*1024,
        ENFORCE_HTTPS=deployed or os.environ.get('ENFORCE_HTTPS', '0') == '1',
    )
    if config:
        app.config.update(config)
    if not app.config['SECRET_KEY']:
        raise RuntimeError('Set SECRET_KEY before starting SmartExpense.')
    # Trust one platform proxy only when deployed behind Vercel.
    if deployed:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    db.init_app(app)
    csrf.init_app(app)
    from .routes import bp, json_request
    app.register_blueprint(bp)

    @app.before_request
    def https_only():
        if app.config['ENFORCE_HTTPS'] and not request.is_secure:
            from flask import redirect
            return redirect(request.url.replace('http://', 'https://', 1), code=308)

    @app.after_request
    def security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'same-origin'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
        if request.is_secure:
            response.headers['Strict-Transport-Security'] = 'max-age=31536000'
        if g.get('user') or request.path in ('/register', '/login'):
            response.headers['Cache-Control'] = 'no-store'
        return response

    @app.errorhandler(SQLAlchemyError)
    def database_error(_):
        db.session.rollback()
        reference = token_hex(6)
        # No passwords, SQL, transaction notes or database credentials in logs.
        app.logger.error('Database operation failed; reference=%s', reference)
        message = 'Your data was not saved. Please retry.'
        if json_request():
            return jsonify(error='SAVE_FAILED', message=message, reference=reference), 500
        return render_template('message.html', title='Unable to save', errors={'save': message}), 500

    @app.get('/health')
    def health():
        db.session.execute(text('SELECT 1'))
        return jsonify(status='ok')

    @app.cli.command('init-db')
    def init_db():
        from .database import initialize_database
        initialize_database()
        print('Database ready.')

    # Register SQLite connection settings before creating any connections.
    from . import database
    return app

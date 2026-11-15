"""Isolated disposable demo server, never the user's personal SQLite database."""
import os
from pathlib import Path
import secrets
import tempfile
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from smartexpense import create_app

folder = tempfile.mkdtemp(prefix='smartexpense-demo-')
app = create_app({'SECRET_KEY': secrets.token_hex(32),
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///'+folder+'/demo.db'})
with app.app_context():
    app.test_cli_runner().invoke(args=['init-db'])
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT','5057')), debug=False)

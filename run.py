"""Start a local demo with a persistent private key and existing data preserved."""
import os
from pathlib import Path
import secrets
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parent
    os.chdir(root)
    if not os.environ.get('SECRET_KEY'):
        instance = root / 'instance'
        instance.mkdir(exist_ok=True)
        key_path = instance / '.local-secret'
        try:
            fd = os.open(key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            pass
        else:
            with os.fdopen(fd, 'w') as output:
                output.write(secrets.token_hex(32))
        os.environ['SECRET_KEY'] = key_path.read_text().strip()
    subprocess.run([sys.executable, '-m', 'flask', '--app', 'smartexpense', 'init-db'], check=True)
    os.execvp(sys.executable, [sys.executable, '-m', 'flask', '--app', 'smartexpense',
                             'run', '--host', '127.0.0.1', '--port', os.environ.get('PORT', '5050'),
                             '--no-debugger', '--no-reload'])


if __name__ == '__main__':
    main()

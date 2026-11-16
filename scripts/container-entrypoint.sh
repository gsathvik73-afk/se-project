#!/bin/sh
set -eu
: "${SECRET_KEY:?Set a long random SECRET_KEY before starting the container}"
python -m flask --app smartexpense init-db
exec gunicorn --bind 0.0.0.0:8000 --workers 1 --threads 4 'smartexpense:create_app()'

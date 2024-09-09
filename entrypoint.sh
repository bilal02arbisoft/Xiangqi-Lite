#!/bin/sh

set -e

if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Applying migrations..."
    python3 manage.py migrate --noinput
fi

echo "Collecting static files..."
python3 manage.py collectstatic --noinput

echo "Starting Daphne server..."
daphne -b 0.0.0.0 -p 8000 xiangqi_lite.asgi:application

exec "$@"

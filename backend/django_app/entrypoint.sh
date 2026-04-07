#!/bin/sh
set -e

echo "=========================================="
echo "  LearnHub Django Startup (MySQL)"
echo "=========================================="

echo "[1/5] Waiting for MySQL ($DB_HOST:$DB_PORT)..."
until nc -z "$DB_HOST" "$DB_PORT" 2>/dev/null; do
  echo "      MySQL not ready, retrying in 2s..."
  sleep 2
done
# Extra wait — MySQL port opens before it's fully ready to accept connections
sleep 3
echo "      MySQL is ready!"

echo "[2/5] Waiting for Redis (redis:6379)..."
until nc -z redis 6379 2>/dev/null; do
  echo "      Redis not ready, retrying in 2s..."
  sleep 2
done
echo "      Redis is ready!"

echo "[3/5] Running migrations..."
python manage.py migrate --noinput

echo "[4/5] Collecting static files..."
python manage.py collectstatic --noinput --quiet

echo "[5/5] Starting Gunicorn on 0.0.0.0:8000..."
exec gunicorn lms_backend.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 2 \
  --threads 2 \
  --timeout 120 \
  --log-level info \
  --access-logfile - \
  --error-logfile -

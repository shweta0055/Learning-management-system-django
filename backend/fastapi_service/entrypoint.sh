#!/bin/sh
set -e

echo "Waiting for MySQL (db:3306)..."
until nc -z db 3306 2>/dev/null; do
  echo "  MySQL not ready, retrying..."
  sleep 2
done
sleep 3
echo "MySQL ready!"

echo "Waiting for Redis (redis:6379)..."
until nc -z redis 6379 2>/dev/null; do
  echo "  Redis not ready, retrying..."
  sleep 2
done
echo "Redis ready!"

exec uvicorn main:app --host 0.0.0.0 --port 8001 --workers 2

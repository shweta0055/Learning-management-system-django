# 🔧 Troubleshooting Guide — LearnHub LMS

## Common errors and fixes

---

### ❌ `django.db.utils.OperationalError: connection refused` (MySQL)
**Cause:** MySQL container not ready or credentials wrong.
```bash
# Check MySQL container is healthy:
docker compose ps

# Check MySQL logs:
docker compose logs db

# Double-check your .env:
DB_HOST=db        # must be "db" inside Docker, not localhost
DB_PORT=3306
DB_NAME=lms_db
DB_USER=lms_user
DB_PASSWORD=lms_password
```

---

### ❌ `ModuleNotFoundError: No module named 'decouple'` (or any package)
**Cause:** Virtual environment not activated, or packages not installed.
```bash
# Make sure you're inside the venv:
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate.bat  # Windows

# Reinstall:
pip install -r requirements.txt
```

---

### ❌ `django.core.exceptions.ImproperlyConfigured: The SECRET_KEY setting must not be empty`
**Cause:** `.env` file missing or not being read.
```bash
# Make sure .env exists in backend/django_app/
ls -la .env

# If missing, copy from example:
cp .env.example .env

# Generate a secret key:
python3 -c "import secrets; print(secrets.token_hex(32))"
# Paste the output into .env as DJANGO_SECRET_KEY=...
```

---

### ❌ `redis.exceptions.ConnectionError: Error connecting to Redis`
**Cause:** Redis is not running.
```bash
# Check:
redis-cli ping   # should return PONG

# Start:
# macOS:   brew services start redis
# Linux:   sudo service redis-server start

# Or disable Redis entirely for local dev — add to .env:
CELERY_TASK_ALWAYS_EAGER=True
# And change CACHES to use LocMemCache (already in settings_local.py)
```

---

### ❌ `CommandError: App 'users' does not have migrations`
**Cause:** Migrations haven't been generated yet.
```bash
# Run for each app in this order:
python manage.py makemigrations users
python manage.py makemigrations courses
python manage.py makemigrations enrollments
python manage.py makemigrations quizzes
python manage.py makemigrations certificates
python manage.py makemigrations payments
python manage.py migrate
```

---

### ❌ `CORS error` in browser console
**Cause:** Django CORS settings don't include your frontend origin.
```python
# In lms_backend/settings.py, add to CORS_ALLOWED_ORIGINS:
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]
```

---

### ❌ React shows blank page or `Network Error`
**Cause:** Django or FastAPI server not running, or wrong URL in `.env`.
```bash
# Check both servers are running:
curl http://localhost:8000/api/courses/   # Django
curl http://localhost:8001/health          # FastAPI

# Check frontend/.env.local:
REACT_APP_DJANGO_API_URL=http://localhost:8000
REACT_APP_FASTAPI_URL=http://localhost:8001

# After editing .env.local, restart npm start
```

---

### ❌ `401 Unauthorized` on all API calls
**Cause:** JWT token expired or not being sent.
- Log out and log back in at http://localhost:3000/login
- The token auto-refreshes — check browser console for errors

---

### ❌ FastAPI returns `{"detail": "Could not validate token"}`
**Cause:** DJANGO_SECRET_KEY in FastAPI `.env` doesn't match Django's.
```bash
# Check both .env files have the exact same key:
grep DJANGO_SECRET_KEY backend/django_app/.env
grep DJANGO_SECRET_KEY backend/fastapi_service/.env
```

---

### ❌ `mysqlclient` install fails on macOS
**Cause:** Missing MySQL client libraries.
```bash
brew install mysql-client pkg-config
export PKG_CONFIG_PATH="/opt/homebrew/opt/mysql-client/lib/pkgconfig"
pip install mysqlclient
```

### ❌ `mysqlclient` install fails on Ubuntu/Debian
**Cause:** Missing dev libraries.
```bash
sudo apt install default-libmysqlclient-dev pkg-config gcc
pip install mysqlclient
```

---

### ❌ `npm install` fails with node-gyp errors
**Cause:** Python/build tools missing (needed by some native npm modules).
```bash
# macOS:
xcode-select --install

# Ubuntu:
sudo apt install build-essential python3-dev

# Then retry:
npm install
```

---

### ❌ Seed data command fails: `unique constraint violation`
**Cause:** You already ran seed_data once. Safe to ignore or run with --clear:
```bash
python manage.py seed_data --clear   # deletes and re-seeds
# OR just ignore the error — existing data is intact
```

---

## Resetting everything from scratch

```bash
# Delete the SQLite database (if using SQLite):
rm backend/django_app/db.sqlite3

# Or drop and recreate PostgreSQL database:
psql -U postgres -c "DROP DATABASE lms_db;"
psql -U postgres -c "CREATE DATABASE lms_db OWNER lms_user;"

# Then re-run migrations and seed:
python manage.py migrate
python manage.py seed_data
```

---

## Checking all services at once

```bash
# Quick health check script — run from lms-project/
echo "=== Django ===" && curl -s http://localhost:8000/api/courses/ | python3 -m json.tool | head -5
echo "=== FastAPI ===" && curl -s http://localhost:8001/health
echo "=== Redis ===" && redis-cli ping
echo "=== MySQL ===" && docker compose exec db mysqladmin ping -h localhost -u lms_user -plms_password
```

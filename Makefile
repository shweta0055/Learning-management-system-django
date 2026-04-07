# LearnHub LMS — Makefile
# Usage: make <target>

.PHONY: help up down build logs shell-django shell-fastapi migrate seed test-django test-fastapi test-all restart clean

help:
	@echo "LearnHub LMS — Available commands:"
	@echo ""
	@echo "  make up            Start all services (Docker)"
	@echo "  make down          Stop all services"
	@echo "  make build         Rebuild all Docker images"
	@echo "  make logs          Tail all service logs"
	@echo "  make logs-django   Tail Django logs"
	@echo "  make logs-fastapi  Tail FastAPI logs"
	@echo ""
	@echo "  make migrate       Run Django migrations"
	@echo "  make seed          Seed demo data"
	@echo "  make superuser     Create Django superuser"
	@echo "  make shell-django  Open Django shell"
	@echo "  make shell-fastapi Open FastAPI container bash"
	@echo ""
	@echo "  make test-django   Run Django tests"
	@echo "  make test-fastapi  Run FastAPI tests"
	@echo "  make test-all      Run all tests"
	@echo ""
	@echo "  make restart       Restart all services"
	@echo "  make clean         Remove volumes & containers"
	@echo "  make setup         Full setup (build + migrate + seed)"

# ─── Docker ──────────────────────────────────────────────────────────────────
up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose up --build -d

logs:
	docker compose logs -f

logs-django:
	docker compose logs -f django

logs-fastapi:
	docker compose logs -f fastapi

logs-celery:
	docker compose logs -f celery

restart:
	docker compose restart

clean:
	docker compose down -v --remove-orphans
	docker system prune -f

# ─── Django ──────────────────────────────────────────────────────────────────
migrate:
	docker compose exec django python manage.py migrate

makemigrations:
	docker compose exec django python manage.py makemigrations

seed:
	docker compose exec django python manage.py seed_data

superuser:
	docker compose exec django python manage.py createsuperuser

shell-django:
	docker compose exec django python manage.py shell

collectstatic:
	docker compose exec django python manage.py collectstatic --noinput

# ─── FastAPI ─────────────────────────────────────────────────────────────────
shell-fastapi:
	docker compose exec fastapi bash

# ─── Tests ───────────────────────────────────────────────────────────────────
test-django:
	docker compose exec django python -m pytest tests/ -v

test-fastapi:
	docker compose exec fastapi python -m pytest tests/ -v

test-all: test-django test-fastapi

# ─── Full setup ──────────────────────────────────────────────────────────────
setup: build migrate seed
	@echo ""
	@echo "✅ LearnHub is ready!"
	@echo "   Frontend:  http://localhost:3000"
	@echo "   Django:    http://localhost:8000/api/"
	@echo "   Admin:     http://localhost:8000/admin/"
	@echo "   FastAPI:   http://localhost:8001/docs"

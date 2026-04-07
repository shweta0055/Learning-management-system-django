#!/usr/bin/env bash
# =============================================================================
# LearnHub LMS — One-Click Setup Script
# Usage: bash setup.sh [--dev | --docker | --reset]
# =============================================================================

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

info()    { echo -e "${BLUE}ℹ  $1${NC}"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠  $1${NC}"; }
error()   { echo -e "${RED}❌ $1${NC}"; exit 1; }

MODE=${1:-"--docker"}

echo ""
echo "╔══════════════════════════════════════╗"
echo "║     LearnHub LMS Platform Setup      ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ─── Check prerequisites ────────────────────────────────────────────────────
check_command() {
    if ! command -v "$1" &> /dev/null; then
        error "$1 is required but not installed. Please install it first."
    fi
}

if [ "$MODE" = "--docker" ]; then
    check_command docker
    check_command docker-compose || check_command "docker compose"
elif [ "$MODE" = "--dev" ]; then
    check_command python3
    check_command node
    check_command npm
    check_command psql
    check_command redis-cli
fi

# ─── Copy env files ─────────────────────────────────────────────────────────
info "Setting up environment files..."

if [ ! -f backend/django_app/.env ]; then
    cp backend/django_app/.env.example backend/django_app/.env
    warning "Created backend/django_app/.env — please review and update secrets!"
fi

if [ ! -f backend/fastapi_service/.env ]; then
    cp backend/fastapi_service/.env.example backend/fastapi_service/.env
    warning "Created backend/fastapi_service/.env — please review!"
fi

if [ ! -f frontend/react_app/.env ]; then
    cp frontend/react_app/.env.example frontend/react_app/.env
    success "Created frontend/react_app/.env"
fi

# ─── Docker mode ─────────────────────────────────────────────────────────────
if [ "$MODE" = "--docker" ]; then
    info "Starting all services with Docker Compose..."
    docker compose up --build -d

    info "Waiting for database to be ready..."
    sleep 8

    info "Running Django migrations..."
    docker compose exec django python manage.py migrate

    info "Collecting static files..."
    docker compose exec django python manage.py collectstatic --noinput

    info "Creating superuser (admin@learnhub.com / Admin123!)..."
    docker compose exec django python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@learnhub.com').exists():
    User.objects.create_superuser(username='admin', email='admin@learnhub.com', password='Admin123!', role='admin', first_name='Admin', last_name='User')
    print('Superuser created.')
else:
    print('Superuser already exists.')
"

    info "Seeding demo data..."
    docker compose exec django python manage.py seed_data || warning "Seed data failed (may already exist)"

    echo ""
    success "LearnHub is running! 🚀"
    echo ""
    echo "  🌐 Frontend:       http://localhost:3000"
    echo "  🔧 Django API:     http://localhost:8000/api/"
    echo "  📚 API Docs:       http://localhost:8000/api/docs/"
    echo "  ⚙️  Django Admin:  http://localhost:8000/admin/"
    echo "  ⚡ FastAPI:        http://localhost:8001"
    echo "  📖 FastAPI Docs:   http://localhost:8001/docs"
    echo "  🔀 Nginx Gateway:  http://localhost:80"
    echo ""
    echo "  👤 Admin login:    admin@learnhub.com / Admin123!"
    echo "  👩‍🏫 Instructor:    john@learnhub.com / Test123!"
    echo "  👩‍🎓 Student:       alice@example.com / Test123!"
    echo ""

# ─── Dev mode ────────────────────────────────────────────────────────────────
elif [ "$MODE" = "--dev" ]; then
    info "Setting up local development environment..."

    # Django
    info "Setting up Django backend..."
    cd backend/django_app
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt -q
    python manage.py migrate
    python manage.py collectstatic --noinput -v 0
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(email='admin@learnhub.com').exists():
    User.objects.create_superuser(username='admin', email='admin@learnhub.com', password='Admin123!', role='admin', first_name='Admin', last_name='User')
"
    python manage.py seed_data || true
    deactivate
    cd ../..
    success "Django backend ready"

    # FastAPI
    info "Setting up FastAPI service..."
    cd backend/fastapi_service
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt -q
    deactivate
    cd ../..
    success "FastAPI service ready"

    # Frontend
    info "Installing React dependencies..."
    cd frontend/react_app
    npm install --silent
    cd ../..
    success "React frontend ready"

    echo ""
    success "Development environment ready! 🎉"
    echo ""
    echo "Start services in separate terminals:"
    echo ""
    echo "  Terminal 1 (Django):"
    echo "    cd backend/django_app && source venv/bin/activate"
    echo "    python manage.py runserver"
    echo ""
    echo "  Terminal 2 (Celery):"
    echo "    cd backend/django_app && source venv/bin/activate"
    echo "    celery -A lms_backend worker --loglevel=info"
    echo ""
    echo "  Terminal 3 (FastAPI):"
    echo "    cd backend/fastapi_service && source venv/bin/activate"
    echo "    uvicorn main:app --reload --port 8001"
    echo ""
    echo "  Terminal 4 (React):"
    echo "    cd frontend/react_app && npm start"
    echo ""

# ─── Reset mode ──────────────────────────────────────────────────────────────
elif [ "$MODE" = "--reset" ]; then
    warning "This will destroy all containers and volumes. Are you sure? (y/N)"
    read -r confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        docker compose down -v --remove-orphans
        docker system prune -f
        success "Reset complete. Run './setup.sh --docker' to start fresh."
    else
        info "Aborted."
    fi

else
    echo "Usage: bash setup.sh [--docker | --dev | --reset]"
    echo ""
    echo "  --docker   Start with Docker Compose (default, recommended)"
    echo "  --dev      Set up local development environment"
    echo "  --reset    Destroy all Docker volumes and containers"
    exit 1
fi

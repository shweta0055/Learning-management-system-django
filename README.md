# 🎓 LearnHub — Full Stack LMS Platform

A production-ready Learning Management System built with **Django + FastAPI + React**.

---

## 🏗️ Architecture

```
Frontend (React + Tailwind)
        ↓
Nginx (Reverse Proxy / API Gateway)
        ↓
┌───────────────────┬─────────────────────┐
│  Django (Port 8000)│  FastAPI (Port 8001) │
│  Core APIs + Admin │  Async Microservice  │
│  JWT Auth          │  Analytics           │
│  Course CRUD       │  Recommendations     │
│  Enrollments       │  Video Streaming     │
│  Quizzes           │  Search              │
│  Certificates      │                     │
│  Payments          │                     │
└───────────────────┴─────────────────────┘
        ↓
MySQL + Redis + Celery
```

---

## 📁 Folder Structure

```
lms-project/
├── backend/
│   ├── django_app/          # Django REST API
│   │   ├── lms_backend/     # Project settings, URLs, Celery
│   │   ├── users/           # Auth, profiles, JWT
│   │   ├── courses/         # Course, Section, Lesson, Review
│   │   ├── enrollments/     # Enrollment, Progress, Wishlist
│   │   ├── quizzes/         # Quiz, Question, Assignment
│   │   ├── certificates/    # PDF certificate generation
│   │   ├── payments/        # Stripe integration, Coupons
│   │   ├── tests/           # pytest test suite
│   │   ├── manage.py
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── .env.example
│   │
│   └── fastapi_service/     # FastAPI Async Microservice
│       ├── routers/
│       │   ├── analytics.py    # Student/Instructor/Admin dashboards
│       │   ├── recommendations.py  # AI-style course recommendations
│       │   ├── streaming.py    # Video streaming / S3 presigned URLs
│       │   └── search.py       # Full-text course search
│       ├── main.py
│       ├── auth.py
│       ├── database.py
│       ├── tests/
│       ├── requirements.txt
│       ├── Dockerfile
│       └── .env.example
│
├── frontend/
│   └── react_app/           # React 18 + Tailwind CSS
│       ├── src/
│       │   ├── components/  # Navbar, Footer, CourseCard
│       │   ├── pages/       # All pages (Home, Courses, Dashboard...)
│       │   ├── services/    # Axios API clients (Django + FastAPI)
│       │   └── context/     # Zustand auth store
│       ├── package.json
│       ├── Dockerfile
│       └── nginx.conf
│
├── nginx/
│   └── nginx.conf           # Reverse proxy config
│
├── .github/
│   └── workflows/
│       └── ci-cd.yml        # GitHub Actions CI/CD
│
└── docker-compose.yml
```

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local frontend dev)
- Python 3.11+ (for local backend dev)

### 1. Clone & configure

```bash
git clone <your-repo-url>
cd lms-project

# Configure Django
cp backend/django_app/.env.example backend/django_app/.env
# Edit .env with your settings

# Configure FastAPI
cp backend/fastapi_service/.env.example backend/fastapi_service/.env
```

### 2. Start with Docker Compose

```bash
docker compose up --build
```

Services will be available at:
| Service | URL |
|---------|-----|
| React Frontend | http://localhost:3000 |
| Django API | http://localhost:8000/api/ |
| Django Admin | http://localhost:8000/admin/ |
| Django API Docs | http://localhost:8000/api/docs/ |
| FastAPI Service | http://localhost:8001 |
| FastAPI Docs | http://localhost:8001/docs |
| Nginx Gateway | http://localhost:80 |

### 3. Create superuser

```bash
docker compose exec django python manage.py createsuperuser
```

---

## 🔧 Local Development (without Docker)

### Backend — Django

```bash
cd backend/django_app
python -m venv venv
source venv/bin/activate         # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # Edit DB settings
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Backend — FastAPI

```bash
cd backend/fastapi_service
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn main:app --reload --port 8001
```

### Celery Workers

```bash
cd backend/django_app
celery -A lms_backend worker --loglevel=info
celery -A lms_backend beat --loglevel=info   # optional: scheduled tasks
```

### Frontend

```bash
cd frontend/react_app
npm install
npm start      # Runs on http://localhost:3000
```

---

## 🧪 Running Tests

### Django
```bash
cd backend/django_app
pytest tests/ -v
```

### FastAPI
```bash
cd backend/fastapi_service
pytest tests/ -v
```

### Frontend
```bash
cd frontend/react_app
npm test
```

---

## 📡 API Reference

### Django REST API (Port 8000)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Register new user |
| POST | `/api/auth/login/` | Login (returns JWT) |
| POST | `/api/auth/logout/` | Logout (blacklist refresh) |
| POST | `/api/auth/token/refresh/` | Refresh access token |
| GET/PATCH | `/api/auth/profile/` | Get/update profile |
| GET | `/api/courses/` | List published courses |
| POST | `/api/courses/create/` | Create course (instructor) |
| GET | `/api/courses/:slug/` | Course detail |
| POST | `/api/enrollments/enroll/` | Enroll in a course |
| GET | `/api/enrollments/my/` | My enrollments |
| POST | `/api/quizzes/:id/submit/` | Submit quiz |
| POST | `/api/payments/checkout/` | Stripe checkout |
| GET | `/api/certificates/my/` | My certificates |
| GET | `/api/certificates/verify/:id/` | Verify certificate |

### FastAPI Service (Port 8001)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/dashboard/student` | Student analytics |
| GET | `/api/analytics/dashboard/instructor` | Instructor analytics |
| GET | `/api/analytics/dashboard/admin` | Platform analytics |
| GET | `/api/recommendations/courses` | Personalized recommendations |
| GET | `/api/recommendations/trending` | Trending courses |
| GET | `/api/recommendations/continue-learning` | Resume learning |
| GET | `/api/search/courses?q=python` | Search courses |
| GET | `/api/search/suggestions?q=py` | Autocomplete |
| GET | `/api/streaming/presigned-url/:lessonId` | S3 video URL |

---

## 🔐 User Roles

| Role | Capabilities |
|------|-------------|
| **Admin** | Full access, Django admin panel, user management |
| **Instructor** | Create/manage courses, view analytics, grade assignments |
| **Student** | Browse, enroll, learn, take quizzes, earn certificates |

---

## 💳 Stripe Setup

1. Create a [Stripe](https://stripe.com) account
2. Get test API keys
3. Add to `backend/django_app/.env`:
```
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```
4. Set up webhook in Stripe dashboard pointing to `/api/payments/webhook/`

---

## ☁️ Deployment

### Environment Variables (Production)

| Variable | Description |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Strong random secret |
| `DEBUG` | Set to `False` |
| `ALLOWED_HOSTS` | Your domain(s) |
| `DB_*` | MySQL connection |
| `REDIS_URL` | Redis connection |
| `USE_S3=True` | Enable S3 storage |
| `AWS_*` | AWS credentials |
| `STRIPE_SECRET_KEY` | Stripe live key |

### CI/CD

The GitHub Actions workflow (`.github/workflows/ci-cd.yml`) automatically:
1. Runs Django, FastAPI, and React tests
2. Builds Docker images and pushes to GitHub Container Registry
3. Deploys to production via SSH on push to `main`

Set these secrets in your GitHub repository:
- `DEPLOY_HOST` — your server IP
- `DEPLOY_USER` — SSH user
- `DEPLOY_SSH_KEY` — private SSH key
- `DJANGO_API_URL` — production Django URL
- `FASTAPI_URL` — production FastAPI URL

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | Django 4.2 + DRF |
| Async Service | FastAPI 0.104 |
| Frontend | React 18 + Tailwind CSS |
| Database | MySQL 8.0 |
| Cache/Queue | Redis 7 |
| Task Queue | Celery |
| Auth | JWT (SimpleJWT) |
| Payments | Stripe |
| Storage | AWS S3 (optional) |
| PDF Gen | ReportLab |
| Reverse Proxy | Nginx |
| Container | Docker + Compose |
| CI/CD | GitHub Actions |

---

## 📄 License

MIT License — free to use, modify, and distribute.

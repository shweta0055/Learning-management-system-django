# LearnHub LMS — Windows Docker Setup Script (MySQL)
# Run in PowerShell: .\setup-windows.ps1

Write-Host "Setting up LearnHub LMS with MySQL..." -ForegroundColor Cyan

# Copy env files
Copy-Item backend\django_app\.env.example backend\django_app\.env -Force
Copy-Item backend\fastapi_service\.env.example backend\fastapi_service\.env -Force
Copy-Item frontend\react_app\.env.example frontend\react_app\.env -Force

Write-Host "Env files copied." -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: Set a real secret key in BOTH .env files:" -ForegroundColor Yellow
Write-Host "  backend\django_app\.env        -> DJANGO_SECRET_KEY=..." -ForegroundColor Yellow
Write-Host "  backend\fastapi_service\.env   -> DJANGO_SECRET_KEY= (same key)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Enter when done editing .env files..."
Read-Host

Write-Host "Building Docker images (5-10 minutes first time)..." -ForegroundColor Cyan
docker compose build --no-cache

Write-Host "Starting all services..." -ForegroundColor Cyan
docker compose up -d

Write-Host "Waiting 45 seconds for MySQL to initialise..." -ForegroundColor Cyan
Start-Sleep -Seconds 45

Write-Host "Running Django migrations..." -ForegroundColor Cyan
docker compose exec django python manage.py migrate

Write-Host "Loading demo data..." -ForegroundColor Cyan
docker compose exec django python manage.py seed_data

Write-Host "Creating admin superuser..." -ForegroundColor Cyan
docker compose exec -it django python manage.py createsuperuser

Write-Host ""
Write-Host "All done!" -ForegroundColor Green
Write-Host "  Frontend:      http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Django API:    http://localhost:8000/api/" -ForegroundColor Cyan
Write-Host "  Admin panel:   http://localhost:8000/admin/" -ForegroundColor Cyan
Write-Host "  API docs:      http://localhost:8000/api/docs/" -ForegroundColor Cyan
Write-Host "  FastAPI docs:  http://localhost:8001/docs" -ForegroundColor Cyan

@echo off
REM NeuroHabit Startup Script for Windows
REM This script automates the complete setup and startup process

echo ============================================================
echo            NeuroHabit - AI Habit Coach Setup
echo ============================================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.

REM Step 1: Environment setup
echo Step 1: Setting up environment variables...
if not exist .env (
    copy .env.example .env >nul
    echo [OK] Created .env file
) else (
    echo [WARNING] .env file already exists, skipping
)
echo.

REM Step 2: Build images
echo Step 2: Building Docker images...
echo This may take 5-10 minutes on first run...
docker-compose build
if errorlevel 1 (
    echo [ERROR] Failed to build Docker images
    pause
    exit /b 1
)
echo [OK] Docker images built successfully
echo.

REM Step 3: Start services
echo Step 3: Starting services...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to start services
    pause
    exit /b 1
)
echo [OK] Services started
echo.

REM Wait for services to be ready
echo Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Step 4: Run migrations
echo Step 4: Running database migrations...
docker-compose exec -T backend alembic upgrade head
if errorlevel 1 (
    echo [ERROR] Failed to run migrations
    pause
    exit /b 1
)
echo [OK] Database migrations completed
echo.

REM Step 5: Train ML model
echo Step 5: Training ML model...
docker-compose exec -T backend python -m app.ml.trainer
if errorlevel 1 (
    echo [ERROR] Failed to train ML model
    pause
    exit /b 1
)
echo [OK] ML model trained
echo.

REM Step 6: Seed data
echo Step 6: Seeding demo data...
docker-compose exec -T backend python seed.py
if errorlevel 1 (
    echo [ERROR] Failed to seed data
    pause
    exit /b 1
)
echo [OK] Demo data seeded
echo.

REM Final status
echo ============================================================
echo            Setup Complete! 🎉
echo ============================================================
echo.
echo Services Status:
docker-compose ps
echo.
echo Access Points:
echo   Frontend:     http://localhost:5173
echo   Backend API:  http://localhost:8000
echo   API Docs:     http://localhost:8000/docs
echo.
echo Demo Credentials:
echo   Email:    demo@neurohabit.com
echo   Password: demo123
echo.
echo Useful Commands:
echo   View logs:        docker-compose logs -f
echo   Stop services:    docker-compose down
echo   Restart:          docker-compose restart
echo   Run tests:        docker-compose exec backend pytest -v
echo.
echo For more information, see RUNBOOK.md
echo ============================================================
echo.
pause

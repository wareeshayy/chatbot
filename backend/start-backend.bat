@echo off
REM Start IJAIKE chatbot backend (requires Docker Desktop running for MongoDB)
cd /d "%~dp0.."
echo === Starting MongoDB ===
docker compose -f docker/docker-compose.yml up -d
if errorlevel 1 (
    echo ERROR: Docker Desktop is not running. Start Docker Desktop first, then run this script again.
    pause
    exit /b 1
)
cd backend
echo === Seeding database ===
call .venv\Scripts\python.exe -m scripts.setup_db
echo === Starting API on http://localhost:8000 ===
call .venv\Scripts\uvicorn.exe app.main:app --reload --port 8000

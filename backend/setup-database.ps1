# IJAIKE Chatbot — MongoDB setup (PowerShell)
# Run from: D:\web-projects\chatbot\backend

$ErrorActionPreference = "Stop"
Write-Host "=== IJAIKE MongoDB Setup ===" -ForegroundColor Cyan

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
    .\.venv\Scripts\pip install -r requirements-core.txt
}

$python = ".\.venv\Scripts\python.exe"

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
}

New-Item -ItemType Directory -Force -Path "uploads", "data\chroma" | Out-Null

Write-Host "Testing MongoDB connection..." -ForegroundColor Cyan
& $python -m scripts.test_db_connection

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Could not connect to MongoDB." -ForegroundColor Red
    Write-Host ""
    Write-Host "Start MongoDB with Docker (from project root):" -ForegroundColor Yellow
    Write-Host "  docker compose -f docker/docker-compose.yml up -d"
    Write-Host ""
    Write-Host "Or set MONGODB_URL in backend\.env for MongoDB Atlas / local install."
    Write-Host "Then run: .\setup-database.ps1" -ForegroundColor Yellow
    exit 1
}

Write-Host "Seeding database..." -ForegroundColor Cyan
& $python -m scripts.setup_db

Write-Host ""
Write-Host "Done! Start API:" -ForegroundColor Green
Write-Host "  .\.venv\Scripts\uvicorn app.main:app --reload --port 8000"

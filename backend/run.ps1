# Start AI Feedback System backend (Sprint 2)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python not found. Install Python 3.11+ from https://www.python.org/downloads/ and enable 'Add to PATH'."
    exit 1
}

if (-not (Test-Path ".venv")) {
    python -m venv .venv
}

& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if (-not (Test-Path ".env")) {
    Copy-Item .env.example .env
    Write-Host "Created .env — update SECRET_KEY and ADMIN_PASSWORD before demo."
}

& .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

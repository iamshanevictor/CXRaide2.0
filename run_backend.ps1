# Run the CXRaide backend locally.

if (-not (Test-Path -Path ".\.venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Green
    python -m venv .venv
}

Write-Host "Activating virtual environment..." -ForegroundColor Green
.\.venv\Scripts\Activate.ps1

Write-Host "Installing backend dependencies..." -ForegroundColor Green
pip install -r server\requirements.txt

$env:FLASK_ENV = "development"
$env:PORT = "5000"
$env:FRONTEND_URL = "http://localhost:5173"
$env:SECRET_KEY = "local-dev-secret-change-me"
$env:USE_MOCK_MODELS = "true"
$env:ALLOW_DEV_LOGIN = "true"

Set-Location -Path ".\server"

Write-Host "Starting Flask server at http://localhost:5000" -ForegroundColor Green
flask run --host=0.0.0.0 --port=5000 --reload

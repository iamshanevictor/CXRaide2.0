# PowerShell script to set up and run the CXRaide backend without Docker

# Create virtual environment if it doesn't exist
if (-not (Test-Path -Path ".\venv")) {
    Write-Host "Creating Python virtual environment..." -ForegroundColor Green
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Green
.\venv\Scripts\Activate.ps1

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Green
pip install -r server\requirements.local.txt

# Set environment variables (no database required)
$env:FLASK_ENV = "development"
$env:SECRET_KEY = "ecd500797722db1d8de3f1330c6890105c13aa4bbe4d1cce"
$env:USE_MOCK_MODELS = "false"
$env:RENDER = "false"

# Change to server directory
Set-Location -Path ".\server"

# Run Flask application
Write-Host "Starting Flask server..." -ForegroundColor Green
flask run --host=0.0.0.0 --port=5000 --reload

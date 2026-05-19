# Run the CXRaide frontend locally.

Set-Location -Path ".\client"

$env:VITE_API_BASE_URL = "http://localhost:5000"

if (-not (Test-Path -Path ".\node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Green
    npm install
}

Write-Host "Starting Vite dev server at http://localhost:5173" -ForegroundColor Green
npm run dev

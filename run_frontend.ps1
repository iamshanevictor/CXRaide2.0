# PowerShell script to set up and run the CXRaide frontend without Docker

# Change to client directory
Set-Location -Path ".\client"

# Set environment variables
$env:VITE_API_URL = "http://localhost:8080"

# Install dependencies if node_modules doesn't exist
if (-not (Test-Path -Path ".\node_modules")) {
    Write-Host "Installing Node.js dependencies..." -ForegroundColor Green
    npm install
}

# Run Vue development server
Write-Host "Starting Vue.js development server..." -ForegroundColor Green
npm run serve

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

# Check if MongoDB is running locally
$mongoRunning = $false
try {
    # Try to connect to local MongoDB
    $testConnection = New-Object System.Net.Sockets.TcpClient
    $testConnection.Connect("localhost", 27017)
    $mongoRunning = $true
    $testConnection.Close()
    Write-Host "Local MongoDB is running. Using local database." -ForegroundColor Green
    $mongoUri = "mongodb://localhost:27017"
}
catch {
    Write-Host "Local MongoDB is not running. Using MongoDB Atlas instead." -ForegroundColor Yellow
    # Use the MongoDB Atlas connection string from the Docker configuration
    $mongoUri = "mongodb+srv://cxraide-admin:OhbYaa4VRXmEolR9@cxraide.av2tc7q.mongodb.net/?retryWrites=true&w=majority&appName=CXRaide"
}

# Set environment variables
$env:FLASK_ENV = "development"
$env:MONGO_URI = $mongoUri
$env:DB_NAME = "cxraide"
$env:SECRET_KEY = "ecd500797722db1d8de3f1330c6890105c13aa4bbe4d1cce"
$env:USE_MOCK_MODELS = "false"
$env:RENDER = "false"

# Change to server directory
Set-Location -Path ".\server"

# Run Flask application
Write-Host "Starting Flask server..." -ForegroundColor Green
flask run --host=0.0.0.0 --port=8080 --reload

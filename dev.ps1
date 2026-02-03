# PowerShell script to manage Docker environment for CXRaide development and production

# Show usage
function Show-Help {
    Write-Host "CXRaide Docker Development Helper" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\dev.ps1 [command]" -ForegroundColor White
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  dev        Start in development mode with hot-reloading"
    Write-Host "  dev-build  Rebuild and start in development mode"
    Write-Host "  prod       Start in production mode"
    Write-Host "  prod-build Rebuild and start in production mode"
    Write-Host "  down       Stop all containers"
    Write-Host "  clean      Stop containers and remove volumes"
    Write-Host "  help       Show this help message"
}

# Check if Docker is running
function Test-Docker {
    try {
        docker info | Out-Null
        return $true
    }
    catch {
        Write-Host "Docker does not seem to be running. Please start Docker first." -ForegroundColor Red
        return $false
    }
}

# Start in development mode
function Start-DevMode {
    if (Test-Docker) {
        Write-Host "Starting in development mode (with rebuild to pick up new deps)..." -ForegroundColor Green
        docker-compose up --build
    }
}

# Rebuild and start in development mode
function Start-DevBuild {
    if (Test-Docker) {
        Write-Host "Rebuilding and starting in development mode..." -ForegroundColor Green
        docker-compose up --build
    }
}

# Start in production mode
function Start-ProdMode {
    if (Test-Docker) {
        Write-Host "Starting in production mode..." -ForegroundColor Green
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
    }
}

# Rebuild and start in production mode
function Start-ProdBuild {
    if (Test-Docker) {
        Write-Host "Rebuilding and starting in production mode..." -ForegroundColor Green
        docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build
    }
}

# Stop all containers
function Stop-Containers {
    if (Test-Docker) {
        Write-Host "Stopping containers..." -ForegroundColor Yellow
        docker-compose down
    }
}

# Stop containers and remove volumes
function Clean-Environment {
    if (Test-Docker) {
        Write-Host "Stopping containers and removing volumes..." -ForegroundColor Yellow
        docker-compose down -v
    }
}

# Main script logic
$command = $args[0]

switch ($command) {
    "dev" { Start-DevMode }
    "dev-build" { Start-DevBuild }
    "prod" { Start-ProdMode }
    "prod-build" { Start-ProdBuild }
    "down" { Stop-Containers }
    "clean" { Clean-Environment }
    default { Show-Help }
} 
# PowerShell script to manage Docker environment for CXRaide development and production

function Get-ComposeCommand {
    # Prefer Docker Compose v2 (`docker compose`) but support legacy `docker-compose`
    try {
        docker compose version | Out-Null
        return @("docker", "compose")
    }
    catch {
        try {
            docker-compose version | Out-Null
            return @("docker-compose")
        }
        catch {
            return $null
        }
    }
}

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

function Invoke-Compose {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Args
    )

    $composeCmd = Get-ComposeCommand
    if (-not $composeCmd) {
        Write-Host "Docker Compose not found. Install Docker Desktop (recommended) or docker-compose." -ForegroundColor Red
        exit 1
    }

    if ($composeCmd.Count -eq 2) {
        & $composeCmd[0] $composeCmd[1] @Args
    }
    else {
        & $composeCmd[0] @Args
    }
}

# Start in development mode
function Start-DevMode {
    if (Test-Docker) {
        Write-Host "Starting in development mode (with rebuild to pick up new deps)..." -ForegroundColor Green
        if (Test-Path -Path "./firebase-adminsdk.json") {
            Invoke-Compose -Args @("-f", "docker-compose.yml", "-f", "docker-compose.firebase.yml", "up", "--build")
        }
        else {
            Invoke-Compose -Args @("-f", "docker-compose.yml", "up", "--build")
        }
    }
}

# Rebuild and start in development mode
function Start-DevBuild {
    if (Test-Docker) {
        Write-Host "Rebuilding and starting in development mode..." -ForegroundColor Green
        if (Test-Path -Path "./firebase-adminsdk.json") {
            Invoke-Compose -Args @("-f", "docker-compose.yml", "-f", "docker-compose.firebase.yml", "up", "--build")
        }
        else {
            Invoke-Compose -Args @("-f", "docker-compose.yml", "up", "--build")
        }
    }
}

# Start in production mode
function Start-ProdMode {
    if (Test-Docker) {
        Write-Host "Starting in production mode..." -ForegroundColor Green
        if (Test-Path -Path "./firebase-adminsdk.json") {
            Invoke-Compose -Args @("-f", "docker-compose.yml", "-f", "docker-compose.firebase.yml", "-f", "docker-compose.prod.yml", "up")
        }
        else {
            Invoke-Compose -Args @("-f", "docker-compose.yml", "-f", "docker-compose.prod.yml", "up")
        }
    }
}

# Rebuild and start in production mode
function Start-ProdBuild {
    if (Test-Docker) {
        Write-Host "Rebuilding and starting in production mode..." -ForegroundColor Green
        if (Test-Path -Path "./firebase-adminsdk.json") {
            Invoke-Compose -Args @("-f", "docker-compose.yml", "-f", "docker-compose.firebase.yml", "-f", "docker-compose.prod.yml", "up", "--build")
        }
        else {
            Invoke-Compose -Args @("-f", "docker-compose.yml", "-f", "docker-compose.prod.yml", "up", "--build")
        }
    }
}

# Stop all containers
function Stop-Containers {
    if (Test-Docker) {
        Write-Host "Stopping containers..." -ForegroundColor Yellow
        Invoke-Compose -Args @("down")
    }
}

# Stop containers and remove volumes
function Clean-Environment {
    if (Test-Docker) {
        Write-Host "Stopping containers and removing volumes..." -ForegroundColor Yellow
        Invoke-Compose -Args @("down", "-v")
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
# CXRaide 2.0

A web application for chest X-ray annotation and AI-assisted analysis.

## Development Setup

### Quick Start with Docker

This project uses Docker for both development and production. The development environment is set up with hot-reloading for faster development iterations.

#### Using Windows (PowerShell)

```powershell
# Start development environment with hot-reloading
.\dev.ps1 dev

# Rebuild and start development environment
.\dev.ps1 dev-build

# Start production environment
.\dev.ps1 prod

# Rebuild and start production environment
.\dev.ps1 prod-build

# Stop all containers
.\dev.ps1 down

# Stop containers and remove volumes
.\dev.ps1 clean
```

#### Using Linux/Mac (Bash)

```bash
# Make the script executable (first time only)
chmod +x dev.sh

# Start development environment with hot-reloading
./dev.sh dev

# Rebuild and start development environment
./dev.sh dev-build

# Start production environment
./dev.sh prod

# Rebuild and start production environment
./dev.sh prod-build

# Stop all containers
./dev.sh down

# Stop containers and remove volumes
./dev.sh clean
```

### Development Workflow

1. Start the development environment: `.\dev.ps1 dev-build` (PowerShell) or `./dev.sh dev-build` (Bash)
2. The frontend will be available at http://localhost:8080
3. The backend API will be available at http://localhost:5000
4. Edit files in the `client/` or `server/` directories - changes will automatically be reflected
5. No need to restart containers for most changes due to hot-reloading

### Deploying to Production

For deployment to platforms like Render.com:

1. Test the production build locally: `.\dev.ps1 prod-build` (PowerShell) or `./dev.sh prod-build` (Bash)
2. Push your changes to GitHub
3. Render.com will automatically deploy from your GitHub repository

## Project Structure

- `client/` - Vue.js frontend application
- `server/` - Flask backend API
- `docker-compose.yml` - Main Docker Compose file for development
- `docker-compose.prod.yml` - Production overrides for Docker Compose
- `dev.ps1` - PowerShell helper script for Windows users
- `dev.sh` - Bash helper script for Linux/Mac users

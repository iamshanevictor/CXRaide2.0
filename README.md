# CXRaide 2.0

A web application for chest X-ray annotation and AI-assisted analysis, featuring a Vue.js frontend and Flask backend with MongoDB database.

## Features

- Chest X-ray image upload and management
- AI-assisted analysis using trained models
- Local MongoDB database for data persistence
- Docker-based development and production environments
- Hot-reloading for rapid development
- Production-ready deployment configuration

## Development Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for local development)
- Node.js 16+ (for local development)
- MongoDB (optional, for local development)

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

### Local Development Setup

1. Clone the repository
2. Set up environment variables in `.env` file
3. Install dependencies:
   ```bash
   # Backend dependencies
   cd server
   pip install -r requirements.txt
   pip install -r requirements.local.txt

   # Frontend dependencies
   cd ../client
   npm install
   ```
4. Start MongoDB locally or use Docker container
5. Initialize the database:
   ```bash
   cd server
   python init_db.py
   ```

### Development Workflow

1. Start the development environment: `.\dev.ps1 dev-build` (PowerShell) or `./dev.sh dev-build` (Bash)
2. The frontend will be available at http://localhost:8080
3. The backend API will be available at http://localhost:5000
4. MongoDB will be available at mongodb://localhost:27017
5. Edit files in the `client/` or `server/` directories - changes will automatically be reflected
6. No need to restart containers for most changes due to hot-reloading

## Project Structure

- `client/` - Vue.js frontend application
  - Modern UI components
  - Responsive design
  - Real-time updates

- `server/` - Flask backend API
  - RESTful endpoints
  - AI model integration
  - MongoDB integration
  - Model caching system

- Configuration Files:
  - `docker-compose.yml` - Main Docker Compose file for development
  - `docker-compose.prod.yml` - Production overrides for Docker Compose
  - `dev.ps1` - PowerShell helper script for Windows users
  - `dev.sh` - Bash helper script for Linux/Mac users
  - `.env` - Environment variables configuration

## Database

The application uses MongoDB as its primary database:
- Development: Runs in a Docker container
- Production: Configured through environment variables
- Data persistence through Docker volumes
- Automatic initialization through `init_db.py`

## AI Models

The application includes pre-trained models for chest X-ray analysis:
- Models are cached in `.model_cache/` directory
- Automatic model downloading and setup
- Support for multiple model versions
- Configurable through environment variables

## Deployment

For deployment to platforms like Render.com:
1. Test the production build locally: `.\dev.ps1 prod-build` (PowerShell) or `./dev.sh prod-build` (Bash)
2. Push your changes to GitHub
3. Render.com will automatically deploy from your GitHub repository

See `RENDER_DEPLOYMENT.md` for detailed deployment instructions.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]

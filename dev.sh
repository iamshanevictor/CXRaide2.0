#!/bin/bash

# Script to manage Docker environment for CXRaide development and production

# Show usage
show_help() {
  echo "CXRaide Docker Development Helper"
  echo ""
  echo "Usage: ./dev.sh [command]"
  echo ""
  echo "Commands:"
  echo "  dev        Start in development mode with hot-reloading"
  echo "  dev-build  Rebuild and start in development mode"
  echo "  prod       Start in production mode"
  echo "  prod-build Rebuild and start in production mode"
  echo "  down       Stop all containers"
  echo "  clean      Stop containers and remove volumes"
  echo "  help       Show this help message"
}

# Check if Docker is running
check_docker() {
  if ! docker info > /dev/null 2>&1; then
    echo "Docker does not seem to be running. Please start Docker first."
    exit 1
  fi
}

# Start in development mode
dev_mode() {
  check_docker
  echo "Starting in development mode..."
  docker-compose up
}

# Rebuild and start in development mode
dev_build() {
  check_docker
  echo "Rebuilding and starting in development mode..."
  docker-compose up --build
}

# Start in production mode
prod_mode() {
  check_docker
  echo "Starting in production mode..."
  docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
}

# Rebuild and start in production mode
prod_build() {
  check_docker
  echo "Rebuilding and starting in production mode..."
  docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build
}

# Stop all containers
down() {
  check_docker
  echo "Stopping containers..."
  docker-compose down
}

# Stop containers and remove volumes
clean() {
  check_docker
  echo "Stopping containers and removing volumes..."
  docker-compose down -v
}

# Main script logic
case "$1" in
  dev)
    dev_mode
    ;;
  dev-build)
    dev_build
    ;;
  prod)
    prod_mode
    ;;
  prod-build)
    prod_build
    ;;
  down)
    down
    ;;
  clean)
    clean
    ;;
  help|*)
    show_help
    ;;
esac 
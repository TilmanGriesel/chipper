#!/bin/bash

set -e

DOCKER_COMPOSE_FILE="docker/docker-compose.yml"

function show_usage() {
    echo "Usage: $0 <command> [args]"
    echo ""
    echo "Commands:"
    echo "  up            - Start containers in detached mode"
    echo "  down          - Stop containers"
    echo "  logs          - Show container logs"
    echo "  ps            - Show container status"
    echo "  rebuild       - Rebuild and recreate containers"
    echo "  clean         - Remove containers, volumes, and orphans"
    echo "  embed [args]  - Run embed tool with optional arguments"
    echo "  scrape [args] - Run scrape tool with optional arguments"
    echo "  dev-api       - Start API in development mode"
    echo "  dev-web       - Start web service in development mode"
    echo "  format        - Run pre-commit formatting hooks"
}

function check_docker_compose() {
    if ! [ -f "$DOCKER_COMPOSE_FILE" ]; then
        echo "Error: Docker Compose file not found at $DOCKER_COMPOSE_FILE"
        exit 1
    fi
}

case "$1" in
    "up")
        check_docker_compose
        docker-compose -f "$DOCKER_COMPOSE_FILE" -p chipper up -d
        ;;
        
    "down")
        check_docker_compose
        docker-compose -f "$DOCKER_COMPOSE_FILE" down
        ;;
        
    "logs")
        check_docker_compose
        docker-compose -f "$DOCKER_COMPOSE_FILE" logs -f
        ;;
        
    "ps")
        check_docker_compose
        docker-compose -f "$DOCKER_COMPOSE_FILE" ps
        ;;
        
    "rebuild")
        check_docker_compose
        docker-compose -f "$DOCKER_COMPOSE_FILE" down -v --remove-orphans
        docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
        docker-compose -f "$DOCKER_COMPOSE_FILE" up -d --force-recreate
        ;;
        
    "clean")
        check_docker_compose
        docker-compose -f "$DOCKER_COMPOSE_FILE" down -v --remove-orphans
        ;;
        
    "embed")
        shift
        cd tools/embed && ./run.sh "$@"
        ;;
        
    "scrape")
        shift
        cd tools/scrape && ./run.sh "$@"
        ;;
        
    "dev-api")
        cd services/api && make dev
        ;;
        
    "dev-web")
        cd services/web && make dev
        ;;
        
    "format")
        echo "Running pre-commit hooks for formatting..."
        pre-commit run --all-files
        echo "Formatting completed successfully!"
        ;;
        
    *)
        show_usage
        exit 1
        ;;
esac
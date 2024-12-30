#!/bin/bash

set -e

DOCKER_COMPOSE_FILE="docker/docker-compose.yml"
USER_DOCKER_COMPOSE_FILE="docker/user.docker-compose.yml"

function show_usage() {
    echo "Usage: $0 <command> [args]"
    echo ""
    echo "Options:"
    echo "  -f, --file         - Specify custom docker-compose file path"
    echo ""
    echo "Commands:"
    echo "  up                  - Start containers in detached mode"
    echo "  down                - Stop containers"
    echo "  logs                - Show container logs"
    echo "  ps                  - Show container status"
    echo "  rebuild             - Rebuild and recreate containers"
    echo "  clean               - Remove containers, volumes, and orphans"
    echo "  embed [args]        - Run embed tool with optional arguments"
    echo "  embed-testdata      - Run embed tool with internal testdata"
    echo "  scrape [args]       - Run scrape tool with optional arguments"
    echo "  dev-api             - Start API in development mode"
    echo "  dev-web             - Start web service in development mode"
    echo "  css                 - Watch and rebuild CSS files"
    echo "  format              - Run pre-commit formatting hooks"
}

function check_docker_running() {
    if ! docker info &> /dev/null; then
        echo "Error: Docker is not running. Please start Docker and try again."
        exit 1
    fi
}

function check_node_available() {
    if ! command -v node &> /dev/null; then
        echo "Error: 'node' is not available. Please install it and try again."
        exit 1
    fi
}

function check_make_available() {
    if ! command -v make &> /dev/null; then
        echo "Error: 'make' is not available. Please install it and try again."
        exit 1
    fi
}

COMPOSE_FILES=(-f "$DOCKER_COMPOSE_FILE")
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--file)
            if [ -f "$2" ]; then
                COMPOSE_FILES=(-f "$2")
            else
                echo "Error: Docker compose file '$2' not found"
                exit 1
            fi
            shift 2
            ;;
        *)
            break
            ;;
    esac
done

if [ -f "$USER_DOCKER_COMPOSE_FILE" ]; then
    echo "Found user compose file"
    COMPOSE_FILES+=(-f "$USER_DOCKER_COMPOSE_FILE")
fi

case "$1" in
    "up")
        check_docker_running
        docker-compose "${COMPOSE_FILES[@]}" -p chipper up -d
        ;;
        
    "down")
        check_docker_running
        docker-compose "${COMPOSE_FILES[@]}" down
        ;;
        
    "logs")
        check_docker_running
        docker-compose "${COMPOSE_FILES[@]}" logs -f
        ;;
        
    "ps")
        check_docker_running
        docker-compose "${COMPOSE_FILES[@]}" ps
        ;;
        
    "rebuild")
        check_docker_running
        docker-compose "${COMPOSE_FILES[@]}" down -v --remove-orphans
        docker-compose "${COMPOSE_FILES[@]}" build --no-cache
        docker-compose "${COMPOSE_FILES[@]}" up -d --force-recreate
        ;;
        
    "clean")
        check_docker_running
        docker-compose "${COMPOSE_FILES[@]}" down -v --remove-orphans
        ;;
        
    "embed")
        shift
        check_docker_running
        cd tools/embed && ./run.sh "$@"
        ;;
    
    "embed-testdata")
        shift
        check_docker_running
        cd tools/embed && ./run.sh $(pwd)/testdata
        ;;

    "scrape")
        shift
        check_docker_running
        cd tools/scrape && ./run.sh "$@"
        ;;
        
    "dev-api")
        check_make_available
        cd services/api && make dev
        ;;
        
    "dev-web")
        check_make_available
        cd services/web && make dev
        ;;

    "css")
        check_node_available
        check_make_available
        cd services/web && make build-watch-css
        ;;

    "cli")
        shift
        cd tools/cli && ./run.sh "$@"
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
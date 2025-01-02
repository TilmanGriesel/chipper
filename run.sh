#!/bin/bash

set -euo pipefail


DOCKER_COMPOSE_FILE_BASE="docker/docker-compose.base.yml"
DOCKER_COMPOSE_FILE="docker/docker-compose.dev.yml"
USER_DOCKER_COMPOSE_FILE="docker/docker-compose.user.yml"
PROJECT_NAME="chipper"
LOCAL_URL="http://localhost:21200"

function show_usage() {
    echo "Usage: $0 <command> [args]"
    echo ""
    echo "Options:"
    echo "  -f, --file         - Specify custom docker-compose file path"
    echo ""
    echo "Commands:"
    echo "  up                  - Start containers in detached mode"
    echo "  down                - Stop containers"
    echo "  rebuild             - Clean, rebuild and recreate images and containers"
    echo "  clean-volumes       - Delete all volumes"
    echo "  logs                - Show container logs"
    echo "  ps                  - Show container status"
    echo "  embed [args]        - Run embed tool with optional arguments"
    echo "  embed-testdata      - Run embed tool with internal testdata"
    echo "  scrape [args]       - Run scrape tool with optional arguments"
    echo "  dev-api             - Start API in development mode"
    echo "  dev-web             - Start web service in development mode"
    echo "  css                 - Watch and rebuild CSS files"
    echo "  format              - Run pre-commit formatting hooks"
    echo "  browser             - Open web-interface in local browser"
    echo "  cli                 - Run cli interface"
    echo "  docs-dev            - Run local vitepress server"
}

function check_dependency() {
    local cmd=$1
    local message=${2:-"Error: '$cmd' is not available. Please install it and try again."}
    
    if ! command -v "$cmd" &> /dev/null; then
        echo "$message"
        exit 1
    fi
}

function docker_compose_cmd() {
    docker-compose "${COMPOSE_FILES[@]}" "$@"
}

function run_in_directory() {
    local dir=$1
    shift
    cd "$dir" && "$@"
}

function open_browser() {
    case "$(uname -s)" in
        Darwin|Linux)
            xdg-open "$LOCAL_URL" 2>/dev/null || open "$LOCAL_URL"
            ;;
        MINGW*|MSYS*|CYGWIN*)
            start "$LOCAL_URL"
            ;;
    esac
}

COMPOSE_FILES=(-f "$DOCKER_COMPOSE_FILE_BASE")
COMPOSE_FILES+=(-f "$DOCKER_COMPOSE_FILE")

while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--file)
            if [ -f "$2" ]; then
                COMPOSE_FILES+=(-f "$2") 
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

[ -f "$USER_DOCKER_COMPOSE_FILE" ] && {
    echo "Found user compose file"
    COMPOSE_FILES+=(-f "$USER_DOCKER_COMPOSE_FILE")
}

if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

case "$1" in
    up|down|logs|ps|rebuild|clean|embed*|scrape)
        check_dependency docker "Error: Docker is not running. Please start Docker and try again."
        ;;
    dev-api|dev-web|css)
        check_dependency make
        ;;
    css)
        check_dependency node
        ;;
esac

case "$1" in
    "up")
        docker compose -p $PROJECT_NAME down --remove-orphans
        docker_compose_cmd -p $PROJECT_NAME up -d
        ;;
    "down")
        docker compose -p $PROJECT_NAME down --remove-orphans
        ;;
    "rebuild")
        echo "Stopping containers..."
        docker compose -p $PROJECT_NAME down --remove-orphans
    
        echo "Removing project-related images..."
        docker images --filter "reference=$PROJECT_NAME*" -q | xargs -r docker rmi -f
        echo "Project images cleaned"
        
        echo "Rebuilding containers..."
        docker_compose_cmd build --no-cache
        
        echo "Starting containers..."
        docker_compose_cmd -p $PROJECT_NAME up -d --force-recreate
        
        echo "Clean and rebuild complete!"
        ;;
    "clean-volumes")
        echo "Stopping containers and removing volumes..."
        docker compose -p $PROJECT_NAME down -v --remove-orphans
        
        echo "Cleaning up volume directories..."
        rm -rfv docker/volumes
        echo "Volume directories cleaned"
        
        echo "Clean complete!"
        ;;
    "embed-testdata")
        run_in_directory "tools/embed" ./run.sh "$(pwd)/tools/embed/testdata"
        ;;
    "embed")
        shift
        run_in_directory "tools/embed" ./run.sh "$@"
        ;;
    "scrape")
        shift
        run_in_directory "tools/scrape" ./run.sh "$@"
        ;;
    "dev-api")
        run_in_directory "services/api" make dev
        ;;
    "dev-web")
        run_in_directory "services/web" make dev
        ;;
    "css")
        run_in_directory "services/web" make build-watch-css
        ;;
    "format")
        echo "Running pre-commit hooks for formatting..."
        pre-commit run --all-files
        echo "Formatting completed successfully!"
        ;;
    "browser")
        open_browser
        ;;
    "cli")
        shift
        run_in_directory "tools/cli" ./run.sh "$@"
        ;;
    "docs-dev")
        echo "Starting vitepress..."
        yarn add -D vitepress
        yarn docs:dev
        ;;
    *)
        show_usage
        exit 1
        ;;
esac


#!/bin/bash

set -e

DOCKER_COMPOSE_FILE="docker/docker-compose.yml"
USER_DOCKER_COMPOSE_FILE="docker/user.docker-compose.yml"
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
    echo "  rebuild             - Rebuild and recreate containers"
    echo "  clean               - Remove containers, volumes, and orphans"
    echo "  logs                - Show container logs"
    echo "  ps                  - Show container status"
    echo "  embed [args]        - Run embed tool with optional arguments"
    echo "  embed-testdata      - Run embed tool with internal testdata"
    echo "  scrape [args]       - Run scrape tool with optional arguments"
    echo "  dev-api             - Start API in development mode"
    echo "  dev-web             - Start web service in development mode"
    echo "  css                 - Watch and rebuild CSS files"
    echo "  format              - Run pre-commit formatting hooks"
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

[ -f "$USER_DOCKER_COMPOSE_FILE" ] && {
    echo "Found user compose file"
    COMPOSE_FILES+=(-f "$USER_DOCKER_COMPOSE_FILE")
}

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
    "clean")
        docker compose -p $PROJECT_NAME down -v --remove-orphans
        echo "Cleaning up volume directories..."
        rm -rfv docker/volumes
        echo "Volume directories cleaned"
        ;;
    "rebuild")
        docker compose -p $PROJECT_NAME down --remove-orphans
        docker_compose_cmd build --no-cache
        docker_compose_cmd up -d --force-recreate
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
    *)
        show_usage
        exit 1
        ;;
esac
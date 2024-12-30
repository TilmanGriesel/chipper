#!/bin/bash

set -e

DOCKER_COMPOSE_FILE="docker/docker-compose.yml"
USER_DOCKER_COMPOSE_FILE="docker/user.docker-compose.yml"
PROJECT_NAME="chipper"

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
    "down"|"clean")
        docker compose -p $PROJECT_NAME down ${1=="clean"? "-v" : ""} --remove-orphans
        ;;
    "logs")
        docker_compose_cmd logs -f
        ;;
    "ps")
        docker_compose_cmd ps
        ;;
    "rebuild")
        docker compose -p $PROJECT_NAME down --remove-orphans
        docker_compose_cmd build --no-cache
        docker_compose_cmd up -d --force-recreate
        ;;
    "embed")
        shift
        run_in_directory "tools/embed" ./run.sh "$@"
        ;;
    "embed-testdata")
        run_in_directory "tools/embed" ./run.sh "$(pwd)/testdata"
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
    *)
        show_usage
        exit 1
        ;;
esac
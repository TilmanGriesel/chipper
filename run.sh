#!/bin/bash

set -euo pipefail

# Configuration
readonly DOCKER_COMPOSE_FILE_BASE="docker/docker-compose.base.yml"
readonly DOCKER_COMPOSE_FILE="docker/docker-compose.dev.yml"
readonly USER_DOCKER_COMPOSE_FILE="docker/docker-compose.user.yml"
readonly PROJECT_NAME="chipper"
readonly LOCAL_URL="http://localhost:21200"
readonly ELASTICVUE_URL="http://localhost:21230"
readonly SCRIPT_VERSION="1.1.0"


function show_welcome() {
    echo ""
    # purple
    echo -e "\e[35m"
    echo "        __    _                      "
    echo "  _____/ /_  (_)___  ____  ___  _____"
    echo " / ___/ __ \/ / __ \/ __ \/ _ \/ ___/"
    echo "/ /__/ / / / / /_/ / /_/ /  __/ /    "
    echo "\___/_/ /_/_/ .___/ .___/\___/_/     "
    echo "           /_/   /_/                 "
    echo -e "\e[0m"
    # blue
    echo -e "\e[34m        Chipper Run v${SCRIPT_VERSION}\e[0m"
    echo ""
}

show_welcome

function show_usage() {
    cat << EOF
Usage: $0 <command> [args]

Options:
  -f, --file         - Specify custom docker-compose file path

Commands:
  up                  - Start containers in detached mode
  down                - Stop containers
  rebuild             - Clean, rebuild and recreate images and containers
  clean-volumes       - Delete all volumes
  clean-env           - Delete all dotfiles like .env and .systemprompt
  logs                - Show container logs
  ps                  - Show container status
  embed [args]        - Run embed tool with optional arguments
  embed-testdata      - Run embed tool with internal testdata
  scrape [args]       - Run scrape tool with optional arguments
  dev-api             - Start API in development mode
  dev-web             - Start web service in development mode
  css                 - Watch and rebuild CSS files
  format              - Run pre-commit formatting hooks
  browser             - Open web-interface in local browser
  evue                - Open elasticvue web-interface in local browser
  cli                 - Run cli interface
  dev-docs            - Run local vitepress server
EOF
}

function check_dependency() {
    local cmd="$1"
    local message="${2:-Error: '$cmd' is not available. Please install it and try again.}"
    
    if ! command -v "$cmd" &> /dev/null; then
        echo "$message" >&2
        exit 1
    fi
}

function check_directory() {
    local dir="$1"
    if [ ! -d "$dir" ]; then
        echo "Error: Directory '$dir' not found" >&2
        exit 1
    fi
}

function detect_docker_compose() {
    if docker compose version >/dev/null 2>&1; then
        echo "docker compose"
    elif docker-compose version >/dev/null 2>&1; then
        echo "docker-compose"
    else
        echo "Error: Neither 'docker compose' nor 'docker-compose' is available" >&2
    fi
}

DOCKER_COMPOSE_CMD=$(detect_docker_compose)

function docker_compose_cmd() {
    if [ "$DOCKER_COMPOSE_CMD" = "docker compose" ]; then
        docker compose "${COMPOSE_FILES[@]}" "$@"
    else
        docker-compose "${COMPOSE_FILES[@]}" "$@"
    fi
}

function run_in_directory() {
    local dir="$1"
    shift
    check_directory "$dir"
    (cd "$dir" && "$@")
}

function open_browser() {
    local url="$LOCAL_URL"
    case "$(uname -s)" in
        Darwin)
            open "$url"
            ;;
        Linux)
            if command -v xdg-open >/dev/null; then
                xdg-open "$url"
            else
                echo "Please install xdg-utils or manually open: $url"
            fi
            ;;
        MINGW*|MSYS*|CYGWIN*)
            start "$url"
            ;;
        *)
            echo "Unsupported operating system for automatic browser opening"
            echo "Please manually open: $url"
            ;;
    esac
}

function open_elasticvue() {
    local url="$ELASTICVUE_URL"
    case "$(uname -s)" in
        Darwin)
            open "$url"
            ;;
        Linux)
            if command -v xdg-open >/dev/null; then
                xdg-open "$url"
            else
                echo "Please install xdg-utils or manually open: $url"
            fi
            ;;
        MINGW*|MSYS*|CYGWIN*)
            start "$url"
            ;;
        *)
            echo "Unsupported operating system for automatic browser opening"
            echo "Please manually open: $url"
            ;;
    esac
}

function check_docker_running() {
    if ! docker info >/dev/null 2>&1; then
        echo "Error: Docker is not running. Please start Docker and try again." >&2
        exit 1
    fi
}

COMPOSE_FILES=(-f "$DOCKER_COMPOSE_FILE_BASE")
COMPOSE_FILES+=(-f "$DOCKER_COMPOSE_FILE")

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--file)
            if [ ! -f "$2" ]; then
                echo "Error: Docker compose file '$2' not found" >&2
                exit 1
            fi
            COMPOSE_FILES+=(-f "$2")
            shift 2
            ;;
        *)
            break
            ;;
    esac
done

# Check for user compose file
if [ -f "$USER_DOCKER_COMPOSE_FILE" ]; then
    echo "Found user compose file"
    COMPOSE_FILES+=(-f "$USER_DOCKER_COMPOSE_FILE")
fi

# Show usage if no command provided
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

# Pre-command dependency checks
case "$1" in
    up|down|logs|ps|rebuild|clean-volumes|embed*|scrape)
        check_docker_running
        ;;
    dev-api|dev-web)
        check_dependency make "Error: 'make' is required for development mode"
        check_directory "services/${1#dev-}"
        ;;
    css)
        check_dependency make
        check_dependency node
        check_directory "services/web"
        ;;
    format)
        check_dependency pre-commit
        ;;
esac

# Main command handling
case "$1" in
    "up")
        python env_setup.py
        if [ "$DOCKER_COMPOSE_CMD" = "docker compose" ]; then
            docker compose -p "$PROJECT_NAME" down --remove-orphans
        else
            if [ "$DOCKER_COMPOSE_CMD" = "docker compose" ]; then
            docker compose -p "$PROJECT_NAME" down --remove-orphans
        else
            docker-compose -p "$PROJECT_NAME" down --remove-orphans
        fi
        fi
        docker_compose_cmd -p "$PROJECT_NAME" up -d
        ;;
    "down")
        docker-compose -p "$PROJECT_NAME" down --remove-orphans
        ;;
    "rebuild")
        echo "Stopping containers..."
        docker-compose -p "$PROJECT_NAME" down --remove-orphans
    
        echo "Removing project-related images..."
        docker images --filter "reference=$PROJECT_NAME*" -q | xargs -r docker rmi -f
        echo "Project images cleaned"
        
        echo "Rebuilding containers..."
        docker_compose_cmd build --no-cache
        
        python env_setup.py

        echo "Starting containers..."
        docker_compose_cmd -p "$PROJECT_NAME" up -d --force-recreate
        
        echo "Clean and rebuild complete!"
        ;;
    "clean-volumes")
        python env_setup.py

        echo "Stopping containers and removing volumes..."
        docker_compose_cmd -p "$PROJECT_NAME" down -v --remove-orphans
        
        echo "Cleaning up volume directories..."
        rm -rfv docker/volumes
        echo "Volume directories cleaned"
        
        echo "Clean complete!"
        ;;
    "clean-env")
        echo "Cleaning environment files..."
        python env_setup.py --clean
        ;;
    "logs")
        docker_compose_cmd -p "$PROJECT_NAME" logs -f
        ;;
    "ps")
        docker_compose_cmd -p "$PROJECT_NAME" ps
        ;;
    "embed-testdata")
        run_in_directory "tools/embed" ./run.sh "$(pwd)/tools/embed/testdata"
        ;;
    "embed")
        shift
        if [ $# -eq 0 ]; then
            echo "Error: embed command requires arguments" >&2
            exit 1
        fi
        run_in_directory "tools/embed" ./run.sh "$@"
        ;;
    "scrape")
        shift
        if [ $# -eq 0 ]; then
            echo "Error: scrape command requires arguments" >&2
            exit 1
        fi
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
    "evue")
        open_elasticvue
        ;;
    "cli")
        shift
        run_in_directory "tools/cli" ./run.sh "$@"
        ;;
    "dev-docs")
        shift
        echo "Starting vitepress..."
        yarn add -D vitepress
        yarn docs:dev "$@"
        ;;
    *)
        show_usage
        exit 1
        ;;
esac

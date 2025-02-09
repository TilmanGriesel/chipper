#!/bin/bash

set -euo pipefail

# configuration
readonly DOCKER_COMPOSE_FILE_BASE="docker/docker-compose.base.yml"
readonly DOCKER_COMPOSE_FILE="docker/docker-compose.dev.yml"
readonly USER_DOCKER_COMPOSE_FILE="docker/docker-compose.user.yml"
readonly PROJECT_NAME="chipper"
readonly LOCAL_URL="http://localhost:21200"
readonly ELASTICVUE_URL="http://localhost:21230"
readonly SCRIPT_VERSION="1.4.0"

# container engine configuration
CONTAINER_ENGINE="${CONTAINER_ENGINE:-docker}"

# common messages
readonly WARN_CLEAN_PROMPT="⚠️  WARNING: This will delete all %s. Are you sure? [y/N] "
readonly ERR_DIR_NOT_FOUND="Error: Directory '%s' not found"
readonly ERR_CMD_NOT_FOUND="Error: '%s' is not available. Please install it and try again."
readonly ERR_ENGINE_NOT_RUNNING="Error: %s is not running. Please start %s and try again."
readonly ERR_COMPOSE_FILE_NOT_FOUND="Error: Docker compose file '%s' not found"
readonly ERR_INVALID_ENGINE="Error: Invalid container engine '%s'. Supported engines: docker, podman"

function show_welcome() {
    printf "\n"
    printf "\033[35m"
    printf "        __    _                      \n"
    printf "  _____/ /_  (_)___  ____  ___  _____\n"
    printf " / ___/ __ \/ / __ \/ __ \/ _ \/ ___/\n"
    printf "/ /__/ / / / / /_/ / /_/ /  __/ /    \n"
    printf "\___/_/ /_/_/ .___/ .___/\___/_/     \n"
    printf "           /_/   /_/                 \n"
    printf "\033[0m\n"
    printf "\033[34m        Chipper Run v%s\033[0m\n" "${SCRIPT_VERSION}"
    printf "\033[34m        Using %s engine\033[0m\n" "${CONTAINER_ENGINE}"
    printf "\n"
}

show_welcome

function show_usage() {
    cat << EOF
Usage: $0 <command> [args]

Options:
  -f, --file         - Specify custom docker-compose file path
  -e, --engine       - Specify container engine (docker|podman)

Commands:
  config              - Launch configuration utility
  up                  - Start containers in detached mode
  down                - Stop containers
  rebuild             - Clean, rebuild and recreate images and containers
  logs                - Show container logs
  ps                  - Show container status
  env                 - Create or update all dotfiles like .env and .systemprompt
  clean-full          - Cleans all project related files, including images, volumes and env files
  clean-volumes       - Delete all volumes
  clean-env           - Delete all dotfiles like .env and .systemprompt
  embed [args]        - Run embed tool with optional arguments
  embed-testdata      - Run embed tool with internal testdata
  scrape [args]       - Run scrape tool with optional arguments
  dev-api             - Start API in development mode
  dev-web             - Start web service in development mode
  dev-docs            - Run local vitepress server
  css                 - Watch and rebuild CSS files
  format              - Run pre-commit formatting hooks
  browser             - Open web-interface in local browser
  evue                - Open elasticvue web-interface in local browser
  cli                 - Run cli interface
EOF
}

function error_exit() {
    echo "$1" >&2
    exit 1
}

function confirm_clean() {
    local target="$1"
    printf "$WARN_CLEAN_PROMPT" "$target"
    read -r response
    case "$response" in
        [yY]|[yY][eE][sS])
            return 0
            ;;
        *)
            echo "Operation cancelled."
            exit 0
            ;;
    esac
}

function check_dependency() {
    local cmd="$1"
    local message="${2:-$(printf "$ERR_CMD_NOT_FOUND" "$cmd")}"
    command -v "$cmd" &> /dev/null || error_exit "$message"
}

function check_directory() {
    local dir="$1"
    [ -d "$dir" ] || error_exit "$(printf "$ERR_DIR_NOT_FOUND" "$dir")"
}

function detect_compose_cmd() {
    local engine="$1"
    if [ "$engine" = "podman" ]; then
        if podman-compose version >/dev/null 2>&1; then
            echo "podman-compose"
        else
            error_exit "$(printf "$ERR_CMD_NOT_FOUND" "podman-compose")"
        fi
    else
        if docker compose version >/dev/null 2>&1; then
            echo "docker compose"
        elif docker-compose version >/dev/null 2>&1; then
            echo "docker-compose"
        else
            error_exit "Neither 'docker compose' nor 'docker-compose' is available"
        fi
    fi
}

function validate_container_engine() {
    case "$1" in
        docker|podman)
            return 0
            ;;
        *)
            error_exit "$(printf "$ERR_INVALID_ENGINE" "$1")"
            ;;
    esac
}

COMPOSE_CMD=$(detect_compose_cmd "$CONTAINER_ENGINE")

function compose_cmd() {
    if [ "$COMPOSE_CMD" = "docker compose" ]; then
        docker compose "${COMPOSE_FILES[@]}" "$@"
    elif [ "$COMPOSE_CMD" = "podman-compose" ]; then
        podman-compose "${COMPOSE_FILES[@]}" "$@"
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

function open_url() {
    local url="$1"
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

function open_browser() {
    open_url "$LOCAL_URL"
}

function open_elasticvue() {
    open_url "$ELASTICVUE_URL"
}

function check_engine_running() {
    if [ "$CONTAINER_ENGINE" = "podman" ]; then
        podman info >/dev/null 2>&1 || error_exit "$(printf "$ERR_ENGINE_NOT_RUNNING" "Podman" "Podman")"
    else
        docker info >/dev/null 2>&1 || error_exit "$(printf "$ERR_ENGINE_NOT_RUNNING" "Docker" "Docker")"
    fi
}

function compose_down() {
    echo "Stopping containers..."
    compose_cmd -p "$PROJECT_NAME" down --remove-orphans
}

function compose_down_clean() {
    echo "Stopping containers and removing volumes..."
    compose_cmd -p "$PROJECT_NAME" down -v --remove-orphans
}

function clean_environment() {
    echo "Cleaning environment files..."
    python setup.py --clean
}

function ensure_environment() {
    python setup.py
}

function clean_project_images() {
    echo "Removing project-related images..."
    $CONTAINER_ENGINE images --filter "reference=$PROJECT_NAME*" -q | xargs -r $CONTAINER_ENGINE rmi -f
    echo "Project images cleaned"
}

function print_local_url() {
    local green="\033[0;32m"
    local reset="\033[0m"
    local bold="\033[1m"

    echo
    echo -e "Open the Chipper Web-Interface at:"
    echo -e "${bold}${green}➜${reset} ${bold}$LOCAL_URL${reset}"
    echo
}

COMPOSE_FILES=(-f "$DOCKER_COMPOSE_FILE_BASE")
COMPOSE_FILES+=(-f "$DOCKER_COMPOSE_FILE")

# parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--file)
            [ -f "$2" ] || error_exit "$(printf "$ERR_COMPOSE_FILE_NOT_FOUND" "$2")"
            COMPOSE_FILES+=(-f "$2")
            shift 2
            ;;
        -e|--engine)
            validate_container_engine "$2"
            CONTAINER_ENGINE="$2"
            COMPOSE_CMD=$(detect_compose_cmd "$CONTAINER_ENGINE")
            shift 2
            ;;
        *)
            break
            ;;
    esac
done

# check for user compose file
if [ -f "$USER_DOCKER_COMPOSE_FILE" ]; then
    echo "Found user compose file"
    COMPOSE_FILES+=(-f "$USER_DOCKER_COMPOSE_FILE")
fi

# show usage if no command provided
[ $# -eq 0 ] && { show_usage; exit 1; }

# pre-command dependency checks
case "$1" in
    up|down|logs|ps|rebuild|clean-volumes|embed*|scrape)
        check_engine_running
        check_dependency "$CONTAINER_ENGINE"
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

# main command handling
case "$1" in
    "config")
        echo "Launching configuration utility..."
        ensure_environment
        run_in_directory "tools/config" ./run.sh "$@"
        ;;
    "up")
        ensure_environment
        compose_down
        compose_cmd -p "$PROJECT_NAME" up -d
        print_local_url
        ;;
    "down")
        compose_down
        ;;
    "rebuild")
        confirm_clean "containers and rebuild all images"
        compose_down

        clean_project_images

        echo "Ensure valid environment..."
        ensure_environment

        echo "Rebuilding containers..."
        compose_cmd build --no-cache

        echo "Starting containers..."
        compose_cmd -p "$PROJECT_NAME" up -d --force-recreate

        echo "Clean and rebuild complete!"
        print_local_url
        ;;
    "logs")
        compose_cmd -p "$PROJECT_NAME" logs -f
        ;;
    "ps")
        compose_cmd -p "$PROJECT_NAME" ps
        ;;
    "env")
        echo "Creating environment files..."
        ensure_environment
        ;;
    "clean-full")
        confirm_clean "containers, volumes, environment files"
        compose_down_clean
        clean_project_images
        clean_environment
        ;;
    "clean-volumes")
        confirm_clean "Docker volumes and volume directories"
        ensure_environment

        compose_down_clean

        echo "Cleaning up volume directories..."
        rm -rfv docker/volumes
        echo "Volume directories cleaned"

        echo "Clean complete!"
        ;;
    "clean-env")
        confirm_clean "environment files (.env, .systemprompt, .ragignore)"
        clean_environment
        ;;
    "embed-testdata")
        shift
        run_in_directory "tools/embed" ./run.sh "$(pwd)/tools/embed/testdata" "$@"
        ;;
    "embed"|"scrape")
        command="$1"
        shift

        [ $# -eq 0 ] && error_exit "Error: ${command} command requires arguments"

        run_in_directory "tools/${command}" ./run.sh "$@"
        ;;
    "dev-api"|"dev-web")
        run_in_directory "services/${1#dev-}" make dev
        ;;
    "dev-docs")
        shift
        echo "Starting vitepress..."
        yarn add -D vitepress
        yarn docs:dev "$@"
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
    *)
        show_usage
        exit 1
        ;;
esac

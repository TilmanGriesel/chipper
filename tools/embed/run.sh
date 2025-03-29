#!/bin/bash

set -euo pipefail

IMAGE_NAME="chipper-embed"
NETWORK_NAME="chipper_network"

export CONTAINER_ENGINE
detect_container_engine() {
    if [ -n "${CONTAINER_ENGINE:-}" ]; then
        echo "Using container engine from environment: $CONTAINER_ENGINE"
    elif command -v podman &> /dev/null; then
        CONTAINER_ENGINE="podman"
        echo "Auto-detected container engine: $CONTAINER_ENGINE"
    elif command -v docker &> /dev/null; then
        CONTAINER_ENGINE="docker"
        echo "Auto-detected container engine: $CONTAINER_ENGINE"
    else
        echo "Error: No container engine (Docker or Podman) found."
        exit 1
    fi
}

build_image() {
    echo "Building image: $IMAGE_NAME"
    $CONTAINER_ENGINE build -t $IMAGE_NAME .
}

parse_args() {
    if [ $# -eq 0 ]; then
        echo "Usage: $0 /path/to/your/local/folder [additional arguments...]"
        exit 1
    fi

    if [ "$1" == "--help" ]; then
        $CONTAINER_ENGINE run --rm --name ${IMAGE_NAME} ${IMAGE_NAME} --help
        exit 0
    fi

    LOCAL_PATH="$1"
    shift
}

handle_windows_path() {
    if [[ "$OS_TYPE" == *"MINGW"* || "$OS_TYPE" == *"MSYS"* ]]; then
        export MSYS_NO_PATHCONV=1
        echo "Detected Windows environment. Setting MSYS_NO_PATHCONV=1 to avoid path conversion issues."
        LOCAL_PATH=$(cygpath -u "$LOCAL_PATH")
        echo "Converted Windows path to Unix-style: $LOCAL_PATH"
    fi
}

validate_path() {
    if [ ! -d "$LOCAL_PATH" ]; then
        echo "Error: Directory $LOCAL_PATH does not exist."
        exit 1
    fi
}

run_container() {
    local run_opts=(
        --rm
        --name "${IMAGE_NAME}"
        --env-file .env
        -v "$LOCAL_PATH:/app/data:z"
        --network="$NETWORK_NAME"
        "${IMAGE_NAME}"
    )

    $CONTAINER_ENGINE run "${run_opts[@]}" "$@"
}

# Main execution
OS_TYPE=$(uname -s)
detect_container_engine
build_image
parse_args "$@"
handle_windows_path
validate_path
run_container "${@:2}"

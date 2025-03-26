#!/bin/bash

set -euo pipefail

OS_TYPE=$(uname -s)
IMAGE_NAME="chipper-scrape"
BASE_URL=$1
shift

if [[ "$OS_TYPE" == *"MINGW"* || "$OS_TYPE" == *"MSYS"* ]]; then
    export MSYS_NO_PATHCONV=1
    echo "Detected Windows environment. Setting MSYS_NO_PATHCONV=1 to avoid path conversion issues."
fi

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

detect_container_engine

$CONTAINER_ENGINE build -t $IMAGE_NAME .
$CONTAINER_ENGINE run --rm \
    --name "${IMAGE_NAME}" \
    -v "${PWD}/output:/app/data:z" \
    "${IMAGE_NAME}" \
    --base-url="${BASE_URL}" "$@"

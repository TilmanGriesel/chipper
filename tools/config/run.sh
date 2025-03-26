#!/bin/bash

set -euo pipefail

IMAGE_NAME="chipper-config"

OS_TYPE=$(uname -s)
if [[ "$OS_TYPE" == *"MINGW"* || "$OS_TYPE" == *"MSYS"* ]]; then
    export MSYS_NO_PATHCONV=1
    echo "Detected Windows environment. Setting MSYS_NO_PATHCONV=1 to avoid path conversion issues."

    LOCAL_PATH=$(cygpath -u "$1")
    echo "Converted Windows path to Unix-style: $LOCAL_PATH"
else
    LOCAL_PATH=$1
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

build_image() {
    echo "Building image: $IMAGE_NAME"
    $CONTAINER_ENGINE build -t $IMAGE_NAME .
}

WD=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
run_container() {
    $CONTAINER_ENGINE run --rm \
        --name ${IMAGE_NAME} \
        -v ${WD}:/app/chipper:z \
        -i \
        ${IMAGE_NAME}
}

detect_container_engine
build_image
run_container

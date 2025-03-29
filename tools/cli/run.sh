#!/bin/bash

set -euo pipefail

IMAGE_NAME="chipper-cli"
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

run_container() {
    if [ $# -eq 0 ]; then
        $CONTAINER_ENGINE run --rm \
            --name ${IMAGE_NAME} \
            -i \
            --env-file .env \
            --network=$NETWORK_NAME \
            ${IMAGE_NAME}
    else
        $CONTAINER_ENGINE run --rm \
            --name ${IMAGE_NAME} \
            -i \
            --env-file .env \
            --network=$NETWORK_NAME \
            ${IMAGE_NAME} "$@"
    fi
}

detect_container_engine
build_image
run_container "$@"

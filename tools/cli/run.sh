#!/bin/bash

set -euo pipefail

IMAGE_NAME="chipper-cli"
CONTAINER_ENGINE=""
NETWORK_NAME="chipper_network"

detect_container_engine() {
    if command -v podman &> /dev/null; then
        CONTAINER_ENGINE="podman"
    elif command -v docker &> /dev/null; then
        CONTAINER_ENGINE="docker"
    else
        echo "Error: No container engine (Docker or Podman) found."
        exit 1
    fi
    echo "Using container engine: $CONTAINER_ENGINE"
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

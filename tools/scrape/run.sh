#!/bin/bash

OS_TYPE=$(uname -s)

if [[ "$OS_TYPE" == *"MINGW"* || "$OS_TYPE" == *"MSYS"* ]]; then
    export MSYS_NO_PATHCONV=1
    echo "Detected Windows environment. Setting MSYS_NO_PATHCONV=1 to avoid path conversion issues."
fi

BASE_URL=$1
shift

IMAGE_NAME="chipper-scrape

docker build -t $IMAGE_NAME .

docker run --rm --name ${IMAGE_NAME} \
    -v "${PWD}/output":/app/data \
    ${IMAGE_NAME} --base-url="${BASE_URL}"

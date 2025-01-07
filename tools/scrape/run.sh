#!/bin/bash

set -euo pipefail

readonly SCRIPT_VERSION="0.1.0"
function show_welcome() {
    printf "\n"
    printf "\033[32m"
    printf "        __    _                      \n"
    printf "  _____/ /_  (_)___  ____  ___  _____\n"
    printf " / ___/ __ \/ / __ \/ __ \/ _ \/ ___/\n"
    printf "/ /__/ / / / / /_/ / /_/ /  __/ /    \n"
    printf "\___/_/ /_/_/ .___/ .___/\___/_/     \n"
    printf "           /_/   /_/                 \n"
    printf "\033[0m\n"
    printf "\033[36m        Chipper Scrape v%s\033[0m\n" "${SCRIPT_VERSION}"
    printf "\n"
}
show_welcome

OS_TYPE=$(uname -s)

if [[ "$OS_TYPE" == *"MINGW"* || "$OS_TYPE" == *"MSYS"* ]]; then
    export MSYS_NO_PATHCONV=1
    echo "Detected Windows environment. Setting MSYS_NO_PATHCONV=1 to avoid path conversion issues."
fi

BASE_URL=$1
shift

IMAGE_NAME="chipper-scrape"

docker build -t $IMAGE_NAME .

docker run --rm \
    --name "${IMAGE_NAME}" \
    -v "${PWD}/output:/app/data" \
    "${IMAGE_NAME}" \
    --base-url="${BASE_URL}"
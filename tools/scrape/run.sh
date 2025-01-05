#!/bin/bash

set -euo pipefail

readonly SCRIPT_VERSION="0.1.0"
function show_welcome() {
    echo ""
    # green
    echo -e "\e[32m"
    echo "        __    _                      "
    echo "  _____/ /_  (_)___  ____  ___  _____"
    echo " / ___/ __ \/ / __ \/ __ \/ _ \/ ___/"
    echo "/ /__/ / / / / /_/ / /_/ /  __/ /    "
    echo "\___/_/ /_/_/ .___/ .___/\___/_/     "
    echo "           /_/   /_/                 "
    echo -e "\e[0m"
    # cyan
    echo -e "\e[36m        Chipper Scrape v${SCRIPT_VERSION}\e[0m"
    echo ""
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
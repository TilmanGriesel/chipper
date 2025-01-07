#!/bin/bash

set -euo pipefail

OS_TYPE=$(uname -s)

readonly SCRIPT_VERSION="0.1.0"
function show_welcome() {
    printf "\n"
    printf "\033[31m"
    printf "        __    _                      \n"
    printf "  _____/ /_  (_)___  ____  ___  _____\n"
    printf " / ___/ __ \/ / __ \/ __ \/ _ \/ ___/\n"
    printf "/ /__/ / / / / /_/ / /_/ /  __/ /    \n"
    printf "\___/_/ /_/_/ .___/ .___/\___/_/     \n"
    printf "           /_/   /_/                 \n"
    printf "\033[0m\n"
    printf "\033[33m        Chipper Embed v%s\033[0m\n" "${SCRIPT_VERSION}"
    printf "\n"
}
show_welcome

if [[ "$OS_TYPE" == *"MINGW"* || "$OS_TYPE" == *"MSYS"* ]]; then
    export MSYS_NO_PATHCONV=1
    echo "Detected Windows environment. Setting MSYS_NO_PATHCONV=1 to avoid path conversion issues."

    LOCAL_PATH=$(cygpath -u "$1")
    echo "Converted Windows path to Unix-style: $LOCAL_PATH"
else
    LOCAL_PATH=$1
fi
shift

if [ -z "$LOCAL_PATH" ]; then
    echo "Usage: $0 /path/to/your/local/folder"
    exit 1
fi

if [ ! -d "$LOCAL_PATH" ]; then
    echo "Error: Directory $LOCAL_PATH does not exist."
    exit 1
fi


IMAGE_NAME="chipper-embed"

docker build -t $IMAGE_NAME .

docker run --rm --name ${IMAGE_NAME} --env-file .env \
    -v "$LOCAL_PATH:/app/data" \
    ${IMAGE_NAME} "$@" 

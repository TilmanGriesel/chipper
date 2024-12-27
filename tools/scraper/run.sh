#!/bin/bash

OS_TYPE=$(uname -s)
if [[ "$OS_TYPE" == *"MINGW"* || "$OS_TYPE" == *"MSYS"* ]]; then
    export MSYS_NO_PATHCONV=1
    echo "Detected Windows environment. Setting MSYS_NO_PATHCONV=1 to avoid path conversion issues."
fi

if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/your/local/folder [additional arguments...]"
    exit 1
fi

LOCAL_PATH=$1
shift

if [[ "$OS_TYPE" == *"MINGW"* || "$OS_TYPE" == *"MSYS"* ]]; then
    LOCAL_PATH=$(cygpath -u "$LOCAL_PATH")
    echo "Converted Windows path to Unix-style: $LOCAL_PATH"
fi

echo "Using local path: $LOCAL_PATH"

if [ ! -d "$LOCAL_PATH" ]; then
    echo "Error: Directory $LOCAL_PATH does not exist."
    exit 1
fi

docker build -t embedding-cli .

docker run \
    -v "$LOCAL_PATH":/app/data \
    embedding-cli "$@"
#!/bin/bash

OS_TYPE=$(uname -s)

if [[ "$OS_TYPE" == *"MINGW"* || "$OS_TYPE" == *"MSYS"* ]]; then
    export MSYS_NO_PATHCONV=1
    echo "Detected Windows environment. Setting MSYS_NO_PATHCONV=1 to avoid path conversion issues."

    LOCAL_PATH=$(cygpath -u "$1")
    echo "Converted Windows path to Unix-style: $LOCAL_PATH"
else
    LOCAL_PATH=$1
fi

if [ -z "$LOCAL_PATH" ]; then
    echo "Usage: $0 /path/to/your/local/folder"
    exit 1
fi

if [ ! -d "$LOCAL_PATH" ]; then
    echo "Error: Directory $LOCAL_PATH does not exist."
    exit 1
fi

docker build -t embedding-cli .

docker run --env-file .env \
    -v "$LOCAL_PATH:/app/data" \
    embedding-cli --stats

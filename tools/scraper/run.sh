#!/bin/bash

# Detect OS type and set MSYS_NO_PATHCONV if needed
OS_TYPE=$(uname -s)
if [[ "$OS_TYPE" == *"MINGW"* || "$OS_TYPE" == *"MSYS"* ]]; then
    export MSYS_NO_PATHCONV=1
    echo "Detected Windows environment. Setting MSYS_NO_PATHCONV=1 to avoid path conversion issues."
fi

# Check if the local path argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 /path/to/your/local/folder"
    exit 1
fi

LOCAL_PATH=$1

# Convert the local path to Unix-style format if on Windows
if [[ "$OS_TYPE" == *"MINGW"* || "$OS_TYPE" == *"MSYS"* ]]; then
    LOCAL_PATH=$(cygpath -u "$LOCAL_PATH")
    echo "Converted Windows path to Unix-style: $LOCAL_PATH"
fi

# Debug: Print the local path
echo "Using local path: $LOCAL_PATH"

# Ensure the directory exists
if [ ! -d "$LOCAL_PATH" ]; then
    echo "Error: Directory $LOCAL_PATH does not exist."
    exit 1
fi

# Build the Docker image
docker build -t embedding-cli .

# Run the Docker container with the specified local path
docker run --env-file .env \
    -v "$LOCAL_PATH":/app/data \
    embedding-cli --stats --path=/app/data

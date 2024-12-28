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

MODEL="large-v3"
LANGUAGE="English"

while getopts ":m:l:" opt; do
  case $opt in
    m)
      MODEL=$OPTARG
      ;;
    l)
      LANGUAGE=$OPTARG
      ;;
    \?)
      echo "Invalid option -$OPTARG" >&2
      exit 1
      ;;
  esac
done
shift $((OPTIND -1))

if [ -z "$LOCAL_PATH" ]; then
    echo "Usage: $0 [-m model] [-l language] /path/to/your/audio/file.mp3 or /path/to/your/audio/folder"
    exit 1
fi

if [ -f "$LOCAL_PATH" ]; then
    FILES=("$(realpath "$LOCAL_PATH")")
elif [ -d "$LOCAL_PATH" ]; then
    mapfile -t FILES < <(find "$LOCAL_PATH" -type f \( -name "*.mp3" -o -name "*.wav" -o -name "*.m4a" \) -print0 | xargs -0 -n 1 realpath)
    if [ ${#FILES[@]} -eq 0 ]; then
        echo "Error: No audio files found in the directory $LOCAL_PATH."
        exit 1
    fi
else
    echo "Error: $LOCAL_PATH is neither a file nor a directory."
    exit 1
fi

IMAGE_NAME="whisper-transcriber"
if [[ "$(docker images -q $IMAGE_NAME 2> /dev/null)" == "" ]]; then
    echo "Docker image '$IMAGE_NAME' not found. Building the image..."
    docker build -t $IMAGE_NAME .
else
    echo "Docker image '$IMAGE_NAME' already exists. Skipping build."
fi

for FILE in "${FILES[@]}"; do
    echo "Processing file: $FILE"

    docker run --gpus all -it \
        -v ${PWD}/models:/root/.cache/whisper \
        -v ${PWD}/output:/output \
        -v "$(dirname "$FILE"):/app" \
        ${IMAGE_NAME} whisper "/app/$(basename "$FILE")" --device cuda --model "$MODEL" --language "$LANGUAGE" --output_dir /output --output_format txt

done

echo "Transcription completed. Check the output directory for the transcriptions."

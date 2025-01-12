#!/bin/bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${SCRIPT_DIR}/../src/static/vendor/tts-sherpa-onnx"
URL="https://huggingface.co/spaces/k2-fsa/web-assembly-tts-sherpa-onnx-en/resolve/main/sherpa-onnx-wasm-main-tts.data"

FILENAME="sherpa-onnx-wasm-main-tts.data"
TARGET_FILE="${TARGET_DIR}/${FILENAME}"
TMP_FILE="/tmp/${FILENAME}.tmp"

cleanup() {
    if [ -f "${TMP_FILE}" ]; then
        rm -f "${TMP_FILE}"
    fi
}

trap cleanup EXIT

if [ ! -d "${TARGET_DIR}" ]; then
    echo "Error: Target directory does not exist: ${TARGET_DIR}" >&2
    exit 1
fi

if [ -f "${TARGET_FILE}" ]; then
    echo "File already exists at: ${TARGET_FILE}"
    echo "Skipping download"
    exit 0
fi

echo "Pulling Wasm client side TTS..."
echo "Downloading file..."

if command -v curl >/dev/null 2>&1; then
    curl -L --progress-bar "${URL}" -o "${TMP_FILE}"
elif command -v wget >/dev/null 2>&1; then
    wget --progress=bar:force:noscroll "${URL}" -O "${TMP_FILE}"
else
    echo "Error: Neither curl nor wget is available" >&2
    exit 1
fi

if [ ! -f "${TMP_FILE}" ]; then
    echo "Error: Download failed" >&2
    exit 1
fi

mv "${TMP_FILE}" "${TARGET_FILE}"

echo "Download completed successfully to: ${TARGET_FILE}"

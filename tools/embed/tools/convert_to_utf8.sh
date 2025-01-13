#!/bin/bash
# Recursively converts text files in a directory from Windows encodings (CP1252, Windows-1252)
# or ISO-8859-1 to UTF-8. Skips already UTF-8 encoded and empty files.
#
# Usage: ./script.sh [input_dir] [debug]
#   input_dir: Directory to process (default: ./input)
#   debug: Enable debug output (default: false)

set -euo pipefail

START_DIR=${1:-./input}
DEBUG=${2:-false}

debug() {
    if [ "$DEBUG" = "true" ]; then
        echo "DEBUG: $1" >&2
    fi
}

if [ ! -d "$START_DIR" ]; then
    printf "Error: Directory '%s' does not exist.\n" "$START_DIR"
    exit 1
fi

TEMP_FILE=$(mktemp)
trap 'rm -f "$TEMP_FILE"' EXIT

try_convert() {
    local file=$1
    local from_enc=$2
    local temp=$3

    debug "Trying $from_enc..."
    # translit replaces unmappable chars
    if LC_ALL=C iconv -f "$from_enc" -t UTF-8//TRANSLIT "$file" > "$temp" 2>/dev/null; then
        mv "$temp" "$file"
        return 0
    fi
    return 1
}

while IFS= read -r -d $'\0' FILE; do
    printf "Converting %-50s" "${FILE:0:50}"

    if [ ! -s "$FILE" ]; then
        echo "[EMPTY]"
        continue
    fi

    if file -bi "$FILE" | grep -q "charset=utf-8"; then
        echo "[SKIPPED]"
        continue
    fi

    # try common windows encodings first
    if try_convert "$FILE" "CP1252" "$TEMP_FILE" || \
       try_convert "$FILE" "WINDOWS-1252" "$TEMP_FILE" || \
       try_convert "$FILE" "ISO-8859-1" "$TEMP_FILE"; then
        echo "[OK]"
    else
        echo "[FAILED]"
        if [ "$DEBUG" = "true" ]; then
            debug "First 100 bytes of file:"
            hexdump -C "$FILE" | head -n 5 >&2
        fi
    fi
done < <(find "$START_DIR" -type f -print0)

printf "\nConversion complete.\n"

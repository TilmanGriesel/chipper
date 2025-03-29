#!/bin/bash
# Usage: ./update_requirements.sh [--upgrade]
# Finds all requirements.in files and runs pip-compile on them.
# Add --upgrade flag to update all packages to their latest versions.

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

UPGRADE_FLAG=""
if [[ "$1" == "--upgrade" ]]; then
    UPGRADE_FLAG="--upgrade"
    echo "Running with --upgrade flag to get latest package versions"
fi

echo "Searching for requirements.in files..."
COUNT=0

while IFS= read -r req_file; do
    dir_path=$(dirname "$req_file")
    echo "Found: $req_file"

    pushd "$dir_path" > /dev/null

    echo "Running pip-compile on $req_file..."
    if pip-compile $UPGRADE_FLAG --strip-extras; then
        echo -e "${GREEN}Successfully compiled $req_file${NC}"
        COUNT=$((COUNT + 1))
    else
        echo -e "${RED}Failed to compile $req_file${NC}"
    fi

    popd > /dev/null

    echo "-----------------------------------"
done < <(find . -name "requirements.in" -type f)

echo "Compilation complete. Processed $COUNT requirements.in files."

#!/bin/bash
set -e

# Configuration
VENV_NAME="venv"
PYTHON_VERSION="3.11"
REQUIREMENTS_FILE="requirements.txt"

# Colors for web
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Setting up Python virtual environment for Chipper project...${NC}"

# Check if Python is installed
if ! command -v python$PYTHON_VERSION &> /dev/null; then
    echo "Python $PYTHON_VERSION is required but not found. Please install it first."
    exit 1
fi

# Create and activate virtual environment
echo -e "${BLUE}Creating virtual environment...${NC}"
python$PYTHON_VERSION -m venv $VENV_NAME

# Determine the correct activate script based on OS
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source $VENV_NAME/Scripts/activate
else
    source $VENV_NAME/bin/activate
fi

# Upgrade pip
echo -e "${BLUE}Upgrading pip...${NC}"
pip install --upgrade pip

# Install requirements
echo -e "${BLUE}Installing requirements...${NC}"
pip3 install -r $REQUIREMENTS_FILE

echo -e "${GREEN}Setup completed successfully!${NC}"
echo -e "${BLUE}To activate the virtual environment, run:${NC}"
echo "source $VENV_NAME/bin/activate  # On Linux/MacOS"
echo "$VENV_NAME\\Scripts\\activate    # On Windows"
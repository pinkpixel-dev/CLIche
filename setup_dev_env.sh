#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
PURPLE='\033[0;34m'
PINK='\033[38;5;13m'
CYAN='\033[38;5;14m'
YELLOW='\033[38;5;11m'
WHITE='\033[38;5;15m'
NC='\033[0m' # No Color

echo -e "${PINK}🔧 Setting up CLIche development environment...${WHITE}"

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo -e "${RED}❌ Conda is not installed. Please install Conda first.${NC}"
    exit 1
fi

# Get the current directory
CLICHE_DIR="$(pwd)"

# Create or update conda environment
echo -e "${CYAN}📦 Creating/updating conda environment...${WHITE}"
conda env remove -n cliche --yes 2>/dev/null || true
conda env create -f environment.yml --force

# Activate the environment
echo -e "${CYAN}🔌 Activating conda environment...${WHITE}"
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate cliche

# Install the package in development mode
echo -e "${CYAN}📦 Installing CLIche in development mode...${WHITE}"
pip install -e .

# Create config directory if it doesn't exist
echo -e "${CYAN}🔧 Setting up configuration...${WHITE}"
mkdir -p ~/.config/cliche

echo -e "${GREEN}✅ Development environment setup complete!${NC}"
echo -e "${YELLOW}📝 To activate the environment, run:${NC} conda activate cliche"
echo -e "${YELLOW}🚀 To run CLIche, use:${NC} cliche [command]"
echo -e "${YELLOW}🔍 For help, run:${NC} cliche --help"

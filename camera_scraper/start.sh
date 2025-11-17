#!/bin/bash
###############################################################################
# QEW Camera Scraper - Startup Script
# Part of ADBA Labs QEW Innovation Corridor Project
#
# This script sets up and starts the QEW Camera Collection GUI
###############################################################################

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  QEW Innovation Corridor - Camera Collection System       ║${NC}"
echo -e "${BLUE}║  ADBA Labs Framework                                       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if Python is installed
echo -e "${YELLOW}[1/5]${NC} Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed.${NC}"
    echo "Please install Python 3.8 or higher from https://www.python.org/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}✓${NC} Found: $PYTHON_VERSION"
echo ""

# Check if virtual environment exists
echo -e "${YELLOW}[2/5]${NC} Setting up virtual environment..."
if [ ! -d "venv" ]; then
    echo "Creating new virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo -e "${YELLOW}[3/5]${NC} Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"
echo ""

# Install/Update dependencies
echo -e "${YELLOW}[4/5]${NC} Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo -e "${GREEN}✓${NC} Dependencies installed"
echo ""

# Check if camera data exists
echo -e "${YELLOW}[5/5]${NC} Pre-flight checks..."
if [ ! -f "qew_cameras_hamilton_mississauga.json" ]; then
    echo -e "${YELLOW}⚠${NC}  Warning: Camera metadata file not found"
    echo "   Expected: qew_cameras_hamilton_mississauga.json"
fi

if [ ! -f "database.py" ]; then
    echo -e "${RED}✗${NC} Error: database.py not found"
    exit 1
fi

if [ ! -f "download_camera_images.py" ]; then
    echo -e "${RED}✗${NC} Error: download_camera_images.py not found"
    exit 1
fi

echo -e "${GREEN}✓${NC} All pre-flight checks passed"
echo ""

# Launch the GUI
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Starting QEW Camera Collection GUI...${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════${NC}"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

python3 qew_camera_gui.py

# Deactivate on exit
deactivate

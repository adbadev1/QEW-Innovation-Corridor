#!/bin/bash
###############################################################################
# QEW Camera Scraper - Repository Cleanup Script
# Part of ADBA Labs QEW Innovation Corridor Project
#
# This script cleans up development artifacts and temporary files
# Use with caution - some operations are destructive!
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

echo -e "${RED}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║  QEW Camera Scraper - Repository Cleanup                  ║${NC}"
echo -e "${RED}║  WARNING: This will delete files!                          ║${NC}"
echo -e "${RED}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to display size
get_size() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        du -sh "$1" 2>/dev/null | cut -f1
    else
        du -sh "$1" 2>/dev/null | cut -f1
    fi
}

# Function to count items
count_items() {
    find "$1" -type f 2>/dev/null | wc -l | tr -d ' '
}

# Display what will be cleaned
echo -e "${YELLOW}Analyzing repository...${NC}"
echo ""

ITEMS_TO_CLEAN=()

# Check __pycache__ directories
PYCACHE_DIRS=$(find . -type d -name "__pycache__" 2>/dev/null)
if [ -n "$PYCACHE_DIRS" ]; then
    PYCACHE_COUNT=$(echo "$PYCACHE_DIRS" | wc -l | tr -d ' ')
    ITEMS_TO_CLEAN+=("__pycache__:$PYCACHE_COUNT directories")
fi

# Check .pyc files
PYC_FILES=$(find . -type f -name "*.pyc" 2>/dev/null | wc -l | tr -d ' ')
if [ "$PYC_FILES" -gt 0 ]; then
    ITEMS_TO_CLEAN+=("*.pyc:$PYC_FILES files")
fi

# Check virtual environment
if [ -d "venv" ]; then
    VENV_SIZE=$(get_size "venv")
    ITEMS_TO_CLEAN+=("venv:$VENV_SIZE")
fi

# Check database
if [ -f "camera_data.db" ]; then
    DB_SIZE=$(get_size "camera_data.db")
    ITEMS_TO_CLEAN+=("camera_data.db:$DB_SIZE")
fi

# Check camera images
if [ -d "camera_images" ]; then
    IMG_COUNT=$(count_items "camera_images")
    IMG_SIZE=$(get_size "camera_images")
    ITEMS_TO_CLEAN+=("camera_images:$IMG_COUNT files ($IMG_SIZE)")
fi

# Check GUI settings
if [ -f "gui_settings.json" ]; then
    ITEMS_TO_CLEAN+=("gui_settings.json:user preferences")
fi

# Check test images
if [ -d "test_images" ]; then
    TEST_COUNT=$(count_items "test_images")
    ITEMS_TO_CLEAN+=("test_images:$TEST_COUNT files")
fi

# Display items
if [ ${#ITEMS_TO_CLEAN[@]} -eq 0 ]; then
    echo -e "${GREEN}✓ Repository is already clean!${NC}"
    exit 0
fi

echo -e "${YELLOW}Items found for cleanup:${NC}"
for item in "${ITEMS_TO_CLEAN[@]}"; do
    key="${item%%:*}"
    value="${item#*:}"
    echo -e "  ${BLUE}•${NC} $key: $value"
done
echo ""

# Interactive cleanup menu
echo -e "${YELLOW}Select cleanup level:${NC}"
echo "  1) Quick clean (Python cache only - SAFE)"
echo "  2) Standard clean (cache + venv - SAFE)"
echo "  3) Deep clean (cache + venv + data - CAUTION)"
echo "  4) Nuclear clean (everything - DANGER)"
echo "  5) Custom cleanup"
echo "  6) Cancel"
echo ""
read -p "Enter choice (1-6): " CHOICE

case $CHOICE in
    1)
        echo -e "${BLUE}Running quick cleanup...${NC}"
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -type f -name "*.pyc" -delete 2>/dev/null || true
        echo -e "${GREEN}✓ Quick cleanup complete${NC}"
        ;;
    2)
        echo -e "${BLUE}Running standard cleanup...${NC}"
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -type f -name "*.pyc" -delete 2>/dev/null || true
        if [ -d "venv" ]; then
            echo "Removing virtual environment..."
            rm -rf venv
            echo -e "${GREEN}✓ Virtual environment removed${NC}"
        fi
        echo -e "${GREEN}✓ Standard cleanup complete${NC}"
        ;;
    3)
        echo -e "${RED}Deep cleanup - this will delete data files!${NC}"
        read -p "Are you sure? Type 'yes' to continue: " CONFIRM
        if [ "$CONFIRM" != "yes" ]; then
            echo "Cancelled"
            exit 0
        fi
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -type f -name "*.pyc" -delete 2>/dev/null || true
        rm -rf venv 2>/dev/null || true
        rm -f camera_data.db 2>/dev/null || true
        rm -f gui_settings.json 2>/dev/null || true
        echo -e "${GREEN}✓ Deep cleanup complete${NC}"
        ;;
    4)
        echo -e "${RED}NUCLEAR CLEANUP - THIS WILL DELETE EVERYTHING!${NC}"
        echo -e "${RED}Including all collected camera images!${NC}"
        read -p "Type 'DELETE EVERYTHING' to confirm: " CONFIRM
        if [ "$CONFIRM" != "DELETE EVERYTHING" ]; then
            echo "Cancelled"
            exit 0
        fi
        find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find . -type f -name "*.pyc" -delete 2>/dev/null || true
        rm -rf venv 2>/dev/null || true
        rm -rf camera_images 2>/dev/null || true
        rm -rf test_images 2>/dev/null || true
        rm -f camera_data.db 2>/dev/null || true
        rm -f gui_settings.json 2>/dev/null || true
        echo -e "${GREEN}✓ Nuclear cleanup complete - repository reset${NC}"
        ;;
    5)
        echo -e "${BLUE}Custom cleanup:${NC}"
        read -p "Clean Python cache? (y/n): " ans
        [ "$ans" = "y" ] && find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        [ "$ans" = "y" ] && find . -type f -name "*.pyc" -delete 2>/dev/null || true

        read -p "Remove virtual environment? (y/n): " ans
        [ "$ans" = "y" ] && rm -rf venv 2>/dev/null || true

        read -p "Delete database? (y/n): " ans
        [ "$ans" = "y" ] && rm -f camera_data.db 2>/dev/null || true

        read -p "Delete camera images? (y/n): " ans
        [ "$ans" = "y" ] && rm -rf camera_images 2>/dev/null || true

        read -p "Delete test images? (y/n): " ans
        [ "$ans" = "y" ] && rm -rf test_images 2>/dev/null || true

        read -p "Delete GUI settings? (y/n): " ans
        [ "$ans" = "y" ] && rm -f gui_settings.json 2>/dev/null || true

        echo -e "${GREEN}✓ Custom cleanup complete${NC}"
        ;;
    6)
        echo "Cleanup cancelled"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}Cleanup completed successfully!${NC}"
echo ""

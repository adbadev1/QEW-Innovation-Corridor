#!/bin/bash
###############################################################################
# QEW Camera Scraper - Stop Script
# Part of ADBA Labs QEW Innovation Corridor Project
#
# This script gracefully stops the QEW Camera Collection GUI
###############################################################################

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  QEW Camera Collection - Stop Script                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Find running camera GUI processes
echo -e "${YELLOW}Searching for running Camera GUI processes...${NC}"

if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    PIDS=$(pgrep -f "qew_camera_gui.py")
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    PIDS=$(pgrep -f "qew_camera_gui.py")
else
    echo -e "${RED}Unsupported operating system: $OSTYPE${NC}"
    exit 1
fi

if [ -z "$PIDS" ]; then
    echo -e "${GREEN}✓${NC} No running Camera GUI processes found"
    echo ""
    exit 0
fi

# Display found processes
echo -e "${YELLOW}Found the following processes:${NC}"
echo "$PIDS" | while read pid; do
    ps -p $pid -o pid,cmd | tail -1
done
echo ""

# Ask for confirmation
read -p "Do you want to stop these processes? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Operation cancelled${NC}"
    exit 0
fi

# Stop processes gracefully (SIGTERM)
echo -e "${YELLOW}Stopping processes gracefully...${NC}"
echo "$PIDS" | while read pid; do
    kill -TERM $pid 2>/dev/null && echo -e "${GREEN}✓${NC} Sent SIGTERM to process $pid"
done

# Wait a few seconds
sleep 3

# Check if processes are still running
REMAINING=$(pgrep -f "qew_camera_gui.py")
if [ -n "$REMAINING" ]; then
    echo -e "${YELLOW}Some processes are still running. Force stopping...${NC}"
    echo "$REMAINING" | while read pid; do
        kill -KILL $pid 2>/dev/null && echo -e "${GREEN}✓${NC} Force stopped process $pid"
    done
fi

echo ""
echo -e "${GREEN}All Camera GUI processes stopped successfully${NC}"
echo ""

# Deactivate virtual environment if active
if [ -n "$VIRTUAL_ENV" ]; then
    echo -e "${YELLOW}Deactivating virtual environment...${NC}"
    deactivate
    echo -e "${GREEN}✓${NC} Virtual environment deactivated"
fi

#!/bin/bash

################################################################################
# QEW Innovation Corridor - Cleanup Script
#
# Purpose: Cleanup build artifacts, logs, cache, and temporary files
# Author: ADBA Labs
# Version: 1.0.0
# Last Updated: 2025-11-17
################################################################################

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

# Log functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_cleanup() {
    echo -e "${CYAN}[CLEANUP]${NC} $1"
}

# Calculate directory size
get_dir_size() {
    if [ -d "$1" ]; then
        du -sh "$1" 2>/dev/null | cut -f1 || echo "0B"
    else
        echo "0B"
    fi
}

# Banner
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     QEW Innovation Corridor - Cleanup Script             ║"
echo "║     ADBA Labs - Project Maintenance                       ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

################################################################################
# Cleanup Level Selection
################################################################################

echo "Select cleanup level:"
echo ""
echo "  1. Light    - Logs and temporary files only"
echo "  2. Standard - Logs, temp files, and build artifacts (RECOMMENDED)"
echo "  3. Deep     - Everything including node_modules (requires npm install)"
echo "  4. Custom   - Select specific items to clean"
echo ""

read -p "Enter choice (1-4): " CLEANUP_LEVEL

case $CLEANUP_LEVEL in
    1)
        CLEANUP_TYPE="light"
        log_info "Light cleanup selected"
        ;;
    2)
        CLEANUP_TYPE="standard"
        log_info "Standard cleanup selected (RECOMMENDED)"
        ;;
    3)
        CLEANUP_TYPE="deep"
        log_warning "Deep cleanup selected - will require npm install afterward"
        ;;
    4)
        CLEANUP_TYPE="custom"
        log_info "Custom cleanup selected"
        ;;
    *)
        log_error "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""

################################################################################
# Pre-cleanup Status
################################################################################

log_info "Calculating current disk usage..."
echo ""

INITIAL_SIZE=0

# Calculate sizes
LOGS_SIZE=$(get_dir_size "logs")
DIST_SIZE=$(get_dir_size "dist")
VITE_SIZE=$(get_dir_size ".vite")
NODE_MODULES_SIZE=$(get_dir_size "node_modules")
PIDS_SIZE=$(get_dir_size ".pids")
CACHE_SIZE=$(get_dir_size ".cache")
TMP_SIZE=$(get_dir_size "tmp")

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Current Disk Usage"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Logs:          $LOGS_SIZE"
echo "  Build (dist):  $DIST_SIZE"
echo "  Vite cache:    $VITE_SIZE"
echo "  Node modules:  $NODE_MODULES_SIZE"
echo "  PID files:     $PIDS_SIZE"
echo "  Cache:         $CACHE_SIZE"
echo "  Temp:          $TMP_SIZE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

################################################################################
# Cleanup Functions
################################################################################

cleanup_logs() {
    log_cleanup "Cleaning log files..."

    if [ -d "logs" ]; then
        rm -rf logs/*
        log_success "Logs cleared"
    else
        log_info "No logs directory found"
    fi

    # Individual log files
    find . -maxdepth 1 -name "*.log" -type f -delete 2>/dev/null || true
    log_success "Root-level log files removed"
}

cleanup_temp_files() {
    log_cleanup "Cleaning temporary files..."

    # PID files
    if [ -d ".pids" ]; then
        rm -rf .pids/*
        log_success "PID files cleared"
    fi

    # GUI settings (camera scraper)
    if [ -f "camera_scraper/gui_settings.json" ]; then
        rm -f camera_scraper/gui_settings.json
        log_success "GUI settings cleared"
    fi

    # Temporary directories
    rm -rf tmp/ temp/ 2>/dev/null || true

    # OS-specific temporary files
    find . -name ".DS_Store" -type f -delete 2>/dev/null || true
    find . -name "Thumbs.db" -type f -delete 2>/dev/null || true
    find . -name "*.swp" -type f -delete 2>/dev/null || true
    find . -name "*.swo" -type f -delete 2>/dev/null || true
    find . -name "*~" -type f -delete 2>/dev/null || true

    log_success "Temporary files removed"
}

cleanup_build_artifacts() {
    log_cleanup "Cleaning build artifacts..."

    # Vite build output
    if [ -d "dist" ]; then
        rm -rf dist/
        log_success "dist/ removed"
    fi

    # Vite cache
    if [ -d ".vite" ]; then
        rm -rf .vite/
        log_success ".vite/ removed"
    fi

    # General cache
    if [ -d ".cache" ]; then
        rm -rf .cache/
        log_success ".cache/ removed"
    fi

    # Python cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    find . -type f -name "*.pyd" -delete 2>/dev/null || true

    # Jupyter checkpoints
    find . -type d -name ".ipynb_checkpoints" -exec rm -rf {} + 2>/dev/null || true

    log_success "Build artifacts removed"
}

cleanup_node_modules() {
    log_cleanup "Removing node_modules..."

    if [ -d "node_modules" ]; then
        log_warning "This will require 'npm install' to restore dependencies"
        read -p "Continue? (y/n) " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf node_modules/
            log_success "node_modules/ removed"
        else
            log_info "Skipped node_modules removal"
        fi
    else
        log_info "No node_modules directory found"
    fi
}

cleanup_docker() {
    log_cleanup "Cleaning Docker resources (Phase 2)..."

    if command -v docker &> /dev/null; then
        # Remove stopped containers
        STOPPED_CONTAINERS=$(docker ps -a -q -f status=exited 2>/dev/null || echo "")
        if [ -n "$STOPPED_CONTAINERS" ]; then
            docker rm $STOPPED_CONTAINERS 2>/dev/null || true
            log_success "Stopped containers removed"
        fi

        # Remove dangling images
        DANGLING_IMAGES=$(docker images -f "dangling=true" -q 2>/dev/null || echo "")
        if [ -n "$DANGLING_IMAGES" ]; then
            docker rmi $DANGLING_IMAGES 2>/dev/null || true
            log_success "Dangling images removed"
        fi

        # Prune build cache
        docker builder prune -f 2>/dev/null || true
        log_success "Docker build cache pruned"
    else
        log_info "Docker not installed, skipping Docker cleanup"
    fi
}

cleanup_git() {
    log_cleanup "Cleaning Git working tree..."

    # Check for uncommitted changes
    if ! git diff-index --quiet HEAD -- 2>/dev/null; then
        log_warning "Uncommitted changes detected"
        git status --short
        echo ""
        read -p "Stash changes? (y/n) " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            git stash push -m "Cleanup script auto-stash $(date +%Y-%m-%d_%H:%M:%S)"
            log_success "Changes stashed"
        else
            log_info "Skipped git stash"
        fi
    else
        log_success "Working tree clean"
    fi

    # Git garbage collection
    git gc --auto 2>/dev/null || true
    log_success "Git garbage collection completed"
}

cleanup_camera_images() {
    log_cleanup "Checking camera image collections..."

    # Don't auto-delete camera images, just report
    CAMERA_DIRS=$(find camera_scraper/camera_images -maxdepth 1 -type d -name "qew_collection_*" 2>/dev/null | wc -l)

    if [ "$CAMERA_DIRS" -gt 0 ]; then
        log_info "Found $CAMERA_DIRS camera image collections"
        echo ""
        read -p "Remove old camera image collections? (y/n) " -n 1 -r
        echo

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf camera_scraper/camera_images/qew_collection_*/ 2>/dev/null || true
            rm -rf camera_scraper/quick_test_db/ 2>/dev/null || true
            rm -rf camera_scraper/test_images_db/ 2>/dev/null || true
            log_success "Camera image collections removed"
        else
            log_info "Skipped camera image cleanup"
        fi
    else
        log_info "No camera image collections found"
    fi
}

################################################################################
# Execute Cleanup Based on Level
################################################################################

echo ""
log_info "Starting cleanup..."
echo ""

case $CLEANUP_TYPE in
    light)
        cleanup_logs
        cleanup_temp_files
        ;;

    standard)
        cleanup_logs
        cleanup_temp_files
        cleanup_build_artifacts
        cleanup_git
        ;;

    deep)
        cleanup_logs
        cleanup_temp_files
        cleanup_build_artifacts
        cleanup_node_modules
        cleanup_docker
        cleanup_git
        cleanup_camera_images
        ;;

    custom)
        echo "Select items to clean (y/n for each):"
        echo ""

        read -p "Clean logs? (y/n) " -n 1 -r
        echo
        [[ $REPLY =~ ^[Yy]$ ]] && cleanup_logs

        read -p "Clean temporary files? (y/n) " -n 1 -r
        echo
        [[ $REPLY =~ ^[Yy]$ ]] && cleanup_temp_files

        read -p "Clean build artifacts? (y/n) " -n 1 -r
        echo
        [[ $REPLY =~ ^[Yy]$ ]] && cleanup_build_artifacts

        read -p "Clean node_modules? (y/n) " -n 1 -r
        echo
        [[ $REPLY =~ ^[Yy]$ ]] && cleanup_node_modules

        read -p "Clean Docker resources? (y/n) " -n 1 -r
        echo
        [[ $REPLY =~ ^[Yy]$ ]] && cleanup_docker

        read -p "Clean Git working tree? (y/n) " -n 1 -r
        echo
        [[ $REPLY =~ ^[Yy]$ ]] && cleanup_git

        read -p "Clean camera images? (y/n) " -n 1 -r
        echo
        [[ $REPLY =~ ^[Yy]$ ]] && cleanup_camera_images
        ;;
esac

################################################################################
# Post-cleanup Status
################################################################################

echo ""
log_info "Calculating disk usage after cleanup..."
echo ""

# Recalculate sizes
LOGS_SIZE_AFTER=$(get_dir_size "logs")
DIST_SIZE_AFTER=$(get_dir_size "dist")
VITE_SIZE_AFTER=$(get_dir_size ".vite")
NODE_MODULES_SIZE_AFTER=$(get_dir_size "node_modules")
PIDS_SIZE_AFTER=$(get_dir_size ".pids")
CACHE_SIZE_AFTER=$(get_dir_size ".cache")
TMP_SIZE_AFTER=$(get_dir_size "tmp")

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Disk Usage After Cleanup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Logs:          $LOGS_SIZE → $LOGS_SIZE_AFTER"
echo "  Build (dist):  $DIST_SIZE → $DIST_SIZE_AFTER"
echo "  Vite cache:    $VITE_SIZE → $VITE_SIZE_AFTER"
echo "  Node modules:  $NODE_MODULES_SIZE → $NODE_MODULES_SIZE_AFTER"
echo "  PID files:     $PIDS_SIZE → $PIDS_SIZE_AFTER"
echo "  Cache:         $CACHE_SIZE → $CACHE_SIZE_AFTER"
echo "  Temp:          $TMP_SIZE → $TMP_SIZE_AFTER"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

################################################################################
# Post-cleanup Actions
################################################################################

# Check if node_modules was removed
if [ ! -d "node_modules" ] && [ "$CLEANUP_TYPE" = "deep" ]; then
    echo ""
    log_warning "node_modules was removed"
    read -p "Run 'npm install' now? (y/n) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Installing dependencies..."
        npm install
        log_success "Dependencies installed"
    else
        log_warning "Remember to run 'npm install' before starting the dev server"
    fi
fi

################################################################################
# Summary
################################################################################

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                   Cleanup Complete!                       ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
log_success "Project cleanup completed successfully"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Next Steps"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ ! -d "node_modules" ]; then
    echo "  1. Run: npm install"
    echo "  2. Run: ./startup.sh"
else
    echo "  1. Run: ./startup.sh"
fi

echo ""
echo "  To rebuild the project:"
echo "    npm run build"
echo ""
echo "  To start development:"
echo "    ./startup.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
log_success "Cleanup script finished ✓"
echo ""

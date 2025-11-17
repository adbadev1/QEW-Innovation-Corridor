#!/bin/bash

################################################################################
# QEW Innovation Corridor - Stop Script
#
# Purpose: Gracefully stop all running project services
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

# Banner
echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║     QEW Innovation Corridor - Stop Script                ║"
echo "║     Gracefully stopping all services                      ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

################################################################################
# Stop Frontend Service
################################################################################

log_info "Stopping frontend dev server..."

# Check for PID file
if [ -f ".pids/frontend.pid" ]; then
    FRONTEND_PID=$(cat .pids/frontend.pid)

    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        log_info "Stopping frontend server (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID 2>/dev/null || true
        sleep 2

        # Force kill if still running
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            log_warning "Force killing frontend server..."
            kill -9 $FRONTEND_PID 2>/dev/null || true
        fi

        rm -f .pids/frontend.pid
        log_success "Frontend server stopped"
    else
        log_warning "Frontend server not running (stale PID file)"
        rm -f .pids/frontend.pid
    fi
else
    log_info "No frontend PID file found"
fi

# Also check port 8200 and kill any process using it
if lsof -Pi :8200 -sTCP:LISTEN -t >/dev/null 2>&1; then
    log_warning "Port 8200 still in use, cleaning up..."
    PID=$(lsof -ti:8200)
    kill -9 $PID 2>/dev/null || true
    log_success "Cleaned up port 8200"
fi

################################################################################
# Stop Backend Services (Phase 2)
################################################################################

if [ -d "backend" ]; then
    log_info "Checking backend services..."

    # Stop Docker Compose services (local development)
    if [ -f "backend/docker-compose.yml" ]; then
        log_info "Stopping Docker Compose services..."
        cd backend
        docker-compose down
        cd ..
        log_success "Backend services stopped"
    fi

    # Stop individual backend PIDs
    for service in detection-agent assessment-agent communication-agent api-gateway; do
        if [ -f ".pids/${service}.pid" ]; then
            PID=$(cat .pids/${service}.pid)
            if ps -p $PID > /dev/null 2>&1; then
                log_info "Stopping $service (PID: $PID)..."
                kill $PID 2>/dev/null || true
                rm -f .pids/${service}.pid
                log_success "$service stopped"
            else
                rm -f .pids/${service}.pid
            fi
        fi
    done
else
    log_info "No local backend services to stop"
fi

################################################################################
# Stop Background Processes
################################################################################

log_info "Checking for other project processes..."

# Kill any npm processes for this project
PROJECT_NAME="qew-digital-twin-dashboard"
PIDS=$(ps aux | grep "$PROJECT_NAME" | grep -v grep | awk '{print $2}' || true)

if [ -n "$PIDS" ]; then
    log_info "Stopping remaining npm processes..."
    echo "$PIDS" | while read -r PID; do
        kill $PID 2>/dev/null || true
    done
    sleep 1
    log_success "Background processes stopped"
fi

# Kill any Vite processes on port 8200
VITE_PIDS=$(ps aux | grep "vite" | grep "8200" | grep -v grep | awk '{print $2}' || true)
if [ -n "$VITE_PIDS" ]; then
    log_info "Stopping Vite processes..."
    echo "$VITE_PIDS" | while read -r PID; do
        kill -9 $PID 2>/dev/null || true
    done
    log_success "Vite processes stopped"
fi

################################################################################
# Cleanup PID Directory
################################################################################

if [ -d ".pids" ]; then
    log_info "Cleaning up PID files..."
    rm -rf .pids/*
    log_success "PID files cleaned"
fi

################################################################################
# GCP Services Check (Informational Only)
################################################################################

if command -v gcloud &> /dev/null && [ "$(gcloud config get-value project 2>/dev/null)" = "qew-innovation-pilot" ]; then
    echo ""
    log_info "GCP Cloud Run services (Phase 2):"
    echo ""
    log_info "Cloud Run services are managed separately and not stopped by this script."
    log_info "To stop GCP services:"
    echo ""
    echo "  # Stop a specific service (scale to 0)"
    echo "  gcloud run services update SERVICE_NAME \\"
    echo "    --project=qew-innovation-pilot \\"
    echo "    --region=northamerica-northeast1 \\"
    echo "    --max-instances=0"
    echo ""
    echo "  # Or delete a service completely"
    echo "  gcloud run services delete SERVICE_NAME \\"
    echo "    --project=qew-innovation-pilot \\"
    echo "    --region=northamerica-northeast1"
    echo ""

    # List running Cloud Run services
    SERVICES=$(gcloud run services list \
        --project=qew-innovation-pilot \
        --region=northamerica-northeast1 \
        --format="table(name,status)" 2>/dev/null || echo "")

    if [ -n "$SERVICES" ]; then
        echo "  Currently deployed Cloud Run services:"
        echo "$SERVICES" | sed 's/^/  /'
    fi
    echo ""
fi

################################################################################
# Final Verification
################################################################################

log_info "Verifying all services stopped..."

# Check port 8200
if lsof -Pi :8200 -sTCP:LISTEN -t >/dev/null 2>&1; then
    log_warning "Port 8200 still in use after cleanup"
else
    log_success "Port 8200 is free"
fi

# Check for any remaining PIDs
if [ -d ".pids" ] && [ -n "$(ls -A .pids 2>/dev/null)" ]; then
    log_warning "Some PID files remain: $(ls .pids)"
else
    log_success "All PID files removed"
fi

################################################################################
# Summary
################################################################################

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                   Shutdown Complete!                      ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
log_success "All local services stopped successfully"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Service Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Frontend:      ❌ STOPPED"
echo "  Backend:       ❌ STOPPED (local)"
echo "  Port 8200:     ✅ FREE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "To start services again:"
echo "  ./startup.sh"
echo ""
echo "To cleanup build artifacts and logs:"
echo "  ./cleanup.sh"
echo ""
log_success "Services stopped safely ✓"
echo ""

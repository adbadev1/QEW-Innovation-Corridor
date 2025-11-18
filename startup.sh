#!/bin/bash

################################################################################
# QEW Innovation Corridor - Startup Script
#
# Purpose: Start all project services (frontend, backend when ready)
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
echo "║     QEW Innovation Corridor - Startup Script             ║"
echo "║     OVIN Pilot Project - ADBA Labs                        ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

################################################################################
# Pre-flight Checks
################################################################################

log_info "Running pre-flight checks..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    log_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    log_error "Node.js version 18+ required. Current: $(node -v)"
    exit 1
fi

log_success "Node.js $(node -v) detected"

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    log_error "npm is not installed"
    exit 1
fi

log_success "npm $(npm -v) detected"

# Check if gcloud is installed (optional, for GCP)
if command -v gcloud &> /dev/null; then
    GCP_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "not-set")
    log_success "gcloud CLI detected (Project: $GCP_PROJECT)"
else
    log_warning "gcloud CLI not installed (optional for Phase 2)"
fi

################################################################################
# Environment Setup
################################################################################

log_info "Checking environment configuration..."

# Check for .env file
if [ ! -f ".env" ]; then
    log_warning ".env file not found"
    if [ -f ".env.example" ]; then
        log_info "Creating .env from .env.example..."
        cp .env.example .env
        log_success ".env file created"
        log_warning "Please update .env with your API keys before continuing"
        read -p "Press Enter to continue or Ctrl+C to exit and configure..."
    fi
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
    log_success "Environment variables loaded"
fi

################################################################################
# Dependency Check
################################################################################

log_info "Checking dependencies..."

if [ ! -d "node_modules" ]; then
    log_warning "node_modules not found. Running npm install..."
    npm install
    log_success "Dependencies installed"
else
    # Check if package.json is newer than node_modules
    if [ "package.json" -nt "node_modules" ]; then
        log_warning "package.json updated. Running npm install..."
        npm install
        log_success "Dependencies updated"
    else
        log_success "Dependencies up to date"
    fi
fi

################################################################################
# Port Management
################################################################################
# Port Configuration: Synchronized with Universal Port Registry
# Source: /Users/adbalabs/config/universal_port_config.md (Line 88-114)
# QEW Innovation Corridor: Port 8200 (ACTIVE)
# Port Range: 8200 (frontend), 8080 (backend Phase 2 - Cloud Run)
################################################################################

log_info "Checking port availability..."

# Check if port 8200 is in use
if lsof -Pi :8200 -sTCP:LISTEN -t >/dev/null 2>&1; then
    log_warning "Port 8200 is already in use"
    PID=$(lsof -ti:8200)
    log_info "Process using port 8200: PID $PID"

    read -p "Kill existing process on port 8200? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill -9 $PID 2>/dev/null || true
        log_success "Killed process $PID"
        sleep 2
    else
        log_error "Cannot start: Port 8200 is in use"
        exit 1
    fi
else
    log_success "Port 8200 available"
fi

################################################################################
# Service Startup
################################################################################

echo ""
log_info "Starting services..."
echo ""

# Create PID directory
mkdir -p .pids

# Frontend Service (Vite Dev Server)
log_info "Starting frontend dev server (port 8200)..."

# Start in background and capture PID
nohup npm run dev > logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > .pids/frontend.pid

# Wait for server to start
log_info "Waiting for dev server to start..."
sleep 3

# Verify server is running
if ps -p $FRONTEND_PID > /dev/null; then
    log_success "Frontend dev server started (PID: $FRONTEND_PID)"
    log_success "Dashboard available at: http://localhost:8200"
else
    log_error "Frontend dev server failed to start"
    log_error "Check logs/frontend.log for details"
    exit 1
fi

# Backend Services (Phase 2 - GCP Cloud Run)
if [ -d "backend" ]; then
    log_info "Backend services detected (Phase 2)"

    # Check if running locally or on GCP
    if [ -f "backend/docker-compose.yml" ]; then
        log_info "Starting local backend services with Docker Compose..."
        cd backend
        docker-compose up -d
        cd ..
        log_success "Backend services started"
    else
        log_info "Backend services deployed to GCP Cloud Run"
        log_info "Project: qew-innovation-pilot (843899919832)"

        # List Cloud Run services
        if command -v gcloud &> /dev/null; then
            log_info "Checking Cloud Run services..."
            gcloud run services list \
                --project=qew-innovation-pilot \
                --region=northamerica-northeast1 \
                --format="table(name,status)" 2>/dev/null || true
        fi
    fi
else
    log_info "Backend services not yet deployed (Phase 2)"
fi

################################################################################
# Health Checks
################################################################################

echo ""
log_info "Running health checks..."

# Frontend health check
if curl -s http://localhost:8200 > /dev/null; then
    log_success "Frontend health check: PASS"
else
    log_warning "Frontend health check: FAIL (may still be starting up)"
fi

# GCP services health check (Phase 2)
if command -v gcloud &> /dev/null && [ "$(gcloud config get-value project 2>/dev/null)" = "qew-innovation-pilot" ]; then
    log_info "Checking GCP services..."

    # Check Cloud Run services
    SERVICES=$(gcloud run services list \
        --project=qew-innovation-pilot \
        --region=northamerica-northeast1 \
        --format="value(name)" 2>/dev/null || echo "")

    if [ -n "$SERVICES" ]; then
        for SERVICE in $SERVICES; do
            URL=$(gcloud run services describe $SERVICE \
                --project=qew-innovation-pilot \
                --region=northamerica-northeast1 \
                --format="value(status.url)" 2>/dev/null)

            if [ -n "$URL" ]; then
                if curl -s -o /dev/null -w "%{http_code}" "$URL" | grep -q "200\|404"; then
                    log_success "Cloud Run service $SERVICE: HEALTHY"
                else
                    log_warning "Cloud Run service $SERVICE: DEGRADED"
                fi
            fi
        done
    fi
fi

################################################################################
# Camera Collection Status Check
################################################################################

echo ""
log_info "Checking camera collection system..."

# Check if camera GUI is running
CAMERA_GUI_RUNNING=false
if ps aux | grep "qew_camera_gui.py" | grep -v grep > /dev/null 2>&1; then
    CAMERA_GUI_PID=$(ps aux | grep "qew_camera_gui.py" | grep -v grep | awk '{print $2}' | head -n 1)
    log_success "Camera collection GUI is running (PID: $CAMERA_GUI_PID)"
    CAMERA_GUI_RUNNING=true
else
    log_info "Camera collection GUI not running"
    log_info "To start: cd camera_scraper && python qew_camera_gui.py"
fi

# Check for Python installation (for camera scraper)
if command -v python &> /dev/null || command -v python3 &> /dev/null; then
    PYTHON_CMD=$(command -v python3 || command -v python)
    log_success "Python detected: $PYTHON_CMD"
else
    log_warning "Python not found - camera collection unavailable"
fi

################################################################################
# Summary
################################################################################

echo ""
echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                    Startup Complete!                      ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
log_success "All services started successfully"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Service Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Frontend:            ✅ RUNNING (PID: $FRONTEND_PID)"
echo "  Port:                8200"
echo "  URL:                 http://localhost:8200"
echo "  Live Demo:           https://adbadev1.github.io/QEW-Innovation-Corridor/"
echo ""
if [ "$CAMERA_GUI_RUNNING" = true ]; then
    echo "  Camera Collection:   ✅ RUNNING (PID: $CAMERA_GUI_PID)"
else
    echo "  Camera Collection:   ⏳ Not started"
fi
echo ""
echo "  Backend:             ⏳ Phase 2 (GCP Cloud Run)"
echo "  GCP Project:         qew-innovation-pilot (843899919832)"
echo "  Region:              northamerica-northeast1"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Logs:"
echo "  Frontend:      tail -f logs/frontend.log"
echo "  All Services:  tail -f logs/*.log"
echo ""
if [ "$CAMERA_GUI_RUNNING" = false ]; then
    echo "Start Camera Collection:"
    echo "  cd camera_scraper && python qew_camera_gui.py"
    echo ""
fi
echo "Stop Services:"
echo "  ./stop.sh      # Stops frontend + camera collection + backend"
echo ""
echo "Cleanup:"
echo "  ./cleanup.sh   # Clean logs, cache, build artifacts"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Open browser (optional)
if command -v open &> /dev/null; then
    read -p "Open browser? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sleep 2
        open http://localhost:8200
    fi
elif command -v xdg-open &> /dev/null; then
    read -p "Open browser? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sleep 2
        xdg-open http://localhost:8200
    fi
fi

log_success "QEW Innovation Corridor is ready! 🚀"
echo ""

#!/bin/bash
# Database Setup Script for QEW Innovation Corridor Backend
#
# This script initializes and seeds the SQLite database with camera data
# Run this after cloning the repository and setting up the virtual environment

set -e  # Exit on error

echo "========================================================================"
echo "🚀 QEW Innovation Corridor - Database Setup"
echo "========================================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Not in backend/api-gateway directory"
    echo "   Please run this script from: backend/api-gateway/"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found"
    echo "   Please run: python3.12 -m venv venv"
    echo "   Then: source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Activate virtual environment
echo "📦 Using Python virtual environment..."
PYTHON="./venv/bin/python3"

# Check if dependencies are installed
if ! $PYTHON -c "import sqlalchemy" 2>/dev/null; then
    echo "❌ Error: Dependencies not installed"
    echo "   Please run: source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

echo "✅ Dependencies verified"
echo ""

# Step 1: Remove old database if it exists
if [ -f "qew_corridor.db" ]; then
    echo "🗑️  Removing old database..."
    rm qew_corridor.db
    echo "✅ Old database removed"
fi

# Step 2: Run Alembic migrations to create schema
echo ""
echo "📐 Creating database schema with Alembic..."
./venv/bin/alembic upgrade head

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to run database migrations"
    exit 1
fi

echo "✅ Database schema created"

# Step 3: Seed cameras
echo ""
echo "📷 Seeding camera data (46 QEW COMPASS cameras)..."
echo "" | $PYTHON seed_cameras.py

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to seed camera data"
    exit 1
fi

# Step 4: Seed camera directions
echo ""
echo "🧭 Seeding camera direction data (48 direction records)..."
echo "" | $PYTHON seed_directions.py

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to seed direction data"
    exit 1
fi

# Step 5: Verify database
echo ""
echo "🔍 Verifying database..."
$PYTHON -c "
import sqlite3
conn = sqlite3.connect('qew_corridor.db')
cursor = conn.cursor()

cursor.execute('SELECT COUNT(*) FROM cameras')
cameras = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM camera_directions')
directions = cursor.fetchone()[0]

cursor.execute('SELECT COUNT(*) FROM cameras WHERE heading IS NOT NULL')
cameras_with_heading = cursor.fetchone()[0]

print(f'✅ Cameras: {cameras}')
print(f'✅ Direction records: {directions}')
print(f'✅ Cameras with heading: {cameras_with_heading}')

conn.close()
"

echo ""
echo "========================================================================"
echo "🎉 Database Setup Complete!"
echo "========================================================================"
echo ""
echo "📍 Database location: backend/api-gateway/qew_corridor.db"
echo ""
echo "Next steps:"
echo "  1. Start the backend server:"
echo "     cd backend/api-gateway"
echo "     source venv/bin/activate"
echo "     python main.py"
echo ""
echo "  2. Test the API:"
echo "     curl http://localhost:8000/api/cameras | jq"
echo "     curl http://localhost:8000/api/directions/cameras | jq"
echo ""
echo "  3. View API docs:"
echo "     http://localhost:8000/api/docs"
echo ""
echo "========================================================================"

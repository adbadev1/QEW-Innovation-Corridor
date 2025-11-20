# 🏗️ Full-Stack Developer Onboarding Guide

**QEW Innovation Corridor - Digital Twin Dashboard**
**Last Updated:** 2025-11-20
**Architecture:** React 18.3 + FastAPI 0.115 + SQLAlchemy 2.0 + SQLite/PostgreSQL

---

## 📋 Table of Contents

1. [Quick Start (5 Minutes)](#quick-start-5-minutes)
2. [System Architecture](#system-architecture)
3. [Backend Setup (FastAPI)](#backend-setup-fastapi)
4. [Frontend Setup (React + Vite)](#frontend-setup-react--vite)
5. [Database Setup](#database-setup)
6. [Development Workflow](#development-workflow)
7. [API Documentation](#api-documentation)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)
10. [Production Deployment](#production-deployment)

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites

- **Python 3.11+** (tested with 3.12)
- **Node.js 18+** and npm
- **Git**
- **PostgreSQL 15+** (optional - SQLite works for local dev)

### Clone and Setup

```bash
# 1. Clone repository
git clone https://github.com/adbadev1/QEW-Innovation-Corridor.git
cd QEW-Innovation-Corridor

# 2. Backend Setup (Terminal 1)
cd backend/api-gateway
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env: Use SQLite for quick start
echo "DATABASE_URL=sqlite+aiosqlite:///./qew_corridor.db" >> .env

# Initialize database
alembic upgrade head

# Seed database with camera data
python seed_cameras.py
python seed_directions.py

# Start backend server
python main.py
# Server: http://localhost:8000
# API Docs: http://localhost:8000/api/docs

# 3. Frontend Setup (Terminal 2)
cd ../..  # Back to project root
npm install

# Create .env file
cp .env.example .env
# Edit .env: VITE_API_BASE_URL=http://localhost:8000

# Start frontend dev server
npm run dev
# Frontend: http://localhost:8200
```

### Verify Installation

```bash
# Check backend health
curl http://localhost:8000/health

# Check camera data
curl http://localhost:8000/api/cameras/stats/summary

# Open browser
open http://localhost:8200
```

**Expected Results:**
- ✅ Map loads with QEW routes
- ✅ 46 camera markers visible
- ✅ Camera spotlights render (directional cones)
- ✅ Backend API accessible at http://localhost:8000/api/docs

---

## 🏛️ System Architecture

### Tech Stack

**Backend:**
- **Framework:** FastAPI 0.115 (async Python web framework)
- **ORM:** SQLAlchemy 2.0 (async with asyncpg/aiosqlite)
- **Migrations:** Alembic 1.14
- **Database:** PostgreSQL 15+ (production) / SQLite (development)
- **AI:** Google Gemini 2.0 Flash (work zone detection)
- **Storage:** GCP Cloud Storage (camera images)
- **Server:** Uvicorn (ASGI server)

**Frontend:**
- **Framework:** React 18.3
- **Build Tool:** Vite 5.4
- **Maps:** Leaflet 1.9 + React-Leaflet 4.2
- **Charts:** Recharts 2.15
- **Styling:** Tailwind CSS 3.4
- **Icons:** Lucide React 0.454

**Infrastructure:**
- **Deployment:** GitHub Pages (frontend), Cloud Run (backend - planned)
- **CI/CD:** GitHub Actions
- **Monitoring:** GCP Cloud Monitoring (planned)

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                      FRONTEND (React 18.3)                      │
│                     http://localhost:8200                       │
├─────────────────────────────────────────────────────────────────┤
│  • App.jsx (Main Dashboard)                                    │
│  • CameraSpotlightLayer (Camera directions)                    │
│  • MLValidationPanel (AI analysis)                             │
│  • TrafficMonitoringPanel (Work zones)                         │
│  • CameraCollectionPanel (Image collection)                    │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  │ HTTP/REST API (CORS enabled)
                  │ src/api/client.js (50+ functions)
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI 0.115)                       │
│                    http://localhost:8000                        │
├─────────────────────────────────────────────────────────────────┤
│  API ENDPOINTS (41 total)                                      │
│  ├─ /api/cameras         (6 endpoints)  - Camera CRUD         │
│  ├─ /api/work-zones      (8 endpoints)  - Work zone mgmt      │
│  ├─ /api/collection      (6 endpoints)  - Image collection    │
│  ├─ /api/directions      (8 endpoints)  - Camera directions   │
│  └─ /api/analysis        (6 endpoints)  - AI analysis         │
├─────────────────────────────────────────────────────────────────┤
│  SERVICES                                                       │
│  ├─ gemini_service.py    - Gemini Vision API integration      │
│  ├─ gcp_storage_service.py - GCP Cloud Storage                │
│  ├─ camera_service.py    - COMPASS camera fetching            │
│  └─ analysis_service.py  - End-to-end orchestration           │
└─────────────────┬───────────────────────────────────────────────┘
                  │
                  │ SQLAlchemy 2.0 (Async ORM)
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│              DATABASE (PostgreSQL / SQLite)                     │
│                   qew_corridor.db (72 KB)                       │
├─────────────────────────────────────────────────────────────────┤
│  TABLES:                                                        │
│  ├─ cameras (46 records)         - QEW COMPASS camera locs    │
│  ├─ camera_directions (48 records) - Camera heading data      │
│  ├─ work_zones (0 records)       - AI-detected work zones     │
│  ├─ collection_runs (0 records)  - Collection sessions        │
│  └─ alembic_version              - Migration tracking         │
└─────────────────────────────────────────────────────────────────┘
                  │
                  │ External APIs
                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL SERVICES                           │
├─────────────────────────────────────────────────────────────────┤
│  • Google Gemini 2.0 Flash (AI work zone detection)           │
│  • GCP Cloud Storage (qew-camera-images-public bucket)         │
│  • MTO COMPASS Cameras (46 traffic cameras via 511ON)         │
│  • vRSU Service (microservice - V2X broadcasts) :8081         │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. Camera Image Collection
   COMPASS API → Backend /api/collection → GCP Storage → Database

2. AI Work Zone Detection
   Camera Image → Gemini Vision API → Work Zone Analysis → Database

3. Frontend Display
   React → API Client → Backend API → Database → JSON Response → UI
```

---

## 🔧 Backend Setup (FastAPI)

### Directory Structure

```
backend/api-gateway/
├── main.py                 # FastAPI app entry point
├── config.py               # Pydantic settings
├── database.py             # SQLAlchemy async engine
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (DO NOT COMMIT)
├── .env.example            # Environment template
├── alembic.ini             # Alembic configuration
├── alembic/
│   ├── env.py              # Migration environment
│   └── versions/           # Migration files
├── api/                    # API endpoint modules
│   ├── __init__.py
│   ├── cameras.py          # Camera endpoints (6)
│   ├── work_zones.py       # Work zone endpoints (8)
│   ├── collection.py       # Collection endpoints (6)
│   ├── directions.py       # Direction endpoints (8)
│   └── analysis.py         # Analysis endpoints (6)
├── models/                 # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── camera.py           # Camera model
│   ├── work_zone.py        # WorkZone model
│   ├── collection.py       # CollectionRun model
│   └── camera_direction.py # CameraDirection model
├── services/               # Business logic services
│   ├── __init__.py
│   ├── gemini_service.py   # Gemini Vision integration
│   ├── gcp_storage_service.py  # GCP Cloud Storage
│   ├── camera_service.py   # COMPASS camera API
│   └── analysis_service.py # Analysis orchestration
├── seed_cameras.py         # Database seeding script
├── seed_directions.py      # Direction seeding script
└── qew_corridor.db         # SQLite database (gitignored)
```

### Environment Variables (`.env`)

```bash
# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./qew_corridor.db
# OR for PostgreSQL:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/qew_corridor

# Google Cloud Platform
GCP_PROJECT_ID=qew-innovation-pilot
GCP_STORAGE_BUCKET=qew-camera-images-public
GCP_STORAGE_API_KEY=your_gcp_api_key_here

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp

# vRSU Service Integration
VRSU_SERVICE_URL=http://localhost:8081
VRSU_ENABLED=true

# CORS Configuration
CORS_ORIGINS=http://localhost:8200,http://localhost:3000,https://adbadev1.github.io

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Feature Flags
ENABLE_RATE_LIMITING=false
ENABLE_CACHING=false
ENABLE_ANALYTICS=false
```

### Database Models

**1. Camera Model** (`models/camera.py`)
```python
class Camera(Base):
    __tablename__ = "cameras"

    id = Column(Integer, primary_key=True)
    camera_id = Column(String(50), unique=True)  # e.g., "C210"
    source = Column(String(50), default="511ON")
    location = Column(String(200))
    latitude = Column(Float)
    longitude = Column(Float)
    heading = Column(Float, nullable=True)  # 0-360 degrees
    direction = Column(String(10), nullable=True)  # N, NE, E, SE, S, SW, W, NW
    direction_confidence = Column(String(10), nullable=True)
    active = Column(Boolean, default=True)
    views = Column(JSON, nullable=True)  # Camera views metadata
```

**2. CameraDirection Model** (`models/camera_direction.py`)
```python
class CameraDirection(Base):
    __tablename__ = "camera_directions"

    id = Column(Integer, primary_key=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    view_id = Column(Integer, nullable=True)
    heading = Column(Float)  # 0-360 degrees
    direction = Column(String(10))  # N, NE, E, SE, S, SW, W, NW
    confidence = Column(String(10))  # high, medium, low
    eastbound_heading = Column(Float, nullable=True)
    westbound_heading = Column(Float, nullable=True)
    model = Column(String(50), default="claude-vision")
    analysis_method = Column(String(50))
    analyzed_at = Column(DateTime, server_default=func.now())
```

**3. WorkZone Model** (`models/work_zone.py`)
```python
class WorkZone(Base):
    __tablename__ = "work_zones"

    id = Column(Integer, primary_key=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"))
    latitude = Column(Float)
    longitude = Column(Float)
    risk_score = Column(Integer)  # 1-10
    confidence = Column(Float)  # 0.0-1.0
    workers = Column(Integer, default=0)
    vehicles = Column(Integer, default=0)
    equipment = Column(Integer, default=0)
    barriers = Column(Boolean, default=False)
    hazards = Column(JSON, nullable=True)
    violations = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    gcp_image_url = Column(String(500), nullable=True)
    status = Column(String(20), default="active")
    detected_at = Column(DateTime, server_default=func.now())
```

**4. CollectionRun Model** (`models/collection.py`)
```python
class CollectionRun(Base):
    __tablename__ = "collection_runs"

    id = Column(Integer, primary_key=True)
    collection_id = Column(String(50), unique=True)
    status = Column(String(20))  # in_progress, completed, failed
    images_collected = Column(Integer, default=0)
    work_zones_detected = Column(Integer, default=0)
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
```

### Running Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "Add new field"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Show current revision
alembic current

# Show migration history
alembic history
```

### Seeding the Database

```bash
# Seed cameras (46 QEW COMPASS cameras)
python seed_cameras.py

# Seed camera directions (48 direction records)
python seed_directions.py

# Verify data
python -c "import sqlite3; conn = sqlite3.connect('qew_corridor.db'); \
  cursor = conn.cursor(); \
  cursor.execute('SELECT COUNT(*) FROM cameras'); \
  print('Cameras:', cursor.fetchone()[0]); \
  cursor.execute('SELECT COUNT(*) FROM camera_directions'); \
  print('Directions:', cursor.fetchone()[0])"
```

---

## ⚛️ Frontend Setup (React + Vite)

### Directory Structure

```
src/
├── App.jsx                 # Main dashboard component
├── main.jsx                # React entry point
├── index.css               # Tailwind CSS imports
├── api/
│   └── client.js           # Backend API client (50+ functions)
├── components/
│   ├── CameraSpotlight.jsx          # Spotlight cone rendering
│   ├── CameraSpotlightLayer.jsx     # Backend-integrated spotlights
│   ├── MLValidationPanel.jsx        # AI validation (legacy)
│   ├── MLValidationPanel_BACKEND.jsx  # AI validation (backend)
│   ├── TrafficMonitoringPanel.jsx   # Traffic monitoring
│   └── CameraCollectionPanel.jsx    # Image collection
├── contexts/
│   ├── CollectionContext.jsx  # Collection state management
│   └── V2XContext.jsx         # V2X RSU integration
├── services/
│   ├── geminiVision.js     # [DEPRECATED] Use backend API
│   ├── gcpStorage.js       # [DEPRECATED] Use backend API
│   ├── imageSearchAPI.js   # [DEPRECATED] Use backend API
│   └── thumbnailStorage.js # UI-only (safe to keep)
├── utils/
│   ├── riskUtils.js        # Risk scoring utilities
│   ├── workZoneHistory.js  # Work zone storage
│   └── imageMetadata.js    # Image metadata helpers
└── data/
    ├── qewData.js          # Camera locations (46 cameras)
    └── qewRoutes.js        # OSRM routes (680 waypoints)
```

### Environment Variables (`.env`)

```bash
# Backend API Configuration
VITE_API_BASE_URL=http://localhost:8000

# ⚠️ DEPRECATED: API keys below are being moved to backend for security
# These will be removed in future versions - use backend API instead

# Google Gemini AI API Key (DEPRECATED - use backend)
VITE_GEMINI_API_KEY=your_gemini_api_key_here

# Google Cloud Platform (DEPRECATED - use backend)
VITE_GCP_PROJECT_ID=your_gcp_project_id_here
VITE_GCP_STORAGE_BUCKET=qew-camera-images
VITE_GCP_API_KEY=your_gcp_api_key_here

# Gemini Model (optional)
VITE_GEMINI_MODEL=gemini-2.0-flash-exp
```

### API Client (`src/api/client.js`)

The API client provides 50+ functions for backend communication:

```javascript
import {
  // Cameras
  getCameras,
  getCamera,
  getCameraStats,

  // Work Zones
  getActiveWorkZones,
  getWorkZoneHistory,
  getWorkZoneStats,

  // Camera Directions (for spotlights)
  getCamerasWithDirections,
  getCameraDirections,

  // Collection
  startCollection,
  getCollectionStatus,
  analyzeCollection,

  // Analysis
  analyzeImage,
  batchAnalyzeImages
} from './api/client';

// Example usage
const cameras = await getCameras({ active_only: true });
const workZones = await getActiveWorkZones(5); // min_risk = 5
const spotlights = await getCamerasWithDirections({ has_direction: true });
```

### Camera Spotlight Integration

The camera spotlights are integrated via `CameraSpotlightLayer.jsx`:

```javascript
// src/components/CameraSpotlightLayer.jsx
const CameraSpotlightLayer = () => {
  const [cameraDirections, setCameraDirections] = useState([]);

  useEffect(() => {
    const fetchCameraDirections = async () => {
      try {
        const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${API_BASE_URL}/api/directions/cameras`);
        const data = await response.json();
        setCameraDirections(data);
      } catch (err) {
        console.error('Failed to load camera directions:', err);
      }
    };

    fetchCameraDirections();
    const interval = setInterval(fetchCameraDirections, 30000); // Refresh every 30s
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      {cameraDirections.map((camera) =>
        camera.direction_views.map((view, viewIndex) => (
          <CameraSpotlight
            key={`spotlight-${camera.camera_id}-${viewIndex}`}
            latitude={camera.latitude}
            longitude={camera.longitude}
            heading={view.heading}
            color={getDirectionColor(view.direction)}
            opacity={0.25}
          />
        ))
      )}
    </>
  );
};
```

### Using Backend-Integrated Components

To use the backend-integrated ML validation panel:

```javascript
// In App.jsx, swap the import:
// import MLValidationPanel from './components/MLValidationPanel';
import MLValidationPanel from './components/MLValidationPanel_BACKEND';

// The backend version uses:
// - getActiveWorkZones() instead of localStorage
// - Backend /api/analysis/image endpoint for AI analysis
// - Real-time polling for work zone updates
```

---

## 🗄️ Database Setup

### Option 1: SQLite (Quick Local Development)

**Pros:** No setup required, perfect for local testing
**Cons:** Not suitable for production, no concurrent writes

```bash
# .env configuration
DATABASE_URL=sqlite+aiosqlite:///./qew_corridor.db

# Initialize
alembic upgrade head

# Seed data
python seed_cameras.py
python seed_directions.py

# Database file location: backend/api-gateway/qew_corridor.db
```

### Option 2: PostgreSQL (Production-Ready)

**Pros:** Production-ready, concurrent writes, better performance
**Cons:** Requires PostgreSQL installation

#### Install PostgreSQL (macOS)

```bash
# Install via Homebrew
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb qew_corridor

# Create user (optional)
createuser -P postgres  # Set password: postgres
```

#### Configure Backend

```bash
# .env configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/qew_corridor

# Initialize
alembic upgrade head

# Seed data
python seed_cameras.py
python seed_directions.py
```

### Database Schema

```sql
-- Cameras table
CREATE TABLE cameras (
    id SERIAL PRIMARY KEY,
    camera_id VARCHAR(50) UNIQUE NOT NULL,
    source VARCHAR(50) DEFAULT '511ON',
    location VARCHAR(200) NOT NULL,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    heading FLOAT,
    direction VARCHAR(10),
    direction_confidence VARCHAR(10),
    active BOOLEAN DEFAULT TRUE,
    views JSON
);

-- Camera directions table
CREATE TABLE camera_directions (
    id SERIAL PRIMARY KEY,
    camera_id INTEGER REFERENCES cameras(id),
    view_id INTEGER,
    heading FLOAT NOT NULL,
    direction VARCHAR(10) NOT NULL,
    confidence VARCHAR(10) DEFAULT 'medium',
    eastbound_heading FLOAT,
    westbound_heading FLOAT,
    model VARCHAR(50) DEFAULT 'claude-vision',
    analysis_method VARCHAR(50) DEFAULT 'satellite_comparison',
    analyzed_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(camera_id, view_id)
);

-- Work zones table
CREATE TABLE work_zones (
    id SERIAL PRIMARY KEY,
    camera_id INTEGER REFERENCES cameras(id),
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    risk_score INTEGER NOT NULL,
    confidence FLOAT NOT NULL,
    workers INTEGER DEFAULT 0,
    vehicles INTEGER DEFAULT 0,
    equipment INTEGER DEFAULT 0,
    barriers BOOLEAN DEFAULT FALSE,
    hazards JSON,
    violations JSON,
    recommendations JSON,
    gcp_image_url VARCHAR(500),
    status VARCHAR(20) DEFAULT 'active',
    detected_at TIMESTAMP DEFAULT NOW()
);

-- Collection runs table
CREATE TABLE collection_runs (
    id SERIAL PRIMARY KEY,
    collection_id VARCHAR(50) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'in_progress',
    images_collected INTEGER DEFAULT 0,
    work_zones_detected INTEGER DEFAULT 0,
    started_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);
```

---

## 🔄 Development Workflow

### Starting Development

```bash
# Terminal 1: Backend
cd backend/api-gateway
source venv/bin/activate
python main.py

# Terminal 2: Frontend
npm run dev

# Terminal 3: Git workflow
git checkout -b feature/my-new-feature
# Make changes...
git add .
git commit -m "feat: add new feature"
git push origin feature/my-new-feature
```

### Hot Reloading

**Backend:** Uvicorn automatically reloads on file changes
**Frontend:** Vite automatically reloads on file changes

### Adding a New API Endpoint

```python
# 1. Create endpoint in backend/api-gateway/api/your_module.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("/your-endpoint")
async def your_endpoint(db: AsyncSession = Depends(get_db)):
    # Your logic here
    return {"message": "Hello"}

# 2. Register router in main.py
from api import your_module
app.include_router(your_module.router, prefix="/api/your-module", tags=["Your Module"])

# 3. Add client function in src/api/client.js
export async function yourEndpoint() {
  return apiRequest('/api/your-module/your-endpoint');
}

# 4. Use in React component
import { yourEndpoint } from '../api/client';

const data = await yourEndpoint();
```

### Adding a New Database Model

```python
# 1. Create model in backend/api-gateway/models/your_model.py
from sqlalchemy import Column, Integer, String
from database import Base

class YourModel(Base):
    __tablename__ = "your_table"

    id = Column(Integer, primary_key=True)
    name = Column(String(100))

# 2. Import in models/__init__.py
from .your_model import YourModel
__all__ = [..., "YourModel"]

# 3. Generate migration
alembic revision --autogenerate -m "Add your_table"

# 4. Apply migration
alembic upgrade head
```

### Code Style

**Backend (Python):**
- PEP 8 style guide
- Type hints encouraged
- Async/await for all I/O operations
- Docstrings for public functions

**Frontend (JavaScript):**
- ES6+ syntax
- Functional components with hooks
- PropTypes or TypeScript (planned)
- Tailwind CSS for styling

---

## 📚 API Documentation

### Interactive API Docs

Once the backend is running, access interactive documentation:

- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc
- **OpenAPI JSON:** http://localhost:8000/api/openapi.json

### Key Endpoints

#### Health & Info

```bash
GET /health
# Response: {"status":"healthy","database":"connected",...}

GET /
# Response: API information and version
```

#### Cameras

```bash
GET /api/cameras
# Query params: skip, limit, active_only, has_direction
# Returns: List of cameras

GET /api/cameras/{camera_id}
# Returns: Single camera details

GET /api/cameras/stats/summary
# Returns: {"total_cameras":46,"active_cameras":46,...}
```

#### Camera Directions (Spotlights)

```bash
GET /api/directions/cameras
# Query params: skip, limit, has_direction
# Returns: Cameras with direction_views array for spotlight rendering

GET /api/directions
# Returns: All direction records

GET /api/directions/stats/summary
# Returns: Direction statistics
```

#### Work Zones

```bash
GET /api/work-zones/active
# Query params: min_risk (default: 5)
# Returns: Active work zones with risk_score >= min_risk

GET /api/work-zones/history
# Returns: All historical work zones

POST /api/work-zones
# Body: { camera_id, latitude, longitude, risk_score, ... }
# Creates new work zone

GET /api/work-zones/stats/summary
# Returns: Work zone statistics
```

#### Collection

```bash
POST /api/collection/start
# Body: { camera_ids: [...], collection_type: "full" }
# Starts new collection run

GET /api/collection/status/{collection_id}
# Returns: Collection progress and status

POST /api/collection/analyze/{collection_id}
# Triggers AI analysis on collected images
```

#### Analysis

```bash
POST /api/analysis/image
# Body: { image_url, camera_id, latitude, longitude, location }
# Analyzes single image for work zone detection

POST /api/analysis/batch
# Body: { image_urls: [...], camera_ids: [...] }
# Batch analyzes multiple images

POST /api/analysis/upload
# Multipart form: file=@image.jpg
# Uploads and analyzes image
```

---

## 🧪 Testing

### Backend Tests

```bash
cd backend/api-gateway
source venv/bin/activate

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_cameras.py

# Run with verbose output
pytest -v
```

### Frontend Tests

```bash
# Run Vite build test
npm run build

# Lint
npm run lint

# Type check (if using TypeScript)
npm run type-check
```

### Integration Testing

```bash
# 1. Start backend
cd backend/api-gateway && python main.py

# 2. Test health endpoint
curl http://localhost:8000/health

# 3. Test camera endpoint
curl http://localhost:8000/api/cameras/stats/summary

# 4. Test directions endpoint (for spotlights)
curl http://localhost:8000/api/directions/cameras | jq

# 5. Start frontend
npm run dev

# 6. Open browser and verify:
# - Map loads
# - Camera markers visible
# - Spotlights render
# - No console errors
```

### Manual Testing Checklist

- [ ] Backend health check passes
- [ ] Database has 46 cameras
- [ ] Database has 48 direction records
- [ ] Frontend map loads
- [ ] Camera markers render (46 total)
- [ ] Camera spotlights render (directional cones)
- [ ] No console errors
- [ ] API calls succeed (check Network tab)

---

## 🐛 Troubleshooting

### Backend Issues

**"ModuleNotFoundError: No module named 'X'"**
```bash
cd backend/api-gateway
source venv/bin/activate
pip install -r requirements.txt
```

**"role 'postgres' does not exist"**
```bash
# Option 1: Create postgres user
createuser -P postgres  # Set password: postgres

# Option 2: Use SQLite instead
echo "DATABASE_URL=sqlite+aiosqlite:///./qew_corridor.db" > .env
alembic upgrade head
```

**"Database initialization failed"**
```bash
# Check database URL
echo $DATABASE_URL

# Re-run migrations
alembic upgrade head

# Check database file exists (SQLite)
ls -lh qew_corridor.db
```

**"Port 8000 already in use"**
```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or change port in .env
echo "API_PORT=8001" >> .env
```

### Frontend Issues

**"Failed to fetch" errors**
```bash
# 1. Check backend is running
curl http://localhost:8000/health

# 2. Check CORS configuration
# backend/api-gateway/.env should include:
CORS_ORIGINS=http://localhost:8200

# 3. Check frontend .env
cat .env
# Should have: VITE_API_BASE_URL=http://localhost:8000

# 4. Restart both servers
```

**Camera spotlights not rendering**
```bash
# 1. Check backend directions endpoint
curl http://localhost:8000/api/directions/cameras

# 2. Check database has direction data
cd backend/api-gateway
python -c "import sqlite3; \
  conn = sqlite3.connect('qew_corridor.db'); \
  cursor = conn.cursor(); \
  cursor.execute('SELECT COUNT(*) FROM camera_directions'); \
  print('Directions:', cursor.fetchone()[0])"

# 3. If no data, re-seed
python seed_directions.py

# 4. Check browser console for errors
# Open DevTools → Console tab
```

**Build errors**
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear Vite cache
rm -rf node_modules/.vite
npm run dev
```

### Database Issues

**"Migration failed"**
```bash
# Check current revision
alembic current

# Downgrade to base
alembic downgrade base

# Re-apply all migrations
alembic upgrade head
```

**"Database locked" (SQLite)**
```bash
# Stop all backend processes
pkill -f "python main.py"

# Remove lock file
rm qew_corridor.db-journal

# Restart backend
python main.py
```

**Data not showing up**
```bash
# Re-seed database
python seed_cameras.py
python seed_directions.py

# Verify data
python -c "import sqlite3; \
  conn = sqlite3.connect('qew_corridor.db'); \
  cursor = conn.cursor(); \
  cursor.execute('SELECT COUNT(*) FROM cameras'); \
  print('Cameras:', cursor.fetchone()[0]); \
  cursor.execute('SELECT COUNT(*) FROM camera_directions'); \
  print('Directions:', cursor.fetchone()[0])"
```

---

## 🚀 Production Deployment

### Backend Deployment (Google Cloud Run)

```bash
# 1. Build Docker image (TODO: Create Dockerfile)
docker build -t qew-backend:latest backend/api-gateway

# 2. Push to Google Container Registry
docker tag qew-backend:latest gcr.io/qew-innovation-pilot/backend:latest
docker push gcr.io/qew-innovation-pilot/backend:latest

# 3. Deploy to Cloud Run
gcloud run deploy qew-backend \
  --image gcr.io/qew-innovation-pilot/backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=postgresql://...cloud.sql..." \
  --set-env-vars="GEMINI_API_KEY=..." \
  --set-env-vars="GCP_STORAGE_BUCKET=qew-camera-images-public"
```

### Database Migration (SQLite → Cloud SQL)

```bash
# 1. Create Cloud SQL PostgreSQL instance
gcloud sql instances create qew-db \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# 2. Create database
gcloud sql databases create qew_corridor --instance=qew-db

# 3. Export SQLite data
sqlite3 qew_corridor.db .dump > data.sql

# 4. Import to PostgreSQL
# (Requires manual conversion or use pgloader)

# 5. Update backend .env
DATABASE_URL=postgresql+asyncpg://postgres:password@/qew_corridor?host=/cloudsql/qew-innovation-pilot:us-central1:qew-db
```

### Frontend Deployment (GitHub Pages)

```bash
# Already configured! Just push to main branch
git push origin main

# Automatic deployment via GitHub Actions
# Live at: https://adbadev1.github.io/QEW-Innovation-Corridor/

# Update API base URL for production
# .env.production:
VITE_API_BASE_URL=https://qew-backend-xxxxx.run.app
```

---

## 📖 Additional Resources

### Documentation

- **Backend README:** `backend/api-gateway/README.md`
- **Refactoring Status:** `REFACTORING_STATUS.md`
- **Test Report:** `TEST_REPORT.md`
- **Integration Guide:** `INTEGRATION_COMPLETE.md`

### External Documentation

- **FastAPI:** https://fastapi.tiangolo.com/
- **SQLAlchemy:** https://docs.sqlalchemy.org/en/20/
- **React:** https://react.dev/
- **Vite:** https://vitejs.dev/
- **Leaflet:** https://leafletjs.com/
- **Tailwind CSS:** https://tailwindcss.com/

### Project Links

- **GitHub Repository:** https://github.com/adbadev1/QEW-Innovation-Corridor
- **Live Demo:** https://adbadev1.github.io/QEW-Innovation-Corridor/
- **API Docs (local):** http://localhost:8000/api/docs

### Support

- **Issues:** https://github.com/adbadev1/QEW-Innovation-Corridor/issues
- **OVIN Program:** https://www.ovinhub.ca/
- **MTO COMPASS:** http://www.mto.gov.on.ca/english/traveller/trip/compass.shtml

---

## ✅ Onboarding Checklist

- [ ] Clone repository
- [ ] Install Python 3.11+
- [ ] Install Node.js 18+
- [ ] Setup backend virtual environment
- [ ] Install backend dependencies
- [ ] Configure backend `.env`
- [ ] Run database migrations
- [ ] Seed database (cameras + directions)
- [ ] Start backend server
- [ ] Verify backend health check
- [ ] Install frontend dependencies
- [ ] Configure frontend `.env`
- [ ] Start frontend dev server
- [ ] Verify map loads with camera markers
- [ ] Verify camera spotlights render
- [ ] Read API documentation
- [ ] Make first test API call
- [ ] Create feature branch
- [ ] Make first commit

---

**Welcome to the QEW Innovation Corridor team!** 🎉

If you have questions or need help, please open an issue or reach out to the development team.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

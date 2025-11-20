# QEW Innovation Corridor - API Gateway

FastAPI backend for work zone safety monitoring system.

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- PostgreSQL 15+ (or use SQLite for local development)

### Installation

```bash
# Navigate to API Gateway directory
cd backend/api-gateway

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file:**
   ```bash
   # Database (PostgreSQL or SQLite)
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/qew_corridor
   # OR for SQLite (local development):
   # DATABASE_URL=sqlite+aiosqlite:///./qew_corridor.db

   # Google Cloud Platform
   GCP_PROJECT_ID=qew-innovation-pilot
   GCP_STORAGE_BUCKET=qew-camera-images-public
   GCP_STORAGE_API_KEY=your_gcp_api_key_here

   # Gemini AI
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.0-flash-exp

   # CORS (add your frontend URL)
   CORS_ORIGINS=http://localhost:8200,http://localhost:3000
   ```

### Database Setup

#### Option 1: PostgreSQL (Recommended for Production)

```bash
# Install PostgreSQL (macOS)
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb qew_corridor

# Run migrations
alembic upgrade head
```

#### Option 2: SQLite (Quick Local Testing)

```bash
# Just update DATABASE_URL in .env:
DATABASE_URL=sqlite+aiosqlite:///./qew_corridor.db

# Run migrations
alembic upgrade head
```

### Run the Server

```bash
# Development mode (auto-reload)
python main.py

# Production mode
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Server will be running at:** http://localhost:8000

## 📚 API Documentation

Once the server is running, access interactive API documentation:

- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc
- **OpenAPI JSON:** http://localhost:8000/api/openapi.json

## 🛠️ API Endpoints

### Health & Info
- `GET /` - API information
- `GET /health` - Health check

### Cameras (`/api/cameras`)
- `GET /api/cameras` - List cameras
- `GET /api/cameras/{camera_id}` - Get specific camera
- `POST /api/cameras` - Create camera
- `PUT /api/cameras/{camera_id}` - Update camera
- `DELETE /api/cameras/{camera_id}` - Delete camera (soft)
- `GET /api/cameras/stats/summary` - Camera statistics

### Work Zones (`/api/work-zones`)
- `GET /api/work-zones` - List work zones
- `GET /api/work-zones/active` - Active work zones (dashboard)
- `GET /api/work-zones/history` - Historical work zones
- `GET /api/work-zones/{id}` - Get specific work zone
- `POST /api/work-zones` - Create work zone
- `PUT /api/work-zones/{id}/resolve` - Resolve work zone
- `DELETE /api/work-zones/{id}` - Delete work zone
- `GET /api/work-zones/stats/summary` - Work zone statistics

### Collection (`/api/collection`)
- `POST /api/collection/start` - Start collection run
- `GET /api/collection/status/{id}` - Get collection status
- `POST /api/collection/analyze/{id}` - Trigger analysis
- `GET /api/collection/history` - Collection history
- `GET /api/collection/latest` - Latest collection
- `GET /api/collection/stats/summary` - Collection statistics

### Camera Directions (`/api/directions`)
- `POST /api/directions/analyze` - Trigger direction analysis
- `GET /api/directions` - List camera directions
- `GET /api/directions/cameras` - Cameras with directions
- `POST /api/directions` - Create direction record
- `PUT /api/directions/{camera_id}` - Update direction
- `POST /api/directions/import-csv` - Import from CSV
- `GET /api/directions/stats/summary` - Direction statistics

### AI Analysis (`/api/analysis`)
- `POST /api/analysis/image` - Analyze single image
- `POST /api/analysis/upload` - Upload and analyze image
- `POST /api/analysis/batch` - Batch analyze images
- `GET /api/analysis/history` - Analysis history
- `POST /api/analysis/prompt` - Test custom prompts
- `GET /api/analysis/stats/summary` - Analysis statistics

## 🧪 Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Get all cameras
curl http://localhost:8000/api/cameras

# Get active work zones
curl http://localhost:8000/api/work-zones/active

# Get cameras with direction data
curl http://localhost:8000/api/directions/cameras
```

### Using Python

```python
import requests

# Health check
response = requests.get('http://localhost:8000/health')
print(response.json())

# Get active work zones
response = requests.get('http://localhost:8000/api/work-zones/active')
work_zones = response.json()
print(f"Found {len(work_zones)} active work zones")
```

### Using Frontend

The React frontend at `http://localhost:8200` automatically connects to the backend via `src/api/client.js`.

## 🗄️ Database Models

### Camera
- QEW COMPASS traffic camera locations
- Includes GPS coordinates, direction data
- Links to multiple views

### WorkZone
- AI-detected work zones from camera images
- Risk scores (1-10), confidence levels
- Hazards, violations, recommendations
- Links to camera and collection run

### CollectionRun
- Tracks camera image collection sessions
- Status tracking (in_progress, completed, failed)
- Statistics (images collected, work zones detected)

### CameraDirection
- Camera heading/direction analysis
- Multiple views per camera
- Confidence levels (high, medium, low)
- Integrates Corey's direction work

## 🔧 Development

### Code Structure

```
backend/api-gateway/
├── main.py              # FastAPI app entry point
├── config.py            # Configuration settings
├── database.py          # Database connection
├── requirements.txt     # Python dependencies
├── alembic.ini          # Database migrations config
├── api/                 # API endpoints
│   ├── cameras.py
│   ├── work_zones.py
│   ├── collection.py
│   ├── directions.py
│   └── analysis.py
├── models/              # SQLAlchemy models
│   ├── camera.py
│   ├── work_zone.py
│   ├── collection.py
│   └── camera_direction.py
└── services/            # Business logic
    ├── gemini_service.py
    ├── gcp_storage_service.py
    ├── camera_service.py
    └── analysis_service.py
```

### Creating Migrations

```bash
# Generate migration
alembic revision --autogenerate -m "Add new field"

# Apply migration
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html
```

## 🚀 Deployment

### Docker (Recommended)

```dockerfile
# TODO: Create Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Cloud Run (GCP)

```bash
# Build and deploy
gcloud run deploy qew-api-gateway \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated
```

## 📝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://...` |
| `GCP_PROJECT_ID` | Google Cloud project ID | - |
| `GCP_STORAGE_BUCKET` | GCS bucket for images | `qew-camera-images-public` |
| `GEMINI_API_KEY` | Gemini AI API key | - |
| `GEMINI_MODEL` | Gemini model to use | `gemini-2.0-flash-exp` |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:8200` |
| `API_HOST` | Server bind address | `0.0.0.0` |
| `API_PORT` | Server port | `8000` |
| `LOG_LEVEL` | Logging level | `INFO` |

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'X'"
```bash
pip install -r requirements.txt
```

### "Connection refused" from frontend
- Ensure backend is running on port 8000
- Check CORS_ORIGINS in .env includes frontend URL
- Verify VITE_API_BASE_URL in frontend .env

### Database connection errors
- Check DATABASE_URL is correct
- Ensure PostgreSQL is running: `brew services list`
- Try SQLite for testing: `DATABASE_URL=sqlite+aiosqlite:///./qew_corridor.db`

### Gemini API errors
- Verify GEMINI_API_KEY is set in .env
- Check API quota: https://console.cloud.google.com/
- Test with mock mode (API key not required)

## 📞 Support

- **Documentation:** `docs/` directory in project root
- **Issues:** https://github.com/adbadev1/QEW-Innovation-Corridor/issues
- **OVIN Program:** https://www.ovinhub.ca/

---

**Built with:** FastAPI 0.115, SQLAlchemy 2.0, PostgreSQL 15, Python 3.11
**License:** Proprietary (OVIN $150K Pilot Application)
**Organization:** ADBA Labs

🤖 Generated with [Claude Code](https://claude.com/claude-code)

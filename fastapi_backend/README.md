# FastAPI Backend - QEW Innovation Corridor

Unified backend integrating camera scraper and AI direction analysis functionality.

## 🏗️ Architecture

```
fastapi_backend/
├── main.py                    # FastAPI application entry point
├── config.py                  # Configuration settings
├── database/                  # Database modules
│   ├── camera_db.py          # Camera data database
│   └── direction_db.py       # AI direction assessments database
└── services/                  # Business logic services
    ├── camera_scraper.py     # Camera scraping service
    ├── direction_analyzer.py # AI direction analysis service
    ├── claude_client.py      # Claude API client
    ├── gemini_analyzer.py    # Gemini API client
    ├── satellite_fetcher.py  # Satellite image fetcher
    └── camera_fetcher.py     # Camera image fetcher
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (if not already created)
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example environment file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Edit .env and add your API keys
```

### 3. Start the Server

```bash
python start_backend.py
```

The server will start at `http://localhost:8000`

## 📡 API Endpoints

### Camera Scraper

- `POST /api/scraper/start` - Start camera scraping
- `POST /api/scraper/stop` - Stop camera scraping
- `GET /api/scraper/status` - Get scraper status

### Camera Data

- `GET /api/cameras/latest` - Get latest camera data with images
- `GET /api/cameras/{camera_id}` - Get specific camera
- `GET /api/collections/latest` - Get latest collection info
- `GET /api/stats` - Get database statistics

### AI Direction Analysis

- `POST /api/directions/analyze` - Analyze single camera direction
- `POST /api/directions/analyze-batch` - Analyze all pending cameras
- `POST /api/directions/stop` - Stop direction analysis
- `GET /api/directions/status` - Get analysis status
- `GET /api/directions/{camera_id}/{view_id}` - Get specific assessment
- `GET /api/directions/pending` - Get pending cameras
- `GET /api/directions` - Get all assessments

### Images

- `GET /api/images/{collection_id}/{filename}` - Serve camera image
- `GET /images/camera/*` - Static camera images
- `GET /images/satellite/*` - Static satellite images

## 📚 API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🔧 Configuration

Edit `.env` file to configure:

```env
# API Keys
CLAUDE_API_KEY=your-key-here
GEMINI_API_KEY=your-key-here
GOOGLE_MAPS_API_KEY=your-key-here

# Server
HOST=0.0.0.0
PORT=8000
RELOAD=true

# Camera Scraper
IMAGES_PER_CAMERA=1
DELAY_BETWEEN_CAPTURES=60

# AI Direction
DEFAULT_AI_PLATFORM=Gemini
DEFAULT_AI_MODEL=Gemini 2.0 Flash
```

## 🎯 Usage Examples

### Start Camera Scraping

```bash
curl -X POST http://localhost:8000/api/scraper/start \
  -H "Content-Type: application/json" \
  -d '{"images_per_camera": 1, "delay_between_captures": 60}'
```

### Get Latest Cameras

```bash
curl http://localhost:8000/api/cameras/latest
```

### Analyze Camera Direction

```bash
curl -X POST http://localhost:8000/api/directions/analyze \
  -H "Content-Type: application/json" \
  -d '{"camera_id": 4, "view_id": 10, "platform": "Gemini", "model": "Gemini 2.0 Flash"}'
```

## 🔗 Integration with GUIs

The PyQt6 GUIs will automatically start this backend when launched. See:
- `gui/camera_scraper_gui.py`
- `gui/direction_analyzer_gui.py`

## 📝 Notes

- The backend uses SQLite databases stored at project root
- Images are stored in `camera_scraper/camera_images/`
- Background tasks run asynchronously
- CORS is enabled for local development


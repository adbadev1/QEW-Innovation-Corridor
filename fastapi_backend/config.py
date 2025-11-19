"""
Configuration settings for FastAPI backend
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).parent.parent

# Load environment variables from .env file in BASE_DIR
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)
CAMERA_SCRAPER_DIR = BASE_DIR / "camera_scraper"
AI_DIRECTION_DIR = BASE_DIR / "ai_camera_direction"

# Database paths
CAMERA_DB_PATH = str(BASE_DIR / "fastapi_backend" / "database" / "camera_data.db")
DIRECTION_DB_PATH = str(BASE_DIR / "fastapi_backend" / "database" / "camera_directions.db")

# Image storage
CAMERA_IMAGES_DIR = str(BASE_DIR / "fastapi_backend" / "database" / "camera_images")
SATELLITE_IMAGES_DIR = str(AI_DIRECTION_DIR / "data" / "images" / "satellite")
CAMERA_TEMP_IMAGES_DIR = str(AI_DIRECTION_DIR / "data" / "images" / "camera")

# Camera data
CAMERA_JSON_PATH = str(CAMERA_SCRAPER_DIR / "qew_cameras_hamilton_mississauga.json")

# API Keys (from environment variables)
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY', '')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')

# Server settings
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 8000))
RELOAD = os.getenv('RELOAD', 'true').lower() == 'true'

# CORS settings
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Camera scraper settings
IMAGES_PER_CAMERA = int(os.getenv('IMAGES_PER_CAMERA', 1))
DELAY_BETWEEN_CAPTURES = int(os.getenv('DELAY_BETWEEN_CAPTURES', 60))
AUTO_SCRAPE_INTERVAL_MINUTES = int(os.getenv('AUTO_SCRAPE_INTERVAL_MINUTES', 10))

# AI Direction settings
DEFAULT_AI_PLATFORM = os.getenv('DEFAULT_AI_PLATFORM', 'Gemini')
DEFAULT_AI_MODEL = os.getenv('DEFAULT_AI_MODEL', 'Gemini 2.0 Flash')


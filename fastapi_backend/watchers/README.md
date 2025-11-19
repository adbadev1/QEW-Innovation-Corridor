# Database Watcher System

Automatic monitoring and export system for QEW camera database changes.

## Overview

The Database Watcher system automatically detects when new camera collections are completed in the SQLite database and exports them to the React webapp's public folder. This eliminates the need for manual export scripts.

## Features

✅ **Automatic Export** - Detects database changes and exports latest collection  
✅ **Relative Paths** - Uses portable relative paths for database portability  
✅ **Cooldown Protection** - Prevents rapid-fire exports (5 second cooldown)  
✅ **Duplicate Prevention** - Only exports new collections, skips already-exported ones  
✅ **Integrated with FastAPI** - Camera scraper auto-exports after completion  
✅ **Standalone Mode** - Can run as independent watcher process  
✅ **Manual Trigger** - API endpoint for manual export on demand  

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Camera Scraper                           │
│  (Downloads images → Saves to database)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              SQLite Database (camera_data.db)               │
│  fastapi_backend/database/camera_data.db                    │
└────────┬────────────────────────────────────┬───────────────┘
         │                                    │
         │ (Auto-export after scraping)       │ (File change detected)
         ▼                                    ▼
┌─────────────────────┐            ┌──────────────────────────┐
│  WebApp Exporter    │            │   Database Watcher       │
│  (Integrated)       │            │   (Standalone)           │
└─────────┬───────────┘            └──────────┬───────────────┘
          │                                   │
          └───────────────┬───────────────────┘
                          ▼
          ┌───────────────────────────────────┐
          │  Export to Public Folder          │
          │  - JSON: public/camera_scraper/   │
          │  - Images: public/camera_images/  │
          └───────────────────────────────────┘
```

## Components

### 1. WebApp Exporter (`webapp_exporter.py`)
- Exports camera data from database to JSON
- Copies images to public folder
- Uses relative paths for portability
- Can be called programmatically or standalone

### 2. Database Watcher (`database_watcher.py`)
- Monitors database file for changes using `watchdog`
- Automatically triggers export when new collection completes
- Prevents duplicate exports with cooldown and collection tracking
- Can run as standalone service

### 3. Standalone Script (`watch_database.py`)
- Command-line interface for the watcher
- Supports multiple modes (watch, export-only, no-initial-export)

## Usage

### Option 1: Automatic (Recommended)

When you run the camera scraper via FastAPI, it automatically exports after completion:

```bash
# Start FastAPI backend
python -m fastapi_backend.main

# Use the API to start scraping
POST http://localhost:8000/api/scraper/start
```

The scraper will automatically export to webapp when complete!

### Option 2: Standalone Watcher

Run the watcher as a separate process to monitor database changes:

```bash
# Watch database and auto-export on changes
python watch_database.py

# Watch without initial export
python watch_database.py --no-export

# Export once and exit (no watching)
python watch_database.py --export-only
```

### Option 3: Manual API Trigger

Trigger export manually via API endpoint:

```bash
# Manual export via API
POST http://localhost:8000/api/export/webapp
```

### Option 4: Direct Python Import

Use the exporter directly in your code:

```python
from fastapi_backend.services import WebAppExporter

exporter = WebAppExporter()
result = exporter.export_latest_collection()

if result:
    print(f"Exported {result['images']} images")
```

## Installation

Install the required dependency:

```bash
pip install watchdog>=3.0.0
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Configuration

The watcher uses paths from `fastapi_backend/config.py`:

- **Database**: `fastapi_backend/database/camera_data.db`
- **Source Images**: `fastapi_backend/database/camera_images/`
- **Public JSON**: `public/camera_scraper/qew_cameras_with_images.json`
- **Public Images**: `public/camera_images/{collection_id}/`

All paths are relative to the project root for portability.

## How It Works

1. **Camera Scraper** downloads images and saves to database
2. **Database Updated** - New collection marked as 'completed'
3. **Watcher Detects** change (if running) OR **Auto-Export** triggers (if integrated)
4. **Exporter Queries** database for latest completed collection
5. **JSON Created** with camera metadata and relative image paths
6. **Images Copied** from backend to public folder
7. **React App** reads updated JSON and displays new images

## Cooldown & Duplicate Prevention

- **5 second cooldown** between exports prevents rapid-fire triggers
- **Collection ID tracking** ensures same collection isn't exported twice
- **Status check** only exports collections with status='completed'

## Logging

All operations are logged with timestamps:

```
================================================================================
QEW Camera Data Export for Web App
================================================================================
Timestamp: 2025-11-19 03:56:00
Database: fastapi_backend/database/camera_data.db

Latest collection: qew_collection_20251119_035600
Total images: 42

Step 1: Exporting camera metadata to JSON...
--------------------------------------------------------------------------------
✓ Exported 14 cameras to public/camera_scraper/qew_cameras_with_images.json

Step 2: Copying images to public folder...
--------------------------------------------------------------------------------
✓ Copied 42 images to public/camera_images/qew_collection_20251119_035600

================================================================================
✓ Web app data export complete!
  Collection: qew_collection_20251119_035600
  Cameras: 14
  Images: 42
================================================================================
```

## Troubleshooting

**Watcher not detecting changes?**
- Ensure watchdog is installed: `pip install watchdog`
- Check database path is correct
- Verify database file has write permissions

**Export not working?**
- Check database has completed collections: `SELECT * FROM collections WHERE status='completed'`
- Verify source images exist in `fastapi_backend/database/camera_images/`
- Ensure public folder exists and is writable

**Duplicate exports?**
- This is prevented automatically with collection ID tracking
- Cooldown period is 5 seconds by default

## API Endpoints

### Export to WebApp
```
POST /api/export/webapp
```

**Response:**
```json
{
  "status": "success",
  "message": "WebApp data exported successfully",
  "collection_id": "qew_collection_20251119_035600",
  "cameras": 14,
  "images": 42,
  "timestamp": "2025-11-19T03:56:00.123456"
}
```

## Benefits

✅ **No Manual Intervention** - Fully automatic workflow  
✅ **Database Portability** - Relative paths work across systems  
✅ **Real-time Updates** - React app always shows latest data  
✅ **Flexible Deployment** - Multiple usage modes  
✅ **Production Ready** - Error handling and logging  


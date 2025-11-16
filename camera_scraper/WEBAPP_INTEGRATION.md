# Web App Integration Guide

## Overview

The camera scraper now uses an SQLite database to store camera metadata and image information. This makes it much easier to reference images in the web application.

## Database Structure

The database (`camera_data.db`) contains the following tables:

### `cameras`
- `camera_id`: Unique camera identifier
- `source`: Camera source (e.g., "COMPASS - Central", "RWIS (MTO)")
- `latitude`, `longitude`: GPS coordinates
- `location`: Human-readable location description
- Other metadata fields

### `camera_views`
- `view_id`: Unique view identifier
- `camera_id`: Foreign key to cameras table
- `url`: Live camera feed URL
- `description`: View description (e.g., "Fort Erie Bound")

### `images`
- `filename`: Short filename (e.g., `c4_v10_r1_20251116_021515.jpg`)
- `camera_id`, `view_id`: Foreign keys
- `location`, `latitude`, `longitude`: Location data
- `timestamp`: Capture timestamp
- `collection_id`: Which collection this image belongs to

### `collections`
- `collection_id`: Unique collection identifier (e.g., `qew_collection_20251116_021515`)
- `output_directory`: Where images are stored
- `total_images`: Number of images in collection
- `status`: 'in_progress' or 'completed'

## Workflow

### 1. Capture Camera Images

Run the camera scraper to capture images:

```bash
cd camera_scraper
python download_camera_images.py
```

This will:
- Create a new collection in the database
- Download images from all cameras
- Store metadata in the SQLite database
- Save images with short filenames to avoid path length issues

### 2. Update Web App Data

After capturing images, update the web app:

```bash
python update_webapp_data.py
```

This script:
1. Queries the database for the latest completed collection
2. Exports camera metadata and image paths to JSON
3. Copies images to the `public/camera_images/` folder
4. Updates `public/camera_scraper/qew_cameras_with_images.json`

### 3. Run the Web App

The React app will automatically load the latest data:

```bash
npm run dev
```

## File Structure

```
qew-innovation-corridor/
├── camera_scraper/
│   ├── camera_data.db              # SQLite database
│   ├── camera_images/              # Source images
│   │   └── qew_collection_*/       # Collection folders
│   ├── download_camera_images.py   # Capture images
│   ├── update_webapp_data.py       # Export to web app
│   └── database.py                 # Database module
│
└── public/
    ├── camera_scraper/
    │   └── qew_cameras_with_images.json  # Camera metadata
    └── camera_images/
        └── qew_collection_*/             # Public images
```

## JSON Data Structure

The exported JSON (`qew_cameras_with_images.json`) has this structure:

```json
[
  {
    "Id": 210,
    "Source": "COMPASS - Central",
    "Latitude": 43.2201,
    "Longitude": -79.65143,
    "Location": "QEW West of Fifty Road",
    "Views": [
      {
        "Id": 570,
        "Url": "https://511on.ca/map/Cctv/570",
        "Description": "",
        "Images": [
          {
            "filename": "c210_v570_r1_20251116_021527.jpg",
            "path": "camera_images/qew_collection_20251116_021515/c210_v570_r1_20251116_021527.jpg",
            "timestamp": "20251116_021527",
            "capture_round": 1
          }
        ]
      }
    ]
  }
]
```

## React App Changes

The `App.jsx` component now:
1. Loads `qew_cameras_with_images.json` instead of separate camera and image files
2. Accesses images directly from the `view.Images` array
3. Constructs image paths using `basePath + image.path`

## Benefits

✅ **Easier image referencing**: Images are included in the camera data structure  
✅ **Short filenames**: Avoids Windows path length issues  
✅ **Collection tracking**: Easy to see which images belong to which capture session  
✅ **Metadata storage**: All camera and image data in one database  
✅ **Automated workflow**: Single script to update web app  

## Querying the Database

You can query the database directly:

```python
from camera_scraper.database import CameraDatabase

db = CameraDatabase('camera_scraper/camera_data.db')

# Get all cameras
cameras = db.get_all_cameras()

# Get images for a specific camera
images = db.get_images_by_camera(camera_id=4)

# Get latest collection
collections = db.get_all_collections()
latest = collections[0]
```

Or use the query script:

```bash
cd camera_scraper
python query_database.py
```


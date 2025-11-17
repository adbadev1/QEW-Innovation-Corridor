# Quick Start Guide - Camera Map Integration

## TL;DR

After capturing camera images, run this single command to update the web app:

```bash
python camera_scraper/update_webapp_data.py
```

Then start the web app:

```bash
npm run dev
```

## Complete Workflow

### 1. Capture Camera Images (First Time or New Collection)

```bash
cd camera_scraper
python download_camera_images.py
```

This will:
- Download images from all QEW cameras
- Store them in `camera_images/qew_collection_TIMESTAMP/`
- Save metadata to `camera_data.db`

### 2. Update Web App Data

```bash
python camera_scraper/update_webapp_data.py
```

This will:
- Export camera data from database to JSON
- Copy images to `public/camera_images/`
- Update `public/camera_scraper/qew_cameras_with_images.json`

### 3. Run the Web App

```bash
npm run dev
```

Open http://localhost:5173 and click on the blue camera markers to see images!

## What Changed?

### Before
- Images had long filenames that caused path issues
- Manual image index creation required
- Hardcoded paths in React app

### After
- Short database-backed filenames (e.g., `c4_v10_r1_20251116_021515.jpg`)
- Automatic JSON export from database
- Single command to update everything

## File Locations

```
qew-innovation-corridor/
├── camera_scraper/
│   ├── camera_data.db                    # SQLite database
│   ├── camera_images/                    # Source images
│   │   └── qew_collection_*/
│   ├── download_camera_images.py         # Capture images
│   └── update_webapp_data.py             # ⭐ Main update script
│
├── public/
│   ├── camera_scraper/
│   │   └── qew_cameras_with_images.json  # Camera metadata
│   └── camera_images/
│       └── qew_collection_*/             # Public images
│
└── src/
    └── App.jsx                            # Updated to use new JSON
```

## Troubleshooting

### No images showing in map?
1. Check if `public/camera_scraper/qew_cameras_with_images.json` exists
2. Check if `public/camera_images/qew_collection_*/` has images
3. Run `python camera_scraper/update_webapp_data.py` again

### Database not found?
Make sure you're in the project root directory when running the update script.

### Old images showing?
The script always uses the latest completed collection. Capture new images and run the update script again.

## Database Queries

To see what's in the database:

```bash
cd camera_scraper
python query_database.py
```

Or use Python:

```python
from camera_scraper.database import CameraDatabase

db = CameraDatabase('camera_scraper/camera_data.db')
collections = db.get_all_collections()
print(f"Latest collection: {collections[0]['collection_id']}")
```

## Need Help?

See `WEBAPP_INTEGRATION.md` for detailed documentation.


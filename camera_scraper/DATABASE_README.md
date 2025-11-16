# Camera Database System

## Overview

The QEW Camera Scraper now uses **SQLite database** to store camera metadata and image records. This solves the file path length issues by using **short filenames** while maintaining all metadata in the database.

## Key Features

### ✅ Short Filenames
- **Old format**: `cam4_view10_QEW_at_Burlington_Skyway_Fort_Erie_Bound_round1_20251115_150317.jpg` (80+ characters)
- **New format**: `c4_v10_r1_20251115_150317.jpg` (29 characters)
- **Benefit**: Prevents Windows path length issues (260 character limit)

### ✅ Complete Metadata Storage
All camera and image information is stored in the SQLite database:
- Camera locations and GPS coordinates
- Camera views and descriptions
- Image capture details
- Collection session information

### ✅ Easy Querying
Use the `query_database.py` tool to:
- View all cameras
- Browse collections
- Find images by camera or collection
- Get database statistics

## Database Schema

### Tables

#### 1. `cameras`
Stores camera metadata:
- `camera_id` (PRIMARY KEY)
- `source`, `source_id`
- `roadway`, `direction`
- `latitude`, `longitude`
- `location`
- `sort_order`
- `created_at`

#### 2. `camera_views`
Stores camera view information:
- `view_id` (PRIMARY KEY)
- `camera_id` (FOREIGN KEY)
- `url`
- `status`
- `description`

#### 3. `images`
Stores image records:
- `id` (PRIMARY KEY, auto-increment)
- `filename` (short filename)
- `camera_id`, `view_id` (FOREIGN KEYS)
- `location`, `latitude`, `longitude`
- `view_description`
- `capture_round`
- `timestamp`
- `url`
- `collection_id`
- `created_at`

#### 4. `collections`
Stores collection session metadata:
- `collection_id` (PRIMARY KEY)
- `start_time`, `end_time`
- `total_images`
- `output_directory`
- `status`

## Usage

### Running the Camera Scraper

The system works exactly as before, but now uses the database automatically:

```bash
# Activate virtual environment
.\venv\Scripts\activate

# Run the GUI
python qew_camera_gui.py

# Or run command-line collection
python download_camera_images.py

# Or run a quick test
python quick_test_db.py
```

### Querying the Database

Use the interactive query tool:

```bash
python query_database.py
```

Menu options:
1. Show all cameras
2. Show all collections
3. Show images for a collection
4. Show images for a camera
5. Show database statistics
6. Exit

### Programmatic Access

```python
from database import CameraDatabase

# Open database
db = CameraDatabase()

# Get camera by ID
camera = db.get_camera_by_id(4)
print(camera['location'])  # "QEW at Burlington Skyway"

# Get all images for a camera
images = db.get_images_by_camera(4)
for img in images:
    print(f"{img['filename']} - {img['timestamp']}")

# Get collection statistics
stats = db.get_collection_stats("qew_collection_20251116_020951")
print(f"Total images: {stats['total_images']}")

# Close database
db.close()
```

## File Structure

```
camera_scraper/
├── database.py                    # Database module (NEW)
├── camera_data.db                 # SQLite database (auto-created)
├── download_camera_images.py      # Updated to use database
├── qew_camera_gui.py             # GUI (works with database)
├── query_database.py             # Database query tool (NEW)
├── test_database.py              # Database test script (NEW)
├── quick_test_db.py              # Quick test script (NEW)
│
├── camera_images/                # Image storage (short filenames)
│   └── qew_collection_YYYYMMDD_HHMMSS/
│       ├── c4_v10_r1_YYYYMMDD_HHMMSS.jpg
│       ├── c4_v11_r1_YYYYMMDD_HHMMSS.jpg
│       ├── ...
│       ├── image_metadata.json   # Backward compatibility
│       └── collection_report.txt
│
└── venv/                         # Virtual environment
```

## Filename Format

Short filenames follow this pattern:
```
c{camera_id}_v{view_id}_r{round}_{timestamp}.jpg
```

Examples:
- `c4_v10_r1_20251116_020951.jpg` - Camera 4, View 10, Round 1
- `c5_v13_r2_20251116_030000.jpg` - Camera 5, View 13, Round 2
- `c210_v570_r1_20251116_040000.jpg` - Camera 210, View 570, Round 1

## Benefits

1. **No Path Length Issues**: Short filenames prevent Windows 260-character path limit errors
2. **Complete Metadata**: All information preserved in database
3. **Easy Querying**: SQL queries for finding specific images
4. **Backward Compatible**: Still generates `image_metadata.json` files
5. **Scalable**: Database can handle thousands of images efficiently
6. **Relational**: Link images to cameras, views, and collections

## Migration Notes

- Existing collections with long filenames will continue to work
- New collections automatically use short filenames and database
- The `image_metadata.json` file is still generated for compatibility
- No changes needed to existing scripts - database integration is automatic

## Testing

Run the test suite:

```bash
# Full database integration test
python test_database.py

# Quick test with 2 cameras
python quick_test_db.py
```

Both tests verify:
- ✅ Database creation
- ✅ Camera metadata loading
- ✅ Short filename generation
- ✅ Image downloading
- ✅ Metadata storage
- ✅ File verification


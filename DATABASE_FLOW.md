# Database Flow: Local → Cloud → Sharing with Corey

Complete data flow architecture for the QEW Innovation Corridor camera system.

---

## 📊 Complete Data Flow Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           511ON MTO COMPASS SYSTEM                          │
│                    46 Cameras | QEW Hamilton → Mississauga                  │
│                   https://511on.ca/map/Cctv/{cameraId}                      │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │ HTTP Requests
                                 ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    🐍 LOCAL: PYTHON CAMERA SCRAPER                          │
│                   /camera_scraper/download_camera_images.py                 │
│─────────────────────────────────────────────────────────────────────────────│
│  1. Fetches camera metadata from qew_cameras_hamilton_mississauga.json      │
│  2. Downloads images from 511ON (1 image per camera per round)              │
│  3. Generates short filenames: c{cameraId}_v{viewId}_r{round}_{timestamp}.jpg │
│  4. Stores locally in: /public/camera_images/                               │
│  5. Records metadata in: camera_data.db (SQLite)                            │
│─────────────────────────────────────────────────────────────────────────────│
│  Database Schema (database.py):                                             │
│    ├── cameras (46 rows)           - Camera GPS, location, direction       │
│    ├── camera_views (50+ rows)     - View URLs, descriptions               │
│    ├── images (50+ rows per run)   - Image records with metadata           │
│    ├── collections (N rows)        - Collection session tracking           │
│    └── camera_details (optional)   - Extended camera orientation data      │
└────────────────────────┬───────────────────────┬────────────────────────────┘
                         │                       │
                         │ Writes                │ Writes
                         ▼                       ▼
┌─────────────────────────────────┐  ┌──────────────────────────────────────┐
│  📁 LOCAL: FILESYSTEM             │  │  💾 LOCAL: SQLITE DATABASE           │
│  /public/camera_images/           │  │  camera_scraper/camera_data.db      │
│─────────────────────────────────│  │──────────────────────────────────────│
│  c210_v570_r1_20251117_174123.jpg │  │  Tables:                             │
│  c211_v571_r1_20251117_174125.jpg │  │    - cameras                         │
│  c212_v572_r1_20251117_174127.jpg │  │    - camera_views                    │
│  ...                              │  │    - images                          │
│  (50 images, ~80KB each)          │  │    - collections                     │
│                                   │  │    - camera_details                  │
│  manifest.json (generated)        │  │                                      │
└─────────────────┬─────────────────┘  └──────────────────────────────────────┘
                  │                              │
                  │                              │ Can export to JSON
                  │                              ▼
                  │                   ┌──────────────────────────────┐
                  │                   │  📄 JSON Exports              │
                  │                   │  - Collection manifests       │
                  │                   │  - Camera metadata            │
                  │                   │  - Image records              │
                  │                   └──────────────────────────────┘
                  │
                  │ Read by React App
                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ⚛️  REACT APP: AUTO-ANALYSIS SYSTEM                      │
│                    src/services/scrapedImageAnalysis.js                     │
│─────────────────────────────────────────────────────────────────────────────│
│  1. App.jsx loads on startup                                                │
│  2. Fetches manifest.json (50 images)                                       │
│  3. For each image:                                                         │
│     - Fetches from /public/camera_images/{filename}                         │
│     - Sends to Gemini Vision API (autoWorkZoneAnalysis.js)                  │
│     - Analyzes for work zones (MTO BOOK 7 compliance)                       │
│  4. Stores results in: localStorage (qew_workzone_camera_history)           │
│  5. Camera pins turn RED if work zones detected                             │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     │ Analyzes
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    🤖 GOOGLE GEMINI 2.0 FLASH VISION API                    │
│                    https://generativelanguage.googleapis.com                │
│─────────────────────────────────────────────────────────────────────────────│
│  Input:  Camera image (JPEG)                                                │
│  Output: Work zone detection results:                                       │
│    - hasWorkZone: boolean                                                   │
│    - riskScore: 0-10                                                        │
│    - workers: count                                                         │
│    - vehicles: count                                                        │
│    - barriers: boolean                                                      │
│    - confidence: 0-1                                                        │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     │ Returns analysis
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    💾 BROWSER: LOCALSTORAGE                                 │
│                    Key: qew_workzone_camera_history                         │
│─────────────────────────────────────────────────────────────────────────────│
│  Array of work zone detections:                                             │
│  [                                                                           │
│    {                                                                         │
│      cameraId: 212,                                                          │
│      viewId: 572,                                                            │
│      location: "QEW near Grays Road",                                       │
│      riskScore: 8,                                                           │
│      workers: 3,                                                             │
│      vehicles: 2,                                                            │
│      detectedAt: "2025-11-20T...",                                          │
│      gcpImageUrl: "https://..."                                             │
│    },                                                                        │
│    ...                                                                       │
│  ]                                                                           │
└────────────────────────────────────┬────────────────────────────────────────┘
                                     │
                                     │ Read by Map
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                    🗺️  LEAFLET MAP: CAMERA MARKERS                          │
│                    src/App.jsx (lines 179-187)                              │
│─────────────────────────────────────────────────────────────────────────────│
│  const hasWorkZone = camera.Views.some(view =>                              │
│    workZoneViewIds.includes(view.Id)  // ← From localStorage               │
│  );                                                                          │
│                                                                              │
│  icon={hasWorkZone ? workZoneCameraIcon : normalCameraIcon}                 │
│       ↓                                   ↓                                  │
│    🔴 RED PIN                          🔵 BLUE PIN                          │
│   (Work zone detected)              (No work zone)                          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ☁️ Cloud Storage Integration (Optional)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    🌐 OPTIONAL: GCP CLOUD STORAGE                           │
│                    Bucket: gs://qew-camera-images-public/                   │
│─────────────────────────────────────────────────────────────────────────────│
│  When CameraCollectionPanel is used in browser:                             │
│                                                                              │
│  1. User clicks "Collect Images" in dashboard                               │
│  2. React app downloads images from 511ON                                   │
│  3. Uploads to GCP Storage via gcpStorage.js                                │
│  4. Structure:                                                               │
│     gs://qew-camera-images-public/                                          │
│       └── collections/                                                       │
│           └── qew_collection_20251120_143000/                               │
│               ├── c210_v570_r1_20251120_143015.jpg                          │
│               ├── c211_v571_r1_20251120_143017.jpg                          │
│               └── ...                                                        │
│                                                                              │
│  Public URLs: https://storage.googleapis.com/qew-camera-images-public/...   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 👥 Sharing with Corey: 5 Methods

### Method 1: **Git Repository (CURRENT)**
```bash
# Corey clones the repo
git clone https://github.com/adbadev1/QEW-Innovation-Corridor.git
cd QEW-Innovation-Corridor

# Access files directly
ls public/camera_images/              # 50 scraped images
ls camera_scraper/*.db                # SQLite database
cat public/camera_images/manifest.json # Image index
cat public/camera_scraper/qew_cameras_with_images.json # Camera metadata (29 updated)
```

**What Corey Gets:**
- ✅ All 50 scraped images (Nov 17, 2025)
- ✅ SQLite database with metadata
- ✅ Camera GPS coordinates (29 cameras updated with real data from Issue #17)
- ✅ Python scripts to run scraper himself
- ✅ Complete codebase for dashboard

**Files to Check:**
- `/public/camera_images/*.jpg` - Scraped images
- `/camera_scraper/camera_data.db` - SQLite database
- `/public/camera_scraper/qew_cameras_with_images.json` - Camera metadata (UPDATED with real GPS)
- `/batch_update_cameras.py` - GPS update script
- `/camera_scraper/download_camera_images.py` - Scraper script

---

### Method 2: **SQLite Database Export**
```bash
# Export database to readable formats

# 1. Export cameras table to CSV
sqlite3 camera_scraper/camera_data.db <<EOF
.mode csv
.headers on
.output cameras_export.csv
SELECT * FROM cameras;
.quit
EOF

# 2. Export images table to CSV
sqlite3 camera_scraper/camera_data.db <<EOF
.mode csv
.headers on
.output images_export.csv
SELECT * FROM images;
.quit
EOF

# 3. Export all data to JSON
python3 <<EOF
import sqlite3
import json

conn = sqlite3.connect('camera_scraper/camera_data.db')
conn.row_factory = sqlite3.Row

# Export all tables
data = {}
for table in ['cameras', 'camera_views', 'images', 'collections']:
    cursor = conn.execute(f'SELECT * FROM {table}')
    data[table] = [dict(row) for row in cursor.fetchall()]

with open('database_export.json', 'w') as f:
    json.dump(data, f, indent=2)

print(f"Exported {sum(len(v) for v in data.values())} total records")
EOF
```

**Send to Corey:**
```bash
# Create archive with all exports
tar -czf qew_data_for_corey.tar.gz \
  public/camera_images/ \
  camera_scraper/camera_data.db \
  cameras_export.csv \
  images_export.csv \
  database_export.json \
  public/camera_scraper/qew_cameras_with_images.json

# Upload to Google Drive / Dropbox / Email
```

---

### Method 3: **GCP Cloud Storage (Public Access)**
```bash
# Upload all images to GCP bucket (if configured)
gsutil -m cp -r public/camera_images/* gs://qew-camera-images-public/scraped_images_nov17/

# Make bucket public
gsutil iam ch allUsers:objectViewer gs://qew-camera-images-public

# Corey can access via URLs:
# https://storage.googleapis.com/qew-camera-images-public/scraped_images_nov17/c210_v570_r1_20251117_174123.jpg
```

**What Corey Gets:**
- ✅ Public URLs for all images
- ✅ No need to clone repo
- ✅ Fast CDN delivery
- ✅ Can view directly in browser

---

### Method 4: **GitHub Releases (Recommended for Large Datasets)**
```bash
# Create a release with data archive
gh release create v1.0-data \
  --title "QEW Camera Data - Nov 17, 2025" \
  --notes "50 camera images + SQLite database + metadata" \
  qew_data_for_corey.tar.gz

# Corey downloads:
# https://github.com/adbadev1/QEW-Innovation-Corridor/releases/latest
```

---

### Method 5: **Live Dashboard (GitHub Pages)**
```bash
# Already deployed at:
# https://adbadev1.github.io/QEW-Innovation-Corridor/

# Corey can:
# - View live map with camera pins
# - See RED pins for detected work zones
# - Click cameras to view images
# - Inspect work zone analysis results
```

**Interactive Features:**
- ✅ Real-time map visualization
- ✅ Camera location markers (Blue/RED)
- ✅ Work zone detection results
- ✅ ML Validation Panel with Gemini analysis

---

## 📋 Complete File Manifest for Corey

### Camera Images (Local Storage)
```
/public/camera_images/
├── c210_v570_r1_20251117_174123.jpg    (29 KB)  Camera #210 - QEW West of Fifty Road
├── c211_v571_r1_20251117_174125.jpg    (56 KB)  Camera #211 - QEW Millen Road
├── c212_v572_r1_20251117_174127.jpg    (57 KB)  Camera #212 - QEW Grays Road ✅ GPS UPDATED
├── c213_v573_r1_20251117_174128.jpg    (58 KB)  Camera #213 - Centennial Parkway ✅ GPS UPDATED
├── c214_v574_r1_20251117_174130.jpg    (50 KB)  Camera #214 - Red Hill Valley ✅ GPS UPDATED
├── ...
├── c1159_v2261_r1_20251117_174325.jpg  (112 KB) Camera #1159 - Winston Churchill ✅ GPS UPDATED
├── manifest.json                        (5 KB)   Index of all images
└── (Total: 50 images, ~4.8 MB)
```

### Database Files
```
camera_scraper/
├── camera_data.db                       (0 KB currently, empty)
├── database.py                          (12 KB)  SQLite schema and API
└── download_camera_images.py            (8 KB)   Image scraper script
```

### Metadata Files
```
public/camera_scraper/
├── qew_cameras_with_images.json         (120 KB) ✅ 29 cameras UPDATED with real GPS
└── camera_image_map.json                (15 KB)  GCP URL mappings
```

### Updated Camera Data (Issue #17)
```
29 cameras updated with REAL GPS coordinates and directions:
- Camera #211: QEW Millen Road (43.239494, -79.728469) → WNW
- Camera #212: QEW Grays Road (43.242601, -79.742223) → West
- Camera #213: Centennial Parkway (43.247601, -79.758361) → West
- Camera #214: Red Hill Valley (43.248234, -79.761738) → WNW
- Camera #215: Nikola Tesla (43.259267, -79.768461) → NNE
- ... (25 more cameras)

See: batch_update_cameras.py for complete update script
See: GitHub Issue #17 for verification details
```

---

## 🔄 Data Synchronization Workflow

### For Corey to Get Latest Data:

```bash
# 1. Clone or pull latest repo
git pull origin main

# 2. Check what's new
git log --oneline --since="3 days ago"

# Commits to look for:
# - de07a61: Auto-analyze scraped camera images
# - 3cc2cb0: Batch update 29 cameras with verified GPS/directions

# 3. Access latest data
ls -lh public/camera_images/            # Check image dates
cat public/camera_images/manifest.json   # View image index
sqlite3 camera_scraper/camera_data.db "SELECT COUNT(*) FROM images;"  # Check DB

# 4. Run scraper himself (if he wants fresh images)
cd camera_scraper
python3 download_camera_images.py
```

---

## 📊 Data Statistics (Current State)

```
Camera Data:
  - Total Cameras: 46 (QEW Hamilton → Mississauga)
  - Cameras with Real GPS: 29 ✅ (Updated from Issue #17)
  - Cameras Pending GPS: 17 (Need verification)
  - Multi-view Cameras: 2 (Camera #4, #5 with 3 views each)

Scraped Images:
  - Total Images: 50 JPEGs
  - File Size Range: 29 KB - 169 KB
  - Average Size: ~96 KB
  - Total Storage: ~4.8 MB
  - Collection Date: Nov 17, 2025 at 5:41 PM
  - Format: c{cameraId}_v{viewId}_r1_20251117_174123.jpg

SQLite Database:
  - Current Size: 0 KB (empty, needs population)
  - Schema Tables: 5 (cameras, camera_views, images, collections, camera_details)
  - Indexes: 5 (optimized for queries)

Work Zone Detection:
  - Analysis Service: ✅ Implemented (scrapedImageAnalysis.js)
  - Auto-analysis: ✅ Triggers on app startup
  - AI Model: Google Gemini 2.0 Flash Vision
  - Storage: Browser localStorage
  - Visual Indicators: RED camera pins on map

GCP Cloud Storage:
  - Bucket: gs://qew-camera-images-public/
  - Status: Configured but images not uploaded yet
  - Public Access: Yes (when images uploaded)
  - CORS: Configured for browser uploads
```

---

## 🚀 Quick Start for Corey

### Option A: View Dashboard Only (Easiest)
```
1. Open browser: https://adbadev1.github.io/QEW-Innovation-Corridor/
2. Explore the live map with camera markers
3. Click cameras to see images and analysis
```

### Option B: Access Raw Data (Moderate)
```bash
1. Clone repo: git clone https://github.com/adbadev1/QEW-Innovation-Corridor.git
2. View images: open public/camera_images/
3. Check manifest: cat public/camera_images/manifest.json
4. View camera metadata: cat public/camera_scraper/qew_cameras_with_images.json
```

### Option C: Run Full System (Advanced)
```bash
1. Clone repo
2. Install dependencies: npm install
3. Run dev server: npm run dev
4. Open: http://localhost:8200
5. Use ML Validation Panel to analyze images
```

### Option D: Run Scraper (Advanced)
```bash
1. cd camera_scraper
2. pip install requests
3. python3 download_camera_images.py
4. Wait ~5 minutes for 50 images to download
5. Check: ls camera_images/
```

---

## 📝 Notes for Corey

1. **GPS Data Updated**: 29 cameras now have VERIFIED GPS coordinates from your field work (Issue #17)
   - See `batch_update_cameras.py` for update script
   - See `public/camera_scraper/qew_cameras_with_images.json` for updated data

2. **Work Zone Analysis**: System now automatically analyzes scraped images using Gemini AI
   - Camera pins turn RED when work zones detected
   - Results stored in browser localStorage
   - See `src/services/scrapedImageAnalysis.js`

3. **Database Note**: SQLite database (`camera_data.db`) is currently empty (0 bytes)
   - Run `download_camera_images.py` to populate it
   - Or use the JSON files instead (easier for Excel/spreadsheet work)

4. **Image Quality**: All images are from 511ON live camera feeds
   - Quality varies by camera (some foggy, some clear)
   - Timestamps in filenames: Nov 17, 2025, 5:41 PM
   - Good for analysis but not high-res

5. **Next Steps**: 17 cameras still need GPS verification
   - See GitHub Issue #17 for remaining cameras
   - Use Google Earth to verify coordinates
   - Submit corrections via issue comments

---

## 🔗 Important Links

- **GitHub Repo**: https://github.com/adbadev1/QEW-Innovation-Corridor
- **Live Dashboard**: https://adbadev1.github.io/QEW-Innovation-Corridor/
- **Issue #17 (GPS Updates)**: https://github.com/adbadev1/QEW-Innovation-Corridor/issues/17
- **GCP Bucket** (when populated): https://storage.googleapis.com/qew-camera-images-public/

---

**Last Updated**: 2025-11-20
**Database Version**: v1.0 (29 cameras updated)
**Image Collection**: Nov 17, 2025
**Total Data Size**: ~5 MB (images + metadata)

🤖 **Generated with [Claude Code](https://claude.com/claude-code)**

# QEW Innovation Corridor - Camera Image Collection

## Project Overview
This project collects traffic camera images from the QEW highway corridor between Hamilton and Mississauga for hazard assessment and proactive safety analysis using AI.

## Data Source
- **Source**: Ontario 511 Traffic Management System (MTO)
- **API**: https://511on.ca/api/v2/get/cameras
- **Coverage**: 46 cameras along QEW between Hamilton and Mississauga
- **Total Views**: 50 camera views (some cameras have multiple angles)

## Camera Coverage

### Geographic Boundaries
- **Western Terminus**: Hamilton area (~43.25°N, -79.87°W)
- **Eastern Terminus**: Mississauga area (~43.59°N, -79.64°W)
- **Highway**: Queen Elizabeth Way (QEW)

### Key Locations Covered
1. **Hamilton Area**
   - Red Hill Valley Parkway
   - Centennial Parkway
   - Nikola Tesla Boulevard

2. **Burlington**
   - Burlington Skyway (multiple cameras)
   - Brant Street
   - Guelph Line
   - Appleby Line
   - Burloak Drive
   - Bronte Road

3. **Oakville**
   - Third Line
   - Fourth Line
   - Dorval Drive
   - Trafalgar Road
   - Ford Drive

4. **Mississauga**
   - Winston Churchill Boulevard
   - Erin Mills Parkway
   - Mississauga Road

## Scripts

### 1. `fetch_qew_cameras.py`
Fetches camera metadata from Ontario 511 API and filters for QEW corridor.

**Features:**
- Retrieves all camera locations with GPS coordinates
- Filters for QEW highway only
- Filters geographic region (Hamilton to Mississauga)
- Saves camera data to JSON file

**Output:**
- `qew_cameras_hamilton_mississauga.json` - Camera metadata with GPS coordinates

**Usage:**
```bash
python fetch_qew_cameras.py
```

### 2. `download_camera_images.py`
Downloads images from all identified cameras for analysis.

**Features:**
- Downloads images from all 46 cameras
- Multiple capture rounds for temporal diversity
- Configurable delay between captures
- Generates metadata for each image (GPS, timestamp, location)
- Creates organized directory structure
- Generates summary report

**Configuration:**
- `IMAGES_PER_CAMERA`: Number of times to capture each camera (default: 3)
- `DELAY_BETWEEN_ROUNDS`: Seconds between capture rounds (default: 300 = 5 minutes)

**Output:**
- `camera_images/qew_collection_[timestamp]/` - Directory with all images
- `image_metadata.json` - Detailed metadata for each image
- `collection_report.txt` - Summary report

**Usage:**
```bash
python download_camera_images.py
```

**Expected Results:**
- 50 views × 3 captures = **150 images** (exceeds 100+ requirement)
- Each image tagged with GPS coordinates
- Temporal diversity (captures at different times)

## Quick Start

### Prerequisites
```bash
pip install requests
```

### Step 1: Fetch Camera Data
```bash
python fetch_qew_cameras.py
```

This will:
- Connect to Ontario 511 API
- Identify 46 cameras along QEW corridor
- Save camera locations and GPS coordinates

### Step 2: Download Images
```bash
python download_camera_images.py
```

This will:
- Download 150+ images from all cameras
- Save images with descriptive filenames
- Generate metadata with GPS coordinates
- Create summary report

**Time Required**: ~10-15 minutes (includes delays for temporal diversity)

## Data Structure

### Camera Metadata Format
```json
{
  "Id": 4,
  "Source": "RWIS (MTO)",
  "Roadway": "QEW",
  "Latitude": 43.30917,
  "Longitude": -79.803,
  "Location": "QEW at Burlington Skyway",
  "Views": [
    {
      "Id": 10,
      "Url": "https://511on.ca/map/Cctv/10",
      "Description": "Fort Erie Bound"
    }
  ]
}
```

### Image Metadata Format
```json
{
  "filename": "cam4_view10_QEW_at_Burlington_Skyway_Fort_Erie_Bound_round1_20250115_143022.jpg",
  "camera_id": 4,
  "view_id": 10,
  "location": "QEW at Burlington Skyway",
  "latitude": 43.30917,
  "longitude": -79.803,
  "view_description": "Fort Erie Bound",
  "capture_round": 1,
  "timestamp": "20250115_143022",
  "url": "https://511on.ca/map/Cctv/10"
}
```

## Use Cases

### Hazard Assessment
- Identify road hazards (debris, accidents, weather conditions)
- Detect traffic congestion patterns
- Monitor road surface conditions

### Safety Analysis
- Analyze traffic flow patterns
- Identify high-risk areas
- Monitor weather impact on traffic
- Assess infrastructure conditions

### AI Analysis
Images include:
- GPS coordinates for spatial analysis
- Timestamps for temporal analysis
- Multiple angles for comprehensive coverage
- Diverse capture times for pattern recognition

## Camera Distribution

| Region | Number of Cameras |
|--------|-------------------|
| Hamilton | 10 |
| Burlington | 15 |
| Oakville | 12 |
| Mississauga | 9 |
| **Total** | **46** |

## Technical Details

### API Information
- **Endpoint**: https://511on.ca/api/v2/get/cameras?format=json
- **Method**: GET
- **Format**: JSON
- **Rate Limiting**: Respectful delays implemented
- **Documentation**: http://511on.ca/help/endpoint/cameras

### Image Format
- **Format**: JPEG
- **Source**: Live traffic cameras
- **Update Frequency**: Real-time (cameras update continuously)
- **Resolution**: Varies by camera

## Future Enhancements

1. **Scheduled Collection**: Set up cron job for regular image collection
2. **AI Integration**: Connect to computer vision models for automated analysis
3. **Database Storage**: Store metadata in database for querying
4. **Web Dashboard**: Visualize camera locations and collected images
5. **Alert System**: Automated hazard detection and notification

## License & Usage

This project uses publicly available data from Ontario 511 (MTO) for safety analysis purposes.

## Contact

For questions about this project, please refer to the QEW Innovation Corridor initiative.


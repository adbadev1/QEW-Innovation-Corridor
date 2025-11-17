# AI Camera Direction Assessment - Setup Guide

## 🎯 Overview

This application uses Claude AI to automatically determine camera directions by analyzing:
1. **Satellite images** (north-oriented aerial view)
2. **Camera images** (ground-level view)
3. **Landmark matching** between both images

## 📁 Project Structure

```
ai_camera_direction/
├── backend/                      # Backend processing modules
│   ├── database.py              # SQLite database for assessments
│   ├── claude_client.py         # Claude API client (TOON format)
│   ├── satellite_fetcher.py     # Downloads satellite images
│   ├── camera_fetcher.py        # Downloads camera images
│   └── processor.py             # Main processing engine
├── frontend/                     # PyQt6 GUI
│   └── main_window.py           # Main application window
├── satellite_images/            # Downloaded satellite images
├── camera_images/               # Downloaded camera images
├── data/                        # Database storage
│   └── camera_directions.db     # Assessment results
├── main.py                      # Application entry point
├── run.bat                      # Quick start script
└── test_setup.py                # Setup verification
```

## ✅ Installation Complete

All dependencies have been installed:
- ✓ anthropic (Claude API)
- ✓ PyQt6 (GUI framework)
- ✓ requests (HTTP library)
- ✓ Pillow (Image processing)

## 🔑 Configuration: .env File

### Step 1: Create .env file

Copy the example file:
```bash
cp .env.example .env
```

Or manually create `.env` in the `ai_camera_direction` folder.

### Step 2: Add Claude API Key (Required)

1. Go to: https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new API key
5. Copy the key (starts with `sk-ant-...`)
6. Edit `.env` and paste your key:

```bash
CLAUDE_API_KEY=sk-ant-your-actual-key-here
```

**Keep this key secure!** The `.env` file is in `.gitignore` and won't be committed.

### Step 3: Add Google Maps API Key (Optional)

For better satellite images (recommended but not required):

1. Go to: https://console.cloud.google.com/
2. Create a project
3. Enable "Maps Static API"
4. Create credentials (API key)
5. Copy the key
6. Edit `.env` and add:

```bash
GOOGLE_MAPS_API_KEY=your-google-maps-key-here
```

Without this, the app will use OpenStreetMap (free but lower quality).

### Your .env file should look like:

```bash
# Claude API Key (Required)
CLAUDE_API_KEY=sk-ant-api03-your-actual-key-here

# Google Maps API Key (Optional)
GOOGLE_MAPS_API_KEY=AIza-your-google-key-here

# Source Database Path
SOURCE_DB_PATH=../camera_scraper/camera_data.db
```

## 🚀 How to Run

**Development Mode** (current):

```bash
..\camera_scraper\venv\Scripts\python.exe main.py
```

The application will automatically load settings from `.env` file.

## 📋 Using the Application

1. **Verify .env file** has your Claude API key
2. **Run the application** (command above)
3. **GUI auto-loads** API keys from .env (green background = loaded)
4. **Click "Start Processing"**

The application will:
- Fetch satellite image for each camera location
- Fetch current camera image
- Send both to Claude AI for analysis
- Display images side-by-side
- Show AI's reasoning in console
- Save direction to database

## 📊 What You'll See

### GUI Layout:
```
┌─────────────────────────────────────────────────────────┐
│  Configuration (API keys, database path)                │
├─────────────────────────────────────────────────────────┤
│  [Start Processing]  [Stop]                             │
├─────────────────────────────────────────────────────────┤
│  Progress Bar                                           │
├──────────────────────┬──────────────────────────────────┤
│  Satellite Image     │  Camera Image                    │
│  (North-oriented)    │  (Ground view)                   │
│                      │                                  │
├──────────────────────┴──────────────────────────────────┤
│  AI Assessment Console                                  │
│  - Direction determined                                 │
│  - Landmarks identified                                 │
│  - Reasoning explanation                                │
│  - Confidence score                                     │
└─────────────────────────────────────────────────────────┘
```

## 🧠 How AI Analysis Works

1. **Satellite Analysis**: AI identifies landmarks in north-oriented satellite view
   - Roads, highways, bridges
   - Buildings, structures
   - Water bodies
   - Distinctive features

2. **Camera Analysis**: AI identifies same landmarks in camera view
   - Matches features from satellite
   - Notes perspective differences

3. **Direction Calculation**: 
   - Matches landmarks between images
   - Uses north orientation from satellite
   - Determines camera heading (0-360°)
   - Assigns compass direction (N, NE, E, SE, S, SW, W, NW)

## 💾 Database Output

Results saved in: `data/camera_directions.db`

### Table: ai_direction_assessments

Key columns:
- `camera_id`, `view_id` - Camera identifiers
- `direction` - Compass direction (N, NE, E, SE, S, SW, W, NW)
- `heading_degrees` - Precise heading (0-360°)
- `confidence_score` - AI confidence (0.0-1.0)
- `landmarks_identified` - Landmarks found
- `reasoning` - AI's explanation
- `satellite_analysis` - What AI saw in satellite image
- `camera_analysis` - What AI saw in camera image
- `landmark_matches` - Which landmarks matched

## 📈 Performance

- **Processing time**: ~10-15 seconds per camera
- **API cost**: ~$0.01-0.02 per camera (Claude API)
- **Total cameras**: 50 views from 46 cameras
- **Estimated total cost**: ~$0.50-1.00
- **Estimated total time**: ~8-12 minutes

## 🔧 TOON Format (Token Optimization)

The system uses TOON (Text-Oriented Object Notation) instead of JSON:

**Traditional JSON** (verbose):
```json
{
  "direction": "E",
  "heading_degrees": 90,
  "confidence": 0.95
}
```

**TOON Format** (efficient):
```
direction: E
heading_degrees: 90
confidence: 0.95
```

**Token savings**: ~40% reduction in API costs!

## ⚠️ Troubleshooting

### "No satellite images"
- Check internet connection
- Try adding Google Maps API key for better results

### "Camera images fail"
- MTO 511 API may be temporarily down
- Try again later

### "API Error"
- Verify Claude API key is correct
- Check API key has available credits
- Ensure API key starts with `sk-ant-`

### "Database error"
- Ensure source database exists: `../camera_scraper/camera_data.db`
- Run camera_scraper first if needed

## 📝 Example Output

```
Camera 4, View 10: QEW at Burlington Skyway
  Direction: W
  Heading: 270.0°
  Confidence: 0.92
  Landmarks: highway, bridge structure, water, road markings
  Reasoning: Camera faces west based on highway alignment and bridge 
             orientation. Satellite shows north-oriented view with 
             bridge running east-west. Camera view shows westbound 
             perspective matching satellite landmarks.
```

## 🎉 Ready to Use!

Everything is set up and ready. Just need your Claude API key to start!

Run: `run.bat` or `..\camera_scraper\venv\Scripts\python.exe main.py`


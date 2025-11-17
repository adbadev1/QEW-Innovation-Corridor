# AI Camera Direction Assessment

Automated camera direction detection using Claude AI with satellite imagery analysis.

## Features

- **AI-Powered Analysis**: Uses Claude 3.5 Sonnet to analyze camera directions
- **Satellite Image Comparison**: Compares north-oriented satellite images with camera views
- **Landmark Matching**: Identifies and matches landmarks between satellite and camera images
- **TOON Format**: Optimized token usage with TOON (Text-Oriented Object Notation)
- **PyQt6 GUI**: User-friendly interface with real-time progress
- **Database Storage**: Stores all assessments in SQLite database

## Project Structure

```
ai_camera_direction/
├── backend/
│   ├── __init__.py
│   ├── database.py           # SQLite database management
│   ├── claude_client.py      # Claude API client with TOON format
│   ├── satellite_fetcher.py  # Satellite image downloader
│   ├── camera_fetcher.py     # Camera image downloader
│   └── processor.py          # Main processing engine
├── frontend/
│   ├── __init__.py
│   └── main_window.py        # PyQt6 GUI
├── satellite_images/         # Downloaded satellite images
├── camera_images/            # Downloaded camera images
├── data/
│   └── camera_directions.db  # Assessment database
├── main.py                   # Application entry point
├── requirements.txt
└── README.md
```

## Installation

1. Create virtual environment:
```bash
cd C:\PycharmProjects\qew-innovation-corridor\ai_camera_direction
python -m venv venv
```

2. Activate virtual environment:
```bash
.\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Environment Variables (.env file)

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` and add your API keys:
```bash
# Claude API Key (Required)
CLAUDE_API_KEY=sk-ant-your-key-here

# Google Maps API Key (Optional)
GOOGLE_MAPS_API_KEY=your-google-maps-key

# Source Database Path
SOURCE_DB_PATH=../camera_scraper/camera_data.db
```

**Get API Keys:**
- **Claude API Key**: Required - Get from https://console.anthropic.com/
- **Google Maps API Key**: Optional - Get from https://console.cloud.google.com/

## Usage

1. Configure `.env` file with your Claude API key

2. Run the application:
```bash
..\camera_scraper\venv\Scripts\python.exe main.py
```

3. The GUI will auto-load settings from `.env`

4. Click "Start Processing"

## How It Works

1. **Fetch Satellite Image**: Downloads north-oriented satellite view of camera location
2. **Fetch Camera Image**: Downloads current camera view from MTO 511
3. **AI Analysis**: Claude analyzes both images to:
   - Identify landmarks in satellite image
   - Identify landmarks in camera image
   - Match landmarks between images
   - Determine camera direction based on north orientation
4. **Save Results**: Stores direction and analysis in database

## Database Schema

### ai_direction_assessments Table

- `camera_id`, `view_id`: Camera identifiers
- `direction`: Compass direction (N, NE, E, SE, S, SW, W, NW)
- `heading_degrees`: Precise heading (0-360°)
- `confidence_score`: AI confidence (0.0-1.0)
- `landmarks_identified`: Landmarks found
- `reasoning`: AI's reasoning
- `satellite_analysis`: Satellite image analysis
- `camera_analysis`: Camera image analysis
- `landmark_matches`: Matched landmarks

## TOON Format

The system uses TOON (Text-Oriented Object Notation) for efficient token usage:

```
direction: E
heading_degrees: 90
confidence: 0.95
landmarks: highway, bridge, building
reasoning: Camera faces east based on highway alignment
```

This format reduces token usage by ~40% compared to JSON.

## Output

- **Console Log**: Real-time AI assessments and reasoning
- **Image Display**: Side-by-side satellite and camera images
- **Database**: All assessments stored for later analysis
- **Progress Bar**: Visual progress indicator

## Notes

- Satellite images use OpenStreetMap by default (free)
- Google Maps API provides better satellite imagery (requires API key)
- Processing time: ~10-15 seconds per camera
- Claude API costs: ~$0.01-0.02 per camera assessment

## Troubleshooting

**No satellite images**: Check internet connection or provide Google Maps API key
**Camera images fail**: MTO 511 API may be temporarily unavailable
**API errors**: Verify Claude API key is valid and has credits

## License

MIT License


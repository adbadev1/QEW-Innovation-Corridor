# QEW Camera Scraper GUI

A PyQt6-based GUI application for automated traffic camera image collection from the QEW highway corridor between Hamilton and Mississauga.

## 🚀 Quick Start

```bash
# From the project root directory
cd camera_scraper

# Activate virtual environment (from root)
..\venv\Scripts\activate

# Launch GUI
python qew_camera_gui.py
```

## 📋 Features

- 🕐 **Real-time Clock** - Multiple timezone support (EST default)
- ⚙️ **Automated Collection** - Schedule image collection at custom intervals
- 📷 **46 Cameras** - Complete QEW corridor coverage with GPS coordinates
- 🎨 **Dark Theme** - Professional dark blue to black gradient interface
- 💾 **Persistent Settings** - Automatically saves your preferences
- 📊 **Status Monitoring** - Real-time collection progress and logs

## 📁 Project Structure

```
camera_scraper/
├── qew_camera_gui.py              # Main GUI application
├── fetch_qew_cameras.py           # Camera metadata fetcher
├── download_camera_images.py      # Image downloader module
├── visualize_cameras.py           # Camera visualization tool
├── quick_test.py                  # Test script
├── requirements.txt               # Python dependencies
├── qew_cameras_hamilton_mississauga.json  # Camera data (46 cameras)
├── camera_locations.csv           # GPS coordinates (CSV format)
├── camera_locations.geojson       # GPS coordinates (GeoJSON format)
├── camera_locations_google_maps.txt  # Google Maps format
├── docs/                          # Documentation
│   ├── README.md                  # Detailed project documentation
│   ├── GUI_README.md              # GUI user guide
│   ├── SETUP_GUIDE.md             # Setup instructions
│   ├── IMPLEMENTATION_PLAN.md     # Technical implementation details
│   └── EXECUTIVE_SUMMARY.md       # Project overview
└── test_images/                   # Test downloads
```

## 🔧 Requirements

- Python 3.8+
- PyQt6
- requests
- pytz

Install dependencies:
```bash
pip install -r requirements.txt
```

## 📖 Documentation

Comprehensive documentation is available in the `docs/` folder:

- **[docs/README.md](docs/README.md)** - Complete project documentation
- **[docs/GUI_README.md](docs/GUI_README.md)** - GUI features and usage
- **[docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)** - Setup instructions
- **[docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md)** - Technical details
- **[docs/EXECUTIVE_SUMMARY.md](docs/EXECUTIVE_SUMMARY.md)** - Project overview

## 🎯 What It Does

1. **Connects** to Ontario 511 API to access MTO traffic cameras
2. **Collects** images from 46 cameras along the QEW corridor
3. **Saves** images with GPS coordinates and metadata
4. **Schedules** automated collection at your chosen intervals
5. **Monitors** collection progress with real-time status updates

## 📊 Data Output

Each collection creates:
- **150+ images** (50 camera views × 3 captures)
- **GPS metadata** for every image
- **Summary report** with collection statistics
- **Organized folders** with timestamps

Output location: `camera_images/qew_collection_[timestamp]/`

## 🛠️ Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Fetch camera data** (first time only):
   ```bash
   python fetch_qew_cameras.py
   ```

3. **Launch GUI**:
   ```bash
   python qew_camera_gui.py
   ```

## 💡 Usage Tips

- **For continuous monitoring**: Set interval to 1 hour and click START COLLECTION
- **For testing**: Set interval to 1 minute with 1 image per camera
- **For maximum data**: Set 30-minute intervals with 3 images per camera

## 🌐 Data Source

- **API**: Ontario 511 Traffic Management System
- **Provider**: Ministry of Transportation Ontario (MTO)
- **Coverage**: QEW corridor from Hamilton to Mississauga
- **Cameras**: 46 cameras with 50 total views

## 📝 License

This project uses publicly available data from Ontario 511 (MTO) for traffic safety analysis purposes.

---

**Status**: ✅ Fully operational and ready to use  
**Version**: 1.0  
**Last Updated**: November 2025


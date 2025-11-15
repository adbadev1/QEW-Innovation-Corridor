# QEW Camera Collection GUI

## Overview
PyQt6-based graphical interface for automated camera image collection from the QEW corridor.

## Features

### 🕐 Real-Time Clock
- Large, easy-to-read clock display
- Timezone selection (EST default)
- Supports multiple timezones:
  - US/Eastern (EST/EDT)
  - US/Central
  - US/Mountain
  - US/Pacific
  - America/Toronto
  - America/Vancouver
  - UTC
  - Europe/London

### ⚙️ Collection Settings
- **Interval Settings**: Set hours and minutes between collections
- **Images per Camera**: Configure how many images to capture per camera (1-10)
- **Persistent Settings**: All settings saved to `gui_settings.json`

### 🎮 Control Panel
- **START COLLECTION**: Begin automated collection at set intervals
- **COLLECT NOW**: Run immediate manual collection
- **Real-time Status Log**: Monitor collection progress

### 🎨 Dark Theme
- Beautiful dark blue to black gradient background
- High contrast for easy reading
- Professional appearance

## Installation

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- `requests` - For API calls and image downloads
- `PyQt6` - GUI framework
- `pytz` - Timezone support

### Step 2: Ensure Camera Data Exists
Make sure you've run the camera fetch script first:
```bash
python fetch_qew_cameras.py
```

This creates `qew_cameras_hamilton_mississauga.json` with camera metadata.

## Usage

### Windows
Double-click `run_gui.bat` or run:
```bash
python qew_camera_gui.py
```

### Linux/Mac
```bash
python3 qew_camera_gui.py
```

## GUI Layout

```
┌─────────────────────────────────────────────────────┐
│     QEW Camera Collection System                    │
├─────────────────────────────────────────────────────┤
│  Current Time                                        │
│  ┌───────────────────────────────────────────────┐  │
│  │         12:34:56 PM                           │  │
│  │    Wednesday, November 15, 2025               │  │
│  │  Timezone: [US/Eastern ▼]                     │  │
│  └───────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│  Collection Settings                                 │
│  ┌───────────────────────────────────────────────┐  │
│  │ Interval: Hours: [1] Minutes: [0]             │  │
│  │ Images per Camera: [1]                        │  │
│  └───────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│  Control                                             │
│  ┌───────────────────────────────────────────────┐  │
│  │  [START COLLECTION]  [COLLECT NOW]            │  │
│  └───────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────┤
│  Status Log                                          │
│  ┌───────────────────────────────────────────────┐  │
│  │ [2025-11-15 12:34:56] Loaded 46 cameras      │  │
│  │ [2025-11-15 12:35:00] Starting collection... │  │
│  │ [2025-11-15 12:36:30] Collection complete!   │  │
│  └───────────────────────────────────────────────┘  │
│  Cameras: 46  Next Collection: 01:35:00 PM          │
└─────────────────────────────────────────────────────┘
```

## How It Works

### Automatic Collection
1. Set your desired interval (hours and minutes)
2. Click **START COLLECTION**
3. The system will:
   - Run an immediate collection
   - Schedule future collections at the set interval
   - Display next collection time
   - Log all activities

### Manual Collection
- Click **COLLECT NOW** at any time
- Runs independently of automatic schedule
- Useful for testing or immediate needs

### Settings Persistence
All settings are automatically saved to `gui_settings.json`:
```json
{
  "timezone": "US/Eastern",
  "interval_hours": 1,
  "interval_minutes": 0,
  "images_per_camera": 1
}
```

Settings are loaded automatically when you restart the application.

## Output

### Image Storage
Images are saved to:
```
camera_images/qew_collection_[timestamp]/
├── cam4_view10_QEW_at_Burlington_Skyway_Fort_Erie_Bound_round1_20251115_123456.jpg
├── cam5_view13_QEW_near_Mississauga_Road_Toronto_Bound_round1_20251115_123457.jpg
├── ...
├── image_metadata.json
└── collection_report.txt
```

### Metadata
Each collection includes:
- Individual image files with descriptive names
- `image_metadata.json` - Complete metadata for all images
- `collection_report.txt` - Summary report

## Configuration

### Interval Settings
- **Hours**: 0-23
- **Minutes**: 0-59
- **Minimum**: At least 1 minute total
- **Recommended**: 1 hour for regular monitoring

### Images per Camera
- **Range**: 1-10
- **Default**: 1
- **Note**: Higher values increase collection time

### Timezone
- **Default**: US/Eastern (EST/EDT)
- **Auto-adjusts**: For daylight saving time
- **Display**: Shows current time in selected timezone

## Tips

### For Continuous Monitoring
1. Set interval to 1 hour (or desired frequency)
2. Click START COLLECTION
3. Minimize window - it will continue running
4. Check status log periodically

### For Testing
1. Set interval to 1 minute
2. Set images per camera to 1
3. Click START COLLECTION
4. Verify collections are working

### For Maximum Data Collection
1. Set interval to 30 minutes
2. Set images per camera to 3
3. Run during peak traffic hours

## Troubleshooting

### "No camera data loaded" Error
**Solution**: Run `python fetch_qew_cameras.py` first to create camera metadata file.

### GUI Doesn't Start
**Solution**: Install PyQt6:
```bash
pip install PyQt6
```

### Clock Shows Wrong Time
**Solution**: Select correct timezone from dropdown menu.

### Collection Fails
**Solution**: 
1. Check internet connection
2. Verify `qew_cameras_hamilton_mississauga.json` exists
3. Check status log for specific error messages

## Advanced Features

### Background Operation
- GUI can be minimized while running
- Collections continue automatically
- Status log tracks all activities

### Thread Safety
- Collections run in separate thread
- GUI remains responsive during collection
- Multiple collections won't overlap

### Error Handling
- Automatic retry logic
- Detailed error logging
- Graceful failure handling

## System Requirements

- **Python**: 3.8 or higher
- **OS**: Windows, Linux, or macOS
- **RAM**: 512 MB minimum
- **Disk Space**: 100 MB for application + storage for images
- **Internet**: Required for camera image downloads

## Performance

### Collection Time
- **46 cameras**: ~30-60 seconds per collection
- **With 3 images per camera**: ~2-3 minutes
- **Network dependent**: Varies with connection speed

### Resource Usage
- **CPU**: Low (< 5% during collection)
- **RAM**: ~100-200 MB
- **Network**: ~3-5 MB per collection

## Future Enhancements

Potential features for future versions:
- [ ] Email notifications on completion
- [ ] Image preview in GUI
- [ ] Collection statistics and charts
- [ ] Export logs to file
- [ ] Custom camera selection
- [ ] Multiple collection profiles

## Support

For issues or questions:
1. Check the status log for error messages
2. Review `gui_settings.json` for configuration
3. Verify camera metadata file exists
4. Check internet connectivity

## License

Part of the QEW Innovation Corridor project for traffic safety analysis.


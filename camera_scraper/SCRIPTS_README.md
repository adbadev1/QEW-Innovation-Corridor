# Camera Scraper Scripts - ADBA Labs Framework

This directory contains automated startup, stop, and cleanup scripts for the QEW Camera Collection system, following the ADBA Labs SaaS framework patterns.

## Available Scripts

### 🚀 `start.sh` / `start.bat`
**Automated startup script** - Sets up and launches the Camera Collection GUI

**What it does:**
1. Checks Python installation
2. Creates virtual environment (if needed)
3. Activates virtual environment
4. Installs/updates dependencies from `requirements.txt`
5. Runs pre-flight checks
6. Launches the QEW Camera GUI

**Usage:**

**macOS/Linux:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

**First-time setup:**
The script will automatically:
- Create a new Python virtual environment in `./venv`
- Install all required packages (PyQt6, requests, pytz)
- Verify all dependencies are present

**Subsequent runs:**
- Reuses existing virtual environment
- Only updates changed dependencies
- Faster startup time

---

### 🛑 `stop.sh` / `stop.bat`
**Graceful shutdown script** - Stops running Camera GUI processes

**What it does:**
1. Searches for running `qew_camera_gui.py` processes
2. Displays found processes
3. Asks for confirmation
4. Gracefully terminates processes (SIGTERM)
5. Force kills if necessary (SIGKILL after timeout)
6. Deactivates virtual environment

**Usage:**

**macOS/Linux:**
```bash
./stop.sh
```

**Windows:**
```cmd
stop.bat
```

**Interactive mode:**
The script will ask for confirmation before stopping processes, showing you:
- Process IDs
- Command lines
- Number of processes found

---

### 🧹 `cleanup-repo.sh` / `cleanup-repo.bat`
**Repository cleanup script** - Removes development artifacts and temporary files

**What it does:**
- Analyzes repository for cleanable items
- Provides multiple cleanup levels
- Interactive confirmation for destructive operations
- Detailed size/count reporting

**Usage:**

**macOS/Linux:**
```bash
./cleanup-repo.sh
```

**Windows:**
```cmd
cleanup-repo.bat
```

**Cleanup Levels:**

#### 1. Quick Clean (SAFE)
Removes:
- `__pycache__/` directories
- `*.pyc` files

**Use when:** Regular development cleanup

#### 2. Standard Clean (SAFE)
Removes:
- Python cache (as above)
- `venv/` virtual environment

**Use when:** Resetting dependencies or saving disk space

#### 3. Deep Clean (CAUTION)
Removes:
- Python cache
- Virtual environment
- `camera_data.db` (database)
- `gui_settings.json` (user preferences)

**Use when:** Fresh start needed, but keeping collected images

**⚠️ Warning:** This deletes your database and settings!

#### 4. Nuclear Clean (DANGER)
Removes:
- Everything from Deep Clean
- `camera_images/` (all collected camera images)
- `test_images/` (test data)

**Use when:** Complete repository reset needed

**⚠️ DANGER:** This deletes ALL collected data!
Requires typing "DELETE EVERYTHING" to confirm.

#### 5. Custom Cleanup
Interactive mode - choose exactly what to clean

#### 6. Cancel
Exit without making changes

---

## Workflow Examples

### First-Time Setup
```bash
# macOS/Linux
./start.sh

# Windows
start.bat
```

The startup script handles everything automatically!

### Daily Development
```bash
# Start the GUI
./start.sh

# ... work with the application ...

# Stop when done
./stop.sh

# Weekly cleanup
./cleanup-repo.sh
# Choose option 1 (Quick Clean)
```

### Resetting Environment
```bash
# Stop any running processes
./stop.sh

# Clean environment
./cleanup-repo.sh
# Choose option 2 (Standard Clean)

# Fresh start
./start.sh
```

### Complete Reset (Nuclear Option)
```bash
# Stop everything
./stop.sh

# DANGER: Delete everything
./cleanup-repo.sh
# Choose option 4 (Nuclear Clean)
# Type "DELETE EVERYTHING"

# Start fresh
./start.sh
```

---

## Directory Structure

```
camera_scraper/
├── start.sh                    # Unix/Mac startup script
├── start.bat                   # Windows startup script
├── stop.sh                     # Unix/Mac stop script
├── stop.bat                    # Windows stop script
├── cleanup-repo.sh             # Unix/Mac cleanup script
├── cleanup-repo.bat            # Windows cleanup script
├── SCRIPTS_README.md           # This file
├── qew_camera_gui.py           # Main GUI application
├── requirements.txt            # Python dependencies
├── venv/                       # Virtual environment (auto-created)
├── camera_data.db              # SQLite database (created on first run)
├── gui_settings.json           # User preferences (created by GUI)
├── camera_images/              # Collected images
└── __pycache__/                # Python cache (auto-generated)
```

---

## Dependencies

**Required Software:**
- Python 3.8 or higher
- pip (Python package manager)

**Python Packages** (installed automatically by start script):
- `requests>=2.31.0` - HTTP library for downloading camera images
- `PyQt6>=6.6.0` - GUI framework
- `pytz>=2023.3` - Timezone handling

---

## Troubleshooting

### Scripts won't run on macOS/Linux
**Problem:** Permission denied
**Solution:**
```bash
chmod +x start.sh stop.sh cleanup-repo.sh
```

### Python not found
**Problem:** `python3: command not found`
**Solution:** Install Python from https://www.python.org/

### Virtual environment activation fails
**Problem:** `venv/bin/activate: No such file or directory`
**Solution:** Delete `venv` folder and run start script again

### GUI won't start
**Problem:** Dependencies missing or corrupted
**Solution:**
```bash
./cleanup-repo.sh  # Choose option 2
./start.sh         # Fresh install
```

### Can't stop processes
**Problem:** Processes still running after stop script
**Solution:**
```bash
# macOS/Linux
pkill -9 -f qew_camera_gui.py

# Windows
taskkill /F /IM python.exe
```

---

## ADBA Labs Framework Integration

These scripts follow the ADBA Labs SaaS framework principles:

✅ **Automation First** - One-command setup and operation
✅ **Safety by Default** - Confirmation prompts for destructive operations
✅ **Cross-Platform** - Works on Windows, macOS, and Linux
✅ **Clear Communication** - Colored output and progress indicators
✅ **Error Handling** - Graceful failures with helpful messages
✅ **Documentation** - Comprehensive inline and external docs

---

## Contributing

When modifying these scripts:

1. **Test on both platforms** - Changes should work on Unix and Windows
2. **Maintain safety** - Add confirmations for destructive operations
3. **Update documentation** - Keep this README in sync with changes
4. **Follow framework** - Adhere to ADBA Labs coding standards
5. **Version control** - Commit scripts and docs together

---

## Support

For issues or questions:
- Check the troubleshooting section above
- Review the main project README
- Check ADBA Labs framework documentation

---

**Part of the QEW Innovation Corridor Project**
**ADBA Labs SaaS Framework**
**2024**

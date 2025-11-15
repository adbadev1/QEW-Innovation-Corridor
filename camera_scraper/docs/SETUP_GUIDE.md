# QEW Camera Collection - Setup Guide

## Virtual Environment Setup (COMPLETED ✅)

### What Was Done

1. ✅ **Created Virtual Environment**
   - Location: `venv/` directory
   - Python Version: 3.12.3
   - Isolated from system Python

2. ✅ **Upgraded pip**
   - Version: 25.3 (latest)

3. ✅ **Installed All Dependencies**
   - `requests` 2.32.5 - HTTP library for API calls
   - `PyQt6` 6.10.0 - GUI framework (latest version)
   - `PyQt6-Qt6` 6.10.0 - Qt bindings
   - `PyQt6-sip` 13.10.2 - SIP bindings
   - `pytz` 2025.2 - Timezone support (latest)
   - `certifi` 2025.11.12 - SSL certificates
   - `charset-normalizer` 3.4.4 - Character encoding
   - `idna` 3.11 - Domain name handling
   - `urllib3` 2.5.0 - HTTP client

### Verification

All packages installed successfully in the virtual environment:
```
Package            Version
------------------ ----------
certifi            2025.11.12
charset-normalizer 3.4.4
idna               3.11
pip                25.3
PyQt6              6.10.0
PyQt6-Qt6          6.10.0
PyQt6_sip          13.10.2
pytz               2025.2
requests           2.32.5
urllib3            2.5.0
```

---

## How to Use the Virtual Environment

### Option 1: Use the Automated Script (Recommended)

**Windows:**
```bash
run_gui.bat
```

This script will:
- Check if virtual environment exists
- Create it if needed
- Install dependencies if needed
- Activate the environment
- Launch the GUI

### Option 2: Manual Activation

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```cmd
.\venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

After activation, you'll see `(venv)` in your prompt:
```
(venv) PS C:\PycharmProjects\qew-innovation-corridor>
```

### Option 3: Quick Activation Script

**Windows:**
```bash
activate_venv.bat
```

This will activate the environment and show you:
- Python version
- Installed packages
- Instructions

---

## Running the Application

### With Virtual Environment Activated

```bash
python qew_camera_gui.py
```

### Without Activating (Direct Path)

**Windows:**
```bash
.\venv\Scripts\python.exe qew_camera_gui.py
```

**Linux/Mac:**
```bash
./venv/bin/python qew_camera_gui.py
```

---

## First Time Setup

### Step 1: Fetch Camera Data (Required)

Before running the GUI, you need camera metadata:

```bash
# Activate virtual environment
.\venv\Scripts\activate.bat

# Fetch camera data
python fetch_qew_cameras.py
```

This creates `qew_cameras_hamilton_mississauga.json` with 46 cameras.

### Step 2: Launch GUI

```bash
python qew_camera_gui.py
```

Or simply double-click `run_gui.bat`

---

## Project Structure

```
qew-innovation-corridor/
├── venv/                          # Virtual environment (isolated Python)
│   ├── Scripts/                   # Executables (Windows)
│   │   ├── python.exe            # Python interpreter
│   │   ├── pip.exe               # Package manager
│   │   └── activate.bat          # Activation script
│   └── Lib/                      # Installed packages
│
├── qew_camera_gui.py             # Main GUI application
├── fetch_qew_cameras.py          # Camera data fetcher
├── download_camera_images.py     # Image downloader
├── visualize_cameras.py          # Camera visualization
├── quick_test.py                 # Test script
│
├── requirements.txt              # Dependencies list
├── run_gui.bat                   # Automated launcher
├── activate_venv.bat             # Quick activation
│
├── gui_settings.json             # GUI settings (auto-created)
├── qew_cameras_hamilton_mississauga.json  # Camera data
│
├── camera_images/                # Downloaded images
├── test_images/                  # Test downloads
│
├── README.md                     # Project documentation
├── GUI_README.md                 # GUI documentation
├── SETUP_GUIDE.md               # This file
└── IMPLEMENTATION_PLAN.md       # Technical plan
```

---

## Troubleshooting

### Virtual Environment Not Found

**Problem:** `venv` directory doesn't exist

**Solution:**
```bash
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Activation Script Fails (PowerShell)

**Problem:** "Execution policy" error

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

### PyQt6 Import Error

**Problem:** `ModuleNotFoundError: No module named 'PyQt6'`

**Solution:**
```bash
.\venv\Scripts\python.exe -m pip install PyQt6
```

### Camera Data Not Found

**Problem:** "No camera data loaded" in GUI

**Solution:**
```bash
python fetch_qew_cameras.py
```

### Wrong Python Version

**Problem:** Using system Python instead of venv

**Solution:** Always activate the virtual environment first:
```bash
.\venv\Scripts\activate.bat
python --version  # Should show Python 3.12.3
```

---

## Updating Dependencies

### Update All Packages

```bash
# Activate virtual environment
.\venv\Scripts\activate.bat

# Update pip
python -m pip install --upgrade pip

# Update all packages
python -m pip install --upgrade -r requirements.txt
```

### Update Specific Package

```bash
python -m pip install --upgrade PyQt6
```

### Check for Outdated Packages

```bash
python -m pip list --outdated
```

---

## Deactivating Virtual Environment

When you're done working:

```bash
deactivate
```

Your prompt will return to normal (no `(venv)` prefix).

---

## Benefits of Virtual Environment

✅ **Isolation**: Project dependencies don't affect system Python  
✅ **Reproducibility**: Same versions across different machines  
✅ **Clean**: Easy to delete and recreate  
✅ **Version Control**: `requirements.txt` tracks exact versions  
✅ **No Conflicts**: Different projects can use different package versions  

---

## Python Version Information

**Current Version:** Python 3.12.3  
**Latest Available:** Python 3.14.0 (as of November 2025)  
**Compatibility:** All packages work with Python 3.12.3  

**Note:** Python 3.12.3 is stable and fully compatible with all project dependencies. Upgrading to 3.14.0 is optional.

---

## Quick Reference Commands

### Activate Environment
```bash
.\venv\Scripts\activate.bat          # Windows CMD
.\venv\Scripts\Activate.ps1          # Windows PowerShell
source venv/bin/activate             # Linux/Mac
```

### Run GUI
```bash
python qew_camera_gui.py             # With venv activated
.\venv\Scripts\python.exe qew_camera_gui.py  # Without activation
```

### Install Packages
```bash
pip install package_name             # Single package
pip install -r requirements.txt      # All packages
```

### Check Installation
```bash
python --version                     # Python version
pip --version                        # pip version
pip list                            # Installed packages
```

### Deactivate
```bash
deactivate                          # Exit virtual environment
```

---

## Next Steps

1. ✅ Virtual environment created and activated
2. ✅ All dependencies installed
3. ⏭️ Run `python fetch_qew_cameras.py` to get camera data
4. ⏭️ Run `python qew_camera_gui.py` to launch GUI
5. ⏭️ Configure settings and start collection

---

## Support

If you encounter issues:

1. **Check virtual environment is activated**: Look for `(venv)` in prompt
2. **Verify Python version**: `python --version` should show 3.12.3
3. **Check installed packages**: `pip list` should show all dependencies
4. **Reinstall if needed**: Delete `venv/` folder and run `run_gui.bat`

---

## Summary

✅ **Virtual environment created**: `venv/`  
✅ **Python 3.12.3 installed**: Latest stable version  
✅ **All dependencies installed**: PyQt6 6.10.0, pytz 2025.2, requests 2.32.5  
✅ **Ready to use**: Run `run_gui.bat` or activate manually  

**You're all set! The project is ready to run.** 🚀


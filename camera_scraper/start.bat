@echo off
REM ############################################################################
REM QEW Camera Scraper - Startup Script (Windows)
REM Part of ADBA Labs QEW Innovation Corridor Project
REM
REM This script sets up and starts the QEW Camera Collection GUI
REM ############################################################################

setlocal enabledelayedexpansion

REM Change to script directory
cd /d "%~dp0"

echo ================================================================
echo   QEW Innovation Corridor - Camera Collection System
echo   ADBA Labs Framework
echo ================================================================
echo.

REM Check if Python is installed
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed.
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo [OK] Found: %PYTHON_VERSION%
echo.

REM Check if virtual environment exists
echo [2/5] Setting up virtual environment...
if not exist "venv\" (
    echo Creating new virtual environment...
    python -m venv venv
    echo [OK] Virtual environment created
) else (
    echo [OK] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
echo [OK] Virtual environment activated
echo.

REM Install/Update dependencies
echo [4/5] Installing dependencies...
python -m pip install --upgrade pip -q
python -m pip install -r requirements.txt -q
echo [OK] Dependencies installed
echo.

REM Check if camera data exists
echo [5/5] Pre-flight checks...
if not exist "qew_cameras_hamilton_mississauga.json" (
    echo [WARNING] Camera metadata file not found
    echo Expected: qew_cameras_hamilton_mississauga.json
)

if not exist "database.py" (
    echo [ERROR] database.py not found
    pause
    exit /b 1
)

if not exist "download_camera_images.py" (
    echo [ERROR] download_camera_images.py not found
    pause
    exit /b 1
)

echo [OK] All pre-flight checks passed
echo.

REM Launch the GUI
echo ================================================================
echo Starting QEW Camera Collection GUI...
echo ================================================================
echo.
echo Press Ctrl+C to stop the application
echo.

python qew_camera_gui.py

REM Deactivate on exit
call venv\Scripts\deactivate.bat

endlocal

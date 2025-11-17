@echo off
REM ############################################################################
REM QEW Camera Scraper - Stop Script (Windows)
REM Part of ADBA Labs QEW Innovation Corridor Project
REM
REM This script gracefully stops the QEW Camera Collection GUI
REM ############################################################################

setlocal enabledelayedexpansion

echo ================================================================
echo   QEW Camera Collection - Stop Script
echo ================================================================
echo.

REM Find running camera GUI processes
echo Searching for running Camera GUI processes...

REM Check for Python processes running qew_camera_gui.py
tasklist /FI "IMAGENAME eq python.exe" /FI "WINDOWTITLE eq QEW*" >nul 2>&1
if errorlevel 1 (
    REM Try alternative method
    set FOUND=0
    for /f "tokens=2" %%i in ('tasklist /FI "IMAGENAME eq python.exe" ^| findstr /C:"python.exe"') do (
        set PID=%%i
        wmic process where ProcessId=!PID! get CommandLine 2>nul | findstr /C:"qew_camera_gui.py" >nul
        if not errorlevel 1 (
            set FOUND=1
            echo Found process: !PID!
            set /p "CONFIRM=Do you want to stop this process? (y/n): "
            if /i "!CONFIRM!"=="y" (
                taskkill /PID !PID! /F
                echo [OK] Process !PID! stopped
            )
        )
    )

    if !FOUND!==0 (
        echo [OK] No running Camera GUI processes found
    )
) else (
    REM Kill all Python windows with "QEW" in title
    taskkill /FI "WINDOWTITLE eq QEW*" /F
    echo [OK] All Camera GUI processes stopped
)

echo.
echo ================================================================
echo Process termination complete
echo ================================================================
echo.

REM Deactivate virtual environment if active
if defined VIRTUAL_ENV (
    echo Deactivating virtual environment...
    call venv\Scripts\deactivate.bat
    echo [OK] Virtual environment deactivated
)

pause
endlocal

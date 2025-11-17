@echo off
REM ############################################################################
REM QEW Camera Scraper - Repository Cleanup Script (Windows)
REM Part of ADBA Labs QEW Innovation Corridor Project
REM
REM This script cleans up development artifacts and temporary files
REM Use with caution - some operations are destructive!
REM ############################################################################

setlocal enabledelayedexpansion

REM Change to script directory
cd /d "%~dp0"

echo ================================================================
echo   QEW Camera Scraper - Repository Cleanup
echo   WARNING: This will delete files!
echo ================================================================
echo.

REM Analyze repository
echo Analyzing repository...
echo.

set FOUND_ITEMS=0

REM Check for __pycache__
if exist "__pycache__" (
    set FOUND_ITEMS=1
    echo [FOUND] __pycache__ directories
)

REM Check for .pyc files
dir /s /b *.pyc >nul 2>&1
if not errorlevel 1 (
    set FOUND_ITEMS=1
    echo [FOUND] .pyc files
)

REM Check for venv
if exist "venv\" (
    set FOUND_ITEMS=1
    echo [FOUND] venv directory
)

REM Check for database
if exist "camera_data.db" (
    set FOUND_ITEMS=1
    echo [FOUND] camera_data.db
)

REM Check for camera images
if exist "camera_images\" (
    set FOUND_ITEMS=1
    echo [FOUND] camera_images directory
)

REM Check for GUI settings
if exist "gui_settings.json" (
    set FOUND_ITEMS=1
    echo [FOUND] gui_settings.json
)

REM Check for test images
if exist "test_images\" (
    set FOUND_ITEMS=1
    echo [FOUND] test_images directory
)

if !FOUND_ITEMS!==0 (
    echo [OK] Repository is already clean!
    pause
    exit /b 0
)

echo.
echo Select cleanup level:
echo   1) Quick clean (Python cache only - SAFE)
echo   2) Standard clean (cache + venv - SAFE)
echo   3) Deep clean (cache + venv + data - CAUTION)
echo   4) Nuclear clean (everything - DANGER)
echo   5) Custom cleanup
echo   6) Cancel
echo.

set /p "CHOICE=Enter choice (1-6): "

if "%CHOICE%"=="1" goto quick
if "%CHOICE%"=="2" goto standard
if "%CHOICE%"=="3" goto deep
if "%CHOICE%"=="4" goto nuclear
if "%CHOICE%"=="5" goto custom
if "%CHOICE%"=="6" goto cancel
echo Invalid choice
pause
exit /b 1

:quick
echo.
echo Running quick cleanup...
if exist "__pycache__" rd /s /q "__pycache__" 2>nul
for /r %%i in (*.pyc) do del /f /q "%%i" 2>nul
echo [OK] Quick cleanup complete
goto end

:standard
echo.
echo Running standard cleanup...
if exist "__pycache__" rd /s /q "__pycache__" 2>nul
for /r %%i in (*.pyc) do del /f /q "%%i" 2>nul
if exist "venv\" (
    echo Removing virtual environment...
    rd /s /q "venv" 2>nul
    echo [OK] Virtual environment removed
)
echo [OK] Standard cleanup complete
goto end

:deep
echo.
echo [WARNING] Deep cleanup - this will delete data files!
set /p "CONFIRM=Are you sure? Type 'yes' to continue: "
if not "!CONFIRM!"=="yes" (
    echo Cancelled
    goto end
)
if exist "__pycache__" rd /s /q "__pycache__" 2>nul
for /r %%i in (*.pyc) do del /f /q "%%i" 2>nul
if exist "venv\" rd /s /q "venv" 2>nul
if exist "camera_data.db" del /f /q "camera_data.db" 2>nul
if exist "gui_settings.json" del /f /q "gui_settings.json" 2>nul
echo [OK] Deep cleanup complete
goto end

:nuclear
echo.
echo [DANGER] NUCLEAR CLEANUP - THIS WILL DELETE EVERYTHING!
echo Including all collected camera images!
set /p "CONFIRM=Type 'DELETE EVERYTHING' to confirm: "
if not "!CONFIRM!"=="DELETE EVERYTHING" (
    echo Cancelled
    goto end
)
if exist "__pycache__" rd /s /q "__pycache__" 2>nul
for /r %%i in (*.pyc) do del /f /q "%%i" 2>nul
if exist "venv\" rd /s /q "venv" 2>nul
if exist "camera_images\" rd /s /q "camera_images" 2>nul
if exist "test_images\" rd /s /q "test_images" 2>nul
if exist "camera_data.db" del /f /q "camera_data.db" 2>nul
if exist "gui_settings.json" del /f /q "gui_settings.json" 2>nul
echo [OK] Nuclear cleanup complete - repository reset
goto end

:custom
echo.
echo Custom cleanup:
set /p "ans=Clean Python cache? (y/n): "
if /i "!ans!"=="y" (
    if exist "__pycache__" rd /s /q "__pycache__" 2>nul
    for /r %%i in (*.pyc) do del /f /q "%%i" 2>nul
)

set /p "ans=Remove virtual environment? (y/n): "
if /i "!ans!"=="y" if exist "venv\" rd /s /q "venv" 2>nul

set /p "ans=Delete database? (y/n): "
if /i "!ans!"=="y" if exist "camera_data.db" del /f /q "camera_data.db" 2>nul

set /p "ans=Delete camera images? (y/n): "
if /i "!ans!"=="y" if exist "camera_images\" rd /s /q "camera_images" 2>nul

set /p "ans=Delete test images? (y/n): "
if /i "!ans!"=="y" if exist "test_images\" rd /s /q "test_images" 2>nul

set /p "ans=Delete GUI settings? (y/n): "
if /i "!ans!"=="y" if exist "gui_settings.json" del /f /q "gui_settings.json" 2>nul

echo [OK] Custom cleanup complete
goto end

:cancel
echo Cleanup cancelled
goto end

:end
echo.
echo ================================================================
echo Cleanup completed!
echo ================================================================
echo.
pause

endlocal

"""
Launch Camera Scraper GUI (No Console Window)
Simple launcher for the integrated camera scraper GUI without terminal window
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from gui.camera_scraper_gui import main

if __name__ == "__main__":
    # Ensure database directory exists
    db_dir = Path(__file__).parent / "fastapi_backend" / "database"
    db_dir.mkdir(parents=True, exist_ok=True)
    
    main()


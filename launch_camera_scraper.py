"""
Launch Camera Scraper GUI
Simple launcher for the integrated camera scraper GUI
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from gui.camera_scraper_gui import main

if __name__ == "__main__":
    print("=" * 80)
    print("QEW Innovation Corridor - Camera Scraper GUI")
    print("=" * 80)
    print("\nLaunching GUI...")
    print("The FastAPI backend will auto-start if not already running.")
    print("\n" + "=" * 80 + "\n")
    
    main()


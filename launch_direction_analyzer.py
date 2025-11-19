"""
Launch AI Direction Analyzer GUI
Simple launcher for the integrated direction analyzer GUI
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from gui.direction_analyzer_gui import main

if __name__ == "__main__":
    print("=" * 80)
    print("QEW Innovation Corridor - AI Direction Analyzer GUI")
    print("=" * 80)
    print("\nLaunching GUI...")
    print("The FastAPI backend will auto-start if not already running.")
    print("\n" + "=" * 80 + "\n")
    
    main()


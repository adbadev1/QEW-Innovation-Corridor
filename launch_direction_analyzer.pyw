"""
Launch AI Direction Analyzer GUI (No Console Window)
Simple launcher for the integrated direction analyzer GUI without terminal window
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from gui.direction_analyzer_gui import main

if __name__ == "__main__":
    main()


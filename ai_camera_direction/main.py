"""
AI Camera Direction Assessment - Main Application
"""
import sys
from PyQt6.QtWidgets import QApplication
from frontend.main_window import MainWindow


def main():
    """Main application entry point"""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()


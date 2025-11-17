"""
PyQt6 GUI for AI Camera Direction Assessment
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QTextEdit, QProgressBar,
                             QGroupBox, QFileDialog, QLineEdit, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont
from pathlib import Path
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.processor import DirectionProcessor


class ProcessorThread(QThread):
    """Worker thread for processing cameras"""

    progress = pyqtSignal(str)
    camera_processed = pyqtSignal(dict)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, api_key, source_db_path, gmaps_key, cameras, platform, model):
        super().__init__()
        self.api_key = api_key
        self.source_db_path = source_db_path
        self.gmaps_key = gmaps_key
        self.cameras = cameras
        self.platform = platform
        self.model = model
        self.is_running = True
        self.processor = None

    def run(self):
        """Process all cameras"""
        try:
            # Create processor in this thread to avoid SQLite threading issues
            self.processor = DirectionProcessor(
                self.api_key,
                self.source_db_path,
                self.gmaps_key,
                self.platform,
                self.model
            )

            for camera in self.cameras:
                if not self.is_running:
                    break

                result = self.processor.process_camera(
                    camera,
                    progress_callback=self.progress.emit
                )

                self.camera_processed.emit(result)

            # Close processor
            if self.processor:
                self.processor.close()

            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        """Stop processing"""
        self.is_running = False


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.processor = None
        self.worker_thread = None
        self.current_satellite_path = None
        self.current_camera_path = None

        # Apply futuristic dark theme
        self.apply_dark_theme()

        self.init_ui()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("AI Camera Direction Assessment")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Configuration section - API keys loaded from .env (not displayed)
        # Store API keys from environment variables
        self.claude_api_key = os.getenv('CLAUDE_API_KEY', '')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY', '')
        self.gmaps_api_key = os.getenv('GOOGLE_MAPS_API_KEY', '')

        config_group = QGroupBox("Configuration")
        config_layout = QVBoxLayout()

        # AI Platform selection
        platform_layout = QHBoxLayout()
        platform_layout.addWidget(QLabel("AI Platform:"))
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["Gemini", "Anthropic"])
        self.platform_combo.setCurrentText("Gemini")  # Default to Gemini
        self.platform_combo.currentTextChanged.connect(self.on_platform_changed)
        platform_layout.addWidget(self.platform_combo)
        platform_layout.addStretch()
        config_layout.addLayout(platform_layout)

        # Model selection
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        # Will be populated based on platform
        model_layout.addWidget(self.model_combo)
        model_layout.addStretch()
        config_layout.addLayout(model_layout)

        # Source DB path
        db_layout = QHBoxLayout()
        db_layout.addWidget(QLabel("Source Database:"))
        self.db_path_input = QLineEdit()
        # Load from environment or use default
        db_path = os.getenv('SOURCE_DB_PATH', '../camera_scraper/camera_data.db')
        self.db_path_input.setText(db_path)
        db_layout.addWidget(self.db_path_input)
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_database)
        db_layout.addWidget(browse_btn)
        config_layout.addLayout(db_layout)

        # API Status indicator (without showing keys)
        status_layout = QHBoxLayout()
        status_layout.addWidget(QLabel("API Keys:"))
        self.status_label = QLabel()
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        config_layout.addLayout(status_layout)

        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)

        # Now populate models and update status (after status_label is created)
        self.on_platform_changed("Gemini")
        
        # Control buttons
        button_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Processing")
        self.start_btn.clicked.connect(self.start_processing)
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; font-size: 14px; padding: 10px;")
        button_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_processing)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("background-color: #f44336; color: white; font-size: 14px; padding: 10px;")
        button_layout.addWidget(self.stop_btn)
        
        main_layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)
        
        # Image display section
        image_layout = QHBoxLayout()
        
        # Satellite image
        sat_group = QGroupBox("Satellite Image (North-Oriented)")
        sat_layout = QVBoxLayout()
        self.satellite_label = QLabel()
        self.satellite_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.satellite_label.setMinimumSize(600, 600)
        self.satellite_label.setStyleSheet("""
            border: 2px solid #1e3a5f;
            background-color: rgba(10, 15, 25, 0.8);
            color: #4da6ff;
            border-radius: 6px;
            padding: 10px;
        """)
        self.satellite_label.setText("Satellite image will appear here")
        sat_layout.addWidget(self.satellite_label)
        sat_group.setLayout(sat_layout)
        image_layout.addWidget(sat_group)
        
        # Camera image
        cam_group = QGroupBox("Camera Image")
        cam_layout = QVBoxLayout()
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setMinimumSize(600, 600)
        self.camera_label.setStyleSheet("""
            border: 2px solid #1e3a5f;
            background-color: rgba(10, 15, 25, 0.8);
            color: #4da6ff;
            border-radius: 6px;
            padding: 10px;
        """)
        self.camera_label.setText("Camera image will appear here")
        cam_layout.addWidget(self.camera_label)
        cam_group.setLayout(cam_layout)
        image_layout.addWidget(cam_group)
        
        main_layout.addLayout(image_layout)
        
        # Console log
        log_group = QGroupBox("AI Assessment Console")
        log_layout = QVBoxLayout()
        self.console_log = QTextEdit()
        self.console_log.setReadOnly(True)
        self.console_log.setMinimumHeight(200)
        font = QFont("Consolas", 10)
        self.console_log.setFont(font)
        log_layout.addWidget(self.console_log)
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

    def on_platform_changed(self, platform: str):
        """Handle platform selection change"""
        self.model_combo.clear()

        if platform == "Gemini":
            # Add Gemini models in the exact order specified
            self.model_combo.addItems([
                "Gemini 2.5 Pro",
                "Gemini 2.5 Flash",
                "Gemini 2.5 Flash Preview",
                "Gemini 2.5 Flash-Lite",
                "Gemini 2.5 Flash-Lite Preview",
                "Gemini 2.0 Flash",
                "Gemini 2.0 Flash-Lite"
            ])
            # Set default to Gemini 2.0 Flash
            self.model_combo.setCurrentText("Gemini 2.0 Flash")
        else:  # Anthropic
            self.model_combo.addItems([
                "Claude 3.5 Sonnet",
                "Claude 3 Opus",
                "Claude 3 Haiku"
            ])
            self.model_combo.setCurrentText("Claude 3.5 Sonnet")

        # Update API status
        self.update_api_status()

    def update_api_status(self):
        """Update API key status indicator"""
        platform = self.platform_combo.currentText()

        if platform == "Gemini":
            if self.gemini_api_key:
                self.status_label.setText("✓ Gemini API key loaded from .env")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.status_label.setText("✗ Gemini API key not found - check .env file")
                self.status_label.setStyleSheet("color: red; font-weight: bold;")
        else:  # Anthropic
            if self.claude_api_key:
                self.status_label.setText("✓ Claude API key loaded from .env")
                self.status_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.status_label.setText("✗ Claude API key not found - check .env file")
                self.status_label.setStyleSheet("color: red; font-weight: bold;")

    def browse_database(self):
        """Browse for source database file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Source Database",
            "",
            "Database Files (*.db);;All Files (*)"
        )
        if file_path:
            self.db_path_input.setText(file_path)

    def log(self, message: str):
        """Add message to console log"""
        self.console_log.append(message)
        self.console_log.verticalScrollBar().setValue(
            self.console_log.verticalScrollBar().maximum()
        )

    def display_images(self, satellite_path: str, camera_path: str):
        """Display satellite and camera images"""
        # Display satellite image
        if os.path.exists(satellite_path):
            pixmap = QPixmap(satellite_path)
            scaled_pixmap = pixmap.scaled(
                580, 580,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.satellite_label.setPixmap(scaled_pixmap)
            self.current_satellite_path = satellite_path

        # Display camera image
        if os.path.exists(camera_path):
            pixmap = QPixmap(camera_path)
            scaled_pixmap = pixmap.scaled(
                580, 580,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.camera_label.setPixmap(scaled_pixmap)
            self.current_camera_path = camera_path

    def start_processing(self):
        """Start processing cameras"""
        # Get selected platform and model
        platform = self.platform_combo.currentText()
        model = self.model_combo.currentText()

        # Validate inputs
        if platform == "Gemini":
            api_key = self.gemini_api_key
            if not api_key:
                QMessageBox.warning(self, "Missing API Key",
                                  "Gemini API key not found in .env file.\n\n"
                                  "Please add GEMINI_API_KEY to the .env file.")
                return
        else:  # Anthropic
            api_key = self.claude_api_key
            if not api_key:
                QMessageBox.warning(self, "Missing API Key",
                                  "Claude API key not found in .env file.\n\n"
                                  "Please add CLAUDE_API_KEY to the .env file.")
                return

        db_path = self.db_path_input.text().strip()
        if not db_path or not os.path.exists(db_path):
            QMessageBox.warning(self, "Invalid Database", "Please select a valid source database")
            return

        # Get optional Google Maps API key
        gmaps_key = self.gmaps_api_key or None

        # Get list of pending cameras (using temporary processor)
        try:
            temp_processor = DirectionProcessor(api_key, db_path, gmaps_key, platform, model)
            cameras = temp_processor.get_pending_cameras()
            temp_processor.close()

            if not cameras:
                QMessageBox.information(self, "No Cameras", "All cameras have been processed!")
                return

            self.log(f"Found {len(cameras)} cameras to process")
            self.log(f"Using {platform} - {model}")
            self.log("=" * 80)

            # Setup progress bar
            self.progress_bar.setMaximum(len(cameras))
            self.progress_bar.setValue(0)

            # Start worker thread (will create its own processor)
            self.worker_thread = ProcessorThread(api_key, db_path, gmaps_key, cameras, platform, model)
            self.worker_thread.progress.connect(self.log)
            self.worker_thread.camera_processed.connect(self.on_camera_processed)
            self.worker_thread.finished.connect(self.on_processing_finished)
            self.worker_thread.error.connect(self.on_error)
            self.worker_thread.start()

            # Update UI
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to start processing: {e}")

    def stop_processing(self):
        """Stop processing"""
        if self.worker_thread:
            self.worker_thread.stop()
            self.log("Stopping processing...")
            self.stop_btn.setEnabled(False)

    def on_camera_processed(self, result: dict):
        """Handle camera processing completion"""
        # Update progress bar
        current = self.progress_bar.value()
        self.progress_bar.setValue(current + 1)

        # Display images
        if result.get('satellite_image_path') and result.get('camera_image_path'):
            self.display_images(
                result['satellite_image_path'],
                result['camera_image_path']
            )

        # Log assessment details
        self.log("")
        self.log(f"Camera {result['camera_id']}, View {result['view_id']}: {result.get('location', 'Unknown')}")
        self.log(f"  Direction: {result['direction']}")

        if result.get('heading_degrees'):
            self.log(f"  Heading: {result['heading_degrees']}°")

        if result.get('confidence_score'):
            self.log(f"  Confidence: {result['confidence_score']:.2f}")

        if result.get('landmarks_identified'):
            self.log(f"  Landmarks: {result['landmarks_identified']}")

        if result.get('reasoning'):
            self.log(f"  Reasoning: {result['reasoning']}")

        self.log("-" * 80)

    def on_processing_finished(self):
        """Handle processing completion"""
        self.log("")
        self.log("=" * 80)
        self.log("✓ ALL CAMERAS PROCESSED!")
        self.log("=" * 80)

        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        # Processor is closed in the worker thread

        QMessageBox.information(self, "Complete", "All cameras have been processed!")

    def on_error(self, error_msg: str):
        """Handle processing error"""
        self.log(f"ERROR: {error_msg}")
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        QMessageBox.critical(self, "Processing Error", error_msg)

    def apply_dark_theme(self):
        """Apply futuristic dark theme with blue-to-black gradient"""
        dark_stylesheet = """
        QMainWindow {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #0a1628,
                stop:0.5 #0d1b2a,
                stop:1 #000000
            );
        }

        QWidget {
            background-color: transparent;
            color: #e0e0e0;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 10pt;
        }

        QGroupBox {
            background-color: rgba(20, 30, 50, 0.7);
            border: 2px solid #1e3a5f;
            border-radius: 8px;
            margin-top: 12px;
            padding-top: 15px;
            color: #ffffff;
            font-weight: bold;
            font-size: 11pt;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 5px 10px;
            color: #4da6ff;
        }

        QPushButton {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #1e5a8e,
                stop:1 #0d3a5f
            );
            color: #ffffff;
            border: 2px solid #2a7fba;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: bold;
            font-size: 10pt;
        }

        QPushButton:hover {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #2a7fba,
                stop:1 #1e5a8e
            );
            border: 2px solid #4da6ff;
        }

        QPushButton:pressed {
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #0d3a5f,
                stop:1 #1e5a8e
            );
        }

        QPushButton:disabled {
            background: #1a1a2e;
            color: #666666;
            border: 2px solid #333333;
        }

        QLineEdit {
            background-color: rgba(30, 40, 60, 0.8);
            color: #ffffff;
            border: 2px solid #1e3a5f;
            border-radius: 4px;
            padding: 6px;
            selection-background-color: #2a7fba;
        }

        QLineEdit:focus {
            border: 2px solid #4da6ff;
        }

        QComboBox {
            background-color: rgba(30, 40, 60, 0.8);
            color: #ffffff;
            border: 2px solid #1e3a5f;
            border-radius: 4px;
            padding: 6px;
            min-width: 200px;
        }

        QComboBox:hover {
            border: 2px solid #4da6ff;
        }

        QComboBox::drop-down {
            border: none;
            width: 30px;
        }

        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 8px solid #4da6ff;
            margin-right: 8px;
        }

        QComboBox QAbstractItemView {
            background-color: #1a2332;
            color: #ffffff;
            selection-background-color: #2a7fba;
            border: 2px solid #4da6ff;
            border-radius: 4px;
        }

        QTextEdit {
            background-color: rgba(10, 15, 25, 0.9);
            color: #00ff00;
            border: 2px solid #1e3a5f;
            border-radius: 6px;
            padding: 8px;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 9pt;
        }

        QProgressBar {
            background-color: rgba(30, 40, 60, 0.8);
            border: 2px solid #1e3a5f;
            border-radius: 6px;
            text-align: center;
            color: #ffffff;
            font-weight: bold;
        }

        QProgressBar::chunk {
            background: qlineargradient(
                x1:0, y1:0, x2:1, y2:0,
                stop:0 #1e5a8e,
                stop:0.5 #2a7fba,
                stop:1 #4da6ff
            );
            border-radius: 4px;
        }

        QLabel {
            color: #e0e0e0;
            background-color: transparent;
        }

        QScrollBar:vertical {
            background-color: rgba(30, 40, 60, 0.5);
            width: 12px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical {
            background-color: #2a7fba;
            border-radius: 6px;
            min-height: 20px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #4da6ff;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }

        QScrollBar:horizontal {
            background-color: rgba(30, 40, 60, 0.5);
            height: 12px;
            border-radius: 6px;
        }

        QScrollBar::handle:horizontal {
            background-color: #2a7fba;
            border-radius: 6px;
            min-width: 20px;
        }

        QScrollBar::handle:horizontal:hover {
            background-color: #4da6ff;
        }

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        """

        self.setStyleSheet(dark_stylesheet)

    def closeEvent(self, event):
        """Handle window close"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.stop()
            self.worker_thread.wait()

        # Processor is closed in the worker thread

        event.accept()


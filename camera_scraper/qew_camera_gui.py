"""
QEW Camera Collection GUI
PyQt6 interface for automated camera image collection with scheduling
"""
import sys
import json
import os
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QSpinBox, 
                             QComboBox, QTextEdit, QGroupBox, QGridLayout)
from PyQt6.QtCore import QTimer, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor, QLinearGradient
import pytz

# Import our camera collection functions
from download_camera_images import (load_camera_data, create_output_directory, 
                                   download_camera_images, generate_summary_report)

class CameraCollectionWorker(QThread):
    """Worker thread for camera image collection"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, cameras, images_per_camera=1):
        super().__init__()
        self.cameras = cameras
        self.images_per_camera = images_per_camera
        self.is_running = True
    
    def run(self):
        """Run the camera collection process"""
        try:
            self.progress.emit("Starting camera image collection...")
            
            # Create output directory
            output_dir = create_output_directory()
            self.progress.emit(f"Output directory: {output_dir}")
            
            # Download images (single round for scheduled collection)
            total_images, metadata = download_camera_images(
                self.cameras, 
                output_dir, 
                images_per_camera=self.images_per_camera,
                delay_between_captures=0  # No delay for scheduled runs
            )
            
            # Generate report
            generate_summary_report(self.cameras, metadata, output_dir)
            
            self.progress.emit(f"Collection complete! {total_images} images downloaded.")
            self.finished.emit(True, f"Successfully collected {total_images} images to {output_dir}")
            
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}")
            self.finished.emit(False, f"Error: {str(e)}")
    
    def stop(self):
        """Stop the collection process"""
        self.is_running = False


class QEWCameraGUI(QMainWindow):
    """Main GUI window for QEW Camera Collection"""
    
    SETTINGS_FILE = "gui_settings.json"
    
    def __init__(self):
        super().__init__()
        self.worker = None
        self.collection_timer = None
        self.is_running = False
        self.cameras = []
        
        # Load settings
        self.settings = self.load_settings()
        
        # Initialize UI
        self.init_ui()
        
        # Start clock timer
        self.clock_timer = QTimer()
        self.clock_timer.timeout.connect(self.update_clock)
        self.clock_timer.start(1000)  # Update every second
        
        # Load camera data
        self.load_camera_metadata()
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("QEW Innovation Corridor - Camera Collection System")
        self.setGeometry(100, 100, 900, 700)
        
        # Apply dark theme
        self.apply_dark_theme()
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("QEW Camera Collection System")
        title_font = QFont("Arial", 24, QFont.Weight.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        title_label.setStyleSheet("color: #4da6ff; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # Clock section
        clock_group = self.create_clock_section()
        main_layout.addWidget(clock_group)
        
        # Settings section
        settings_group = self.create_settings_section()
        main_layout.addWidget(settings_group)
        
        # Control section
        control_group = self.create_control_section()
        main_layout.addWidget(control_group)
        
        # Status section
        status_group = self.create_status_section()
        main_layout.addWidget(status_group)
        
        # Add stretch to push everything up
        main_layout.addStretch()
        
        central_widget.setLayout(main_layout)
    
    def create_clock_section(self):
        """Create the clock display section"""
        group = QGroupBox("Current Time")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #4da6ff;
                border: 2px solid #2d5a7b;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)

        # Single horizontal layout for everything
        layout = QHBoxLayout()

        # Clock display
        self.clock_label = QLabel()
        clock_font = QFont("Arial", 12, QFont.Weight.Bold)
        self.clock_label.setFont(clock_font)
        self.clock_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.clock_label.setStyleSheet("color: #66ccff; padding: 5px;")
        layout.addWidget(self.clock_label)

        # Add spacing
        layout.addSpacing(20)

        # Timezone selector
        tz_label = QLabel("Timezone:")
        tz_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        layout.addWidget(tz_label)

        self.timezone_combo = QComboBox()
        self.timezone_combo.addItems([
            "US/Eastern", "US/Central", "US/Mountain", "US/Pacific",
            "America/Toronto", "America/Vancouver", "UTC", "Europe/London"
        ])
        self.timezone_combo.setCurrentText(self.settings.get("timezone", "US/Eastern"))
        self.timezone_combo.currentTextChanged.connect(self.on_timezone_changed)
        self.timezone_combo.setStyleSheet("""
            QComboBox {
                background-color: #1a1a2e;
                color: #ffffff;
                border: 1px solid #2d5a7b;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #4da6ff;
            }
        """)
        layout.addWidget(self.timezone_combo)

        # Add stretch to push everything to the left
        layout.addStretch()

        group.setLayout(layout)

        return group
    
    def create_settings_section(self):
        """Create the settings section"""
        group = QGroupBox("Collection Settings")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #4da6ff;
                border: 2px solid #2d5a7b;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)

        # Single horizontal layout for everything
        layout = QHBoxLayout()

        # Interval settings
        interval_label = QLabel("Interval:")
        interval_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        layout.addWidget(interval_label)

        # Hours
        hours_label = QLabel("Hours:")
        hours_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        layout.addWidget(hours_label)

        self.hours_spin = QSpinBox()
        self.hours_spin.setRange(0, 23)
        self.hours_spin.setValue(self.settings.get("interval_hours", 1))
        self.hours_spin.valueChanged.connect(self.on_settings_changed)
        self.hours_spin.setFixedWidth(60)
        self.hours_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1a1a2e;
                color: #ffffff;
                border: 1px solid #2d5a7b;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.hours_spin)

        # Minutes
        minutes_label = QLabel("Minutes:")
        minutes_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        layout.addWidget(minutes_label)

        self.minutes_spin = QSpinBox()
        self.minutes_spin.setRange(0, 59)
        self.minutes_spin.setValue(self.settings.get("interval_minutes", 0))
        self.minutes_spin.valueChanged.connect(self.on_settings_changed)
        self.minutes_spin.setFixedWidth(60)
        self.minutes_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1a1a2e;
                color: #ffffff;
                border: 1px solid #2d5a7b;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.minutes_spin)

        # Add spacing
        layout.addSpacing(20)

        # Images per collection
        images_label = QLabel("Images per Camera:")
        images_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        layout.addWidget(images_label)

        self.images_spin = QSpinBox()
        self.images_spin.setRange(1, 10)
        self.images_spin.setValue(self.settings.get("images_per_camera", 1))
        self.images_spin.valueChanged.connect(self.on_settings_changed)
        self.images_spin.setFixedWidth(60)
        self.images_spin.setStyleSheet("""
            QSpinBox {
                background-color: #1a1a2e;
                color: #ffffff;
                border: 1px solid #2d5a7b;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.images_spin)

        # Add stretch to push everything to the left
        layout.addStretch()

        group.setLayout(layout)
        return group

    def create_control_section(self):
        """Create the control buttons section"""
        group = QGroupBox("Control")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #4da6ff;
                border: 2px solid #2d5a7b;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)

        layout = QHBoxLayout()

        # Start/Stop button
        self.start_button = QPushButton("START COLLECTION")
        self.start_button.setMinimumHeight(50)
        self.start_button.clicked.connect(self.toggle_collection)
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #0d7377;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
            QPushButton:pressed {
                background-color: #0a5f62;
            }
        """)
        layout.addWidget(self.start_button)

        # Manual collection button
        self.manual_button = QPushButton("COLLECT NOW")
        self.manual_button.setMinimumHeight(50)
        self.manual_button.clicked.connect(self.manual_collection)
        self.manual_button.setStyleSheet("""
            QPushButton {
                background-color: #2d5a7b;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #3d7a9b;
            }
            QPushButton:pressed {
                background-color: #1d4a6b;
            }
        """)
        layout.addWidget(self.manual_button)

        group.setLayout(layout)
        return group

    def create_status_section(self):
        """Create the status display section"""
        group = QGroupBox("Status Log")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #4da6ff;
                border: 2px solid #2d5a7b;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 5px;
            }
        """)

        layout = QVBoxLayout()

        # Status text area
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMinimumHeight(200)
        self.status_text.setStyleSheet("""
            QTextEdit {
                background-color: #0f0f1e;
                color: #00ff00;
                border: 1px solid #2d5a7b;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Courier New';
                font-size: 11px;
            }
        """)
        layout.addWidget(self.status_text)

        # Info labels
        info_layout = QHBoxLayout()

        self.camera_count_label = QLabel("Cameras: 0")
        self.camera_count_label.setStyleSheet("color: #ffffff; font-size: 11px;")
        info_layout.addWidget(self.camera_count_label)

        self.next_collection_label = QLabel("Next Collection: Not scheduled")
        self.next_collection_label.setStyleSheet("color: #ffffff; font-size: 11px;")
        info_layout.addWidget(self.next_collection_label)

        info_layout.addStretch()

        layout.addLayout(info_layout)

        group.setLayout(layout)
        return group

    def apply_dark_theme(self):
        """Apply dark blue to black gradient theme"""
        palette = QPalette()

        # Set colors
        palette.setColor(QPalette.ColorRole.Window, QColor(15, 15, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(26, 26, 46))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(45, 90, 123))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(45, 90, 123))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))

        self.setPalette(palette)

        # Apply gradient stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f0f1e,
                    stop:1 #000000
                );
            }
        """)

    def update_clock(self):
        """Update the clock display"""
        timezone = self.timezone_combo.currentText()
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)
        time_str = current_time.strftime("%I:%M:%S %p")
        date_str = current_time.strftime("%A, %B %d, %Y")
        self.clock_label.setText(f"{time_str} - {date_str}")

    def load_camera_metadata(self):
        """Load camera metadata"""
        try:
            self.cameras = load_camera_data()
            self.camera_count_label.setText(f"Cameras: {len(self.cameras)}")
            self.log_status(f"Loaded {len(self.cameras)} cameras from QEW corridor")
        except Exception as e:
            self.log_status(f"Error loading camera data: {str(e)}")
            self.cameras = []

    def log_status(self, message):
        """Add a message to the status log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.status_text.append(f"[{timestamp}] {message}")

    def on_timezone_changed(self, timezone):
        """Handle timezone change"""
        self.settings["timezone"] = timezone
        self.save_settings()
        self.update_clock()
        self.log_status(f"Timezone changed to {timezone}")

    def on_settings_changed(self):
        """Handle settings change"""
        self.settings["interval_hours"] = self.hours_spin.value()
        self.settings["interval_minutes"] = self.minutes_spin.value()
        self.settings["images_per_camera"] = self.images_spin.value()
        self.save_settings()

        # Update next collection time if running
        if self.is_running:
            self.update_next_collection_time()

    def load_settings(self):
        """Load settings from JSON file"""
        default_settings = {
            "timezone": "US/Eastern",
            "interval_hours": 1,
            "interval_minutes": 0,
            "images_per_camera": 1
        }

        if os.path.exists(self.SETTINGS_FILE):
            try:
                with open(self.SETTINGS_FILE, 'r') as f:
                    settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    return {**default_settings, **settings}
            except Exception as e:
                print(f"Error loading settings: {e}")
                return default_settings

        return default_settings

    def save_settings(self):
        """Save settings to JSON file"""
        try:
            with open(self.SETTINGS_FILE, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            self.log_status(f"Error saving settings: {str(e)}")

    def toggle_collection(self):
        """Toggle automatic collection on/off"""
        if not self.is_running:
            self.start_collection()
        else:
            self.stop_collection()

    def start_collection(self):
        """Start automatic collection"""
        if not self.cameras:
            self.log_status("Error: No camera data loaded. Please check qew_cameras_hamilton_mississauga.json")
            return

        interval_hours = self.hours_spin.value()
        interval_minutes = self.minutes_spin.value()

        if interval_hours == 0 and interval_minutes == 0:
            self.log_status("Error: Please set a collection interval greater than 0")
            return

        self.is_running = True
        self.start_button.setText("STOP COLLECTION")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #c41e3a;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #e4264a;
            }
            QPushButton:pressed {
                background-color: #a41e3a;
            }
        """)

        # Disable settings while running
        self.hours_spin.setEnabled(False)
        self.minutes_spin.setEnabled(False)
        self.images_spin.setEnabled(False)

        # Calculate interval in milliseconds
        interval_ms = (interval_hours * 3600 + interval_minutes * 60) * 1000

        # Create timer
        self.collection_timer = QTimer()
        self.collection_timer.timeout.connect(self.run_collection)
        self.collection_timer.start(interval_ms)

        self.log_status(f"Automatic collection started (every {interval_hours}h {interval_minutes}m)")
        self.update_next_collection_time()

        # Run first collection immediately
        self.run_collection()

    def stop_collection(self):
        """Stop automatic collection"""
        self.is_running = False

        if self.collection_timer:
            self.collection_timer.stop()
            self.collection_timer = None

        self.start_button.setText("START COLLECTION")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #0d7377;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #14a085;
            }
            QPushButton:pressed {
                background-color: #0a5f62;
            }
        """)

        # Re-enable settings
        self.hours_spin.setEnabled(True)
        self.minutes_spin.setEnabled(True)
        self.images_spin.setEnabled(True)

        self.next_collection_label.setText("Next Collection: Not scheduled")
        self.log_status("Automatic collection stopped")

    def manual_collection(self):
        """Run a manual collection"""
        if not self.cameras:
            self.log_status("Error: No camera data loaded")
            return

        if self.worker and self.worker.isRunning():
            self.log_status("Collection already in progress...")
            return

        self.run_collection()

    def run_collection(self):
        """Run the camera collection process"""
        if self.worker and self.worker.isRunning():
            self.log_status("Previous collection still in progress, skipping...")
            return

        self.log_status("Starting camera image collection...")

        # Disable buttons during collection
        self.manual_button.setEnabled(False)

        # Create and start worker thread
        images_per_camera = self.images_spin.value()
        self.worker = CameraCollectionWorker(self.cameras, images_per_camera)
        self.worker.progress.connect(self.log_status)
        self.worker.finished.connect(self.on_collection_finished)
        self.worker.start()

        # Update next collection time
        if self.is_running:
            self.update_next_collection_time()

    def on_collection_finished(self, success, message):
        """Handle collection completion"""
        self.log_status(message)
        self.manual_button.setEnabled(True)

        if success:
            self.log_status("=" * 50)

    def update_next_collection_time(self):
        """Update the next collection time display"""
        if not self.is_running:
            return

        interval_hours = self.hours_spin.value()
        interval_minutes = self.minutes_spin.value()

        timezone = self.timezone_combo.currentText()
        tz = pytz.timezone(timezone)
        current_time = datetime.now(tz)

        from datetime import timedelta
        next_time = current_time + timedelta(hours=interval_hours, minutes=interval_minutes)
        next_time_str = next_time.strftime("%I:%M:%S %p")

        self.next_collection_label.setText(f"Next Collection: {next_time_str}")

    def closeEvent(self, event):
        """Handle window close event"""
        if self.is_running:
            self.stop_collection()

        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()

        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)

    # Set application-wide font
    font = QFont("Arial", 10)
    app.setFont(font)

    # Create and show main window
    window = QEWCameraGUI()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()


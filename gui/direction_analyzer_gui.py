"""
AI Camera Direction Assessment GUI - Integrated with FastAPI Backend
PyQt6 interface for AI-powered camera direction analysis
"""
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QTextEdit, QProgressBar,
                             QGroupBox, QFileDialog, QLineEdit, QMessageBox, QComboBox, QApplication,
                             QDialog, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QDialogButtonBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont, QPalette, QColor
from pathlib import Path
import sys
import os
import requests
import time
import sqlite3

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from gui.backend_manager import BackendManager


class ProcessorThread(QThread):
    """Worker thread for processing cameras with detailed logging"""

    progress = pyqtSignal(str)
    camera_processed = pyqtSignal(dict)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, backend_manager: BackendManager, platform: str, model: str,
                 batch_mode: bool = True, existing_images_folder: str = None):
        super().__init__()
        self.backend_manager = backend_manager
        self.platform = platform
        self.model = model
        self.batch_mode = batch_mode
        self.existing_images_folder = existing_images_folder
        self.is_running = True
        self.analyzer = None

    def run(self):
        """Process cameras with detailed logging"""
        try:
            # Import the direction analyzer service
            from fastapi_backend.services.direction_analyzer import DirectionAnalyzerService

            # Create analyzer with progress callback
            self.analyzer = DirectionAnalyzerService(
                platform=self.platform,
                model=self.model,
                progress_callback=self.progress.emit,
                existing_images_folder=self.existing_images_folder
            )

            self.progress.emit("=" * 80)
            self.progress.emit("AI Camera Direction Assessment")
            self.progress.emit("=" * 80)
            self.progress.emit(f"Platform: {self.platform}")
            self.progress.emit(f"Model: {self.model}")
            self.progress.emit("")

            # Get pending cameras count
            pending_count = self.analyzer.get_pending_count()
            self.progress.emit(f"Found {pending_count} cameras pending analysis")

            if pending_count == 0:
                self.progress.emit("No cameras to process!")
                self.finished.emit()
                return

            self.progress.emit("")
            self.progress.emit("Starting batch analysis...")
            self.progress.emit("")

            # Run batch analysis
            result = self.analyzer.analyze_pending_cameras(
                platform=self.platform,
                model=self.model,
                result_callback=self.camera_processed.emit
            )

            if result['status'] == 'success':
                self.progress.emit("")
                self.progress.emit("=" * 80)
                self.progress.emit(f"✓ Analysis Complete!")
                self.progress.emit(f"Processed: {result.get('processed', 0)} cameras")
                self.progress.emit(f"Successful: {result.get('successful', 0)}")
                self.progress.emit(f"Failed: {result.get('failed', 0)}")
                self.progress.emit("=" * 80)
                self.finished.emit()
            else:
                error_msg = result.get('error', 'Unknown error')
                self.progress.emit(f"✗ Analysis failed: {error_msg}")
                self.error.emit(error_msg)

        except Exception as e:
            self.progress.emit(f"✗ Error: {str(e)}")
            import traceback
            self.progress.emit(traceback.format_exc())
            self.error.emit(str(e))

    def stop(self):
        """Stop processing"""
        self.is_running = False
        if self.analyzer:
            self.analyzer.stop_analysis()
            self.progress.emit("Stopping analysis...")


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.worker_thread = None
        self.current_satellite_path = None
        self.current_camera_path = None
        self.selected_images_folder = None  # For existing images

        # Initialize backend manager
        self.backend_manager = BackendManager()

        # Apply futuristic dark theme
        self.apply_dark_theme()

        # History tracking
        self.history = []
        self.current_history_index = -1
        self.history_file = "current_run_history.json"
        # Clear history file on start
        if os.path.exists(self.history_file):
            try:
                os.remove(self.history_file)
            except:
                pass

        self.init_ui()

        # Start backend
        self.startup_backend()
    
    def startup_backend(self):
        """Start backend"""
        if not self.backend_manager.start_backend(wait_time=8):
            QMessageBox.warning(
                self,
                "Backend Error",
                "Failed to start FastAPI backend.\n\n"
                "Please ensure:\n"
                "1. Virtual environment is set up (venv/)\n"
                "2. Dependencies are installed (pip install -r requirements.txt)\n"
                "3. Port 8000 is available"
            )
            return
        
        self.log("✓ Backend connected successfully")
        self.load_pending_count()
    
    def load_pending_count(self):
        """Load count of pending cameras"""
        try:
            url = self.backend_manager.get_api_url('/api/directions/pending')
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                count = data.get('count', 0)
                self.log(f"Found {count} cameras pending analysis")
        except Exception as e:
            self.log(f"Error loading pending count: {e}")
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("AI Camera Direction Assessment")
        self.setGeometry(100, 100, 1600, 1000)  # Increased size for better image viewing

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # --- Top Control Panel ---
        control_group = QGroupBox("AI Camera Direction Assessment")
        control_layout = QHBoxLayout()
        control_layout.setSpacing(15)
        
        # 1. AI Platform
        control_layout.addWidget(QLabel("Platform:"))
        self.platform_combo = QComboBox()
        self.platform_combo.addItems(["Gemini", "Anthropic"])
        self.platform_combo.setCurrentText("Gemini")
        self.platform_combo.currentTextChanged.connect(self.on_platform_changed)
        self.platform_combo.setFixedWidth(100)
        control_layout.addWidget(self.platform_combo)

        # 2. Model
        control_layout.addWidget(QLabel("Model:"))
        self.model_combo = QComboBox()
        self.model_combo.setFixedWidth(180)
        control_layout.addWidget(self.model_combo)

        # 3. Existing Images Folder
        control_layout.addWidget(QLabel("Images:"))
        self.folder_path_edit = QLineEdit()
        self.folder_path_edit.setPlaceholderText("Select collection database...")
        self.folder_path_edit.setReadOnly(True)
        control_layout.addWidget(self.folder_path_edit)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.select_images_folder)
        browse_btn.setFixedWidth(80)
        browse_btn.setStyleSheet("background-color: #2196F3; color: white; font-weight: bold;")
        control_layout.addWidget(browse_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_images_folder)
        clear_btn.setFixedWidth(60)
        control_layout.addWidget(clear_btn)

        # Spacer to push buttons to the right
        control_layout.addStretch()

        # Navigation Buttons
        self.prev_btn = QPushButton("<")
        self.prev_btn.clicked.connect(self.prev_image)
        self.prev_btn.setFixedWidth(40)
        self.prev_btn.setEnabled(False)
        self.prev_btn.setStyleSheet("background-color: #555; color: white; font-weight: bold;")
        control_layout.addWidget(self.prev_btn)

        self.next_btn = QPushButton(">")
        self.next_btn.clicked.connect(self.next_image)
        self.next_btn.setFixedWidth(40)
        self.next_btn.setEnabled(False)
        self.next_btn.setStyleSheet("background-color: #555; color: white; font-weight: bold;")
        control_layout.addWidget(self.next_btn)

        # 4. Start/Stop Buttons
        self.start_btn = QPushButton("Start Processing")
        self.start_btn.clicked.connect(self.start_processing)
        self.start_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold; padding: 5px 15px;")
        self.start_btn.setMinimumWidth(120)
        control_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_processing)
        self.stop_btn.setStyleSheet("background-color: #F44336; color: white; font-weight: bold; padding: 5px 15px;")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumWidth(80)
        control_layout.addWidget(self.stop_btn)

        control_group.setLayout(control_layout)
        main_layout.addWidget(control_group)

        # --- Image Display Area ---
        images_layout = QHBoxLayout()
        
        # Satellite Image
        sat_group = QGroupBox("Satellite Image (North-Oriented)")
        sat_layout = QVBoxLayout()
        self.satellite_label = QLabel()
        self.satellite_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.satellite_label.setStyleSheet("background-color: #1e1e1e; border: 1px solid #333;")
        self.satellite_label.setMinimumHeight(600)  # Increased height
        self.satellite_label.setText("Satellite image will appear here")
        sat_layout.addWidget(self.satellite_label)
        sat_group.setLayout(sat_layout)
        images_layout.addWidget(sat_group)

        # Camera Image
        cam_group = QGroupBox("Camera Image")
        cam_layout = QVBoxLayout()
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.camera_label.setStyleSheet("background-color: #1e1e1e; border: 1px solid #333;")
        self.camera_label.setMinimumHeight(600)  # Increased height
        self.camera_label.setText("Camera image will appear here")
        cam_layout.addWidget(self.camera_label)
        cam_group.setLayout(cam_layout)
        images_layout.addWidget(cam_group)

        main_layout.addLayout(images_layout, stretch=1)  # Give images more stretch factor

        # --- Console Log ---
        log_group = QGroupBox("AI Assessment Console")
        log_layout = QVBoxLayout()
        self.console_log = QTextEdit()
        self.console_log.setReadOnly(True)
        self.console_log.setStyleSheet("background-color: #000; color: #0f0; font-family: Consolas, monospace;")
        self.console_log.setMaximumHeight(200)
        log_layout.addWidget(self.console_log)
        
        # Status bar inside console group
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #888;")
        log_layout.addWidget(self.status_label)
        
        self.progress_bar = QProgressBar()
        log_layout.addWidget(self.progress_bar)
        
        log_group.setLayout(log_layout)
        main_layout.addWidget(log_group)

        # Initialize state
        self.on_platform_changed(self.platform_combo.currentText())
        
        # Source info label (hidden but kept for logic compatibility if needed, or we can remove usage)
        self.source_info_label = QLabel("") 

    def on_platform_changed(self, platform: str):
        """Handle platform selection change"""
        self.model_combo.clear()

        if platform == "Gemini":
            self.model_combo.addItems([
                "Gemini 2.5 Pro",
                "Gemini 2.5 Flash",
                "Gemini 2.5 Flash Preview",
                "Gemini 2.5 Flash-Lite",
                "Gemini 2.5 Flash-Lite Preview",
                "Gemini 2.0 Flash",
                "Gemini 2.0 Flash-Lite"
            ])
            self.model_combo.setCurrentText("Gemini 2.0 Flash")
        else:  # Anthropic
            self.model_combo.addItems([
                "Claude 3.5 Sonnet",
                "Claude 3 Opus",
                "Claude 3 Haiku"
            ])
            self.model_combo.setCurrentText("Claude 3.5 Sonnet")

        self.update_status_label()

    def update_status_label(self):
        """Update API status label"""
        platform = self.platform_combo.currentText()
        self.status_label.setText(f"✓ Backend Ready ({platform})")
        self.status_label.setStyleSheet("color: #4CAF50; font-weight: bold;")

    def start_processing(self):
        """Start processing cameras"""
        platform = self.platform_combo.currentText()
        model = self.model_combo.currentText()

        self.log(f"Starting AI direction analysis...")
        self.log(f"Platform: {platform}")
        self.log(f"Model: {model}")

        # Disable start button, enable stop button
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress

        # Create and start worker thread
        self.worker_thread = ProcessorThread(
            self.backend_manager,
            platform,
            model,
            batch_mode=True,
            existing_images_folder=self.selected_images_folder
        )
        self.worker_thread.progress.connect(self.log)
        self.worker_thread.camera_processed.connect(self.on_camera_processed)
        self.worker_thread.finished.connect(self.on_processing_finished)
        self.worker_thread.error.connect(self.on_processing_error)
        self.worker_thread.start()

    def stop_processing(self):
        """Stop processing"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.log("Stopping processing...")
            self.worker_thread.stop()
            self.worker_thread.wait()
            self.on_processing_finished()

    def prev_image(self):
        """Show previous image in history"""
        if self.current_history_index > 0:
            self.current_history_index -= 1
            self.show_result_at_index(self.current_history_index)
            self.update_navigation_buttons()

    def next_image(self):
        """Show next image in history"""
        if self.current_history_index < len(self.history) - 1:
            self.current_history_index += 1
            self.show_result_at_index(self.current_history_index)
            self.update_navigation_buttons()

    def update_navigation_buttons(self):
        """Update enable state of navigation buttons"""
        self.prev_btn.setEnabled(self.current_history_index > 0)
        self.next_btn.setEnabled(self.current_history_index < len(self.history) - 1)

    def show_result_at_index(self, index):
        """Display result at specific history index"""
        if 0 <= index < len(self.history):
            result = self.history[index]
            
            # Update images
            satellite_path = result.get('satellite_image_path')
            camera_path = result.get('camera_image_path')
            
            if satellite_path and camera_path:
                self.display_images(satellite_path, camera_path)
            
            # Update status label to show we are viewing history
            camera_id = result.get('camera_id')
            view_id = result.get('view_id')
            self.status_label.setText(f"Viewing result {index + 1}/{len(self.history)}: Camera {camera_id} View {view_id}")

    def save_to_history_log(self, result):
        """Save result to JSON history log"""
        import json
        try:
            # Read existing
            data = []
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    try:
                        data = json.load(f)
                    except:
                        pass
            
            # Append new
            data.append(result)
            
            # Write back
            with open(self.history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")

    def on_camera_processed(self, result: dict):
        """Handle camera processing result"""
        camera_id = result.get('camera_id', 'Unknown')
        view_id = result.get('view_id', 'Unknown')
        
        # Get inner result
        inner_result = result.get('result', {})
        direction = inner_result.get('direction', 'Unknown')
        confidence = inner_result.get('confidence', 0.0)
        
        # Log basic info
        self.log(f"✓ Camera {camera_id}, View {view_id}: {direction} (Conf: {confidence:.2f})")
        
        # Log location info
        lat = result.get('latitude')
        lon = result.get('longitude')
        url = result.get('camera_url')
        if lat and lon:
            self.log(f"  Location: {lat}, {lon}")
        if url:
            self.log(f"  URL: {url}")
        
        # Log enhanced info
        lanes = inner_result.get('lanes_detected')
        if lanes:
            self.log(f"  Lanes: {lanes}")
        features = inner_result.get('road_features')
        if features:
            self.log(f"  Features: {features}")

        # Add to history
        self.history.append(result)
        self.current_history_index = len(self.history) - 1
        self.save_to_history_log(result)
        self.update_navigation_buttons()
        self.show_result_at_index(self.current_history_index) # Display the newly processed result

    def on_processing_finished(self):
        """Handle processing completion"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setRange(0, 100) # Reset to normal range
        self.progress_bar.setValue(100)
        self.status_label.setText("Processing complete")
        self.log("Processing finished")
        QMessageBox.information(self, "Complete", "Direction analysis completed successfully!")

    def display_images(self, satellite_path: str, camera_path: str):
        """Display satellite and camera images"""
        # Display satellite image
        if satellite_path and os.path.exists(satellite_path):
            pixmap = QPixmap(satellite_path)
            scaled_pixmap = pixmap.scaled(
                self.satellite_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.satellite_label.setPixmap(scaled_pixmap)
        else:
            self.satellite_label.setText("Satellite Image Not Available")

        # Display camera image
        if camera_path and os.path.exists(camera_path):
            pixmap = QPixmap(camera_path)
            scaled_pixmap = pixmap.scaled(
                self.camera_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.camera_label.setPixmap(scaled_pixmap)
        else:
            self.camera_label.setText("Camera Image Not Available")

    def select_images_folder(self):
        """Select database to browse collections"""
        db_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Camera Data Database",
            str(Path.home()),
            "Database Files (*.db);;All Files (*)"
        )

        if db_path:
            self.show_collection_dialog(db_path)

    def show_collection_dialog(self, db_path: str):
        """Show dialog to select a collection from the database"""
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT collection_id, start_time, total_images, output_directory FROM collections ORDER BY start_time DESC")
            collections = cursor.fetchall()
            conn.close()

            if not collections:
                QMessageBox.warning(self, "No Collections", "No collections found in the selected database.")
                return

            dialog = QDialog(self)
            dialog.setWindowTitle("Select Image Collection")
            dialog.setMinimumWidth(600)
            layout = QVBoxLayout(dialog)

            table = QTableWidget()
            table.setColumnCount(4)
            table.setHorizontalHeaderLabels(["Collection ID", "Start Time", "Images", "Directory"])
            table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
            table.setRowCount(len(collections))

            for i, (col_id, start, total, out_dir) in enumerate(collections):
                table.setItem(i, 0, QTableWidgetItem(str(col_id)))
                table.setItem(i, 1, QTableWidgetItem(str(start)))
                table.setItem(i, 2, QTableWidgetItem(str(total)))
                table.setItem(i, 3, QTableWidgetItem(str(out_dir)))

            layout.addWidget(table)

            btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
            btn_box.accepted.connect(dialog.accept)
            btn_box.rejected.connect(dialog.reject)
            layout.addWidget(btn_box)
            
            # Select first row by default
            table.selectRow(0)

            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected_items = table.selectedItems()
                if selected_items:
                    row = selected_items[0].row()
                    output_dir = collections[row][3]
                    
                    # Handle relative paths
                    if not os.path.isabs(output_dir):
                        # Assume relative to the database file location
                        db_dir = os.path.dirname(db_path)
                        potential_path = os.path.abspath(os.path.join(db_dir, output_dir))
                        if os.path.exists(potential_path):
                            output_dir = potential_path
                    
                    # Verify directory exists
                    if os.path.exists(output_dir):
                        self.selected_images_folder = output_dir
                        self.folder_path_edit.setText(output_dir)
                        self.source_info_label.setText(f"📁 Using collection: {collections[row][0]}")
                        self.source_info_label.setStyleSheet("color: #4CAF50; font-style: italic; padding: 5px;")
                        self.log(f"Selected collection: {collections[row][0]}")
                        self.log(f"Images directory: {output_dir}")
                    else:
                        QMessageBox.warning(self, "Directory Not Found", f"The directory for this collection does not exist:\n{output_dir}\n\nExpected at: {os.path.abspath(output_dir)}")

        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Error reading database: {str(e)}")

    def clear_images_folder(self):
        """Clear selected images folder"""
        self.selected_images_folder = None
        self.folder_path_edit.clear()
        self.source_info_label.setText("📥 Will download images from internet")
        self.source_info_label.setStyleSheet("color: #4da6ff; font-style: italic; padding: 5px;")
        self.log("Cleared existing images folder - will download from internet")

        self.status_label.setText("Processing complete")
        self.log("Processing finished")
        QMessageBox.information(self, "Complete", "Direction analysis completed successfully!")

    def on_processing_error(self, error_msg: str):
        """Handle processing error"""
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("Error occurred")
        self.log(f"Error: {error_msg}")
        QMessageBox.critical(self, "Error", f"An error occurred during processing:\n{error_msg}")

    def log(self, message: str):
        """Add message to console log with full timestamp"""
        from datetime import datetime
        # Get current time with date and time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Format the message with timestamp
        formatted_message = f"[{timestamp}] {message}"

        # Append to console log
        self.console_log.append(formatted_message)

        # Auto-scroll to bottom
        scrollbar = self.console_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def apply_dark_theme(self):
        """Apply futuristic dark theme"""
        palette = QPalette()

        # Dark blue/black gradient background
        palette.setColor(QPalette.ColorRole.Window, QColor(10, 15, 25))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(77, 166, 255))
        palette.setColor(QPalette.ColorRole.Base, QColor(15, 20, 30))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(30, 60, 95))
        palette.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.Button, QColor(30, 58, 95))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(77, 166, 255))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(77, 166, 255))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))

        self.setPalette(palette)

        # Additional styling
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0a0f19,
                    stop:1 #000000
                );
            }
            QGroupBox {
                border: 2px solid #1e3a5f;
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                font-weight: bold;
                color: #4da6ff;
                background-color: rgba(10, 15, 25, 0.6);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #4da6ff;
            }
            QTextEdit {
                background-color: rgba(10, 15, 25, 0.8);
                color: #00ff00;
                border: 1px solid #1e3a5f;
                border-radius: 6px;
                padding: 8px;
            }
            QComboBox, QLineEdit {
                background-color: #0f1419;
                color: #ffffff;
                border: 1px solid #1e3a5f;
                border-radius: 4px;
                padding: 6px;
            }
            QProgressBar {
                border: 1px solid #1e3a5f;
                border-radius: 4px;
                text-align: center;
                background-color: #0f1419;
                color: #4da6ff;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4da6ff,
                    stop:1 #00d4ff
                );
            }
        """)

    def closeEvent(self, event):
        """Handle window close event"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.stop()
            self.worker_thread.wait()
        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)

    # Set application-wide font
    font = QFont("Arial", 10)
    app.setFont(font)

    # Create and show main window
    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()



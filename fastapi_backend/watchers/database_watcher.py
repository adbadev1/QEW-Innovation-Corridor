"""
Database Watcher Service
Monitors the camera database for changes and automatically exports to webapp
Uses watchdog library for file system monitoring
"""
import time
import sqlite3
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from fastapi_backend.config import CAMERA_DB_PATH, BASE_DIR
from fastapi_backend.services.webapp_exporter import WebAppExporter


class DatabaseChangeHandler(FileSystemEventHandler):
    """Handler for database file changes"""
    
    def __init__(self, db_path: Path, exporter: WebAppExporter):
        self.db_path = db_path
        self.exporter = exporter
        self.last_export_time = None
        self.last_collection_id = None
        self.cooldown_seconds = 5  # Prevent multiple exports in quick succession
        
    def on_modified(self, event):
        """Called when database file is modified"""
        if event.src_path == str(self.db_path):
            self._handle_database_change()
    
    def _handle_database_change(self):
        """Handle database modification event"""
        # Check cooldown to prevent rapid-fire exports
        now = datetime.now()
        if self.last_export_time:
            elapsed = (now - self.last_export_time).total_seconds()
            if elapsed < self.cooldown_seconds:
                return
        
        print(f"\n[{now.strftime('%H:%M:%S')}] Database change detected!")
        
        # Check if there's a new completed collection
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT collection_id FROM collections 
                WHERE status='completed' 
                ORDER BY start_time DESC 
                LIMIT 1
            """)
            result = cursor.fetchone()
            conn.close()
            
            if result:
                collection_id = result['collection_id']
                
                # Only export if this is a new collection
                if collection_id != self.last_collection_id:
                    print(f"New collection detected: {collection_id}")
                    print("Starting automatic export...")
                    
                    export_result = self.exporter.export_latest_collection()
                    
                    if export_result:
                        self.last_collection_id = collection_id
                        self.last_export_time = now
                        print(f"✓ Automatic export completed for {collection_id}")
                    else:
                        print(f"✗ Export failed")
                else:
                    print(f"Collection {collection_id} already exported, skipping...")
            else:
                print("No completed collections found")
                
        except Exception as e:
            print(f"✗ Error checking database: {e}")


class DatabaseWatcher:
    """Watches database file for changes and triggers exports"""
    
    def __init__(self):
        self.base_dir = Path(BASE_DIR)
        self.db_path = Path(CAMERA_DB_PATH)
        self.exporter = WebAppExporter()
        self.observer = None
        self.is_running = False
        
    def start(self):
        """Start watching the database"""
        if self.is_running:
            print("Watcher is already running")
            return
        
        print(f"\n{'='*80}")
        print(f"QEW Camera Database Watcher")
        print(f"{'='*80}")
        print(f"Monitoring: {self.db_path.relative_to(self.base_dir)}")
        print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")
        
        # Create event handler
        event_handler = DatabaseChangeHandler(self.db_path, self.exporter)
        
        # Create observer
        self.observer = Observer()
        self.observer.schedule(
            event_handler,
            path=str(self.db_path.parent),
            recursive=False
        )
        
        # Start observer
        self.observer.start()
        self.is_running = True
        
        print("✓ Watcher started successfully")
        print("  Waiting for database changes...")
        print("  Press Ctrl+C to stop\n")
        
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """Stop watching the database"""
        if not self.is_running:
            return
        
        print("\n\nStopping watcher...")
        
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        self.is_running = False
        print("✓ Watcher stopped")
        print(f"Stopped: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    def export_now(self):
        """Manually trigger an export"""
        print("\nManual export triggered...")
        result = self.exporter.export_latest_collection()
        return result


if __name__ == '__main__':
    watcher = DatabaseWatcher()
    
    # Do an initial export
    print("Performing initial export...")
    watcher.export_now()
    
    # Start watching
    watcher.start()


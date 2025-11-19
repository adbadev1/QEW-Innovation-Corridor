"""
WebApp Exporter Service
Exports camera data from FastAPI backend database to public JSON for React app
Uses relative paths for portability
"""
import sqlite3
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from fastapi_backend.config import CAMERA_DB_PATH, BASE_DIR


class WebAppExporter:
    """Service to export camera data to web app public folder"""
    
    def __init__(self):
        self.base_dir = Path(BASE_DIR)
        self.db_path = Path(CAMERA_DB_PATH)
        self.public_dir = self.base_dir / 'public'
        self.backend_images_dir = self.base_dir / 'fastapi_backend' / 'database' / 'camera_images'
        
    def export_latest_collection(self) -> Optional[Dict]:
        """
        Export latest camera collection to public folder
        Returns dict with export info or None if no collections found
        """
        print(f"\n{'='*80}")
        print(f"QEW Camera Data Export for Web App")
        print(f"{'='*80}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Database: {self.db_path.relative_to(self.base_dir)}")
        print()
        
        # Connect to database
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get the latest completed collection
        cursor.execute("""
            SELECT * FROM collections 
            WHERE status='completed' 
            ORDER BY start_time DESC 
            LIMIT 1
        """)
        latest_collection = cursor.fetchone()
        
        if not latest_collection:
            print("✗ No completed collections found in database")
            conn.close()
            return None
        
        collection_id = latest_collection['collection_id']
        output_directory = latest_collection['output_directory']
        total_images = latest_collection['total_images']
        
        print(f"Latest collection: {collection_id}")
        print(f"Total images: {total_images}")
        print()
        
        # Step 1: Export camera metadata to JSON
        print("Step 1: Exporting camera metadata to JSON...")
        print(f"{'-'*80}")
        
        camera_data = self._build_camera_data(cursor, collection_id)
        
        # Save camera data JSON
        output_path = self.public_dir / 'camera_scraper' / 'qew_cameras_with_images.json'
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(camera_data, f, indent=2)
        
        print(f"✓ Exported {len(camera_data)} cameras to {output_path.relative_to(self.base_dir)}")
        
        # Step 2: Copy images to public folder
        print()
        print("Step 2: Copying images to public folder...")
        print(f"{'-'*80}")
        
        # Source is in fastapi_backend/database/camera_images/collection_id
        source_dir = self.backend_images_dir / collection_id
        dest_dir = self.public_dir / 'camera_images' / collection_id
        dest_dir.mkdir(parents=True, exist_ok=True)
        
        image_count = 0
        if source_dir.exists():
            image_files = list(source_dir.glob('*.jpg'))
            for img_file in image_files:
                shutil.copy2(img_file, dest_dir / img_file.name)
            image_count = len(image_files)
            print(f"✓ Copied {image_count} images to {dest_dir.relative_to(self.base_dir)}")
        else:
            print(f"✗ Source directory not found: {source_dir.relative_to(self.base_dir)}")
            conn.close()
            return None
        
        conn.close()
        
        print()
        print(f"{'='*80}")
        print("✓ Web app data export complete!")
        print(f"  Collection: {collection_id}")
        print(f"  Cameras: {len(camera_data)}")
        print(f"  Images: {image_count}")
        print(f"{'='*80}\n")
        
        return {
            'collection_id': collection_id,
            'cameras': len(camera_data),
            'images': image_count,
            'timestamp': datetime.now().isoformat()
        }
    
    def _build_camera_data(self, cursor, collection_id: str) -> List[Dict]:
        """Build camera data structure with images"""
        cursor.execute("SELECT * FROM cameras ORDER BY sort_order")
        cameras = cursor.fetchall()
        
        camera_data = []
        
        for camera in cameras:
            camera_id = camera['camera_id']
            
            # Get views for this camera
            cursor.execute("SELECT * FROM camera_views WHERE camera_id = ?", (camera_id,))
            views = cursor.fetchall()
            
            # Get images for this camera from the latest collection
            cursor.execute("""
                SELECT * FROM images
                WHERE camera_id = ? AND collection_id = ?
                ORDER BY view_id, timestamp DESC, capture_round DESC
            """, (camera_id, collection_id))
            images = cursor.fetchall()
            
            # Build view data with image paths (RELATIVE PATHS)
            view_data = []
            for view in views:
                view_id = view['view_id']
                view_images = [img for img in images if img['view_id'] == view_id]
                
                view_info = {
                    'Id': view_id,
                    'Url': view['url'],
                    'Status': view['status'],
                    'Description': view['description'],
                    'Images': [
                        {
                            'filename': img['filename'],
                            'path': f"camera_images/{collection_id}/{img['filename']}",  # Relative path
                            'timestamp': img['timestamp'],
                            'capture_round': img['capture_round']
                        }
                        for img in view_images
                    ]
                }
                view_data.append(view_info)
            
            # Build camera object
            camera_obj = {
                'Id': camera_id,
                'Source': camera['source'],
                'SourceId': camera['source_id'],
                'Roadway': camera['roadway'],
                'Direction': camera['direction'],
                'Latitude': camera['latitude'],
                'Longitude': camera['longitude'],
                'Location': camera['location'],
                'SortOrder': camera['sort_order'],
                'Views': view_data
            }
            camera_data.append(camera_obj)
        
        return camera_data


if __name__ == '__main__':
    exporter = WebAppExporter()
    result = exporter.export_latest_collection()
    
    if result:
        print(f"\n✓ Export successful!")
        print(f"  Collection ID: {result['collection_id']}")
        print(f"  Cameras: {result['cameras']}")
        print(f"  Images: {result['images']}")
    else:
        print(f"\n✗ Export failed - no collections found")


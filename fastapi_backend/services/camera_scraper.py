"""
Camera Scraper Service
Downloads images from MTO cameras along QEW corridor
"""
import requests
import json
import os
import time
from datetime import datetime
from typing import List, Dict, Callable, Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from fastapi_backend.database import CameraDatabase
from fastapi_backend.config import (
    CAMERA_JSON_PATH,
    CAMERA_IMAGES_DIR,
    IMAGES_PER_CAMERA,
    DELAY_BETWEEN_CAPTURES
)
from fastapi_backend.services.webapp_exporter import WebAppExporter


class CameraScraperService:
    """Service for scraping camera images"""

    def __init__(self, db: CameraDatabase = None, auto_export: bool = True):
        """Initialize camera scraper service

        Args:
            db: Database instance (creates new if None)
            auto_export: Automatically export to webapp after scraping completes
        """
        self.db = db or CameraDatabase()
        self.is_running = False
        self.current_status = "idle"
        self.progress_callback = None
        self.auto_export = auto_export
        self.exporter = WebAppExporter() if auto_export else None
        
    def load_camera_data(self, filename: str = None) -> List[Dict]:
        """Load camera data from JSON file"""
        if filename is None:
            filename = CAMERA_JSON_PATH
        with open(filename, 'r') as f:
            return json.load(f)
    
    def create_output_directory(self, base_dir: str = None) -> str:
        """Create directory for storing images"""
        if base_dir is None:
            base_dir = CAMERA_IMAGES_DIR
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(base_dir, f"qew_collection_{timestamp}")
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def download_image(self, url: str, output_path: str, timeout: int = 5) -> bool:
        """Download a single image from URL"""
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            
            # Check if response is actually an image
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type.lower():
                self.log(f"Warning: URL did not return an image (content-type: {content_type})")
                return False
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            return True
        except Exception as e:
            self.log(f"Error downloading {url}: {e}")
            return False
    
    def log(self, message: str):
        """Log message (can be overridden with callback)"""
        if self.progress_callback:
            self.progress_callback(message)
        else:
            print(message)
    
    def scrape_cameras(self, 
                      images_per_camera: int = None,
                      delay_between_captures: int = None,
                      progress_callback: Optional[Callable] = None) -> Dict:
        """
        Scrape images from all cameras
        
        Args:
            images_per_camera: Number of times to capture each camera view
            delay_between_captures: Seconds to wait between captures
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Dict with scraping results
        """
        if images_per_camera is None:
            images_per_camera = IMAGES_PER_CAMERA
        if delay_between_captures is None:
            delay_between_captures = DELAY_BETWEEN_CAPTURES
            
        self.progress_callback = progress_callback
        self.is_running = True
        self.current_status = "running"
        
        try:
            # Load camera data
            cameras = self.load_camera_data()
            
            # Load camera metadata into database
            self.db.load_cameras_from_json(cameras)
            
            # Create output directory
            output_dir = self.create_output_directory()
            
            # Create collection record
            collection_id = os.path.basename(output_dir)
            self.db.create_collection(collection_id, output_dir)
            
            total_images = 0
            failed_downloads = []  # Track failed downloads for retry

            self.log(f"Starting image collection...")
            self.log(f"Target: {len(cameras)} cameras x {images_per_camera} captures")
            self.log(f"Output directory: {output_dir}")
            self.log(f"Collection ID: {collection_id}")

            for capture_round in range(images_per_camera):
                self.log(f"\n{'='*80}")
                self.log(f"Capture Round {capture_round + 1} of {images_per_camera}")
                self.log(f"{'='*80}\n")
                
                for camera_idx, camera in enumerate(cameras, 1):
                    if not self.is_running:
                        self.log("Scraping stopped by user")
                        break
                        
                    camera_id = camera.get('Id')
                    location = camera.get('Location', 'Unknown')
                    latitude = camera.get('Latitude')
                    longitude = camera.get('Longitude')
                    views = camera.get('Views', [])
                    
                    self.log(f"[{camera_idx}/{len(cameras)}] Camera {camera_id}: {location}")

                    for view in views:
                        view_id = view.get('Id')
                        url = view.get('Url')
                        description = view.get('Description', 'Unknown view')

                        if not url:
                            self.log(f"  View {view_id}: No URL available")
                            continue

                        # Generate short filename
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = self.db.generate_short_filename(
                            camera_id, view_id, capture_round + 1, timestamp
                        )
                        output_path = os.path.join(output_dir, filename)

                        # Download image
                        self.log(f"  View {view_id} ({description}): Downloading...")
                        success = self.download_image(url, output_path)

                        if success:
                            # Save image record to database
                            image_data = {
                                'filename': filename,
                                'camera_id': camera_id,
                                'view_id': view_id,
                                'location': location,
                                'latitude': latitude,
                                'longitude': longitude,
                                'view_description': description,
                                'capture_round': capture_round + 1,
                                'timestamp': timestamp,
                                'url': url,
                                'collection_id': collection_id
                            }
                            self.db.insert_image(image_data)
                            total_images += 1
                            self.log(f"  ✓ Saved as {filename}")
                        else:
                            self.log(f"  ✗ Failed to download - URL: {url}")
                            # Track failed download for retry
                            failed_downloads.append({
                                'camera_id': camera_id,
                                'view_id': view_id,
                                'url': url,
                                'description': description,
                                'location': location,
                                'latitude': latitude,
                                'longitude': longitude,
                                'capture_round': capture_round + 1,
                                'output_dir': output_dir,
                                'collection_id': collection_id
                            })

                # Delay between capture rounds
                if capture_round < images_per_camera - 1 and self.is_running:
                    self.log(f"\nWaiting {delay_between_captures} seconds before next round...")
                    time.sleep(delay_between_captures)

            # Retry failed downloads once
            if failed_downloads and self.is_running:
                self.log(f"\n{'='*80}")
                self.log(f"Retrying Failed Downloads ({len(failed_downloads)} cameras)")
                self.log(f"{'='*80}\n")

                retry_success = 0
                for idx, failed in enumerate(failed_downloads, 1):
                    if not self.is_running:
                        self.log("Retry stopped by user")
                        break

                    self.log(f"[{idx}/{len(failed_downloads)}] Retry Camera {failed['camera_id']}: {failed['location']}")
                    self.log(f"  View {failed['view_id']} ({failed['description']}): Downloading...")
                    self.log(f"  URL: {failed['url']}")

                    # Generate new filename with current timestamp
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = self.db.generate_short_filename(
                        failed['camera_id'],
                        failed['view_id'],
                        failed['capture_round'],
                        timestamp
                    )
                    output_path = os.path.join(failed['output_dir'], filename)

                    # Retry download
                    success = self.download_image(failed['url'], output_path)

                    if success:
                        # Save image record to database
                        image_data = {
                            'filename': filename,
                            'camera_id': failed['camera_id'],
                            'view_id': failed['view_id'],
                            'location': failed['location'],
                            'latitude': failed['latitude'],
                            'longitude': failed['longitude'],
                            'view_description': failed['description'],
                            'capture_round': failed['capture_round'],
                            'timestamp': timestamp,
                            'url': failed['url'],
                            'collection_id': failed['collection_id']
                        }
                        self.db.insert_image(image_data)
                        total_images += 1
                        retry_success += 1
                        self.log(f"  ✓ Retry successful! Saved as {filename}")
                    else:
                        self.log(f"  ✗ Retry failed - URL: {failed['url']}")

                self.log(f"\nRetry complete: {retry_success}/{len(failed_downloads)} successful")

            # Complete collection
            self.db.complete_collection(collection_id, total_images)

            self.current_status = "completed"
            self.log(f"\n{'='*80}")
            self.log(f"Collection Complete!")
            self.log(f"Total images downloaded: {total_images}")
            if failed_downloads:
                final_failures = len(failed_downloads) - retry_success
                self.log(f"Failed downloads: {final_failures}")
            self.log(f"Collection ID: {collection_id}")
            self.log(f"{'='*80}")

            # Auto-export to webapp if enabled
            if self.auto_export and self.exporter:
                self.log(f"\n{'='*80}")
                self.log(f"Auto-Export to WebApp")
                self.log(f"{'='*80}")
                try:
                    export_result = self.exporter.export_latest_collection()
                    if export_result:
                        self.log(f"✓ WebApp data exported successfully!")
                        self.log(f"  Collection: {export_result['collection_id']}")
                        self.log(f"  Cameras: {export_result['cameras']}")
                        self.log(f"  Images: {export_result['images']}")
                    else:
                        self.log(f"✗ WebApp export failed - no collections found")
                except Exception as e:
                    self.log(f"✗ WebApp export error: {e}")
                self.log(f"{'='*80}\n")

            return {
                'status': 'success',
                'collection_id': collection_id,
                'total_images': total_images,
                'output_directory': output_dir
            }

        except Exception as e:
            self.current_status = "error"
            self.log(f"Error during scraping: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
        finally:
            self.is_running = False

    def stop_scraping(self):
        """Stop the scraping process"""
        self.is_running = False
        self.current_status = "stopped"

    def get_status(self) -> Dict:
        """Get current scraping status"""
        return {
            'is_running': self.is_running,
            'status': self.current_status
        }


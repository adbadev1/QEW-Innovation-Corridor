"""
Direction Analyzer Service
AI-powered camera direction assessment using Claude or Gemini
"""
import time
from typing import Dict, Optional, Callable, List
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from fastapi_backend.database import DirectionDatabase, CameraDatabase
from fastapi_backend.config import (
    CLAUDE_API_KEY,
    GEMINI_API_KEY,
    GOOGLE_MAPS_API_KEY,
    DEFAULT_AI_PLATFORM,
    DEFAULT_AI_MODEL
)
from .satellite_fetcher import SatelliteFetcher
from .camera_fetcher import CameraFetcher
from .claude_client import ClaudeDirectionAnalyzer
from .gemini_analyzer import GeminiDirectionAnalyzer


# Model name mappings
GEMINI_MODEL_MAP = {
    "Gemini 2.5 Pro": "gemini-2.5-pro",
    "Gemini 2.5 Flash": "gemini-2.5-flash",
    "Gemini 2.5 Flash Preview": "gemini-2.5-flash-preview",
    "Gemini 2.5 Flash-Lite": "gemini-2.5-flash-lite",
    "Gemini 2.5 Flash-Lite Preview": "gemini-2.5-flash-lite-preview",
    "Gemini 2.0 Flash": "gemini-2.0-flash",
    "Gemini 2.0 Flash-Lite": "gemini-2.0-flash-lite"
}

CLAUDE_MODEL_MAP = {
    "Claude 3.5 Sonnet": "claude-3-5-sonnet-20241022",
    "Claude 3 Opus": "claude-3-opus-20240229",
    "Claude 3 Haiku": "claude-3-haiku-20240307"
}


class DirectionAnalyzerService:
    """Service for AI-powered camera direction analysis"""

    def __init__(self,
                 direction_db: DirectionDatabase = None,
                 camera_db: CameraDatabase = None,
                 platform: str = None,
                 model: str = None,
                 api_key: str = None,
                 progress_callback: Optional[Callable] = None,
                 existing_images_folder: str = None):
        """Initialize direction analyzer service

        Args:
            existing_images_folder: Optional path to folder with existing images.
                                   If provided, will use existing images instead of downloading.
        """
        # Set progress callback FIRST before any log() calls
        self.progress_callback = progress_callback
        self.is_running = False
        self.current_status = "idle"

        self.direction_db = direction_db or DirectionDatabase()
        self.camera_db = camera_db or CameraDatabase()

        # Create timestamped folder for this analysis run
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        analysis_folder = f"data/images/analysis_{timestamp}"

        # If using existing images folder, use that instead
        if existing_images_folder:
            self.analysis_folder = existing_images_folder
            self.use_existing_images = True
            self.log(f"Using existing images from: {existing_images_folder}")
        else:
            self.analysis_folder = analysis_folder
            self.use_existing_images = False
            Path(self.analysis_folder).mkdir(parents=True, exist_ok=True)

        self.satellite_fetcher = SatelliteFetcher(base_output_dir=self.analysis_folder)
        self.camera_fetcher = CameraFetcher(base_output_dir=self.analysis_folder)

        # Set platform and model
        self.platform = platform or DEFAULT_AI_PLATFORM
        self.model = model or DEFAULT_AI_MODEL

        # Get API key
        if api_key is None:
            if self.platform == "Gemini":
                api_key = GEMINI_API_KEY
            else:
                api_key = CLAUDE_API_KEY

        # Initialize AI analyzer
        if self.platform == "Gemini":
            model_id = GEMINI_MODEL_MAP.get(self.model, "gemini-2.0-flash")
            self.analyzer = GeminiDirectionAnalyzer(api_key, model_id)
        else:  # Anthropic
            self.analyzer = ClaudeDirectionAnalyzer(api_key)
    
    def log(self, message: str):
        """Log message (can be overridden with callback)"""
        if self.progress_callback:
            self.progress_callback(message)
        else:
            print(message)

    def get_pending_count(self) -> int:
        """Get count of pending cameras"""
        pending = self.direction_db.get_pending_cameras()
        return len(pending)

    def stop_analysis(self):
        """Stop the analysis process"""
        self.is_running = False
        self.current_status = "stopped"
    
    def analyze_camera(self, 
                      camera_id: int,
                      view_id: int,
                      progress_callback: Optional[Callable] = None,
                      table_name: str = 'ai_direction_assessments') -> Dict:
        """
        Analyze direction for a single camera view
        
        Args:
            camera_id: Camera ID
            view_id: View ID
            progress_callback: Optional callback for progress updates
            table_name: Database table to store results in
            
        Returns:
            Dict with analysis results
        """
        self.progress_callback = progress_callback
        start_time = time.time()
        
        try:
            # Get camera info from database
            camera = self.camera_db.get_camera_by_id(camera_id)
            if not camera:
                raise ValueError(f"Camera {camera_id} not found in database")
            
            views = self.camera_db.get_camera_views(camera_id)
            view = next((v for v in views if v['view_id'] == view_id), None)
            if not view:
                raise ValueError(f"View {view_id} not found for camera {camera_id}")
            
            camera_info = {
                'camera_id': camera_id,
                'view_id': view_id,
                'location': camera['location'],
                'latitude': camera['latitude'],
                'longitude': camera['longitude'],
                'url': view['url'],
                'description': view['description']
            }

            # Log location details
            self.log(f"Coordinates: {camera['latitude']}, {camera['longitude']}")
            self.log(f"URL: {view['url']}")
            
            # Step 1: Get or fetch satellite image
            satellite_path = None
            if self.use_existing_images:
                # Look for existing satellite image
                # Check nested structure first
                nested_path = Path(self.analysis_folder) / f"cam{camera_id}_v{view_id}" / "satellite.jpg"
                if nested_path.exists():
                    satellite_path = str(nested_path)
                else:
                    # Check flat structure (any file starting with c{id}_v{view}_ and containing satellite)
                    # Note: camera_scraper usually doesn't download satellite images, so this might fail
                    # We'll check for it anyway
                    import glob
                    pattern = str(Path(self.analysis_folder) / f"c{camera_id}_v{view_id}_*_satellite.jpg")
                    matches = glob.glob(pattern)
                    if matches:
                        satellite_path = matches[0]
                
                if satellite_path:
                    self.log(f"Using existing satellite image: {satellite_path}")
                else:
                    self.log(f"Satellite image not found in existing folder, fetching from API...")
            
            # If not found in existing folder, fetch it
            if not satellite_path:
                if GOOGLE_MAPS_API_KEY:
                    satellite_path = self.satellite_fetcher.fetch_google_satellite(
                        camera['latitude'],
                        camera['longitude'],
                        camera_id,
                        view_id,
                        GOOGLE_MAPS_API_KEY
                    )
                else:
                    satellite_path = self.satellite_fetcher.fetch_satellite_image(
                        camera['latitude'],
                        camera['longitude'],
                        camera_id,
                        view_id
                    )
                self.log(f"Satellite image saved: {satellite_path}")

            # Step 2: Get or fetch camera image
            camera_image_path = None
            if self.use_existing_images:
                # Look for existing camera image
                # Check nested structure first
                nested_path = Path(self.analysis_folder) / f"cam{camera_id}_v{view_id}" / "camera.jpg"
                if nested_path.exists():
                    camera_image_path = str(nested_path)
                else:
                    # Check flat structure (c{id}_v{view}_*.jpg)
                    import glob
                    pattern = str(Path(self.analysis_folder) / f"c{camera_id}_v{view_id}_*.jpg")
                    matches = glob.glob(pattern)
                    # Filter out satellite images if they match the pattern
                    matches = [m for m in matches if "satellite" not in m]
                    
                    if matches:
                        # Use the most recent one if multiple exist
                        camera_image_path = matches[-1]
                
                if not camera_image_path:
                    raise FileNotFoundError(f"Camera image not found for Camera {camera_id} View {view_id} in {self.analysis_folder}")
                self.log(f"Using existing camera image: {camera_image_path}")
            else:
                self.log(f"Fetching camera image...")
                camera_image_path = self.camera_fetcher.fetch_camera_image(
                    view['url'],
                    camera_id,
                    view_id
                )
                self.log(f"Camera image saved: {camera_image_path}")

            # Step 3: Analyze with AI
            self.log(f"Analyzing direction with {self.platform} ({self.model})...")
            result = self.analyzer.analyze_direction(
                satellite_path,
                camera_image_path,
                camera_info
            )

            # Step 4: Save to database
            assessment = {
                'camera_id': camera_id,
                'view_id': view_id,
                'location': camera['location'],
                'latitude': camera['latitude'],
                'longitude': camera['longitude'],
                'camera_url': view['url'],
                'satellite_image_path': satellite_path,
                'camera_image_path': camera_image_path,
                'direction': result.get('direction'),
                'confidence_score': result.get('confidence'),
                'compass_direction_8': result.get('direction'),
                'compass_direction_16': result.get('direction_16'),
                'heading_degrees': result.get('heading_degrees'),
                'lanes_detected': result.get('lanes_detected'),
                'road_features': result.get('road_features'),
                'lane_counts': result.get('lane_counts'),
                'landmarks_identified': result.get('landmarks'),
                'reasoning': result.get('reasoning'),
                'satellite_analysis': result.get('satellite_features'),
                'camera_analysis': result.get('camera_features'),
                'landmark_matches': result.get('matches'),
                'ai_model': f"{self.platform} - {self.model}",
                'processing_time_seconds': time.time() - start_time,
                'status': 'completed'
            }

            self.direction_db.insert_assessment(assessment, table_name=table_name)

            processing_time = time.time() - start_time
            self.log(f"✓ Analysis complete in {processing_time:.2f}s")
            self.log(f"Direction: {result.get('direction')} ({result.get('heading_degrees')}°)")
            if result.get('lanes_detected'):
                self.log(f"Lanes: {result.get('lanes_detected')}")

            return {
                'status': 'success',
                'camera_id': camera_id,
                'view_id': view_id,
                'result': result,
                'satellite_image_path': satellite_path,
                'camera_image_path': camera_image_path,
                'processing_time': processing_time,
                'latitude': camera['latitude'],
                'longitude': camera['longitude'],
                'camera_url': view['url']
            }

        except Exception as e:
            error_msg = str(e)
            self.log(f"✗ Error analyzing camera: {error_msg}")

            # Log stack trace for debugging
            import traceback
            self.log(traceback.format_exc())

            return {
                'status': 'error',
                'camera_id': camera_id,
                'view_id': view_id,
                'error': error_msg
            }

    def analyze_pending_cameras(self,
                               platform: str = None,
                               model: str = None,
                               progress_callback: Optional[Callable] = None,
                               result_callback: Optional[Callable] = None) -> Dict:
        """
        Analyze all cameras that haven't been assessed yet

        Args:
            platform: AI platform to use (optional, uses instance default if not specified)
            model: Model to use (optional, uses instance default if not specified)
            progress_callback: Optional callback for progress updates
            result_callback: Optional callback for individual camera results

        Returns:
            Dict with batch analysis results
        """
        # Update platform/model if provided
        if platform:
            self.platform = platform
        if model:
            self.model = model

        self.progress_callback = progress_callback or self.progress_callback
        self.is_running = True
        self.current_status = "running"

        try:
            # Get pending cameras
            pending = self.direction_db.get_pending_cameras()

            if len(pending) == 0:
                self.log("No pending cameras to analyze")
                return {
                    'status': 'success',
                    'total': 0,
                    'successful': 0,
                    'failed': 0,
                    'processed': 0,
                    'results': []
                }

            self.log(f"Found {len(pending)} cameras pending analysis")
            
            # Create a new table for this run
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            table_name = f"run_{timestamp}"
            self.log(f"Creating new database table for this run: {table_name}")
            self.direction_db.create_run_table(table_name)

            results = []
            for idx, camera in enumerate(pending, 1):
                if not self.is_running:
                    self.log("Analysis stopped by user")
                    break

                self.log(f"\n[{idx}/{len(pending)}] Processing Camera {camera['camera_id']}, View {camera['view_id']}")
                self.log(f"Location: {camera.get('location', 'Unknown')}")

                result = self.analyze_camera(
                    camera['camera_id'],
                    camera['view_id'],
                    progress_callback,
                    table_name=table_name
                )
                results.append(result)
                
                # Emit result via callback if provided
                if result_callback:
                    result_callback(result)

                # Log result status
                if result['status'] == 'error':
                    self.log(f"✗ Failed: {result.get('error', 'Unknown error')}")
                else:
                    self.log(f"✓ Success")

            self.current_status = "completed"
            successful = sum(1 for r in results if r['status'] == 'success')

            self.log(f"\nBatch analysis complete: {successful}/{len(results)} successful")

            return {
                'status': 'success',
                'total': len(results),
                'successful': successful,
                'failed': len(results) - successful,
                'processed': len(results),
                'results': results
            }

        except Exception as e:
            self.current_status = "error"
            self.log(f"Error during batch analysis: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
        finally:
            self.is_running = False

    def stop_analysis(self):
        """Stop the analysis process"""
        self.is_running = False
        self.current_status = "stopped"

    def get_status(self) -> Dict:
        """Get current analysis status"""
        return {
            'is_running': self.is_running,
            'status': self.current_status,
            'platform': self.platform,
            'model': self.model
        }

    def get_pending_count(self) -> int:
        """Get count of pending cameras"""
        pending = self.direction_db.get_pending_cameras()
        return len(pending)


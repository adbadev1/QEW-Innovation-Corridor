"""
Main Processing Engine
Coordinates satellite fetching, camera fetching, and AI analysis
"""
import time
from typing import Dict, Optional, Callable
from .database import DirectionDatabase
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


class DirectionProcessor:
    """Main processor for camera direction assessment"""

    def __init__(self, api_key: str, source_db_path: str,
                 google_maps_api_key: Optional[str] = None,
                 platform: str = "Gemini",
                 model: str = "Gemini 2.0 Flash"):
        """
        Initialize processor

        Args:
            api_key: API key (Claude or Gemini)
            source_db_path: Path to source camera database
            google_maps_api_key: Optional Google Maps API key for better satellite images
            platform: AI platform ("Gemini" or "Anthropic")
            model: Model name
        """
        # Don't create DB connection here - will create per thread
        self.db = None
        self.satellite_fetcher = SatelliteFetcher()
        self.camera_fetcher = CameraFetcher()

        # Initialize AI analyzer based on platform
        self.platform = platform
        self.model = model

        if platform == "Gemini":
            model_id = GEMINI_MODEL_MAP.get(model, "gemini-2.0-flash")
            self.analyzer = GeminiDirectionAnalyzer(api_key, model_id)
        else:  # Anthropic
            self.analyzer = ClaudeDirectionAnalyzer(api_key)

        self.source_db_path = source_db_path
        self.google_maps_api_key = google_maps_api_key

    def _get_db(self):
        """Get or create database connection for current thread"""
        if self.db is None:
            self.db = DirectionDatabase()
        return self.db
    
    def process_camera(self, camera_info: Dict, 
                      progress_callback: Optional[Callable] = None) -> Dict:
        """
        Process a single camera view
        
        Args:
            camera_info: Dict with camera_id, view_id, location, latitude, longitude, url
            progress_callback: Optional callback function for progress updates
        
        Returns:
            Assessment results dict
        """
        camera_id = camera_info['camera_id']
        view_id = camera_info['view_id']
        
        start_time = time.time()
        
        try:
            # Step 1: Fetch satellite image
            if progress_callback:
                progress_callback(f"Fetching satellite image for Camera {camera_id}, View {view_id}...")
            
            if self.google_maps_api_key:
                satellite_path = self.satellite_fetcher.fetch_google_satellite(
                    camera_info['latitude'],
                    camera_info['longitude'],
                    camera_id,
                    view_id,
                    self.google_maps_api_key
                )
            else:
                satellite_path = self.satellite_fetcher.fetch_satellite_image(
                    camera_info['latitude'],
                    camera_info['longitude'],
                    camera_id,
                    view_id
                )
            
            # Step 2: Fetch camera image
            if progress_callback:
                progress_callback(f"Fetching camera image for Camera {camera_id}, View {view_id}...")
            
            camera_path = self.camera_fetcher.fetch_camera_image(view_id, camera_id)
            
            # Step 3: Analyze with AI
            if progress_callback:
                progress_callback(f"Analyzing direction with AI for Camera {camera_id}, View {view_id}...")

            # Use appropriate analyzer based on platform
            if self.platform == "Gemini":
                analysis = self.analyzer.analyze_direction(satellite_path, camera_path)
            else:  # Anthropic
                analysis = self.analyzer.analyze_direction(satellite_path, camera_path, camera_info)
            
            # Step 4: Prepare assessment data
            processing_time = time.time() - start_time
            
            assessment = {
                'camera_id': camera_id,
                'view_id': view_id,
                'location': camera_info.get('location'),
                'latitude': camera_info.get('latitude'),
                'longitude': camera_info.get('longitude'),
                'camera_url': camera_info.get('url'),
                'satellite_image_path': satellite_path,
                'camera_image_path': camera_path,
                'direction': analysis.get('direction', 'UNKNOWN'),
                'confidence_score': analysis.get('confidence_score'),
                'compass_direction_8': analysis.get('compass_direction_8'),
                'compass_direction_16': analysis.get('compass_direction_16'),
                'heading_degrees': analysis.get('heading_degrees'),
                'landmarks_identified': analysis.get('landmarks_identified'),
                'reasoning': analysis.get('reasoning'),
                'satellite_analysis': analysis.get('satellite_analysis'),
                'camera_analysis': analysis.get('camera_analysis'),
                'landmark_matches': analysis.get('landmark_matches'),
                'ai_model': analysis.get('ai_model'),
                'processing_time_seconds': processing_time,
                'status': 'completed'
            }
            
            # Step 5: Save to database
            db = self._get_db()
            db.insert_assessment(assessment)
            
            if progress_callback:
                progress_callback(f"✓ Completed Camera {camera_id}, View {view_id}: Direction = {assessment['direction']}")
            
            return assessment
        
        except Exception as e:
            # Handle errors
            processing_time = time.time() - start_time
            
            error_assessment = {
                'camera_id': camera_id,
                'view_id': view_id,
                'location': camera_info.get('location'),
                'latitude': camera_info.get('latitude'),
                'longitude': camera_info.get('longitude'),
                'camera_url': camera_info.get('url'),
                'direction': 'ERROR',
                'processing_time_seconds': processing_time,
                'status': 'failed',
                'error_message': str(e)
            }
            
            db = self._get_db()
            db.insert_assessment(error_assessment)
            
            if progress_callback:
                progress_callback(f"✗ Error processing Camera {camera_id}, View {view_id}: {e}")
            
            return error_assessment
    
    def get_pending_cameras(self) -> list:
        """Get list of cameras that haven't been assessed yet"""
        db = self._get_db()
        return db.get_pending_cameras(self.source_db_path)
    
    def close(self):
        """Close database connection"""
        self.db.close()


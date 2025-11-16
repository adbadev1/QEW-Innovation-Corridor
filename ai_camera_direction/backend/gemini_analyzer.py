"""
Gemini Direction Analyzer
Uses Google Gemini API to analyze camera direction from images
"""
import google.generativeai as genai
import base64
from typing import Dict, Optional
import time


# Gemini model configurations with rate limits
GEMINI_MODELS = {
    "gemini-2.5-pro": {
        "name": "gemini-2.5-pro",
        "rpm": 2,
        "tpm": 125000,
        "rpd": 50
    },
    "gemini-2.5-flash": {
        "name": "gemini-2.5-flash",
        "rpm": 10,
        "tpm": 250000,
        "rpd": 250
    },
    "gemini-2.5-flash-preview": {
        "name": "gemini-2.5-flash-preview",
        "rpm": 10,
        "tpm": 250000,
        "rpd": 250
    },
    "gemini-2.5-flash-lite": {
        "name": "gemini-2.5-flash-lite",
        "rpm": 15,
        "tpm": 250000,
        "rpd": 1000
    },
    "gemini-2.5-flash-lite-preview": {
        "name": "gemini-2.5-flash-lite-preview",
        "rpm": 15,
        "tpm": 250000,
        "rpd": 1000
    },
    "gemini-2.0-flash": {
        "name": "gemini-2.0-flash",
        "rpm": 15,
        "tpm": 1000000,
        "rpd": 200
    },
    "gemini-2.0-flash-lite": {
        "name": "gemini-2.0-flash-lite",
        "rpm": 30,
        "tpm": 1000000,
        "rpd": 200
    }
}


class GeminiDirectionAnalyzer:
    """Analyzes camera direction using Google Gemini"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash"):
        """
        Initialize Gemini analyzer
        
        Args:
            api_key: Gemini API key
            model_name: Model to use (default: gemini-2.0-flash)
        """
        genai.configure(api_key=api_key)
        
        if model_name not in GEMINI_MODELS:
            raise ValueError(f"Invalid model: {model_name}. Must be one of {list(GEMINI_MODELS.keys())}")
        
        self.model_name = model_name
        self.model_config = GEMINI_MODELS[model_name]
        self.model = genai.GenerativeModel(model_name)
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 60.0 / self.model_config['rpm']  # seconds between requests
    
    def analyze_direction(self, satellite_image_path: str, camera_image_path: str) -> Dict:
        """
        Analyze camera direction from satellite and camera images
        
        Args:
            satellite_image_path: Path to satellite image
            camera_image_path: Path to camera image
            
        Returns:
            Dictionary with direction analysis
        """
        # Rate limiting
        self._wait_for_rate_limit()
        
        # Prepare prompt
        prompt = self._create_prompt()
        
        # Load images
        satellite_image = self._load_image(satellite_image_path)
        camera_image = self._load_image(camera_image_path)
        
        # Generate response
        response = self.model.generate_content([
            prompt,
            satellite_image,
            camera_image
        ])
        
        # Parse response
        return self._parse_response(response.text)
    
    def _wait_for_rate_limit(self):
        """Wait to respect rate limits"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def _load_image(self, image_path: str):
        """Load image for Gemini"""
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        return {
            'mime_type': 'image/jpeg',
            'data': image_data
        }
    
    def _create_prompt(self) -> str:
        """Create analysis prompt"""
        return """You are analyzing a traffic camera's direction.

You will be shown two images:
1. A satellite/aerial view of the camera location
2. The actual camera view

Your task is to determine which compass direction the camera is facing.

Analyze the images and provide your assessment in this EXACT format:

DIRECTION: [One of: N, NNE, NE, ENE, E, ESE, SE, SSE, S, SSW, SW, WSW, W, WNW, NW, NNW]
HEADING: [Degrees 0-360, where 0=North, 90=East, 180=South, 270=West]
CONFIDENCE: [0.0-1.0]
LANDMARKS: [Brief description of visible landmarks]
REASONING: [Brief explanation of how you determined the direction]

Be precise and use the 16-point compass system."""
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse Gemini response"""
        lines = response_text.strip().split('\n')
        result = {
            'direction': 'UNKNOWN',
            'heading_degrees': 0,
            'confidence_score': 0.0,
            'landmarks_identified': '',
            'reasoning': ''
        }
        
        for line in lines:
            line = line.strip()
            if line.startswith('DIRECTION:'):
                result['direction'] = line.split(':', 1)[1].strip()
            elif line.startswith('HEADING:'):
                try:
                    result['heading_degrees'] = int(line.split(':', 1)[1].strip())
                except:
                    pass
            elif line.startswith('CONFIDENCE:'):
                try:
                    result['confidence_score'] = float(line.split(':', 1)[1].strip())
                except:
                    pass
            elif line.startswith('LANDMARKS:'):
                result['landmarks_identified'] = line.split(':', 1)[1].strip()
            elif line.startswith('REASONING:'):
                result['reasoning'] = line.split(':', 1)[1].strip()
        
        return result


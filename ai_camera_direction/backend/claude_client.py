"""
Claude API Client for Camera Direction Assessment
Uses TOON format for efficient token usage
"""
import anthropic
import base64
import os
from typing import Dict, Tuple
from pathlib import Path


class ClaudeDirectionAnalyzer:
    """Claude API client for analyzing camera directions"""
    
    def __init__(self, api_key: str):
        """Initialize Claude client"""
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
    
    def encode_image(self, image_path: str) -> Tuple[str, str]:
        """Encode image to base64"""
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # Determine media type
        ext = Path(image_path).suffix.lower()
        media_type_map = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        media_type = media_type_map.get(ext, 'image/jpeg')
        
        return base64.standard_b64encode(image_data).decode('utf-8'), media_type
    
    def analyze_direction(self, satellite_image_path: str, camera_image_path: str, 
                         camera_info: Dict) -> Dict:
        """
        Analyze camera direction using satellite and camera images
        
        Args:
            satellite_image_path: Path to satellite image (north-oriented)
            camera_image_path: Path to camera image
            camera_info: Dict with camera_id, view_id, location, latitude, longitude
        
        Returns:
            Dict with direction analysis results
        """
        # Encode images
        sat_b64, sat_media = self.encode_image(satellite_image_path)
        cam_b64, cam_media = self.encode_image(camera_image_path)
        
        # Create TOON-optimized prompt
        prompt = f"""TASK: Determine camera direction from satellite+camera images.

SATELLITE IMAGE: North-oriented aerial view at {camera_info['latitude']}, {camera_info['longitude']}
CAMERA IMAGE: Ground-level view from same location

INSTRUCTIONS:
1. Analyze satellite image - identify landmarks (roads, buildings, water, bridges, signs)
2. Analyze camera image - identify same landmarks
3. Match landmarks between images
4. Determine camera heading using north orientation from satellite

OUTPUT FORMAT (TOON):
direction: [N/NE/E/SE/S/SW/W/NW]
heading_degrees: [0-360]
confidence: [0.0-1.0]
landmarks: [comma-separated list]
reasoning: [brief explanation]
satellite_features: [what you see in satellite]
camera_features: [what you see in camera]
matches: [which landmarks match]

RULES:
- Direction must be ONE of: N, NE, E, SE, S, SW, W, NW
- Heading: 0=N, 45=NE, 90=E, 135=SE, 180=S, 225=SW, 270=W, 315=NW
- Be precise and confident
- Focus on distinctive landmarks
- Consider highway direction if visible

Location: {camera_info.get('location', 'Unknown')}"""

        # Call Claude API
        message = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": sat_media,
                                "data": sat_b64
                            }
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": cam_media,
                                "data": cam_b64
                            }
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        
        # Parse TOON response
        response_text = message.content[0].text
        result = self.parse_toon_response(response_text)
        
        # Add metadata
        result['ai_model'] = self.model
        result['input_tokens'] = message.usage.input_tokens
        result['output_tokens'] = message.usage.output_tokens
        
        return result
    
    def parse_toon_response(self, response: str) -> Dict:
        """Parse TOON-formatted response"""
        result = {}
        lines = response.strip().split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower().replace(' ', '_')
                value = value.strip()
                
                if key == 'direction':
                    result['direction'] = value
                    result['compass_direction_8'] = value
                    # Convert to 16-point if needed
                    result['compass_direction_16'] = value
                elif key == 'heading_degrees':
                    try:
                        result['heading_degrees'] = float(value)
                    except:
                        result['heading_degrees'] = None
                elif key == 'confidence':
                    try:
                        result['confidence_score'] = float(value)
                    except:
                        result['confidence_score'] = 0.5
                elif key == 'landmarks':
                    result['landmarks_identified'] = value
                elif key == 'reasoning':
                    result['reasoning'] = value
                elif key == 'satellite_features':
                    result['satellite_analysis'] = value
                elif key == 'camera_features':
                    result['camera_analysis'] = value
                elif key == 'matches':
                    result['landmark_matches'] = value
        
        return result


"""
Camera Image Fetcher
Downloads camera images from MTO 511 API
"""
import requests
from pathlib import Path
import time


class CameraFetcher:
    """Fetches camera images from MTO 511"""

    def __init__(self, base_output_dir: str = 'data/images'):
        """Initialize camera fetcher"""
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "https://511on.ca/map/Cctv"

    def fetch_camera_image(self, url: str, camera_id: int, view_id: int,
                          max_retries: int = 3) -> str:
        """
        Fetch camera image from URL

        Args:
            url: Full URL to camera image
            camera_id: Camera ID for filename
            view_id: View ID for filename
            max_retries: Maximum number of retry attempts

        Returns:
            Path to saved camera image
        """
        # Create individual folder for this camera
        camera_folder = self.base_output_dir / f"cam{camera_id}_v{view_id}"
        camera_folder.mkdir(parents=True, exist_ok=True)

        filename = "camera.jpg"
        output_path = camera_folder / filename

        # Check if already exists
        if output_path.exists():
            return str(output_path)

        # Use provided URL
        image_url = url
        
        # Try to fetch image
        for attempt in range(max_retries):
            try:
                response = requests.get(image_url, timeout=30, headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                })
                response.raise_for_status()
                
                # Check if we got an image
                content_type = response.headers.get('Content-Type', '')
                if 'image' not in content_type:
                    # Try alternative URL format
                    alt_url = f"https://511on.ca/map/Cctv/{view_id}/image"
                    response = requests.get(alt_url, timeout=30, headers={
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                    response.raise_for_status()
                
                # Save image
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                return str(output_path)
            
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)  # Wait before retry
                    continue
                else:
                    raise Exception(f"Failed to fetch camera image after {max_retries} attempts: {e}")
        
        return str(output_path)
    
    def fetch_from_url(self, url: str, camera_id: int, view_id: int) -> str:
        """
        Fetch camera image from custom URL
        
        Args:
            url: Full URL to camera image
            camera_id: Camera ID for filename
            view_id: View ID for filename
        
        Returns:
            Path to saved image
        """
        filename = f"camera_cam{camera_id}_view{view_id}.jpg"
        output_path = self.output_dir / filename
        
        if output_path.exists():
            return str(output_path)
        
        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return str(output_path)


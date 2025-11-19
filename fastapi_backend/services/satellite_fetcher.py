"""
Satellite Image Fetcher
Downloads satellite imagery from Google Maps Static API or similar services
"""
import requests
from pathlib import Path
from typing import Tuple


class SatelliteFetcher:
    """Fetches satellite imagery for camera locations"""

    def __init__(self, base_output_dir: str = 'data/images'):
        """Initialize satellite fetcher"""
        self.base_output_dir = Path(base_output_dir)
        self.base_output_dir.mkdir(parents=True, exist_ok=True)

    def fetch_satellite_image(self, latitude: float, longitude: float,
                             camera_id: int, view_id: int,
                             zoom: int = 18, size: str = "640x640") -> str:
        """
        Fetch satellite image for given coordinates

        Uses Google Maps Static API (requires API key) or OpenStreetMap
        For now, using a free alternative: Mapbox Static Images API

        Args:
            latitude: Camera latitude
            longitude: Camera longitude
            camera_id: Camera ID for filename
            view_id: View ID for filename
            zoom: Zoom level (higher = more detail)
            size: Image size

        Returns:
            Path to saved satellite image
        """
        # Create individual folder for this camera
        camera_folder = self.base_output_dir / f"cam{camera_id}_v{view_id}"
        camera_folder.mkdir(parents=True, exist_ok=True)

        # Filename
        filename = "satellite.jpg"
        output_path = camera_folder / filename

        # Check if already exists
        if output_path.exists():
            return str(output_path)
        
        # Using OpenStreetMap Static Map API (free, no key required)
        # Alternative: Use Google Maps Static API with your API key
        
        # Method 1: Using staticmap.openstreetmap.de (free)
        url = f"https://staticmap.openstreetmap.de/staticmap.php"
        params = {
            'center': f"{latitude},{longitude}",
            'zoom': zoom,
            'size': size,
            'maptype': 'mapnik',
            'markers': f"{latitude},{longitude},red"
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            return str(output_path)
        
        except Exception as e:
            # Fallback: Try alternative service
            return self._fetch_alternative(latitude, longitude, camera_id, view_id, zoom, size)
    
    def _fetch_alternative(self, latitude: float, longitude: float,
                          camera_id: int, view_id: int,
                          zoom: int, size: str) -> str:
        """
        Alternative satellite image fetcher using different service
        """
        # Create individual folder for this camera
        camera_folder = self.base_output_dir / f"cam{camera_id}_v{view_id}"
        camera_folder.mkdir(parents=True, exist_ok=True)

        filename = "satellite.jpg"
        output_path = camera_folder / filename
        
        # Using MapQuest Open Static Map API (free tier available)
        # Or use a placeholder for now
        
        # For development: Create a placeholder
        # In production, you should use Google Maps Static API with your key
        
        # Google Maps Static API format (requires API key):
        # url = f"https://maps.googleapis.com/maps/api/staticmap"
        # params = {
        #     'center': f"{latitude},{longitude}",
        #     'zoom': zoom,
        #     'size': size,
        #     'maptype': 'satellite',
        #     'markers': f"color:red|{latitude},{longitude}",
        #     'key': 'YOUR_GOOGLE_MAPS_API_KEY'
        # }
        
        # For now, using a simple tile-based approach
        width, height = map(int, size.split('x'))
        
        # Calculate tile coordinates
        tile_x, tile_y = self._lat_lon_to_tile(latitude, longitude, zoom)
        
        # Fetch tile from OpenStreetMap
        tile_url = f"https://tile.openstreetmap.org/{zoom}/{tile_x}/{tile_y}.png"
        
        try:
            response = requests.get(tile_url, timeout=30, headers={
                'User-Agent': 'QEW-Camera-Direction-Analyzer/1.0'
            })
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            return str(output_path)
        
        except Exception as e:
            raise Exception(f"Failed to fetch satellite image: {e}")
    
    def _lat_lon_to_tile(self, lat: float, lon: float, zoom: int) -> Tuple[int, int]:
        """Convert lat/lon to tile coordinates"""
        import math
        
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        x = int((lon + 180.0) / 360.0 * n)
        y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
        
        return x, y
    
    def fetch_google_satellite(self, latitude: float, longitude: float,
                              camera_id: int, view_id: int,
                              api_key: str, zoom: int = 18) -> str:
        """
        Fetch satellite image using Google Maps Static API

        Args:
            latitude: Camera latitude
            longitude: Camera longitude
            camera_id: Camera ID
            view_id: View ID
            api_key: Google Maps API key
            zoom: Zoom level

        Returns:
            Path to saved image
        """
        # Create individual folder for this camera
        camera_folder = self.base_output_dir / f"cam{camera_id}_v{view_id}"
        camera_folder.mkdir(parents=True, exist_ok=True)

        filename = "satellite.jpg"
        output_path = camera_folder / filename

        if output_path.exists():
            return str(output_path)
        
        url = "https://maps.googleapis.com/maps/api/staticmap"
        params = {
            'center': f"{latitude},{longitude}",
            'zoom': zoom,
            'size': '640x640',
            'maptype': 'satellite',
            'markers': f"color:red|{latitude},{longitude}",
            'key': api_key
        }
        
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return str(output_path)


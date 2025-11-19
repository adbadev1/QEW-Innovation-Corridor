"""
Camera Direction API Router
Provides camera direction data from AI assessments for visualization
"""
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
import sqlite3
from pathlib import Path
from collections import defaultdict

router = APIRouter(prefix="/api/camera-directions", tags=["camera-directions"])

# Database path
BASE_DIR = Path(__file__).parent.parent
DIRECTIONS_DB_PATH = BASE_DIR / "database" / "camera_directions.db"


def get_camera_directions() -> List[Dict[str, Any]]:
    """
    Get camera direction data from the latest assessment run.
    Groups cameras by location (lat/lon) and includes all viewing directions.
    """
    if not DIRECTIONS_DB_PATH.exists():
        raise HTTPException(status_code=404, detail="Camera directions database not found")
    
    conn = sqlite3.connect(str(DIRECTIONS_DB_PATH))
    cursor = conn.cursor()
    
    # Get the latest run table (most recent assessment)
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name LIKE 'run_%'
        ORDER BY name DESC
        LIMIT 1
    """)
    
    result = cursor.fetchone()
    if not result:
        conn.close()
        raise HTTPException(status_code=404, detail="No assessment runs found in database")
    
    table_name = result[0]
    
    # Query all camera directions from the latest run
    cursor.execute(f"""
        SELECT 
            camera_id,
            view_id,
            location,
            latitude,
            longitude,
            compass_direction_8,
            heading_degrees,
            lanes_detected,
            road_features
        FROM {table_name}
        WHERE status = 'completed'
        ORDER BY latitude, longitude, camera_id
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    # Group by location (lat/lon)
    location_groups = defaultdict(list)
    
    for row in rows:
        camera_id, view_id, location, lat, lon, direction, heading, lanes, features = row
        
        # Use lat/lon as key (rounded to 6 decimals for grouping)
        key = (round(lat, 6), round(lon, 6))
        
        location_groups[key].append({
            'cameraId': camera_id,
            'viewId': view_id,
            'direction': direction,
            'heading': heading if heading is not None else 0,
            'lanes': lanes,
            'features': features
        })
    
    # Convert to output format
    output = []
    for (lat, lon), cameras in location_groups.items():
        # Get location name from first camera
        location_name = None
        for row in rows:
            if round(row[3], 6) == lat and round(row[4], 6) == lon:
                location_name = row[2]
                break
        
        output.append({
            'location': location_name or 'Unknown',
            'latitude': lat,
            'longitude': lon,
            'cameras': cameras
        })
    
    return output


@router.get("/", response_model=List[Dict[str, Any]])
async def get_all_camera_directions():
    """
    Get all camera directions for map visualization.
    
    Returns:
        List of camera locations with their viewing directions
        
    Example response:
    [
        {
            "location": "QEW at Burlington Skyway",
            "latitude": 43.30917,
            "longitude": -79.803,
            "cameras": [
                {
                    "cameraId": 4,
                    "viewId": 10,
                    "direction": "N",
                    "heading": 360.0,
                    "lanes": "Northbound",
                    "features": "Bridge"
                },
                {
                    "cameraId": 4,
                    "viewId": 11,
                    "direction": "NW",
                    "heading": 315.0,
                    "lanes": "Northbound",
                    "features": "Highway"
                }
            ]
        }
    ]
    """
    try:
        return get_camera_directions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching camera directions: {str(e)}")


@router.get("/stats")
async def get_camera_direction_stats():
    """
    Get statistics about camera directions.
    
    Returns:
        Statistics including total locations, total cameras, direction distribution
    """
    try:
        directions_data = get_camera_directions()
        
        total_locations = len(directions_data)
        total_cameras = sum(len(loc['cameras']) for loc in directions_data)
        
        # Count direction distribution
        direction_counts = defaultdict(int)
        for loc in directions_data:
            for cam in loc['cameras']:
                direction_counts[cam['direction']] += 1
        
        return {
            'totalLocations': total_locations,
            'totalCameras': total_cameras,
            'directionDistribution': dict(direction_counts),
            'multiCameraLocations': sum(1 for loc in directions_data if len(loc['cameras']) > 1)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")


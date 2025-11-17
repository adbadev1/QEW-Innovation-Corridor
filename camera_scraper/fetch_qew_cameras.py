"""
Script to fetch MTO camera data for QEW corridor between Hamilton and Mississauga
"""
import requests
import json
from typing import List, Dict

def fetch_all_cameras() -> List[Dict]:
    """Fetch all cameras from Ontario 511 API"""
    url = "https://511on.ca/api/v2/get/cameras?format=json"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def filter_qew_cameras(cameras: List[Dict]) -> List[Dict]:
    """Filter cameras for QEW highway"""
    return [c for c in cameras if 'QEW' in c.get('Roadway', '')]

def filter_hamilton_mississauga_corridor(cameras: List[Dict]) -> List[Dict]:
    """
    Filter cameras between Hamilton and Mississauga based on GPS coordinates
    
    Approximate boundaries:
    - Hamilton (west): Latitude ~43.25, Longitude ~-79.87
    - Mississauga (east): Latitude ~43.59, Longitude ~-79.64
    - QEW runs roughly east-west in this region
    """
    filtered = []
    for camera in cameras:
        lat = camera.get('Latitude')
        lon = camera.get('Longitude')
        
        if lat is None or lon is None:
            continue
            
        # QEW corridor between Hamilton and Mississauga
        # Longitude range: -79.87 (Hamilton) to -79.64 (Mississauga)
        # Latitude range: 43.2 to 43.65 (covers the corridor)
        if -79.90 <= lon <= -79.60 and 43.2 <= lat <= 43.65:
            filtered.append(camera)
    
    return filtered

def save_camera_data(cameras: List[Dict], filename: str = "qew_cameras.json"):
    """Save camera data to JSON file"""
    with open(filename, 'w') as f:
        json.dump(cameras, f, indent=2)
    print(f"Saved {len(cameras)} cameras to {filename}")

def print_camera_summary(cameras: List[Dict]):
    """Print summary of cameras"""
    print(f"\n{'='*80}")
    print(f"Total cameras found: {len(cameras)}")
    print(f"{'='*80}\n")
    
    for i, camera in enumerate(cameras, 1):
        print(f"{i}. {camera.get('Location', 'Unknown')}")
        print(f"   Roadway: {camera.get('Roadway')}")
        print(f"   GPS: ({camera.get('Latitude')}, {camera.get('Longitude')})")
        print(f"   Views: {len(camera.get('Views', []))}")
        print()

def main():
    print("Fetching camera data from Ontario 511 API...")
    all_cameras = fetch_all_cameras()
    print(f"Total cameras in Ontario: {len(all_cameras)}")
    
    print("\nFiltering for QEW cameras...")
    qew_cameras = filter_qew_cameras(all_cameras)
    print(f"Total QEW cameras: {len(qew_cameras)}")
    
    print("\nFiltering for Hamilton-Mississauga corridor...")
    corridor_cameras = filter_hamilton_mississauga_corridor(qew_cameras)
    
    print_camera_summary(corridor_cameras)
    
    # Save to file
    save_camera_data(corridor_cameras, "qew_cameras_hamilton_mississauga.json")
    
    # Calculate total image views available
    total_views = sum(len(c.get('Views', [])) for c in corridor_cameras)
    print(f"\n{'='*80}")
    print(f"Total camera views available: {total_views}")
    print(f"Each camera can be captured multiple times for 100+ images")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()


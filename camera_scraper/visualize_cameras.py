"""
Script to visualize camera locations along QEW corridor
Creates a simple text-based map and exports coordinates for mapping tools
"""
import json
from typing import List, Dict

def load_camera_data(filename: str = "qew_cameras_hamilton_mississauga.json") -> List[Dict]:
    """Load camera data from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)

def print_camera_map(cameras: List[Dict]):
    """Print a text-based visualization of camera locations"""
    print("\n" + "="*80)
    print("QEW CORRIDOR CAMERA LOCATIONS MAP")
    print("Hamilton (West) ←→ Mississauga (East)")
    print("="*80 + "\n")
    
    # Sort cameras by longitude (west to east)
    sorted_cameras = sorted(cameras, key=lambda c: c.get('Longitude', 0), reverse=True)
    
    # Group by approximate region
    regions = {
        'Hamilton': [],
        'Burlington': [],
        'Oakville': [],
        'Mississauga': []
    }
    
    for camera in sorted_cameras:
        location = camera.get('Location', '')
        lon = camera.get('Longitude', 0)
        
        # Classify by longitude
        if lon < -79.78:
            regions['Hamilton'].append(camera)
        elif lon < -79.70:
            regions['Burlington'].append(camera)
        elif lon < -79.63:
            regions['Oakville'].append(camera)
        else:
            regions['Mississauga'].append(camera)
    
    # Print by region
    for region, cams in regions.items():
        if cams:
            print(f"\n{'─'*80}")
            print(f"📍 {region.upper()} ({len(cams)} cameras)")
            print(f"{'─'*80}")
            
            for i, cam in enumerate(cams, 1):
                location = cam.get('Location', 'Unknown')
                lat = cam.get('Latitude')
                lon = cam.get('Longitude')
                views = len(cam.get('Views', []))
                
                print(f"{i:2d}. {location}")
                print(f"    GPS: {lat:.6f}, {lon:.6f}")
                print(f"    Views: {views}")

def export_for_google_maps(cameras: List[Dict], filename: str = "camera_locations_google_maps.txt"):
    """Export camera coordinates in format for Google Maps"""
    with open(filename, 'w') as f:
        f.write("QEW Corridor Camera Locations - Google Maps Format\n")
        f.write("="*80 + "\n\n")
        f.write("Copy and paste these coordinates into Google Maps:\n\n")
        
        for camera in cameras:
            location = camera.get('Location', 'Unknown')
            lat = camera.get('Latitude')
            lon = camera.get('Longitude')
            
            f.write(f"{location}\n")
            f.write(f"{lat},{lon}\n\n")
    
    print(f"\n✓ Google Maps coordinates exported to: {filename}")

def export_for_gps_tools(cameras: List[Dict], filename: str = "camera_locations.csv"):
    """Export camera coordinates as CSV for GPS tools"""
    with open(filename, 'w') as f:
        # CSV header
        f.write("Camera_ID,Location,Latitude,Longitude,Views,Roadway\n")
        
        for camera in cameras:
            cam_id = camera.get('Id')
            location = camera.get('Location', 'Unknown').replace(',', ';')
            lat = camera.get('Latitude')
            lon = camera.get('Longitude')
            views = len(camera.get('Views', []))
            roadway = camera.get('Roadway', 'QEW')
            
            f.write(f"{cam_id},{location},{lat},{lon},{views},{roadway}\n")
    
    print(f"✓ CSV coordinates exported to: {filename}")

def export_geojson(cameras: List[Dict], filename: str = "camera_locations.geojson"):
    """Export camera coordinates as GeoJSON for mapping applications"""
    features = []
    
    for camera in cameras:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [camera.get('Longitude'), camera.get('Latitude')]
            },
            "properties": {
                "id": camera.get('Id'),
                "location": camera.get('Location'),
                "roadway": camera.get('Roadway'),
                "views": len(camera.get('Views', [])),
                "source": camera.get('Source')
            }
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    with open(filename, 'w') as f:
        json.dump(geojson, f, indent=2)
    
    print(f"✓ GeoJSON exported to: {filename}")

def print_statistics(cameras: List[Dict]):
    """Print statistics about camera coverage"""
    print("\n" + "="*80)
    print("CAMERA COVERAGE STATISTICS")
    print("="*80)
    
    # Calculate bounds
    lats = [c.get('Latitude') for c in cameras if c.get('Latitude')]
    lons = [c.get('Longitude') for c in cameras if c.get('Longitude')]
    
    print(f"\nTotal Cameras: {len(cameras)}")
    print(f"Total Views: {sum(len(c.get('Views', [])) for c in cameras)}")
    
    print(f"\nGeographic Coverage:")
    print(f"  Latitude Range:  {min(lats):.6f} to {max(lats):.6f}")
    print(f"  Longitude Range: {min(lons):.6f} to {max(lons):.6f}")
    
    # Calculate approximate distance (rough estimate)
    # 1 degree longitude ≈ 85 km at this latitude
    lon_distance = (max(lons) - min(lons)) * 85
    print(f"  Approximate Distance: {abs(lon_distance):.1f} km")
    
    # Average spacing
    avg_spacing = abs(lon_distance) / len(cameras)
    print(f"  Average Camera Spacing: {avg_spacing:.2f} km")
    
    print(f"\nCamera Density:")
    print(f"  Cameras per 10 km: {10 / avg_spacing:.1f}")

def main():
    print("QEW Corridor Camera Visualization Tool")
    print("="*80)
    
    # Load camera data
    print("\nLoading camera data...")
    cameras = load_camera_data()
    print(f"Loaded {len(cameras)} cameras")
    
    # Print text-based map
    print_camera_map(cameras)
    
    # Print statistics
    print_statistics(cameras)
    
    # Export in various formats
    print("\n" + "="*80)
    print("EXPORTING COORDINATES")
    print("="*80 + "\n")
    
    export_for_google_maps(cameras)
    export_for_gps_tools(cameras)
    export_geojson(cameras)
    
    print("\n" + "="*80)
    print("USAGE INSTRUCTIONS")
    print("="*80)
    print("\n1. Google Maps:")
    print("   - Open 'camera_locations_google_maps.txt'")
    print("   - Copy coordinates and paste into Google Maps search")
    
    print("\n2. GPS Tools / Excel:")
    print("   - Open 'camera_locations.csv' in Excel or GPS software")
    
    print("\n3. GIS Applications:")
    print("   - Import 'camera_locations.geojson' into QGIS, ArcGIS, or web maps")
    print("   - Compatible with Leaflet, Mapbox, Google Maps API")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    main()


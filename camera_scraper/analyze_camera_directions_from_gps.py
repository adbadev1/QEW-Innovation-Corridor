"""
Analyze camera directions based on GPS coordinates and highway alignment
Uses the QEW highway path to determine likely camera orientations
"""
import math
from typing import Tuple, List, Dict
from database import CameraDatabase


class HighwayDirectionAnalyzer:
    """Analyzes camera directions based on highway alignment"""
    
    def __init__(self):
        # QEW generally runs East-West in this corridor
        # Hamilton (west) to Mississauga/Toronto (east)
        pass
    
    def calculate_bearing(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate bearing between two GPS points"""
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        lon_diff = math.radians(lon2 - lon1)
        
        # Calculate bearing
        x = math.sin(lon_diff) * math.cos(lat2_rad)
        y = math.cos(lat1_rad) * math.sin(lat2_rad) - \
            math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(lon_diff)
        
        bearing = math.atan2(x, y)
        bearing_degrees = math.degrees(bearing)
        
        # Normalize to 0-360
        bearing_degrees = (bearing_degrees + 360) % 360
        
        return bearing_degrees
    
    def get_highway_direction_at_point(self, cameras: List[Dict], current_camera: Dict) -> Tuple[float, float]:
        """
        Estimate highway direction at a camera location
        Returns (eastbound_heading, westbound_heading)
        """
        current_lat = current_camera['latitude']
        current_lon = current_camera['longitude']
        
        # Find nearest cameras before and after this one
        sorted_cameras = sorted(cameras, key=lambda c: c['longitude'])
        
        current_idx = next((i for i, c in enumerate(sorted_cameras) 
                          if c['camera_id'] == current_camera['camera_id']), None)
        
        if current_idx is None:
            # Default to general QEW direction (roughly east-west)
            return 90.0, 270.0
        
        # Get cameras before and after
        prev_camera = sorted_cameras[current_idx - 1] if current_idx > 0 else None
        next_camera = sorted_cameras[current_idx + 1] if current_idx < len(sorted_cameras) - 1 else None
        
        if prev_camera and next_camera:
            # Calculate bearing from previous to next camera
            bearing = self.calculate_bearing(
                prev_camera['latitude'], prev_camera['longitude'],
                next_camera['latitude'], next_camera['longitude']
            )
        elif next_camera:
            # Use bearing to next camera
            bearing = self.calculate_bearing(
                current_lat, current_lon,
                next_camera['latitude'], next_camera['longitude']
            )
        elif prev_camera:
            # Use bearing from previous camera
            bearing = self.calculate_bearing(
                prev_camera['latitude'], prev_camera['longitude'],
                current_lat, current_lon
            )
        else:
            # Default
            bearing = 90.0
        
        # Eastbound is the calculated bearing
        eastbound = bearing
        # Westbound is opposite direction
        westbound = (bearing + 180) % 360
        
        return eastbound, westbound
    
    def analyze_all_cameras(self, db: CameraDatabase):
        """Analyze all cameras and suggest directions"""
        print("=" * 80)
        print("ANALYZING CAMERA DIRECTIONS FROM GPS")
        print("=" * 80)
        
        cameras = db.get_all_cameras()
        
        results = []
        
        for camera in cameras:
            camera_id = camera['camera_id']
            location = camera['location']
            
            # Get highway direction at this point
            eastbound, westbound = self.get_highway_direction_at_point(cameras, camera)
            
            print(f"\n[Camera {camera_id}] {location}")
            print(f"  Highway Direction: {eastbound:.1f}° (Eastbound) / {westbound:.1f}° (Westbound)")
            
            # Get views
            views = db.get_camera_views(camera_id)
            
            for view in views:
                view_id = view['view_id']
                description = view['description'].lower()
                url = view['url']
                
                # Determine likely heading based on description
                suggested_heading = None
                confidence = "low"
                
                if "toronto bound" in description or "east" in description:
                    suggested_heading = eastbound
                    confidence = "high"
                elif "fort erie bound" in description or "niagara" in description or "hamilton" in description or "west" in description:
                    suggested_heading = westbound
                    confidence = "high"
                elif "looking down" in description or "overhead" in description:
                    suggested_heading = None
                    confidence = "n/a"
                else:
                    # No clear direction - could be either
                    # Check if location name gives hints
                    if "toronto" in location.lower():
                        suggested_heading = eastbound
                        confidence = "medium"
                    elif "hamilton" in location.lower():
                        suggested_heading = westbound
                        confidence = "medium"
                    else:
                        # Default to eastbound for unknown
                        suggested_heading = eastbound
                        confidence = "low"
                
                results.append({
                    'camera_id': camera_id,
                    'view_id': view_id,
                    'location': location,
                    'description': view['description'],
                    'url': url,
                    'suggested_heading': suggested_heading,
                    'confidence': confidence,
                    'eastbound_heading': eastbound,
                    'westbound_heading': westbound
                })
                
                if suggested_heading is not None:
                    print(f"  View {view_id} ({view['description']}): {suggested_heading:.1f}° [{confidence} confidence]")
                else:
                    print(f"  View {view_id} ({view['description']}): Overhead/Variable")
        
        return results


def export_analysis_to_csv(results: List[Dict], output_file: str = "camera_directions_analysis.csv"):
    """Export analysis results to CSV"""
    import csv
    
    fieldnames = [
        'camera_id', 'view_id', 'location', 'description', 'url',
        'suggested_heading', 'confidence', 'eastbound_heading', 'westbound_heading'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n✓ Exported analysis to: {output_file}")


def main():
    """Main execution"""
    db = CameraDatabase('camera_data.db')
    
    try:
        analyzer = HighwayDirectionAnalyzer()
        results = analyzer.analyze_all_cameras(db)
        
        # Export to CSV
        export_analysis_to_csv(results)
        
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"\nAnalyzed {len(results)} camera views")
        print("\nConfidence levels:")
        high_conf = sum(1 for r in results if r['confidence'] == 'high')
        medium_conf = sum(1 for r in results if r['confidence'] == 'medium')
        low_conf = sum(1 for r in results if r['confidence'] == 'low')
        print(f"  High: {high_conf}")
        print(f"  Medium: {medium_conf}")
        print(f"  Low: {low_conf}")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()


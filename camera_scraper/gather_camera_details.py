"""
Script to gather detailed camera information and populate camera_details table
Analyzes camera orientation, coverage, and physical characteristics
"""
import json
import math
import requests
from typing import Dict, List, Tuple, Optional
from database import CameraDatabase


class CameraDetailsGatherer:
    """Gathers detailed information about cameras"""
    
    # 16-point compass directions with degree ranges
    COMPASS_16 = [
        (0, 11.25, "N"), (11.25, 33.75, "NNE"), (33.75, 56.25, "NE"), (56.25, 78.75, "ENE"),
        (78.75, 101.25, "E"), (101.25, 123.75, "ESE"), (123.75, 146.25, "SE"), (146.25, 168.75, "SSE"),
        (168.75, 191.25, "S"), (191.25, 213.75, "SSW"), (213.75, 236.25, "SW"), (236.25, 258.75, "WSW"),
        (258.75, 281.25, "W"), (281.25, 303.75, "WNW"), (303.75, 326.25, "NW"), (326.25, 348.75, "NNW"),
        (348.75, 360, "N")
    ]
    
    # 8-point compass directions
    COMPASS_8 = [
        (0, 22.5, "N"), (22.5, 67.5, "NE"), (67.5, 112.5, "E"), (112.5, 157.5, "SE"),
        (157.5, 202.5, "S"), (202.5, 247.5, "SW"), (247.5, 292.5, "W"), (292.5, 337.5, "NW"),
        (337.5, 360, "N")
    ]
    
    # Full direction names
    DIRECTION_NAMES = {
        "N": "North", "NNE": "North-Northeast", "NE": "Northeast", "ENE": "East-Northeast",
        "E": "East", "ESE": "East-Southeast", "SE": "Southeast", "SSE": "South-Southeast",
        "S": "South", "SSW": "South-Southwest", "SW": "Southwest", "WSW": "West-Southwest",
        "W": "West", "WNW": "West-Northwest", "NW": "Northwest", "NNW": "North-Northwest"
    }
    
    def __init__(self, db: CameraDatabase):
        self.db = db
    
    def degrees_to_compass_16(self, degrees: float) -> str:
        """Convert degrees to 16-point compass direction"""
        degrees = degrees % 360
        for start, end, direction in self.COMPASS_16:
            if start <= degrees < end:
                return direction
        return "N"
    
    def degrees_to_compass_8(self, degrees: float) -> str:
        """Convert degrees to 8-point compass direction"""
        degrees = degrees % 360
        for start, end, direction in self.COMPASS_8:
            if start <= degrees < end:
                return direction
        return "N"
    
    def get_direction_description(self, degrees: float) -> str:
        """Get full direction description"""
        compass_16 = self.degrees_to_compass_16(degrees)
        direction_name = self.DIRECTION_NAMES.get(compass_16, compass_16)
        return f"{direction_name} ({degrees:.1f}°)"
    
    def analyze_view_description(self, description: str) -> Dict:
        """Analyze view description to determine heading"""
        description_lower = description.lower()
        
        # Map common descriptions to approximate headings
        heading_map = {
            "toronto bound": 90,  # East
            "fort erie bound": 270,  # West
            "niagara bound": 270,  # West
            "hamilton bound": 270,  # West
            "looking down": None,  # Overhead view
            "looking up": None,  # Upward view
            "north": 0,
            "northeast": 45,
            "east": 90,
            "southeast": 135,
            "south": 180,
            "southwest": 225,
            "west": 270,
            "northwest": 315,
        }
        
        for key, heading in heading_map.items():
            if key in description_lower:
                return {"heading": heading, "confidence": "medium"}
        
        return {"heading": None, "confidence": "unknown"}
    
    def estimate_vertical_angle(self, description: str) -> Tuple[Optional[float], str, str]:
        """Estimate vertical angle from description"""
        description_lower = description.lower()
        
        if "looking down" in description_lower or "overhead" in description_lower:
            angle = -45.0  # Looking down at 45 degrees
            label = "Downward"
            desc = f"{abs(angle):.1f}° Downward"
        elif "looking up" in description_lower:
            angle = 30.0  # Looking up at 30 degrees
            label = "Upward"
            desc = f"{angle:.1f}° Upward"
        else:
            angle = -5.0  # Slight downward angle for traffic cameras
            label = "Slightly Downward"
            desc = f"{abs(angle):.1f}° Downward"
        
        return angle, label, desc
    
    def estimate_mount_height(self, location: str) -> Tuple[float, float]:
        """Estimate camera mount height based on location"""
        location_lower = location.lower()

        if "skyway" in location_lower or "bridge" in location_lower:
            # Bridge-mounted cameras are higher
            height_meters = 25.0
        elif "ramp" in location_lower or "ic" in location_lower:
            # Interchange cameras
            height_meters = 12.0
        else:
            # Standard highway cameras
            height_meters = 8.0

        height_feet = height_meters * 3.28084
        return height_meters, height_feet

    def get_ground_altitude(self, latitude: float, longitude: float) -> Tuple[float, float]:
        """Get ground altitude from coordinates using elevation API"""
        try:
            # Using Open-Elevation API (free, no API key required)
            url = f"https://api.open-elevation.com/api/v1/lookup?locations={latitude},{longitude}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                if data.get('results'):
                    elevation_meters = data['results'][0]['elevation']
                    elevation_feet = elevation_meters * 3.28084
                    return elevation_meters, elevation_feet
        except Exception as e:
            print(f"  Warning: Could not fetch elevation data: {e}")

        # Fallback: Estimate based on location (QEW corridor is relatively flat)
        # Average elevation in the area is around 75-100 meters
        elevation_meters = 85.0
        elevation_feet = elevation_meters * 3.28084
        return elevation_meters, elevation_feet

    def estimate_coverage(self, vertical_angle: float, height: float) -> Dict:
        """Estimate camera coverage based on angle and height"""
        # Calculate view distance based on height and angle
        if vertical_angle and vertical_angle < 0:  # Looking down
            angle_rad = math.radians(abs(vertical_angle))
            # Simple trigonometry: distance = height / tan(angle)
            view_distance_meters = height / math.tan(angle_rad) if angle_rad > 0 else height * 10
        else:
            # Horizontal or upward view - use typical highway camera range
            view_distance_meters = 300.0

        view_distance_feet = view_distance_meters * 3.28084

        # Effective range is typically 70% of view distance for clear identification
        effective_range_meters = view_distance_meters * 0.7
        effective_range_feet = effective_range_meters * 3.28084

        # Typical highway camera field of view
        fov_horizontal = 60.0  # degrees
        fov_vertical = 40.0    # degrees
        fov_total = math.sqrt(fov_horizontal**2 + fov_vertical**2)

        return {
            "view_distance_meters": view_distance_meters,
            "view_distance_feet": view_distance_feet,
            "effective_range_meters": effective_range_meters,
            "effective_range_feet": effective_range_feet,
            "field_of_view_degrees": fov_total,
            "field_of_view_horizontal": fov_horizontal,
            "field_of_view_vertical": fov_vertical
        }

    def calculate_coverage_polygon(self, latitude: float, longitude: float,
                                   heading: Optional[float], fov: float,
                                   distance: float) -> str:
        """Calculate coverage area polygon"""
        if heading is None:
            return None

        # Calculate polygon points for coverage area
        # This is a simplified version - real implementation would be more complex
        points = []

        # Camera position
        points.append(f"{latitude},{longitude}")

        # Calculate left and right edges of field of view
        left_heading = (heading - fov/2) % 360
        right_heading = (heading + fov/2) % 360

        # Convert distance to approximate lat/lon offset (rough approximation)
        # 1 degree latitude ≈ 111 km
        # 1 degree longitude ≈ 111 km * cos(latitude)
        lat_offset = (distance / 1000) / 111
        lon_offset = (distance / 1000) / (111 * math.cos(math.radians(latitude)))

        # Left edge point
        left_lat = latitude + lat_offset * math.cos(math.radians(left_heading))
        left_lon = longitude + lon_offset * math.sin(math.radians(left_heading))
        points.append(f"{left_lat},{left_lon}")

        # Right edge point
        right_lat = latitude + lat_offset * math.cos(math.radians(right_heading))
        right_lon = longitude + lon_offset * math.sin(math.radians(right_heading))
        points.append(f"{right_lat},{right_lon}")

        # Close the polygon
        points.append(points[0])

        return ";".join(points)

    def determine_mount_type(self, location: str, description: str) -> Tuple[str, str]:
        """Determine camera mount type"""
        location_lower = location.lower()
        description_lower = description.lower()

        if "skyway" in location_lower or "bridge" in location_lower:
            return "Bridge Mount", "Mounted on bridge structure"
        elif "looking down" in description_lower:
            return "Overhead Gantry", "Mounted on overhead gantry structure"
        elif "ramp" in location_lower:
            return "Pole Mount", "Mounted on pole at interchange ramp"
        else:
            return "Pole Mount", "Mounted on roadside pole"

    def gather_details_for_view(self, camera: Dict, view: Dict) -> Dict:
        """Gather all details for a specific camera view"""
        camera_id = camera['camera_id']
        view_id = view['view_id']
        location = camera['location']
        latitude = camera['latitude']
        longitude = camera['longitude']
        description = view['description']

        print(f"  Processing Camera {camera_id}, View {view_id}: {description}")

        # Analyze heading
        heading_info = self.analyze_view_description(description)
        heading = heading_info['heading']
        confidence = heading_info['confidence']

        # Get compass directions
        if heading is not None:
            compass_16 = self.degrees_to_compass_16(heading)
            compass_8 = self.degrees_to_compass_8(heading)
            heading_desc = self.get_direction_description(heading)
        else:
            compass_16 = None
            compass_8 = None
            heading_desc = "Unknown (Overhead/Variable)"

        # Estimate vertical angle
        vertical_angle, v_label, v_desc = self.estimate_vertical_angle(description)

        # Get mount height
        height_meters, height_feet = self.estimate_mount_height(location)

        # Get ground altitude
        ground_alt_m, ground_alt_ft = self.get_ground_altitude(latitude, longitude)

        # Calculate altitude above sea level
        alt_asl_m = ground_alt_m + height_meters
        alt_asl_ft = ground_alt_ft + height_feet

        # Determine mount type
        mount_type, mount_desc = self.determine_mount_type(location, description)

        # Estimate coverage
        coverage = self.estimate_coverage(vertical_angle, height_meters)

        # Calculate coverage polygon
        if heading is not None:
            coverage_polygon = self.calculate_coverage_polygon(
                latitude, longitude, heading,
                coverage['field_of_view_horizontal'],
                coverage['view_distance_meters']
            )
        else:
            coverage_polygon = None

        # Compile all details
        details = {
            'camera_id': camera_id,
            'view_id': view_id,
            'compass_direction_16': compass_16,
            'compass_direction_8': compass_8,
            'heading_degrees': heading,
            'heading_description': heading_desc,
            'vertical_angle_degrees': vertical_angle,
            'vertical_angle_label': v_label,
            'vertical_angle_description': v_desc,
            'height_above_ground_meters': height_meters,
            'height_above_ground_feet': height_feet,
            'altitude_above_sea_level_meters': alt_asl_m,
            'altitude_above_sea_level_feet': alt_asl_ft,
            'ground_altitude_meters': ground_alt_m,
            'ground_altitude_feet': ground_alt_ft,
            'mount_type': mount_type,
            'mount_description': mount_desc,
            'view_distance_meters': coverage['view_distance_meters'],
            'view_distance_feet': coverage['view_distance_feet'],
            'effective_range_meters': coverage['effective_range_meters'],
            'effective_range_feet': coverage['effective_range_feet'],
            'field_of_view_degrees': coverage['field_of_view_degrees'],
            'field_of_view_horizontal': coverage['field_of_view_horizontal'],
            'field_of_view_vertical': coverage['field_of_view_vertical'],
            'coverage_area_polygon': coverage_polygon,
            'data_source': 'Automated Analysis',
            'confidence_level': confidence,
            'notes': f"Auto-generated from view description: {description}"
        }

        return details

    def process_all_cameras(self):
        """Process all cameras and gather details"""
        print("=" * 80)
        print("GATHERING CAMERA DETAILS")
        print("=" * 80)

        # Get all cameras from database
        cameras = self.db.get_all_cameras()
        print(f"\nFound {len(cameras)} cameras in database")

        total_views = 0
        processed_views = 0

        for camera in cameras:
            camera_id = camera['camera_id']
            location = camera['location']

            print(f"\n[Camera {camera_id}] {location}")

            # Get all views for this camera
            views = self.db.get_camera_views(camera_id)
            total_views += len(views)

            for view in views:
                try:
                    # Gather details for this view
                    details = self.gather_details_for_view(camera, view)

                    # Insert into database
                    self.db.insert_camera_details(details)
                    processed_views += 1

                    print(f"    ✓ Saved details for view {view['view_id']}")

                except Exception as e:
                    print(f"    ✗ Error processing view {view['view_id']}: {e}")

        print("\n" + "=" * 80)
        print(f"COMPLETE: Processed {processed_views}/{total_views} camera views")
        print("=" * 80)


def display_sample_details(db: CameraDatabase, num_samples: int = 3):
    """Display sample camera details"""
    print("\n" + "=" * 80)
    print("SAMPLE CAMERA DETAILS")
    print("=" * 80)

    details_list = db.get_all_camera_details()

    for i, details in enumerate(details_list[:num_samples]):
        print(f"\n--- Camera {details['camera_id']}, View {details['view_id']} ---")

        # Direction info
        if details['heading_degrees'] is not None:
            print(f"Direction: {details['heading_description']}")
            print(f"  16-Point Compass: {details['compass_direction_16']}")
            print(f"  8-Point Compass: {details['compass_direction_8']}")
            print(f"  Exact Heading: {details['heading_degrees']:.1f}°")
        else:
            print(f"Direction: {details['heading_description']}")

        # Vertical angle
        print(f"\nVertical Angle: {details['vertical_angle_description']}")
        print(f"  Angle: {details['vertical_angle_degrees']:.1f}°")
        print(f"  Label: {details['vertical_angle_label']}")

        # Altitude info
        print(f"\nAltitude Information:")
        print(f"  Height Above Ground: {details['height_above_ground_meters']:.1f}m ({details['height_above_ground_feet']:.1f}ft)")
        print(f"  Ground Altitude: {details['ground_altitude_meters']:.1f}m ({details['ground_altitude_feet']:.1f}ft)")
        print(f"  Altitude ASL: {details['altitude_above_sea_level_meters']:.1f}m ({details['altitude_above_sea_level_feet']:.1f}ft)")

        # Mount info
        print(f"\nMount Information:")
        print(f"  Type: {details['mount_type']}")
        print(f"  Description: {details['mount_description']}")

        # Coverage info
        print(f"\nCoverage Details:")
        print(f"  View Distance: {details['view_distance_meters']:.1f}m ({details['view_distance_feet']:.1f}ft)")
        print(f"  Effective Range: {details['effective_range_meters']:.1f}m ({details['effective_range_feet']:.1f}ft)")
        print(f"  Field of View: {details['field_of_view_degrees']:.1f}° total")
        print(f"    Horizontal: {details['field_of_view_horizontal']:.1f}°")
        print(f"    Vertical: {details['field_of_view_vertical']:.1f}°")

        # Metadata
        print(f"\nMetadata:")
        print(f"  Data Source: {details['data_source']}")
        print(f"  Confidence: {details['confidence_level']}")
        print(f"  Last Updated: {details['last_updated']}")


def main():
    """Main execution"""
    print("\n" + "=" * 80)
    print("QEW CAMERA DETAILS GATHERER")
    print("=" * 80)
    print("\nThis script will analyze all cameras in the database and gather:")
    print("  • 16-point and 8-point compass directions")
    print("  • Exact heading (0-360°)")
    print("  • Vertical angle and tilt information")
    print("  • Altitude and mount height details")
    print("  • Coverage area and field of view")
    print("  • Mount type and description")
    print("\n" + "=" * 80)

    # Connect to database
    db = CameraDatabase('camera_data.db')

    try:
        # Create gatherer instance
        gatherer = CameraDetailsGatherer(db)

        # Process all cameras
        gatherer.process_all_cameras()

        # Display sample results
        display_sample_details(db, num_samples=5)

        # Show statistics
        print("\n" + "=" * 80)
        print("DATABASE STATISTICS")
        print("=" * 80)

        db.cursor.execute('SELECT COUNT(*) FROM camera_details')
        total_details = db.cursor.fetchone()[0]
        print(f"Total camera details records: {total_details}")

        db.cursor.execute('SELECT COUNT(DISTINCT camera_id) FROM camera_details')
        unique_cameras = db.cursor.fetchone()[0]
        print(f"Cameras with details: {unique_cameras}")

        print("\n✓ Camera details successfully gathered and stored!")
        print("\nYou can now query camera details using:")
        print("  • db.get_camera_details(camera_id, view_id)")
        print("  • db.get_all_camera_details()")
        print("  • python query_database.py (for interactive queries)")

    finally:
        db.close()


if __name__ == "__main__":
    main()


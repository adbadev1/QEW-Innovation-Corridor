"""
Interactive viewer for camera details
Query and display detailed camera information from the database
"""
from database import CameraDatabase


def display_camera_detail(details: dict):
    """Display detailed information for a camera view"""
    print("\n" + "=" * 80)
    print(f"CAMERA {details['camera_id']} - VIEW {details['view_id']}")
    print("=" * 80)
    
    # Direction Information
    print("\n📍 DIRECTION INFORMATION")
    print("-" * 80)
    if details['heading_degrees'] is not None:
        print(f"Heading Description: {details['heading_description']}")
        print(f"Exact Heading: {details['heading_degrees']:.1f}°")
        print(f"16-Point Compass: {details['compass_direction_16']}")
        print(f"8-Point Compass: {details['compass_direction_8']}")
    else:
        print(f"Heading: {details['heading_description']}")
    
    # Vertical Angle
    print("\n📐 VERTICAL ANGLE (TILT)")
    print("-" * 80)
    print(f"Description: {details['vertical_angle_description']}")
    print(f"Angle: {details['vertical_angle_degrees']:.1f}°")
    print(f"Label: {details['vertical_angle_label']}")
    
    # Altitude Information
    print("\n🏔️  ALTITUDE INFORMATION")
    print("-" * 80)
    print(f"Height Above Ground:")
    print(f"  • {details['height_above_ground_meters']:.1f} meters")
    print(f"  • {details['height_above_ground_feet']:.1f} feet")
    print(f"\nGround Altitude:")
    print(f"  • {details['ground_altitude_meters']:.1f} meters above sea level")
    print(f"  • {details['ground_altitude_feet']:.1f} feet above sea level")
    print(f"\nCamera Altitude (ASL):")
    print(f"  • {details['altitude_above_sea_level_meters']:.1f} meters")
    print(f"  • {details['altitude_above_sea_level_feet']:.1f} feet")
    
    # Mount Information
    print("\n🔧 MOUNT INFORMATION")
    print("-" * 80)
    print(f"Mount Type: {details['mount_type']}")
    print(f"Description: {details['mount_description']}")
    
    # Coverage Details
    print("\n📹 COVERAGE DETAILS")
    print("-" * 80)
    print(f"View Distance:")
    print(f"  • {details['view_distance_meters']:.1f} meters ({details['view_distance_feet']:.1f} feet)")
    print(f"\nEffective Range:")
    print(f"  • {details['effective_range_meters']:.1f} meters ({details['effective_range_feet']:.1f} feet)")
    print(f"\nField of View:")
    print(f"  • Total: {details['field_of_view_degrees']:.1f}°")
    print(f"  • Horizontal: {details['field_of_view_horizontal']:.1f}°")
    print(f"  • Vertical: {details['field_of_view_vertical']:.1f}°")
    
    if details['coverage_area_polygon']:
        print(f"\nCoverage Area Polygon:")
        print(f"  {details['coverage_area_polygon'][:100]}...")
    
    # Metadata
    print("\n📊 METADATA")
    print("-" * 80)
    print(f"Data Source: {details['data_source']}")
    print(f"Confidence Level: {details['confidence_level']}")
    print(f"Last Updated: {details['last_updated']}")
    if details['notes']:
        print(f"Notes: {details['notes']}")


def show_all_cameras_summary(db: CameraDatabase):
    """Show summary of all cameras with details"""
    print("\n" + "=" * 80)
    print("ALL CAMERAS - SUMMARY")
    print("=" * 80)
    
    details_list = db.get_all_camera_details()
    
    current_camera = None
    for details in details_list:
        if details['camera_id'] != current_camera:
            current_camera = details['camera_id']
            camera = db.get_camera_by_id(current_camera)
            print(f"\n[Camera {current_camera}] {camera['location']}")
        
        view_id = details['view_id']
        heading = details['heading_description']
        mount = details['mount_type']
        range_m = details['effective_range_meters']
        
        print(f"  View {view_id}: {heading} | {mount} | Range: {range_m:.0f}m")


def main():
    """Main interactive menu"""
    db = CameraDatabase('camera_data.db')
    
    try:
        while True:
            print("\n" + "=" * 80)
            print("CAMERA DETAILS VIEWER")
            print("=" * 80)
            print("\n1. View details for specific camera view")
            print("2. View all details for a camera")
            print("3. Show summary of all cameras")
            print("4. Search by direction (e.g., 'East', 'NE')")
            print("5. Search by mount type")
            print("6. Exit")
            
            choice = input("\nEnter choice (1-6): ").strip()
            
            if choice == '1':
                camera_id = int(input("Enter camera ID: "))
                view_id = int(input("Enter view ID: "))
                details = db.get_camera_details(camera_id, view_id)
                if details:
                    display_camera_detail(details)
                else:
                    print("❌ No details found for that camera/view")
            
            elif choice == '2':
                camera_id = int(input("Enter camera ID: "))
                camera = db.get_camera_by_id(camera_id)
                if camera:
                    print(f"\n[Camera {camera_id}] {camera['location']}")
                    views = db.get_camera_views(camera_id)
                    for view in views:
                        details = db.get_camera_details(camera_id, view['view_id'])
                        if details:
                            display_camera_detail(details)
                else:
                    print("❌ Camera not found")
            
            elif choice == '3':
                show_all_cameras_summary(db)
            
            elif choice == '4':
                direction = input("Enter direction (N, NE, E, SE, S, SW, W, NW, etc.): ").strip().upper()
                db.cursor.execute('''
                    SELECT * FROM camera_details 
                    WHERE compass_direction_16 = ? OR compass_direction_8 = ?
                ''', (direction, direction))
                results = [dict(row) for row in db.cursor.fetchall()]
                print(f"\nFound {len(results)} cameras facing {direction}")
                for details in results:
                    camera = db.get_camera_by_id(details['camera_id'])
                    print(f"  Camera {details['camera_id']} View {details['view_id']}: {camera['location']}")
            
            elif choice == '5':
                print("\nMount types: Bridge Mount, Overhead Gantry, Pole Mount")
                mount_type = input("Enter mount type: ").strip()
                db.cursor.execute('''
                    SELECT * FROM camera_details WHERE mount_type LIKE ?
                ''', (f'%{mount_type}%',))
                results = [dict(row) for row in db.cursor.fetchall()]
                print(f"\nFound {len(results)} cameras with mount type '{mount_type}'")
                for details in results[:10]:  # Show first 10
                    camera = db.get_camera_by_id(details['camera_id'])
                    print(f"  Camera {details['camera_id']} View {details['view_id']}: {camera['location']}")
            
            elif choice == '6':
                print("\n👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice")
    
    finally:
        db.close()


if __name__ == "__main__":
    main()


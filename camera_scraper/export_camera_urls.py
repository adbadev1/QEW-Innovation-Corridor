"""
Export camera URLs with details for manual assessment
Creates a CSV file with all camera information including URLs
"""
import csv
from database import CameraDatabase


def export_camera_urls_csv(db: CameraDatabase, output_file: str = "camera_urls_for_assessment.csv"):
    """Export all camera URLs with details to CSV"""
    
    print("=" * 80)
    print("EXPORTING CAMERA URLs FOR ASSESSMENT")
    print("=" * 80)
    
    # Get all cameras
    cameras = db.get_all_cameras()
    
    rows = []
    
    for camera in cameras:
        camera_id = camera['camera_id']
        location = camera['location']
        latitude = camera['latitude']
        longitude = camera['longitude']
        
        # Get all views for this camera
        views = db.get_camera_views(camera_id)
        
        for view in views:
            view_id = view['view_id']
            url = view['url']
            description = view['description']
            
            # Get current details if they exist
            details = db.get_camera_details(camera_id, view_id)
            
            if details:
                current_heading = details.get('heading_degrees', 'NULL')
                current_compass_16 = details.get('compass_direction_16', 'NULL')
                current_compass_8 = details.get('compass_direction_8', 'NULL')
                mount_type = details.get('mount_type', 'NULL')
            else:
                current_heading = 'NULL'
                current_compass_16 = 'NULL'
                current_compass_8 = 'NULL'
                mount_type = 'NULL'
            
            rows.append({
                'camera_id': camera_id,
                'view_id': view_id,
                'location': location,
                'latitude': latitude,
                'longitude': longitude,
                'view_description': description,
                'url': url,
                'current_heading_degrees': current_heading,
                'current_compass_16': current_compass_16,
                'current_compass_8': current_compass_8,
                'mount_type': mount_type,
                'needs_manual_review': 'YES' if current_heading == 'NULL' or current_heading is None else 'NO'
            })
    
    # Write to CSV
    fieldnames = [
        'camera_id', 'view_id', 'location', 'latitude', 'longitude',
        'view_description', 'url', 'current_heading_degrees',
        'current_compass_16', 'current_compass_8', 'mount_type',
        'needs_manual_review'
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"\n✓ Exported {len(rows)} camera views to: {output_file}")
    
    # Count cameras needing review
    needs_review = sum(1 for row in rows if row['needs_manual_review'] == 'YES')
    print(f"\nCameras needing manual review: {needs_review}/{len(rows)}")
    
    return output_file


def export_camera_urls_text(db: CameraDatabase, output_file: str = "camera_urls_for_assessment.txt"):
    """Export camera URLs in readable text format"""
    
    cameras = db.get_all_cameras()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("QEW CAMERA URLs FOR MANUAL ASSESSMENT\n")
        f.write("=" * 80 + "\n\n")
        
        for camera in cameras:
            camera_id = camera['camera_id']
            location = camera['location']
            latitude = camera['latitude']
            longitude = camera['longitude']
            
            f.write(f"\n{'=' * 80}\n")
            f.write(f"CAMERA {camera_id}: {location}\n")
            f.write(f"GPS: {latitude}, {longitude}\n")
            f.write(f"{'=' * 80}\n")
            
            views = db.get_camera_views(camera_id)
            
            for view in views:
                view_id = view['view_id']
                url = view['url']
                description = view['description']
                
                details = db.get_camera_details(camera_id, view_id)
                
                f.write(f"\n  View {view_id}: {description}\n")
                f.write(f"  URL: {url}\n")
                
                if details:
                    if details.get('heading_degrees') is not None:
                        f.write(f"  Current Direction: {details['heading_description']}\n")
                        f.write(f"  Compass: {details['compass_direction_16']} ({details['compass_direction_8']})\n")
                    else:
                        f.write(f"  Current Direction: Unknown - NEEDS MANUAL REVIEW\n")
                    f.write(f"  Mount: {details['mount_type']}\n")
                else:
                    f.write(f"  Status: No details found\n")
                
                f.write(f"  Manual Assessment: [Enter heading 0-360°] _______\n")
                f.write(f"  Manual Compass: [Enter N/NE/E/SE/S/SW/W/NW] _______\n")
                f.write("\n")
    
    print(f"✓ Exported text format to: {output_file}")
    return output_file


def main():
    """Main execution"""
    db = CameraDatabase('camera_data.db')
    
    try:
        # Export CSV
        csv_file = export_camera_urls_csv(db)
        
        # Export text format
        text_file = export_camera_urls_text(db)
        
        print("\n" + "=" * 80)
        print("EXPORT COMPLETE")
        print("=" * 80)
        print(f"\nFiles created:")
        print(f"  1. {csv_file} - For spreadsheet analysis")
        print(f"  2. {text_file} - For manual annotation")
        print("\nYou can:")
        print("  • Open the CSV in Excel/Google Sheets")
        print("  • Visit each URL to assess the camera direction")
        print("  • Fill in the correct heading degrees and compass direction")
        print("  • Use the data to update the database")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()


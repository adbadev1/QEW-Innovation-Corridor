"""
Complete workflow to update web app with latest camera data from database
This script:
1. Exports camera metadata and image references from SQLite database to JSON
2. Copies the latest image collection to the public folder
"""
import sqlite3
import shutil
import json
from pathlib import Path


def update_webapp_with_latest_data():
    """
    Main function to update web app with latest camera data
    """
    print("QEW Camera Data Update for Web App")
    print("=" * 80)
    print()
    
    # Get paths
    script_dir = Path(__file__).parent
    db_path = script_dir / 'camera_data.db'
    public_dir = script_dir.parent / 'public'
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get the latest completed collection
    cursor.execute("""
        SELECT * FROM collections 
        WHERE status='completed' 
        ORDER BY start_time DESC 
        LIMIT 1
    """)
    latest_collection = cursor.fetchone()
    
    if not latest_collection:
        print("✗ No completed collections found in database")
        conn.close()
        return None
    
    collection_id = latest_collection['collection_id']
    output_directory = latest_collection['output_directory']
    total_images = latest_collection['total_images']
    
    print(f"Latest collection: {collection_id}")
    print(f"Total images: {total_images}")
    print()
    
    # Step 1: Export camera data to JSON
    print("Step 1: Exporting camera metadata to JSON...")
    print("-" * 80)
    
    cursor.execute("SELECT * FROM cameras ORDER BY sort_order")
    cameras = cursor.fetchall()
    
    camera_data = []
    
    for camera in cameras:
        camera_id = camera['camera_id']
        
        # Get views for this camera
        cursor.execute("SELECT * FROM camera_views WHERE camera_id = ?", (camera_id,))
        views = cursor.fetchall()
        
        # Get images for this camera from the latest collection
        cursor.execute("""
            SELECT * FROM images 
            WHERE camera_id = ? AND collection_id = ?
            ORDER BY view_id, capture_round
        """, (camera_id, collection_id))
        images = cursor.fetchall()
        
        # Build view data with image paths
        view_data = []
        for view in views:
            view_id = view['view_id']
            view_images = [img for img in images if img['view_id'] == view_id]
            
            view_info = {
                'Id': view_id,
                'Url': view['url'],
                'Status': view['status'],
                'Description': view['description'],
                'Images': [
                    {
                        'filename': img['filename'],
                        'path': f"camera_images/{collection_id}/{img['filename']}",
                        'timestamp': img['timestamp'],
                        'capture_round': img['capture_round']
                    }
                    for img in view_images
                ]
            }
            view_data.append(view_info)
        
        # Build camera object
        camera_obj = {
            'Id': camera_id,
            'Source': camera['source'],
            'SourceId': camera['source_id'],
            'Roadway': camera['roadway'],
            'Direction': camera['direction'],
            'Latitude': camera['latitude'],
            'Longitude': camera['longitude'],
            'Location': camera['location'],
            'SortOrder': camera['sort_order'],
            'Views': view_data
        }
        camera_data.append(camera_obj)
    
    # Save camera data JSON
    output_path = public_dir / 'camera_scraper' / 'qew_cameras_with_images.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(camera_data, f, indent=2)
    
    print(f"✓ Exported {len(camera_data)} cameras to {output_path.name}")
    
    # Step 2: Copy images to public folder
    print()
    print("Step 2: Copying images to public folder...")
    print("-" * 80)
    
    source_dir = script_dir / output_directory
    dest_dir = public_dir / 'camera_images' / collection_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    if source_dir.exists():
        image_files = list(source_dir.glob('*.jpg'))
        for img_file in image_files:
            shutil.copy2(img_file, dest_dir / img_file.name)
        print(f"✓ Copied {len(image_files)} images to public/camera_images/{collection_id}/")
    else:
        print(f"✗ Source directory not found: {source_dir}")
        return None
    
    conn.close()
    
    print()
    print("=" * 80)
    print("✓ Web app data update complete!")
    print(f"  Collection: {collection_id}")
    print(f"  Cameras: {len(camera_data)}")
    print(f"  Images: {len(image_files)}")
    print()
    print("The React app will now display the latest camera images.")
    
    return {
        'collection_id': collection_id,
        'cameras': len(camera_data),
        'images': len(image_files)
    }


if __name__ == '__main__':
    update_webapp_with_latest_data()


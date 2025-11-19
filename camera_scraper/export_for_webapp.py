"""
Export camera data from SQLite database to JSON format for web app
Generates camera metadata and image paths for the React map application
"""
import sqlite3
import json
import os
from pathlib import Path


def export_camera_data_for_webapp(db_path='camera_data.db', output_dir='../public'):
    """
    Export camera data and image references from database to JSON files
    for use in the React web application
    """
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
        print("No completed collections found in database")
        conn.close()
        return
    
    collection_id = latest_collection['collection_id']
    output_directory = latest_collection['output_directory']
    
    print(f"Using collection: {collection_id}")
    print(f"Output directory: {output_directory}")
    print(f"Total images: {latest_collection['total_images']}")
    print()
    
    # Get all cameras with their views and images
    cursor.execute("SELECT * FROM cameras ORDER BY sort_order")
    cameras = cursor.fetchall()
    
    camera_data = []
    image_map = {}
    
    for camera in cameras:
        camera_id = camera['camera_id']
        
        # Get views for this camera
        cursor.execute("SELECT * FROM camera_views WHERE camera_id = ?", (camera_id,))
        views = cursor.fetchall()
        
        # Get images for this camera from the latest collection
        # Order by timestamp DESC to get most recent images first
        cursor.execute("""
            SELECT * FROM images
            WHERE camera_id = ? AND collection_id = ?
            ORDER BY view_id, timestamp DESC, capture_round DESC
        """, (camera_id, collection_id))
        images = cursor.fetchall()
        
        # Build view data with image paths
        view_data = []
        for view in views:
            view_id = view['view_id']
            
            # Find images for this view
            view_images = [img for img in images if img['view_id'] == view_id]
            
            view_info = {
                'Id': view_id,
                'Url': view['url'],
                'Status': view['status'],
                'Description': view['description'],
                'Images': []
            }
            
            # Add image paths
            for img in view_images:
                # Path relative to public folder
                # output_directory already contains 'camera_images\collection_id'
                image_path = f"{output_directory.replace(chr(92), '/')}/{img['filename']}"
                view_info['Images'].append({
                    'filename': img['filename'],
                    'path': image_path,
                    'timestamp': img['timestamp'],
                    'capture_round': img['capture_round']
                })
            
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
        
        # Also build a simple camera_id -> images mapping
        if images:
            image_map[str(camera_id)] = [
                {
                    'view_id': img['view_id'],
                    'filename': img['filename'],
                    'path': f"{output_directory.replace(chr(92), '/')}/{img['filename']}",
                    'description': img['view_description']
                }
                for img in images
            ]
    
    # Save camera data JSON
    output_path = Path(output_dir) / 'camera_scraper' / 'qew_cameras_with_images.json'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(camera_data, f, indent=2)
    
    print(f"✓ Exported {len(camera_data)} cameras to {output_path}")
    
    # Save simple image map
    image_map_path = Path(output_dir) / 'camera_images' / 'camera_image_map.json'
    image_map_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(image_map_path, 'w') as f:
        json.dump({
            'collection_id': collection_id,
            'collection_directory': output_directory,
            'total_cameras': len(camera_data),
            'total_images': latest_collection['total_images'],
            'cameras': image_map
        }, f, indent=2)
    
    print(f"✓ Exported image map to {image_map_path}")
    
    conn.close()
    
    return {
        'collection_id': collection_id,
        'cameras_exported': len(camera_data),
        'images_exported': latest_collection['total_images']
    }


if __name__ == '__main__':
    print("QEW Camera Data Export for Web App")
    print("=" * 80)
    print()

    # Get the script directory
    script_dir = Path(__file__).parent
    db_path = script_dir / 'camera_data.db'
    output_dir = script_dir.parent / 'public'

    result = export_camera_data_for_webapp(str(db_path), str(output_dir))

    if result:
        print()
        print("=" * 80)
        print("Export complete!")
        print(f"Collection: {result['collection_id']}")
        print(f"Cameras: {result['cameras_exported']}")
        print(f"Images: {result['images_exported']}")


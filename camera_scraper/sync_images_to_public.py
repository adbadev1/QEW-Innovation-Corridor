"""
Sync the latest camera image collection to the public folder for the web app
"""
import sqlite3
import shutil
from pathlib import Path


def sync_latest_collection_to_public(db_path='camera_data.db'):
    """
    Copy the latest completed collection's images to the public folder
    """
    # Get script directory
    script_dir = Path(__file__).parent
    db_full_path = script_dir / db_path
    
    # Connect to database
    conn = sqlite3.connect(db_full_path)
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
    
    print(f"Latest collection: {collection_id}")
    print(f"Source directory: {output_directory}")
    print(f"Total images: {latest_collection['total_images']}")
    print()
    
    # Source and destination paths
    source_dir = script_dir / output_directory
    public_dir = script_dir.parent / 'public' / 'camera_images' / collection_id
    
    # Create public directory if it doesn't exist
    public_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy all images
    if source_dir.exists():
        image_files = list(source_dir.glob('*.jpg'))
        print(f"Copying {len(image_files)} images to public folder...")
        
        for img_file in image_files:
            dest_file = public_dir / img_file.name
            shutil.copy2(img_file, dest_file)
        
        print(f"✓ Copied {len(image_files)} images to {public_dir}")
    else:
        print(f"✗ Source directory not found: {source_dir}")
    
    conn.close()
    
    return {
        'collection_id': collection_id,
        'images_copied': len(image_files) if source_dir.exists() else 0,
        'destination': str(public_dir)
    }


if __name__ == '__main__':
    print("QEW Camera Images Sync to Public Folder")
    print("=" * 80)
    print()
    
    result = sync_latest_collection_to_public()
    
    if result:
        print()
        print("=" * 80)
        print("Sync complete!")
        print(f"Collection: {result['collection_id']}")
        print(f"Images copied: {result['images_copied']}")
        print(f"Destination: {result['destination']}")


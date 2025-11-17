"""
Cleanup Script - Delete all processed data and images
Run this to start fresh with the new folder structure
"""
import sqlite3
import shutil
from pathlib import Path


def cleanup_all_data():
    """Delete all processed data and images"""
    
    print("🗑️  Cleaning up old data and images...")
    print("=" * 60)
    
    # 1. Clear database
    db_path = Path('data/camera_directions.db')
    if db_path.exists():
        print(f"\n📁 Found database: {db_path}")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Count existing records
        cursor.execute('SELECT COUNT(*) FROM ai_direction_assessments')
        count = cursor.fetchone()[0]
        print(f"   Records in database: {count}")
        
        # Delete all records
        cursor.execute('DELETE FROM ai_direction_assessments')
        conn.commit()
        conn.close()
        
        print(f"   ✅ Deleted {count} records from database")
    else:
        print(f"\n📁 No database found at {db_path}")
    
    # 2. Delete old image folders
    old_folders = [
        Path('satellite_images'),
        Path('camera_images'),
        Path('data/images')
    ]
    
    for folder in old_folders:
        if folder.exists():
            print(f"\n📁 Found old folder: {folder}")
            
            # Count files
            file_count = len(list(folder.rglob('*.*')))
            print(f"   Files in folder: {file_count}")
            
            # Delete folder
            shutil.rmtree(folder)
            print(f"   ✅ Deleted folder and all contents")
        else:
            print(f"\n📁 Folder not found: {folder}")
    
    # 3. Create fresh images directory
    images_dir = Path('data/images')
    images_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n✅ Created fresh images directory: {images_dir}")
    
    print("\n" + "=" * 60)
    print("✅ Cleanup complete! Ready for fresh processing.")
    print("\nNew folder structure will be:")
    print("  data/images/")
    print("    ├── cam1_v1/")
    print("    │   ├── satellite.jpg")
    print("    │   └── camera.jpg")
    print("    ├── cam1_v2/")
    print("    │   ├── satellite.jpg")
    print("    │   └── camera.jpg")
    print("    └── ...")
    print("=" * 60)


if __name__ == '__main__':
    # Ask for confirmation
    print("\n⚠️  WARNING: This will delete ALL processed data and images!")
    print("   - All records in the database")
    print("   - All satellite images")
    print("   - All camera images")
    print()
    
    response = input("Are you sure you want to continue? (yes/no): ").strip().lower()
    
    if response == 'yes':
        cleanup_all_data()
    else:
        print("\n❌ Cleanup cancelled.")


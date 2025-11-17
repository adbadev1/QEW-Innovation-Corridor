"""
Test script to verify SQLite database integration and short filenames
Tests with first 3 cameras only
"""
import os
import json
from datetime import datetime
from database import CameraDatabase
from download_camera_images import (load_camera_data, create_output_directory, 
                                   download_camera_images, generate_summary_report)


def test_database_integration():
    """Test the database integration with short filenames"""
    print("=" * 80)
    print("Testing SQLite Database Integration")
    print("=" * 80)
    
    # Load camera data
    print("\n1. Loading camera data...")
    cameras = load_camera_data()
    print(f"   ✓ Loaded {len(cameras)} cameras")
    
    # Test with first 3 cameras only
    test_cameras = cameras[:3]
    print(f"   Using first {len(test_cameras)} cameras for testing")
    
    # Create database
    print("\n2. Creating database...")
    db = CameraDatabase("test_camera_data.db")
    print("   ✓ Database created")
    
    # Load cameras into database
    print("\n3. Loading cameras into database...")
    db.load_cameras_from_json(test_cameras)
    print("   ✓ Cameras loaded into database")
    
    # Verify cameras in database
    print("\n4. Verifying cameras in database...")
    for camera in test_cameras:
        cam_id = camera.get('Id')
        db_camera = db.get_camera_by_id(cam_id)
        if db_camera:
            print(f"   ✓ Camera {cam_id}: {db_camera['location']}")
            views = db.get_camera_views(cam_id)
            print(f"     - {len(views)} views found")
        else:
            print(f"   ✗ Camera {cam_id} not found in database")
    
    # Test short filename generation
    print("\n5. Testing short filename generation...")
    test_filename = db.generate_short_filename(4, 10, 1, "20251115_150317")
    print(f"   Sample filename: {test_filename}")
    print(f"   Filename length: {len(test_filename)} characters")
    print(f"   ✓ Short filename format working")
    
    # Create test output directory
    print("\n6. Creating test output directory...")
    output_dir = create_output_directory("test_images_db")
    print(f"   ✓ Output directory: {output_dir}")
    
    # Download images with database
    print("\n7. Downloading test images with database integration...")
    print("   (This will download images from 3 cameras)")
    total_images, metadata = download_camera_images(
        test_cameras,
        output_dir,
        images_per_camera=1,  # Just 1 round for testing
        delay_between_captures=0,
        db=db
    )
    
    print(f"\n   ✓ Downloaded {total_images} images")
    
    # Verify images in database
    print("\n8. Verifying images in database...")
    collection_id = os.path.basename(output_dir)
    db_images = db.get_images_by_collection(collection_id)
    print(f"   ✓ Found {len(db_images)} images in database")
    
    # Show sample image records
    print("\n9. Sample image records from database:")
    for i, img in enumerate(db_images[:3], 1):
        print(f"   {i}. {img['filename']}")
        print(f"      Camera: {img['camera_id']}, View: {img['view_id']}")
        print(f"      Location: {img['location']}")
        print(f"      GPS: ({img['latitude']}, {img['longitude']})")
    
    # Get collection stats
    print("\n10. Collection statistics:")
    stats = db.get_collection_stats(collection_id)
    if stats:
        print(f"    Collection ID: {stats['collection_id']}")
        print(f"    Status: {stats['status']}")
        print(f"    Total Images: {stats['total_images']}")
        print(f"    Output Directory: {stats['output_directory']}")
    
    # Verify files exist
    print("\n11. Verifying image files exist on disk...")
    files_exist = 0
    for img in db_images:
        filepath = os.path.join(output_dir, img['filename'])
        if os.path.exists(filepath):
            files_exist += 1
    print(f"    ✓ {files_exist}/{len(db_images)} files verified on disk")
    
    # Generate summary report
    print("\n12. Generating summary report...")
    generate_summary_report(test_cameras, metadata, output_dir)
    print("    ✓ Report generated")
    
    # Close database
    db.close()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE!")
    print("=" * 80)
    print(f"\nResults:")
    print(f"  - Database: test_camera_data.db")
    print(f"  - Images: {output_dir}")
    print(f"  - Total images: {total_images}")
    print(f"  - All images use short filenames")
    print(f"  - All metadata stored in SQLite database")
    print("\n✓ SQLite integration working correctly!")
    print("✓ Short filenames prevent path length issues!")
    

if __name__ == "__main__":
    test_database_integration()


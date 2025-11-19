"""
Test Relative Path Storage in Databases
Verifies that databases store relative paths and convert to absolute when retrieving
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from fastapi_backend.database.camera_db import CameraDatabase
from fastapi_backend.database.direction_db import DirectionDatabase
from fastapi_backend.config import BASE_DIR

def test_camera_db_paths():
    """Test camera database path conversion"""
    print("=" * 80)
    print("Testing Camera Database - Relative Path Storage")
    print("=" * 80)
    print()
    
    db = CameraDatabase()
    
    # Test path conversion methods
    print("1. Testing path conversion methods:")
    print(f"   BASE_DIR: {BASE_DIR}")
    print()
    
    # Test absolute to relative
    test_abs_path = str(Path(BASE_DIR) / "camera_scraper" / "camera_images" / "test.jpg")
    rel_path = db._to_relative_path(test_abs_path)
    print(f"   Absolute: {test_abs_path}")
    print(f"   Relative: {rel_path}")
    print()
    
    # Test relative to absolute
    abs_path = db._to_absolute_path(rel_path)
    print(f"   Back to Absolute: {abs_path}")
    print()
    
    # Verify they match
    if Path(test_abs_path).resolve() == Path(abs_path).resolve():
        print("   ✓ Path conversion works correctly!")
    else:
        print("   ✗ Path conversion failed!")
    
    print()
    print("2. Testing collection creation with relative paths:")
    
    # Create a test collection
    test_output_dir = str(Path(BASE_DIR) / "camera_scraper" / "camera_images" / "test_collection")
    collection_id = "test_collection_001"
    
    try:
        db.create_collection(collection_id, test_output_dir)
        print(f"   ✓ Created collection: {collection_id}")
        
        # Retrieve and check
        collection = db.get_collection_stats(collection_id)
        if collection:
            stored_path = collection['output_directory']
            print(f"   Retrieved path: {stored_path}")
            
            # Check if it's absolute (should be converted back)
            if Path(stored_path).is_absolute():
                print("   ✓ Retrieved path is absolute (as expected)")
            else:
                print("   ✗ Retrieved path is not absolute")
            
            # Check the raw database value
            db.cursor.execute('SELECT output_directory FROM collections WHERE collection_id = ?', (collection_id,))
            raw_row = db.cursor.fetchone()
            raw_path = raw_row[0]
            print(f"   Raw DB value: {raw_path}")
            
            if not Path(raw_path).is_absolute():
                print("   ✓ Database stores relative path!")
            else:
                print("   ✗ Database stores absolute path")
        
        # Clean up
        db.cursor.execute('DELETE FROM collections WHERE collection_id = ?', (collection_id,))
        db.conn.commit()
        print("   ✓ Test collection cleaned up")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
    
    print()

def test_direction_db_paths():
    """Test direction database path conversion"""
    print("=" * 80)
    print("Testing Direction Database - Relative Path Storage")
    print("=" * 80)
    print()
    
    db = DirectionDatabase()
    
    print("1. Testing path conversion methods:")
    print(f"   BASE_DIR: {BASE_DIR}")
    print()
    
    # Test absolute to relative
    test_sat_path = str(Path(BASE_DIR) / "ai_camera_direction" / "data" / "images" / "satellite" / "test.jpg")
    rel_path = db._to_relative_path(test_sat_path)
    print(f"   Absolute: {test_sat_path}")
    print(f"   Relative: {rel_path}")
    print()
    
    # Test relative to absolute
    abs_path = db._to_absolute_path(rel_path)
    print(f"   Back to Absolute: {abs_path}")
    print()
    
    # Verify they match
    if Path(test_sat_path).resolve() == Path(abs_path).resolve():
        print("   ✓ Path conversion works correctly!")
    else:
        print("   ✗ Path conversion failed!")
    
    print()
    print("2. Testing assessment creation with relative paths:")
    
    # Create a test assessment
    test_assessment = {
        'camera_id': 9999,
        'view_id': 1,
        'location': 'Test Location',
        'satellite_image_path': str(Path(BASE_DIR) / "ai_camera_direction" / "data" / "images" / "satellite" / "test_sat.jpg"),
        'camera_image_path': str(Path(BASE_DIR) / "ai_camera_direction" / "data" / "images" / "camera" / "test_cam.jpg"),
        'direction': 'North',
        'status': 'completed'
    }
    
    try:
        db.insert_assessment(test_assessment)
        print(f"   ✓ Created assessment for camera {test_assessment['camera_id']}")
        
        # Retrieve and check
        assessment = db.get_assessment(test_assessment['camera_id'], test_assessment['view_id'])
        if assessment:
            sat_path = assessment['satellite_image_path']
            cam_path = assessment['camera_image_path']
            print(f"   Retrieved satellite path: {sat_path}")
            print(f"   Retrieved camera path: {cam_path}")
            
            # Check if they're absolute (should be converted back)
            if Path(sat_path).is_absolute() and Path(cam_path).is_absolute():
                print("   ✓ Retrieved paths are absolute (as expected)")
            else:
                print("   ✗ Retrieved paths are not absolute")
            
            # Check the raw database values
            db.cursor.execute('''
                SELECT satellite_image_path, camera_image_path 
                FROM ai_direction_assessments 
                WHERE camera_id = ? AND view_id = ?
            ''', (test_assessment['camera_id'], test_assessment['view_id']))
            raw_row = db.cursor.fetchone()
            raw_sat = raw_row[0]
            raw_cam = raw_row[1]
            print(f"   Raw DB satellite: {raw_sat}")
            print(f"   Raw DB camera: {raw_cam}")
            
            if not Path(raw_sat).is_absolute() and not Path(raw_cam).is_absolute():
                print("   ✓ Database stores relative paths!")
            else:
                print("   ✗ Database stores absolute paths")
        
        # Clean up
        db.cursor.execute('DELETE FROM ai_direction_assessments WHERE camera_id = ?', (test_assessment['camera_id'],))
        db.conn.commit()
        print("   ✓ Test assessment cleaned up")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print()

if __name__ == "__main__":
    test_camera_db_paths()
    test_direction_db_paths()
    
    print("=" * 80)
    print("✅ Relative Path Storage Tests Complete!")
    print("=" * 80)
    print()
    print("Summary:")
    print("- Databases now store RELATIVE paths (portable)")
    print("- API methods return ABSOLUTE paths (for application use)")
    print("- Database files can be moved to different directories/systems")
    print()


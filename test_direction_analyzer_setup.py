"""Test direction analyzer setup"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 80)
print("Testing Direction Analyzer Setup")
print("=" * 80)

# Test 1: Check .env file loading
print("\n1. Testing .env file loading...")
from fastapi_backend.config import CLAUDE_API_KEY, GEMINI_API_KEY, GOOGLE_MAPS_API_KEY

print(f"   CLAUDE_API_KEY: {'✓ Loaded' if CLAUDE_API_KEY else '✗ Not found'}")
print(f"   GEMINI_API_KEY: {'✓ Loaded' if GEMINI_API_KEY else '✗ Not found'}")
print(f"   GOOGLE_MAPS_API_KEY: {'✓ Loaded' if GOOGLE_MAPS_API_KEY else '✗ Not found'}")

if GOOGLE_MAPS_API_KEY:
    print(f"   Google Maps API Key: {GOOGLE_MAPS_API_KEY[:20]}...")

# Test 2: Check database connections
print("\n2. Testing database connections...")
from fastapi_backend.database import CameraDatabase, DirectionDatabase

camera_db = CameraDatabase()
direction_db = DirectionDatabase()

# Get camera count
cameras = camera_db.get_all_cameras()
print(f"   Camera database: ✓ {len(cameras)} cameras found")

# Get pending count
pending = direction_db.get_pending_cameras()
print(f"   Direction database: ✓ {len(pending)} cameras pending analysis")

# Test 3: Check service imports
print("\n3. Testing service imports...")
try:
    from fastapi_backend.services.direction_analyzer import DirectionAnalyzerService
    from fastapi_backend.services.satellite_fetcher import SatelliteFetcher
    from fastapi_backend.services.camera_fetcher import CameraFetcher
    print("   ✓ All services imported successfully")
except Exception as e:
    print(f"   ✗ Import error: {e}")

# Test 4: Test timestamped folder creation
print("\n4. Testing timestamped folder creation...")
try:
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    analysis_folder = f"data/images/analysis_{timestamp}"
    Path(analysis_folder).mkdir(parents=True, exist_ok=True)
    print(f"   ✓ Created folder: {analysis_folder}")
    
    # Test camera folder creation
    test_camera_folder = Path(analysis_folder) / "cam4_v10"
    test_camera_folder.mkdir(parents=True, exist_ok=True)
    print(f"   ✓ Created camera folder: {test_camera_folder}")
    
except Exception as e:
    print(f"   ✗ Folder creation error: {e}")

# Test 5: Check if old images folder exists
print("\n5. Checking for existing images folders...")
old_images_folder = Path("ai_camera_direction/data/images")
if old_images_folder.exists():
    # Count camera folders
    camera_folders = [f for f in old_images_folder.iterdir() if f.is_dir() and f.name.startswith('cam')]
    print(f"   ✓ Found old images folder: {old_images_folder}")
    print(f"   ✓ Contains {len(camera_folders)} camera folders")
    
    # Show first 5 camera folders
    if camera_folders:
        print("   Sample folders:")
        for folder in camera_folders[:5]:
            sat_img = folder / "satellite.jpg"
            cam_img = folder / "camera.jpg"
            print(f"     - {folder.name}: sat={'✓' if sat_img.exists() else '✗'}, cam={'✓' if cam_img.exists() else '✗'}")
else:
    print(f"   ✗ Old images folder not found: {old_images_folder}")

# Test 6: Check old database
print("\n6. Checking old direction database...")
old_db_path = Path("ai_camera_direction/data/camera_directions.db")
if old_db_path.exists():
    import sqlite3
    conn = sqlite3.connect(str(old_db_path))
    c = conn.cursor()
    
    # Get table names
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in c.fetchall()]
    print(f"   ✓ Found old database: {old_db_path}")
    print(f"   Tables: {tables}")
    
    # Get assessment count
    if 'ai_direction_assessments' in tables:
        c.execute("SELECT COUNT(*) FROM ai_direction_assessments")
        count = c.fetchone()[0]
        print(f"   ✓ Contains {count} assessments")
        
        # Show sample
        if count > 0:
            c.execute("SELECT camera_id, view_id, direction, heading_degrees FROM ai_direction_assessments LIMIT 3")
            print("   Sample assessments:")
            for row in c.fetchall():
                print(f"     - Camera {row[0]}, View {row[1]}: {row[2]} ({row[3]}°)")
    
    conn.close()
else:
    print(f"   ✗ Old database not found: {old_db_path}")

print("\n" + "=" * 80)
print("Setup test complete!")
print("=" * 80)


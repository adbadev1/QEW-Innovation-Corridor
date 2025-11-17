"""
Test script to verify setup
"""
import sys
from pathlib import Path

print("=" * 80)
print("AI CAMERA DIRECTION ASSESSMENT - SETUP TEST")
print("=" * 80)

# Test 1: Check Python version
print("\n1. Python Version:")
print(f"   {sys.version}")
if sys.version_info < (3, 8):
    print("   ❌ Python 3.8+ required")
else:
    print("   ✓ Python version OK")

# Test 2: Check required packages
print("\n2. Required Packages:")
packages = {
    'anthropic': 'Claude API client',
    'PyQt6': 'GUI framework',
    'requests': 'HTTP library',
    'PIL': 'Image processing'
}

for package, description in packages.items():
    try:
        if package == 'PIL':
            import PIL
        else:
            __import__(package)
        print(f"   ✓ {package:15} - {description}")
    except ImportError:
        print(f"   ❌ {package:15} - {description} (NOT INSTALLED)")

# Test 3: Check directory structure
print("\n3. Directory Structure:")
required_dirs = [
    'backend',
    'frontend',
    'satellite_images',
    'camera_images',
    'data'
]

for dir_name in required_dirs:
    dir_path = Path(dir_name)
    if dir_path.exists():
        print(f"   ✓ {dir_name}/")
    else:
        print(f"   ❌ {dir_name}/ (MISSING)")
        dir_path.mkdir(exist_ok=True)
        print(f"      Created {dir_name}/")

# Test 4: Check backend modules
print("\n4. Backend Modules:")
backend_modules = [
    'database',
    'claude_client',
    'satellite_fetcher',
    'camera_fetcher',
    'processor'
]

for module in backend_modules:
    try:
        exec(f"from backend.{module} import *")
        print(f"   ✓ backend.{module}")
    except Exception as e:
        print(f"   ❌ backend.{module} - {e}")

# Test 5: Check source database
print("\n5. Source Database:")
source_db = Path("../camera_scraper/camera_data.db")
if source_db.exists():
    print(f"   ✓ Found: {source_db}")
    
    # Check database contents
    import sqlite3
    conn = sqlite3.connect(str(source_db))
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM cameras")
    camera_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM camera_views")
    view_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"   ✓ Cameras: {camera_count}")
    print(f"   ✓ Views: {view_count}")
else:
    print(f"   ❌ Not found: {source_db}")
    print("      Please run camera_scraper first to create the database")

# Test 6: Test database creation
print("\n6. Test Database Creation:")
try:
    from backend.database import DirectionDatabase
    
    test_db = DirectionDatabase('data/test.db')
    print("   ✓ Database created successfully")
    
    # Test insert
    test_assessment = {
        'camera_id': 999,
        'view_id': 999,
        'direction': 'N',
        'confidence_score': 0.95,
        'heading_degrees': 0.0
    }
    test_db.insert_assessment(test_assessment)
    print("   ✓ Test insert successful")
    
    # Test retrieve
    result = test_db.get_assessment(999, 999)
    if result and result['direction'] == 'N':
        print("   ✓ Test retrieve successful")
    
    test_db.close()
    
    # Clean up
    Path('data/test.db').unlink()
    print("   ✓ Test database cleaned up")

except Exception as e:
    print(f"   ❌ Database test failed: {e}")

# Summary
print("\n" + "=" * 80)
print("SETUP TEST COMPLETE")
print("=" * 80)
print("\nNext steps:")
print("1. Get Claude API key from: https://console.anthropic.com/")
print("2. (Optional) Get Google Maps API key from: https://console.cloud.google.com/")
print("3. Run: python main.py")
print("=" * 80)


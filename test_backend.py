"""
Test script to verify FastAPI backend setup
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from fastapi_backend import config
        print("✓ Config module imported")
        
        from fastapi_backend.database import CameraDatabase, DirectionDatabase
        print("✓ Database modules imported")
        
        from fastapi_backend.services import CameraScraperService, DirectionAnalyzerService
        print("✓ Service modules imported")
        
        from fastapi_backend.main import app
        print("✓ FastAPI app imported")
        
        print("\n✅ All imports successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_config():
    """Test configuration"""
    print("\nTesting configuration...")
    
    try:
        from fastapi_backend import config
        
        print(f"  Camera DB Path: {config.CAMERA_DB_PATH}")
        print(f"  Direction DB Path: {config.DIRECTION_DB_PATH}")
        print(f"  Camera Images Dir: {config.CAMERA_IMAGES_DIR}")
        print(f"  Host: {config.HOST}")
        print(f"  Port: {config.PORT}")
        
        print("\n✅ Configuration loaded successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Configuration test failed: {e}")
        return False


def test_database_connection():
    """Test database connections"""
    print("\nTesting database connections...")
    
    try:
        from fastapi_backend.database import CameraDatabase, DirectionDatabase
        
        # Test camera database
        camera_db = CameraDatabase()
        cameras = camera_db.get_all_cameras()
        print(f"  ✓ Camera DB connected - {len(cameras)} cameras found")
        camera_db.close()
        
        # Test direction database
        direction_db = DirectionDatabase()
        assessments = direction_db.get_all_assessments()
        print(f"  ✓ Direction DB connected - {len(assessments)} assessments found")
        direction_db.close()
        
        print("\n✅ Database connections successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_services():
    """Test service initialization"""
    print("\nTesting services...")
    
    try:
        from fastapi_backend.services import CameraScraperService, DirectionAnalyzerService
        
        # Test camera scraper service
        scraper = CameraScraperService()
        status = scraper.get_status()
        print(f"  ✓ Camera Scraper Service initialized - Status: {status['status']}")
        
        # Test direction analyzer service
        analyzer = DirectionAnalyzerService()
        status = analyzer.get_status()
        print(f"  ✓ Direction Analyzer Service initialized - Status: {status['status']}")
        
        print("\n✅ Services initialized successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 80)
    print("FastAPI Backend - Setup Verification")
    print("=" * 80)
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Database Connections", test_database_connection()))
    results.append(("Services", test_services()))
    
    print("\n" + "=" * 80)
    print("Test Results Summary")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<50} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("=" * 80)
    if all_passed:
        print("✅ All tests passed! Backend is ready to use.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and add your API keys")
        print("2. Run: python start_backend.py")
        print("3. Visit: http://localhost:8000/docs")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 80)
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


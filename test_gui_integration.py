"""
Test GUI Integration - Phase 2 Verification
Tests that the integrated GUIs can be imported and initialized
"""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all GUI modules can be imported"""
    print("=" * 80)
    print("Phase 2: GUI Integration - Verification Test")
    print("=" * 80)
    print()
    
    try:
        print("1. Testing backend_manager import...")
        from gui.backend_manager import BackendManager
        print("   ✓ backend_manager imported successfully")
        
        print("\n2. Testing camera_scraper_gui import...")
        from gui.camera_scraper_gui import QEWCameraGUI, CameraCollectionWorker
        print("   ✓ camera_scraper_gui imported successfully")
        
        print("\n3. Testing direction_analyzer_gui import...")
        from gui.direction_analyzer_gui import MainWindow, ProcessorThread
        print("   ✓ direction_analyzer_gui imported successfully")
        
        print("\n4. Testing BackendManager initialization...")
        backend_manager = BackendManager()
        print(f"   ✓ BackendManager initialized")
        print(f"   - API URL: {backend_manager.get_api_url('/test')}")
        
        print("\n" + "=" * 80)
        print("✅ All imports successful!")
        print("=" * 80)
        print()
        print("Phase 2 is ready to use!")
        print()
        print("To launch the GUIs:")
        print("  - Camera Scraper:      python launch_camera_scraper.py")
        print("  - Direction Analyzer:  python launch_direction_analyzer.py")
        print()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)


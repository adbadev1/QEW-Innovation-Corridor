"""
Quick test script to verify camera image download functionality
Downloads images from first 3 cameras only
"""
import requests
import json
import os
from datetime import datetime

def test_camera_download():
    """Test downloading images from a few cameras"""
    print("Testing camera image download...")
    print("=" * 80)
    
    # Load camera data
    with open("qew_cameras_hamilton_mississauga.json", 'r') as f:
        cameras = json.load(f)
    
    # Test with first 3 cameras
    test_cameras = cameras[:3]
    
    # Create test output directory
    output_dir = "test_images"
    os.makedirs(output_dir, exist_ok=True)
    
    success_count = 0
    fail_count = 0
    
    for camera in test_cameras:
        location = camera.get('Location', 'Unknown')
        print(f"\nTesting: {location}")
        print(f"GPS: ({camera.get('Latitude')}, {camera.get('Longitude')})")
        
        for view in camera.get('Views', []):
            view_url = view.get('Url')
            view_desc = view.get('Description', 'Unknown')
            
            print(f"  View: {view_desc}")
            print(f"  URL: {view_url}")
            
            try:
                response = requests.get(view_url, timeout=10)
                response.raise_for_status()
                
                # Check content type
                content_type = response.headers.get('content-type', '')
                print(f"  Content-Type: {content_type}")
                
                if 'image' in content_type.lower():
                    # Save test image
                    filename = f"test_cam{camera['Id']}_view{view['Id']}.jpg"
                    filepath = os.path.join(output_dir, filename)
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    file_size = len(response.content)
                    print(f"  ✓ Downloaded successfully ({file_size:,} bytes)")
                    print(f"  Saved to: {filepath}")
                    success_count += 1
                else:
                    print(f"  ✗ Not an image (content-type: {content_type})")
                    fail_count += 1
                    
            except Exception as e:
                print(f"  ✗ Error: {e}")
                fail_count += 1
    
    print("\n" + "=" * 80)
    print("TEST RESULTS")
    print("=" * 80)
    print(f"Successful downloads: {success_count}")
    print(f"Failed downloads: {fail_count}")
    print(f"Test images saved to: {output_dir}/")
    
    if success_count > 0:
        print("\n✓ Camera download system is working!")
        print("You can now run 'python download_camera_images.py' to collect all images.")
    else:
        print("\n✗ No images were downloaded. Please check the camera URLs.")

if __name__ == "__main__":
    test_camera_download()


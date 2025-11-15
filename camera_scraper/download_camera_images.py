"""
Script to download images from MTO cameras along QEW corridor
Downloads 100+ images for hazard assessment and safety analysis
"""
import requests
import json
import os
import time
from datetime import datetime
from typing import List, Dict
import hashlib

def load_camera_data(filename: str = "qew_cameras_hamilton_mississauga.json") -> List[Dict]:
    """Load camera data from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)

def create_output_directory(base_dir: str = "camera_images") -> str:
    """Create directory for storing images"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(base_dir, f"qew_collection_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def sanitize_filename(text: str) -> str:
    """Sanitize text for use in filename"""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        text = text.replace(char, '_')
    return text.strip()

def download_image(url: str, output_path: str, timeout: int = 10) -> bool:
    """Download a single image from URL"""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        
        # Check if response is actually an image
        content_type = response.headers.get('content-type', '')
        if 'image' not in content_type.lower():
            print(f"  Warning: URL did not return an image (content-type: {content_type})")
            return False
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return True
    except Exception as e:
        print(f"  Error downloading {url}: {e}")
        return False

def download_camera_images(cameras: List[Dict], output_dir: str, 
                          images_per_camera: int = 3, 
                          delay_between_captures: int = 60):
    """
    Download images from all cameras
    
    Args:
        cameras: List of camera dictionaries
        output_dir: Directory to save images
        images_per_camera: Number of times to capture each camera view
        delay_between_captures: Seconds to wait between captures (for temporal diversity)
    """
    total_images = 0
    metadata = []
    
    print(f"\nStarting image collection...")
    print(f"Target: {len(cameras)} cameras x {images_per_camera} captures")
    print(f"Output directory: {output_dir}\n")
    
    for capture_round in range(images_per_camera):
        print(f"\n{'='*80}")
        print(f"Capture Round {capture_round + 1} of {images_per_camera}")
        print(f"{'='*80}\n")
        
        for camera_idx, camera in enumerate(cameras, 1):
            camera_id = camera.get('Id')
            location = camera.get('Location', 'Unknown')
            latitude = camera.get('Latitude')
            longitude = camera.get('Longitude')
            views = camera.get('Views', [])
            
            print(f"[{camera_idx}/{len(cameras)}] {location}")
            
            for view in views:
                view_id = view.get('Id')
                view_url = view.get('Url')
                view_desc = view.get('Description', 'Unknown')
                
                if not view_url:
                    continue
                
                # Create filename
                safe_location = sanitize_filename(location)
                safe_desc = sanitize_filename(view_desc)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"cam{camera_id}_view{view_id}_{safe_location}_{safe_desc}_round{capture_round+1}_{timestamp}.jpg"
                output_path = os.path.join(output_dir, filename)
                
                # Download image
                print(f"  Downloading view: {view_desc}...", end=" ")
                success = download_image(view_url, output_path)
                
                if success:
                    print("✓")
                    total_images += 1
                    
                    # Store metadata
                    metadata.append({
                        "filename": filename,
                        "camera_id": camera_id,
                        "view_id": view_id,
                        "location": location,
                        "latitude": latitude,
                        "longitude": longitude,
                        "view_description": view_desc,
                        "capture_round": capture_round + 1,
                        "timestamp": timestamp,
                        "url": view_url
                    })
                else:
                    print("✗")
                
                # Small delay between views
                time.sleep(1)
            
            # Small delay between cameras
            time.sleep(0.5)
        
        # Delay between capture rounds (except after last round)
        if capture_round < images_per_camera - 1:
            print(f"\nWaiting {delay_between_captures} seconds before next capture round...")
            time.sleep(delay_between_captures)
    
    # Save metadata
    metadata_file = os.path.join(output_dir, "image_metadata.json")
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Collection Complete!")
    print(f"{'='*80}")
    print(f"Total images downloaded: {total_images}")
    print(f"Metadata saved to: {metadata_file}")
    print(f"Images saved to: {output_dir}")
    
    return total_images, metadata

def generate_summary_report(cameras: List[Dict], metadata: List[Dict], output_dir: str):
    """Generate a summary report of the collection"""
    report_file = os.path.join(output_dir, "collection_report.txt")
    
    with open(report_file, 'w') as f:
        f.write("QEW CORRIDOR CAMERA IMAGE COLLECTION REPORT\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Collection Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Corridor: QEW Highway (Hamilton to Mississauga)\n\n")
        
        f.write(f"SUMMARY\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total Cameras: {len(cameras)}\n")
        f.write(f"Total Images Collected: {len(metadata)}\n")
        f.write(f"Total Camera Views: {sum(len(c.get('Views', [])) for c in cameras)}\n\n")
        
        f.write(f"CAMERA LOCATIONS\n")
        f.write("-" * 80 + "\n")
        for i, camera in enumerate(cameras, 1):
            f.write(f"{i}. {camera.get('Location')}\n")
            f.write(f"   GPS: ({camera.get('Latitude')}, {camera.get('Longitude')})\n")
            f.write(f"   Views: {len(camera.get('Views', []))}\n\n")
        
        f.write(f"\nPURPOSE\n")
        f.write("-" * 80 + "\n")
        f.write("These images are collected for:\n")
        f.write("- Hazard assessment and identification\n")
        f.write("- Proactive safety analysis\n")
        f.write("- AI-based image analysis for traffic safety\n")
    
    print(f"Summary report saved to: {report_file}")

def main():
    # Configuration
    IMAGES_PER_CAMERA = 3  # Number of times to capture each camera
    DELAY_BETWEEN_ROUNDS = 300  # 5 minutes between capture rounds (for temporal diversity)
    
    print("QEW Corridor Camera Image Collection")
    print("=" * 80)
    
    # Load camera data
    print("\nLoading camera data...")
    cameras = load_camera_data()
    print(f"Loaded {len(cameras)} cameras")
    
    # Create output directory
    output_dir = create_output_directory()
    
    # Estimate total images
    total_views = sum(len(c.get('Views', [])) for c in cameras)
    estimated_images = total_views * IMAGES_PER_CAMERA
    print(f"\nEstimated images to collect: {estimated_images}")
    print(f"This will take approximately {(IMAGES_PER_CAMERA - 1) * DELAY_BETWEEN_ROUNDS / 60:.1f} minutes")
    
    # Download images
    total_images, metadata = download_camera_images(
        cameras, 
        output_dir, 
        images_per_camera=IMAGES_PER_CAMERA,
        delay_between_captures=DELAY_BETWEEN_ROUNDS
    )
    
    # Generate summary report
    generate_summary_report(cameras, metadata, output_dir)
    
    print(f"\n{'='*80}")
    print("All done! Images ready for AI hazard assessment and safety analysis.")
    print(f"{'='*80}")

if __name__ == "__main__":
    main()


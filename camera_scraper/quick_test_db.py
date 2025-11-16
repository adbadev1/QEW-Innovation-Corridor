"""
Quick test to verify the updated system works with 2 cameras
"""
from download_camera_images import (load_camera_data, create_output_directory, 
                                   download_camera_images, generate_summary_report)
from database import CameraDatabase

print("Quick Test - Database Integration")
print("=" * 80)

# Load camera data
cameras = load_camera_data()
print(f"Loaded {len(cameras)} cameras")

# Test with just 2 cameras
test_cameras = cameras[:2]
print(f"Testing with {len(test_cameras)} cameras\n")

# Create output directory
output_dir = create_output_directory("quick_test_db")
print(f"Output directory: {output_dir}\n")

# Download images
total_images, metadata = download_camera_images(
    test_cameras,
    output_dir,
    images_per_camera=1,
    delay_between_captures=0
)

# Generate report
generate_summary_report(test_cameras, metadata, output_dir)

print("\n" + "=" * 80)
print("QUICK TEST COMPLETE!")
print("=" * 80)
print(f"Total images: {total_images}")
print(f"Output: {output_dir}")
print("\nCheck the database with: python query_database.py")


"""
Utility script to query the camera database
Allows viewing cameras, images, and collections
"""
import sys
from database import CameraDatabase


def print_separator(char="=", length=80):
    """Print a separator line"""
    print(char * length)


def show_all_cameras(db: CameraDatabase):
    """Show all cameras in the database"""
    print_separator()
    print("ALL CAMERAS")
    print_separator()
    
    db.cursor.execute("SELECT * FROM cameras ORDER BY camera_id")
    cameras = [dict(row) for row in db.cursor.fetchall()]
    
    if not cameras:
        print("No cameras found in database.")
        return
    
    for camera in cameras:
        print(f"\nCamera ID: {camera['camera_id']}")
        print(f"  Location: {camera['location']}")
        print(f"  Roadway: {camera['roadway']}")
        print(f"  GPS: ({camera['latitude']}, {camera['longitude']})")
        
        views = db.get_camera_views(camera['camera_id'])
        print(f"  Views: {len(views)}")
        for view in views:
            print(f"    - View {view['view_id']}: {view['description']}")


def show_all_collections(db: CameraDatabase):
    """Show all collections"""
    print_separator()
    print("ALL COLLECTIONS")
    print_separator()
    
    collections = db.get_all_collections()
    
    if not collections:
        print("No collections found in database.")
        return
    
    for coll in collections:
        print(f"\nCollection ID: {coll['collection_id']}")
        print(f"  Status: {coll['status']}")
        print(f"  Start Time: {coll['start_time']}")
        print(f"  End Time: {coll['end_time']}")
        print(f"  Total Images: {coll['total_images']}")
        print(f"  Output Directory: {coll['output_directory']}")


def show_collection_images(db: CameraDatabase, collection_id: str):
    """Show all images for a specific collection"""
    print_separator()
    print(f"IMAGES FOR COLLECTION: {collection_id}")
    print_separator()
    
    images = db.get_images_by_collection(collection_id)
    
    if not images:
        print(f"No images found for collection: {collection_id}")
        return
    
    print(f"\nTotal images: {len(images)}\n")
    
    for i, img in enumerate(images, 1):
        print(f"{i}. {img['filename']}")
        print(f"   Camera: {img['camera_id']} | View: {img['view_id']}")
        print(f"   Location: {img['location']}")
        print(f"   GPS: ({img['latitude']}, {img['longitude']})")
        print(f"   Timestamp: {img['timestamp']}")
        print()


def show_camera_images(db: CameraDatabase, camera_id: int):
    """Show all images for a specific camera"""
    print_separator()
    print(f"IMAGES FOR CAMERA: {camera_id}")
    print_separator()
    
    camera = db.get_camera_by_id(camera_id)
    if camera:
        print(f"Location: {camera['location']}\n")
    
    images = db.get_images_by_camera(camera_id)
    
    if not images:
        print(f"No images found for camera: {camera_id}")
        return
    
    print(f"Total images: {len(images)}\n")
    
    for i, img in enumerate(images, 1):
        print(f"{i}. {img['filename']}")
        print(f"   View: {img['view_id']} - {img['view_description']}")
        print(f"   Collection: {img['collection_id']}")
        print(f"   Timestamp: {img['timestamp']}")
        print()


def show_database_stats(db: CameraDatabase):
    """Show overall database statistics"""
    print_separator()
    print("DATABASE STATISTICS")
    print_separator()
    
    # Count cameras
    db.cursor.execute("SELECT COUNT(*) as count FROM cameras")
    camera_count = db.cursor.fetchone()['count']
    
    # Count views
    db.cursor.execute("SELECT COUNT(*) as count FROM camera_views")
    view_count = db.cursor.fetchone()['count']
    
    # Count images
    db.cursor.execute("SELECT COUNT(*) as count FROM images")
    image_count = db.cursor.fetchone()['count']
    
    # Count collections
    db.cursor.execute("SELECT COUNT(*) as count FROM collections")
    collection_count = db.cursor.fetchone()['count']
    
    print(f"\nTotal Cameras: {camera_count}")
    print(f"Total Views: {view_count}")
    print(f"Total Images: {image_count}")
    print(f"Total Collections: {collection_count}")
    print()


def main():
    """Main menu for database queries"""
    db = CameraDatabase()
    
    while True:
        print("\n" + "=" * 80)
        print("CAMERA DATABASE QUERY TOOL")
        print("=" * 80)
        print("\n1. Show all cameras")
        print("2. Show all collections")
        print("3. Show images for a collection")
        print("4. Show images for a camera")
        print("5. Show database statistics")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            show_all_cameras(db)
        elif choice == "2":
            show_all_collections(db)
        elif choice == "3":
            collection_id = input("Enter collection ID: ").strip()
            show_collection_images(db, collection_id)
        elif choice == "4":
            try:
                camera_id = int(input("Enter camera ID: ").strip())
                show_camera_images(db, camera_id)
            except ValueError:
                print("Invalid camera ID. Please enter a number.")
        elif choice == "5":
            show_database_stats(db)
        elif choice == "6":
            print("\nClosing database...")
            db.close()
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1-6.")


if __name__ == "__main__":
    main()


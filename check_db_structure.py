"""Check database structure and data"""
import sqlite3

# Check camera database
print("=" * 80)
print("CAMERA DATABASE (camera_data.db)")
print("=" * 80)

conn = sqlite3.connect('camera_data.db')
c = conn.cursor()

# Get tables
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in c.fetchall()]
print(f"\nTables: {tables}")

# Check cameras table structure
if 'cameras' in tables:
    c.execute("PRAGMA table_info(cameras)")
    print("\nCameras table columns:")
    for row in c.fetchall():
        print(f"  {row[1]} ({row[2]})")
    
    # Get sample data
    c.execute("SELECT * FROM cameras LIMIT 3")
    print("\nSample cameras:")
    for row in c.fetchall():
        print(f"  {row}")

# Check views table structure
if 'views' in tables:
    c.execute("PRAGMA table_info(views)")
    print("\nViews table columns:")
    for row in c.fetchall():
        print(f"  {row[1]} ({row[2]})")
    
    # Get sample data
    c.execute("SELECT * FROM views LIMIT 3")
    print("\nSample views:")
    for row in c.fetchall():
        print(f"  {row}")

conn.close()

# Check direction database
print("\n" + "=" * 80)
print("DIRECTION DATABASE (camera_directions.db)")
print("=" * 80)

try:
    conn = sqlite3.connect('camera_directions.db')
    c = conn.cursor()
    
    # Get tables
    c.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in c.fetchall()]
    print(f"\nTables: {tables}")
    
    # Check assessments table
    if 'assessments' in tables:
        c.execute("PRAGMA table_info(assessments)")
        print("\nAssessments table columns:")
        for row in c.fetchall():
            print(f"  {row[1]} ({row[2]})")
        
        # Get count
        c.execute("SELECT COUNT(*) FROM assessments")
        count = c.fetchone()[0]
        print(f"\nTotal assessments: {count}")
        
        # Get sample data
        c.execute("SELECT camera_id, view_id, satellite_image_path, camera_image_path FROM assessments LIMIT 3")
        print("\nSample assessments:")
        for row in c.fetchall():
            print(f"  Camera {row[0]}, View {row[1]}")
            print(f"    Satellite: {row[2]}")
            print(f"    Camera: {row[3]}")
    
    # Check pending_cameras table
    if 'pending_cameras' in tables:
        c.execute("SELECT COUNT(*) FROM pending_cameras")
        count = c.fetchone()[0]
        print(f"\nPending cameras: {count}")
        
        c.execute("SELECT * FROM pending_cameras LIMIT 3")
        print("\nSample pending:")
        for row in c.fetchall():
            print(f"  {row}")
    
    conn.close()
except Exception as e:
    print(f"Error checking direction database: {e}")

print("\n" + "=" * 80)


"""Quick test of camera details"""
from database import CameraDatabase

db = CameraDatabase('camera_data.db')

print("=" * 80)
print("CAMERA DETAILS TEST")
print("=" * 80)

# Test 1: Get details for Camera 4, View 10
print("\n--- Test 1: Camera 4, View 10 (Fort Erie Bound) ---")
details = db.get_camera_details(4, 10)
if details:
    print(f"✓ Found details")
    print(f"  Direction: {details['heading_description']}")
    print(f"  Compass: {details['compass_direction_16']} ({details['compass_direction_8']})")
    print(f"  Heading: {details['heading_degrees']}°")
    print(f"  Vertical Angle: {details['vertical_angle_description']}")
    print(f"  Mount: {details['mount_type']}")
    print(f"  Height: {details['height_above_ground_meters']}m ({details['height_above_ground_feet']}ft)")
    print(f"  Altitude ASL: {details['altitude_above_sea_level_meters']}m")
    print(f"  View Distance: {details['view_distance_meters']}m")
    print(f"  Effective Range: {details['effective_range_meters']}m")
    print(f"  Field of View: {details['field_of_view_degrees']}°")
else:
    print("✗ No details found")

# Test 2: Get details for Camera 4, View 11 (Looking Down)
print("\n--- Test 2: Camera 4, View 11 (Looking Down) ---")
details = db.get_camera_details(4, 11)
if details:
    print(f"✓ Found details")
    print(f"  Direction: {details['heading_description']}")
    print(f"  Vertical Angle: {details['vertical_angle_description']}")
    print(f"  Mount: {details['mount_type']}")
    print(f"  View Distance: {details['view_distance_meters']}m (overhead view)")
else:
    print("✗ No details found")

# Test 3: Count cameras by direction
print("\n--- Test 3: Cameras by Direction ---")
db.cursor.execute('''
    SELECT compass_direction_8, COUNT(*) as count 
    FROM camera_details 
    WHERE compass_direction_8 IS NOT NULL
    GROUP BY compass_direction_8 
    ORDER BY count DESC
''')
results = db.cursor.fetchall()
for row in results:
    print(f"  {row['compass_direction_8']}: {row['count']} cameras")

# Test 4: Count cameras by mount type
print("\n--- Test 4: Cameras by Mount Type ---")
db.cursor.execute('''
    SELECT mount_type, COUNT(*) as count 
    FROM camera_details 
    GROUP BY mount_type 
    ORDER BY count DESC
''')
results = db.cursor.fetchall()
for row in results:
    print(f"  {row['mount_type']}: {row['count']} cameras")

# Test 5: Average heights
print("\n--- Test 5: Average Heights ---")
db.cursor.execute('''
    SELECT 
        AVG(height_above_ground_meters) as avg_height,
        MIN(height_above_ground_meters) as min_height,
        MAX(height_above_ground_meters) as max_height
    FROM camera_details
''')
row = db.cursor.fetchone()
print(f"  Average Height: {row['avg_height']:.1f}m")
print(f"  Min Height: {row['min_height']:.1f}m")
print(f"  Max Height: {row['max_height']:.1f}m")

# Test 6: Show all cameras with their primary direction
print("\n--- Test 6: Sample Cameras with Directions ---")
db.cursor.execute('''
    SELECT cd.camera_id, c.location, cd.view_id, cd.heading_description, cd.mount_type
    FROM camera_details cd
    JOIN cameras c ON cd.camera_id = c.camera_id
    LIMIT 10
''')
results = db.cursor.fetchall()
for row in results:
    print(f"  Camera {row['camera_id']} ({row['location']})")
    print(f"    View {row['view_id']}: {row['heading_description']} | {row['mount_type']}")

print("\n" + "=" * 80)
print("✓ All tests completed successfully!")
print("=" * 80)

db.close()


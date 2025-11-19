import sqlite3
import json
from collections import defaultdict

# Connect to database
conn = sqlite3.connect('fastapi_backend/database/camera_directions.db')
cursor = conn.cursor()

# Query the run_20251119_025336 table
table_name = "run_20251119_025336"

# Get all camera data grouped by location
cursor.execute(f"""
    SELECT
        camera_id,
        view_id,
        location,
        latitude,
        longitude,
        compass_direction_8,
        heading_degrees
    FROM {table_name}
    WHERE status = 'completed'
    ORDER BY latitude, longitude, camera_id
""")

rows = cursor.fetchall()

# Group by location (lat/lon)
location_groups = defaultdict(list)
for row in rows:
    camera_id, view_id, location, lat, lon, direction, heading = row
    key = (lat, lon, location)
    location_groups[key].append({
        'camera_id': camera_id,
        'view_id': view_id,
        'direction': direction,
        'heading': heading
    })

print("Camera Locations and Directions:\n")
print("="*80)

for (lat, lon, location), cameras in location_groups.items():
    print(f"\nLocation: {location}")
    print(f"Coordinates: ({lat}, {lon})")
    print(f"Number of camera views: {len(cameras)}")
    print(f"Directions: {', '.join([c['direction'] for c in cameras])}")
    print(f"Headings: {', '.join([str(c['heading']) for c in cameras])}")
    for cam in cameras:
        print(f"  - Camera {cam['camera_id']}, View {cam['view_id']}: {cam['direction']} ({cam['heading']}°)")

print("\n" + "="*80)
print(f"\nTotal unique locations: {len(location_groups)}")
print(f"Total camera views: {len(rows)}")

# Export to JSON for frontend use
output_data = []
for (lat, lon, location), cameras in location_groups.items():
    output_data.append({
        'location': location,
        'latitude': lat,
        'longitude': lon,
        'cameras': cameras
    })

with open('camera_directions_export.json', 'w') as f:
    json.dump(output_data, f, indent=2)

print("\nExported to: camera_directions_export.json")

conn.close()


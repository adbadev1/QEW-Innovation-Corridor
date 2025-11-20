#!/usr/bin/env python3
"""
Fix camera directions to match Issue #17 requirements
Updates camera_directions table with correct headings
"""
import sqlite3
import sys

# Direction to heading mapping
DIRECTION_HEADINGS = {
    'N': 0,
    'NNE': 22.5,
    'NE': 45,
    'ENE': 67.5,
    'E': 90,
    'ESE': 112.5,
    'SE': 135,
    'SSE': 157.5,
    'S': 180,
    'SSW': 202.5,
    'SW': 225,
    'WSW': 247.5,
    'W': 270,
    'WNW': 292.5,
    'NW': 315,
    'NNW': 337.5
}

# Issue #17 Required Directions
# Format: (camera_id_string, required_direction, location)
ISSUE_17_CORRECTIONS = [
    ('C251', 'SW', 'QEW East of Erin Mills Parkway'),
    ('C250', 'W', 'QEW near Southbound Road/Erin Mills Parkway'),
    ('C249', 'SW', 'QEW West of Erin Mills Parkway'),
    ('C1159', 'SW', 'QEW near Winston Churchill Boulevard'),
    ('C247', 'SW', 'QEW West of Winston Churchill Boulevard'),
    ('C246', 'NW', 'QEW near Highway 403 (Oakville)'),
    ('C245', 'SW', 'QEW near Ford Drive'),
    ('C243', 'SW', 'QEW near Royal Windsor Drive'),
    ('C223', 'SW', 'QEW near Trafalgar Road'),
    ('C242', 'SW', 'QEW East of Dorval Drive'),
    ('C241', 'SW', 'QEW near Dorval Drive'),
    ('C238', 'SW', 'QEW near Third Line'),
    ('C239', 'SW', 'QEW East of Third Line'),
    ('C211', 'WNW', 'QEW near Millen Road'),
]

def main():
    db_path = 'qew_corridor.db'

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        print("=" * 80)
        print("Fixing Camera Directions Per Issue #17")
        print("=" * 80)
        print()

        updated_count = 0

        for camera_id_str, required_direction, location in ISSUE_17_CORRECTIONS:
            # Get the internal camera ID from cameras table
            cursor.execute(
                'SELECT id FROM cameras WHERE camera_id = ?',
                (camera_id_str,)
            )
            result = cursor.fetchone()

            if not result:
                print(f"❌ Camera {camera_id_str} not found in database")
                continue

            camera_internal_id = result[0]
            required_heading = DIRECTION_HEADINGS[required_direction]

            # Get current direction for comparison
            cursor.execute(
                '''SELECT heading, direction FROM camera_directions
                   WHERE camera_id = ? LIMIT 1''',
                (camera_internal_id,)
            )
            current = cursor.fetchone()
            current_heading = current[0] if current else None
            current_direction = current[1] if current else None

            # Update camera_directions table
            cursor.execute(
                '''UPDATE camera_directions
                   SET heading = ?, direction = ?, confidence = 'verified'
                   WHERE camera_id = ?''',
                (required_heading, required_direction, camera_internal_id)
            )

            rows_affected = cursor.rowcount

            if rows_affected > 0:
                print(f"✅ {camera_id_str}: {current_direction} ({current_heading:.1f}°) → {required_direction} ({required_heading:.1f}°)")
                print(f"   Location: {location}")
                print(f"   Updated {rows_affected} direction record(s)")
                updated_count += 1
            else:
                print(f"⚠️  {camera_id_str}: No direction records found to update")

            print()

        # Commit changes
        conn.commit()

        print("=" * 80)
        print(f"✅ Successfully updated {updated_count} cameras with Issue #17 directions")
        print("=" * 80)
        print()

        # Verify updates
        print("Verifying updates...")
        for camera_id_str, required_direction, _ in ISSUE_17_CORRECTIONS:
            cursor.execute(
                '''SELECT cd.heading, cd.direction
                   FROM camera_directions cd
                   JOIN cameras c ON cd.camera_id = c.id
                   WHERE c.camera_id = ?
                   LIMIT 1''',
                (camera_id_str,)
            )
            result = cursor.fetchone()
            if result:
                heading, direction = result
                expected_heading = DIRECTION_HEADINGS[required_direction]
                status = "✅" if heading == expected_heading and direction == required_direction else "❌"
                print(f"{status} {camera_id_str}: {direction} ({heading:.1f}°)")

        conn.close()

    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

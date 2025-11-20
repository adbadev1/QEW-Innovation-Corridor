"""
Seed Camera Direction Data from CSV
====================================

Imports camera direction analysis from camera_scraper/camera_directions_analysis.csv
into the database.

Usage:
    python seed_directions.py
"""

import asyncio
import csv
import sys
from pathlib import Path
from sqlalchemy import select

# Add current directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from database import AsyncSessionLocal
from models import Camera, CameraDirection
from config import settings


async def seed_directions():
    """Seed camera directions from CSV file"""

    # Path to CSV file (relative to project root)
    csv_path = Path(__file__).parent.parent.parent / "camera_scraper/camera_directions_analysis.csv"

    if not csv_path.exists():
        print(f"❌ Direction data file not found: {csv_path}")
        return

    print(f"📂 Reading direction data from: {csv_path}")

    # Load CSV data
    directions_data = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        directions_data = list(reader)

    print(f"📊 Found {len(directions_data)} direction records in CSV file")

    # Initialize database connection
    async with AsyncSessionLocal() as session:
        # Check if directions already exist
        result = await session.execute(select(CameraDirection))
        existing_directions = result.scalars().all()

        if existing_directions:
            print(f"⚠️  Database already contains {len(existing_directions)} direction records")
            response = input("Do you want to delete existing directions and re-seed? (y/N): ")
            if response.lower() == 'y':
                for direction in existing_directions:
                    await session.delete(direction)
                await session.commit()
                print("✅ Deleted existing direction records")
            else:
                print("❌ Seeding cancelled")
                return

        # Get all cameras from database to map camera_id
        result = await session.execute(select(Camera))
        cameras = result.scalars().all()
        camera_map = {cam.camera_id: cam.id for cam in cameras}
        print(f"📊 Found {len(cameras)} cameras in database")

        # Insert direction records
        directions_inserted = 0
        directions_skipped = 0

        for row in directions_data:
            try:
                # Extract direction metadata
                camera_id_str = f"C{row['camera_id']}"  # e.g., C210
                view_id = int(row['view_id'])
                location = row.get('location', '')
                description = row.get('description', '')
                url = row.get('url', '')
                suggested_heading = row.get('suggested_heading', '')
                confidence = row.get('confidence', 'n/a')
                eastbound_heading = row.get('eastbound_heading', '')
                westbound_heading = row.get('westbound_heading', '')

                # Skip if confidence is n/a or no heading
                if confidence == 'n/a' or not suggested_heading:
                    directions_skipped += 1
                    continue

                # Get camera database ID
                db_camera_id = camera_map.get(camera_id_str)
                if not db_camera_id:
                    print(f"⚠️  Camera {camera_id_str} not found in database, skipping direction record")
                    directions_skipped += 1
                    continue

                # Parse heading
                try:
                    heading = float(suggested_heading)
                except ValueError:
                    print(f"⚠️  Invalid heading for camera {camera_id_str} view {view_id}: {suggested_heading}")
                    directions_skipped += 1
                    continue

                # Determine direction from heading (N, NE, E, SE, S, SW, W, NW)
                direction = get_direction_from_heading(heading)

                # Create direction record
                direction_record = CameraDirection(
                    camera_id=db_camera_id,
                    view_id=view_id,
                    heading=heading,
                    direction=direction,
                    confidence=confidence,
                    eastbound_heading=float(eastbound_heading) if eastbound_heading else None,
                    westbound_heading=float(westbound_heading) if westbound_heading else None,
                    model="camera_directions_analysis",
                    analysis_method="corey_analysis"
                )

                session.add(direction_record)
                directions_inserted += 1

                # Print progress every 10 records
                if directions_inserted % 10 == 0:
                    print(f"  ✅ Inserted {directions_inserted} direction records...")

            except Exception as e:
                print(f"❌ Error processing direction for camera {row.get('camera_id')} view {row.get('view_id')}: {e}")
                directions_skipped += 1
                continue

        # Commit all directions
        await session.commit()

        print("\n" + "=" * 60)
        print(f"✅ Direction seeding complete!")
        print(f"📊 Direction records inserted: {directions_inserted}")
        print(f"⚠️  Direction records skipped: {directions_skipped}")
        print("=" * 60)

        # Verify insertion
        result = await session.execute(select(CameraDirection))
        total_directions = len(result.scalars().all())
        print(f"✅ Total direction records in database: {total_directions}")

        # Update camera table with primary heading
        print("\n🔄 Updating cameras with primary heading...")
        updated_cameras = 0
        for camera in cameras:
            result = await session.execute(
                select(CameraDirection)
                .where(CameraDirection.camera_id == camera.id)
                .where(CameraDirection.confidence.in_(['high', 'medium']))
                .order_by(CameraDirection.view_id)
            )
            camera_directions = result.scalars().all()

            if camera_directions:
                # Use first high/medium confidence direction as primary
                primary_direction = camera_directions[0]
                camera.heading = primary_direction.heading
                camera.direction = primary_direction.direction
                camera.direction_confidence = primary_direction.confidence
                updated_cameras += 1

        await session.commit()
        print(f"✅ Updated {updated_cameras} cameras with primary heading data")


def get_direction_from_heading(heading):
    """
    Convert heading (0-360 degrees) to compass direction

    N = 0°, E = 90°, S = 180°, W = 270°
    """
    # Normalize to 0-360
    heading = heading % 360

    if heading >= 337.5 or heading < 22.5:
        return 'N'
    elif heading >= 22.5 and heading < 67.5:
        return 'NE'
    elif heading >= 67.5 and heading < 112.5:
        return 'E'
    elif heading >= 112.5 and heading < 157.5:
        return 'SE'
    elif heading >= 157.5 and heading < 202.5:
        return 'S'
    elif heading >= 202.5 and heading < 247.5:
        return 'SW'
    elif heading >= 247.5 and heading < 292.5:
        return 'W'
    elif heading >= 292.5 and heading < 337.5:
        return 'NW'
    else:
        return 'N'


if __name__ == "__main__":
    print("🚀 Starting camera direction seeding...")
    print(f"📊 Database URL: {settings.DATABASE_URL}")
    print()

    asyncio.run(seed_directions())

"""
Seed Camera Data from JSON
===========================

Imports QEW COMPASS camera data from public/camera_scraper/qew_cameras_with_images.json
into the database.

Usage:
    python seed_cameras.py
"""

import asyncio
import json
import sys
from pathlib import Path
from sqlalchemy import select

# Add current directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from database import AsyncSessionLocal, init_db
from models import Camera
from config import settings


async def seed_cameras():
    """Seed cameras from JSON file"""

    # Path to camera data JSON (relative to project root)
    json_path = Path(__file__).parent.parent.parent / "public/camera_scraper/qew_cameras_with_images.json"

    if not json_path.exists():
        print(f"❌ Camera data file not found: {json_path}")
        return

    print(f"📂 Reading camera data from: {json_path}")

    # Load camera data
    with open(json_path, 'r') as f:
        cameras_data = json.load(f)

    print(f"📊 Found {len(cameras_data)} cameras in JSON file")

    # Initialize database connection
    async with AsyncSessionLocal() as session:
        # Check if cameras already exist
        result = await session.execute(select(Camera))
        existing_cameras = result.scalars().all()

        if existing_cameras:
            print(f"⚠️  Database already contains {len(existing_cameras)} cameras")
            response = input("Do you want to delete existing cameras and re-seed? (y/N): ")
            if response.lower() == 'y':
                for camera in existing_cameras:
                    await session.delete(camera)
                await session.commit()
                print("✅ Deleted existing cameras")
            else:
                print("❌ Seeding cancelled")
                return

        # Insert cameras
        cameras_inserted = 0
        cameras_skipped = 0

        for camera_data in cameras_data:
            try:
                # Extract camera metadata
                camera_id = f"C{camera_data['Id']}"  # e.g., C210
                location = camera_data.get('Location', '')
                latitude = camera_data.get('Latitude')
                longitude = camera_data.get('Longitude')
                direction = camera_data.get('Direction', 'Unknown')
                source = camera_data.get('Source', '511ON')
                views = camera_data.get('Views', [])

                # Validate required fields
                if not latitude or not longitude:
                    print(f"⚠️  Skipping camera {camera_id}: Missing coordinates")
                    cameras_skipped += 1
                    continue

                # Create camera record
                camera = Camera(
                    camera_id=camera_id,
                    source=source,
                    location=location,
                    latitude=latitude,
                    longitude=longitude,
                    direction=direction if direction != 'Unknown' else None,
                    active=True,
                    views=views  # Store views as JSON
                )

                session.add(camera)
                cameras_inserted += 1

                # Print progress every 10 cameras
                if cameras_inserted % 10 == 0:
                    print(f"  ✅ Inserted {cameras_inserted} cameras...")

            except Exception as e:
                print(f"❌ Error processing camera {camera_data.get('Id')}: {e}")
                cameras_skipped += 1
                continue

        # Commit all cameras
        await session.commit()

        print("\n" + "=" * 60)
        print(f"✅ Database seeding complete!")
        print(f"📊 Cameras inserted: {cameras_inserted}")
        print(f"⚠️  Cameras skipped: {cameras_skipped}")
        print("=" * 60)

        # Verify insertion
        result = await session.execute(select(Camera))
        total_cameras = len(result.scalars().all())
        print(f"✅ Total cameras in database: {total_cameras}")


if __name__ == "__main__":
    print("🚀 Starting camera database seeding...")
    print(f"📊 Database URL: {settings.DATABASE_URL}")
    print()

    asyncio.run(seed_cameras())

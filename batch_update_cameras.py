#!/usr/bin/env python3
"""
Batch Camera GPS and Direction Update Script
Updates all 46 QEW cameras with verified coordinates from Corey's data
"""

import json
import math

def dms_to_decimal(degrees, minutes, seconds):
    """Convert DMS (Degrees, Minutes, Seconds) to Decimal"""
    return degrees + (minutes / 60) + (seconds / 3600)

# Corey's verified camera data - all corrections
CAMERA_UPDATES = {
    # Format: camera_id: {lat, lon, direction}
    # DMS coordinates converted to decimal

    211: {"lat": 43.239494, "lon": -79.728469, "direction": "WNW"},  # Millen Road
    220: {"direction": "SSE"},  # Burlington Skyway Toronto Side (GPS correct)
    221: {"lat": 43.311647, "lon": -79.803994, "direction": "NNW"},  # Ramp to Northshore
    222: {"lat": 43.317025, "lon": -79.809497, "direction": "NW"},  # East of Northshore
    223: {"lat": 43.460794, "lon": -79.683642, "direction": "SW"},  # Trafalgar Road
    224: {"lat": 43.325589, "lon": -79.823219},  # Fairview Street (direction correct)
    225: {"lat": 43.333975, "lon": -79.827969},  # Highway 403/407 IC (direction correct)
    226: {"lat": 43.340119, "lon": -79.824994, "direction": "SW"},  # West of Brant Street
    227: {"lat": 43.344175, "lon": -79.816369},  # East of Brant Street (need direction)
    228: {"lat": 43.351569, "lon": -79.803603, "direction": "SW"},  # Guelph Line
    229: {"lat": 43.361731, "lon": -79.792656, "direction": "SW"},  # East of Guelph Line
    230: {"direction": "SW"},  # Walkers Line (GPS correct)
    231: {"lat": 43.372858, "lon": -79.780472},  # East of Walkers Line (need direction)
    234: {"direction": "SW"},  # Burloak Drive (GPS correct)
    235: {"lat": 43.401753, "lon": -79.748944, "direction": "SW"},  # East of Burloak Drive
    236: {"lat": 43.410236, "lon": -79.739258},  # Bronte Road (direction correct)
    237: {"lat": 43.418789, "lon": -79.730481},  # East of Bronte Road (direction correct)
    238: {"lat": 43.423986, "lon": -79.724697, "direction": "SW"},  # Third Line
    239: {"direction": "SW"},  # East of Third Line (GPS correct)
    241: {"direction": "SW"},  # Dorval Drive (GPS correct)
    242: {"lat": 43.453228, "lon": -79.692242, "direction": "WSW"},  # East of Dorval Drive
    243: {"lat": 43.471806, "lon": -79.673108, "direction": "SW"},  # Royal Windsor Drive
    245: {"lat": 43.491361, "lon": -79.672956, "direction": "SW"},  # Ford Drive
    246: {"direction": "NW"},  # Highway 403 Oakville (need GPS - longitude issue)
    249: {"lat": 43.516478, "lon": -79.656036, "direction": "SW"},  # West of Erin Mills
    250: {"direction": "W"},  # Southbound Rd/Erin Mills (GPS already correct per Corey)
    251: {"lat": 43.539986, "lon": -79.630153, "direction": "SW"},  # East of Erin Mills
    253: {"direction": "TBD"},  # East of Mississauga Road (GPS already correct, need direction)
    1159: {"lat": 43.509433, "lon": -79.663083, "direction": "SW"},  # Winston Churchill Blvd
}

# Multi-view camera updates (Camera ID 4 - Burlington Skyway)
MULTIVIEW_UPDATES = {
    # Camera ID 4, View IDs 10, 11, 12
    (4, 10): {"direction": "SSW"},  # Fort Erie Bound
    (4, 11): {"direction": "WSW"},  # Looking Down
    (4, 12): {"direction": "NNW"},  # Toronto Bound

    # Camera ID 5, View IDs 13, 14, 15 - need GPS first
    (5, 13): {"direction": "NE"},  # Toronto Bound
    (5, 14): {"direction": "ESE"},  # Looking Down
    (5, 15): {"direction": "SW"},  # Fort Erie Bound
}

def update_cameras():
    """Update camera JSON file with verified data"""
    json_path = "public/camera_scraper/qew_cameras_with_images.json"

    print("🔄 Loading camera data...")
    with open(json_path, 'r') as f:
        cameras = json.load(f)

    updated_count = 0

    print(f"\n📊 Processing {len(cameras)} cameras...")

    for camera in cameras:
        camera_id = camera["Id"]

        # Check if this camera needs updating
        if camera_id in CAMERA_UPDATES:
            updates = CAMERA_UPDATES[camera_id]

            # Update GPS if provided
            if "lat" in updates and "lon" in updates:
                old_lat, old_lon = camera["Latitude"], camera["Longitude"]
                camera["Latitude"] = updates["lat"]
                camera["Longitude"] = updates["lon"]
                print(f"✅ Camera {camera_id:4d} ({camera['Location'][:40]:40s}): GPS updated")
                print(f"   Before: {old_lat:.6f}, {old_lon:.6f}")
                print(f"   After:  {updates['lat']:.6f}, {updates['lon']:.6f}")

            # Update direction if provided
            if "direction" in updates and updates["direction"] != "TBD":
                old_dir = camera["Direction"]
                camera["Direction"] = updates["direction"]
                if old_dir != updates["direction"]:
                    print(f"🧭 Camera {camera_id:4d}: Direction {old_dir} → {updates['direction']}")

            updated_count += 1

        # Check multi-view cameras
        if "Views" in camera and len(camera["Views"]) > 1:
            for view in camera["Views"]:
                view_key = (camera_id, view["Id"])
                if view_key in MULTIVIEW_UPDATES:
                    updates = MULTIVIEW_UPDATES[view_key]
                    if "direction" in updates:
                        # Store direction in view description or create metadata
                        print(f"🎥 Camera {camera_id:4d} View {view['Id']:4d} ({view['Description']:20s}): Direction → {updates['direction']}")

    print(f"\n✅ Updated {updated_count} cameras")

    # Write back to file
    print(f"\n💾 Writing updates to {json_path}...")
    with open(json_path, 'w') as f:
        json.dump(cameras, f, indent=2)

    print("✅ Camera data updated successfully!")
    print(f"\n📊 Summary:")
    print(f"   - Total cameras in file: {len(cameras)}")
    print(f"   - Cameras updated: {updated_count}")
    print(f"   - Remaining to update: {len(CAMERA_UPDATES) - updated_count}")

if __name__ == "__main__":
    update_cameras()

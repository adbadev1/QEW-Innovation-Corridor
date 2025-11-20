#!/usr/bin/env python3
"""Generate manifest.json from scraped camera images"""
import os
import json
import re

image_dir = "public/camera_images"
output_file = os.path.join(image_dir, "manifest.json")

# Pattern: c{cameraId}_v{viewId}_r{round}_{timestamp}.jpg
pattern = r'c(\d+)_v(\d+)_r(\d+)_(\d+_\d+)\.jpg'

images = []

for filename in sorted(os.listdir(image_dir)):
    if not filename.endswith('.jpg'):
        continue

    match = re.match(pattern, filename)
    if match:
        camera_id = int(match.group(1))
        view_id = int(match.group(2))
        round_num = int(match.group(3))
        timestamp = match.group(4)

        images.append({
            "filename": filename,
            "cameraId": camera_id,
            "viewId": view_id,
            "round": round_num,
            "timestamp": timestamp
        })
        print(f"✓ {filename} -> Camera {camera_id}, View {view_id}")

# Write manifest
with open(output_file, 'w') as f:
    json.dump(images, f, indent=2)

print(f"\n✅ Generated manifest with {len(images)} images")
print(f"📄 Saved to: {output_file}")

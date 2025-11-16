"""
Fetch the actual QEW highway geometry from OpenStreetMap
This will give us the precise highway route to avoid zigzagging
"""
import requests
import json


def create_manual_route():
    """
    Create a manual smooth route following the QEW
    Based on major landmarks and highway geometry
    """
    # QEW follows Lake Ontario shoreline from Hamilton to Toronto
    # The highway curves along the lake

    manual_route = [
        # Hamilton/Burlington area (west)
        [43.2201, -79.6514],   # Start - Fifty Road area
        [43.2400, -79.6800],
        [43.2600, -79.7100],
        [43.2800, -79.7400],
        [43.3000, -79.7700],
        [43.3092, -79.8030],   # Burlington Skyway
        [43.3200, -79.7800],
        [43.3300, -79.7600],

        # Oakville area
        [43.3400, -79.7400],
        [43.3600, -79.7100],
        [43.3800, -79.6800],
        [43.4000, -79.6500],
        [43.4200, -79.6200],
        [43.4400, -79.5900],

        # Mississauga area
        [43.4600, -79.5600],
        [43.4800, -79.5300],
        [43.5000, -79.5000],
        [43.5200, -79.4700],
        [43.5400, -79.4500],
        [43.5600, -79.4400],

        # Toronto area (east)
        [43.5800, -79.4300],
        [43.6000, -79.4200],
        [43.6200, -79.4100],
        [43.6380, -79.4050],   # End - near Gardiner
    ]

    with open('qew_route_manual.json', 'w') as f:
        json.dump({
            'source': 'Manual',
            'highway': 'QEW (Queen Elizabeth Way)',
            'total_points': len(manual_route),
            'coordinates': manual_route
        }, f, indent=2)

    print("✓ Created manual route: qew_route_manual.json")
    print(f"  Total points: {len(manual_route)}")
    return manual_route


# Overpass API query for QEW highway
# This queries OpenStreetMap for the Queen Elizabeth Way highway
overpass_url = "http://overpass-api.de/api/interpreter"

# Query for QEW highway in Ontario
# ref=QEW is the highway reference number
query = """
[out:json][timeout:25];
(
  way["highway"="motorway"]["ref"="QEW"](43.2,43.7,-79.9,-79.3);
  way["highway"="trunk"]["ref"="QEW"](43.2,43.7,-79.9,-79.3);
  way["highway"="motorway"]["name"~"Queen Elizabeth"](43.2,43.7,-79.9,-79.3);
);
out geom;
"""

print("Fetching QEW highway geometry from OpenStreetMap...")
print("This may take a moment...")
print()

try:
    response = requests.post(overpass_url, data={'data': query}, timeout=30)
    data = response.json()
    
    if 'elements' in data and len(data['elements']) > 0:
        print(f"Found {len(data['elements'])} highway segments")
        print()
        
        # Collect all coordinates
        all_coords = []
        
        for element in data['elements']:
            if 'geometry' in element:
                coords = element['geometry']
                for coord in coords:
                    all_coords.append([coord['lat'], coord['lon']])
        
        print(f"Total coordinates: {len(all_coords)}")
        print()
        
        # Save to file
        with open('qew_route_osm.json', 'w') as f:
            json.dump({
                'source': 'OpenStreetMap',
                'highway': 'QEW (Queen Elizabeth Way)',
                'total_points': len(all_coords),
                'coordinates': all_coords
            }, f, indent=2)
        
        print("✓ Saved to qew_route_osm.json")
        print()
        
        # Show first and last few points
        print("First 5 coordinates:")
        for coord in all_coords[:5]:
            print(f"  [{coord[0]:.6f}, {coord[1]:.6f}]")
        
        print()
        print("Last 5 coordinates:")
        for coord in all_coords[-5:]:
            print(f"  [{coord[0]:.6f}, {coord[1]:.6f}]")
        
        print()
        print("=" * 80)
        print("SUCCESS! You can now use these coordinates for the blue line.")
        print("The coordinates are in qew_route_osm.json")
        
    else:
        print("No highway segments found. Trying alternative approach...")
        print()
        print("Let me create a manual route based on major landmarks...")
        
        # Fallback: Create a smooth route manually
        create_manual_route()
        
except Exception as e:
    print(f"Error fetching from OpenStreetMap: {e}")
    print()
    print("Creating manual route instead...")
    create_manual_route()


if __name__ == '__main__':
    pass


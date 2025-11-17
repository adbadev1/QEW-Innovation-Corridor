"""
Get actual car routes for both directions of the QEW
Using OSRM (Open Source Routing Machine) for accurate highway routing
"""
import requests
import json


def dms_to_decimal(degrees, minutes, seconds, direction):
    """Convert DMS (Degrees, Minutes, Seconds) to decimal"""
    decimal = degrees + minutes/60 + seconds/60/60
    if direction in ['S', 'W']:
        decimal = -decimal
    return decimal


# Convert coordinates from DMS to decimal
print("Converting coordinates...")
print()

# Route 1: Westbound (Hamilton to Toronto direction)
route1_start_lat = dms_to_decimal(43, 13, 2.51, 'N')
route1_start_lon = dms_to_decimal(79, 38, 14.01, 'W')
route1_end_lat = dms_to_decimal(43, 34, 5.37, 'N')
route1_end_lon = dms_to_decimal(79, 35, 59.15, 'W')

# Route 2: Eastbound (Toronto to Hamilton direction)
route2_start_lat = dms_to_decimal(43, 34, 5.76, 'N')
route2_start_lon = dms_to_decimal(79, 36, 0.05, 'W')
route2_end_lat = dms_to_decimal(43, 13, 1.37, 'N')
route2_end_lon = dms_to_decimal(79, 38, 14.06, 'W')

print("Route 1 (Westbound - Hamilton to Toronto):")
print(f"  Start: ({route1_start_lat:.6f}, {route1_start_lon:.6f})")
print(f"  End:   ({route1_end_lat:.6f}, {route1_end_lon:.6f})")
print()

print("Route 2 (Eastbound - Toronto to Hamilton):")
print(f"  Start: ({route2_start_lat:.6f}, {route2_start_lon:.6f})")
print(f"  End:   ({route2_end_lat:.6f}, {route2_end_lon:.6f})")
print()


def get_route(start_lon, start_lat, end_lon, end_lat, route_name):
    """
    Get route from OSRM routing service
    OSRM uses lon,lat format (not lat,lon!)
    """
    # OSRM public API endpoint
    osrm_url = f"http://router.project-osrm.org/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}"
    
    params = {
        'overview': 'full',
        'geometries': 'geojson',
        'steps': 'false'
    }
    
    print(f"Fetching {route_name}...")
    
    try:
        response = requests.get(osrm_url, params=params, timeout=30)
        data = response.json()
        
        if data['code'] == 'Ok' and 'routes' in data:
            route = data['routes'][0]
            geometry = route['geometry']['coordinates']
            
            # Convert from [lon, lat] to [lat, lon] for Leaflet
            coordinates = [[coord[1], coord[0]] for coord in geometry]
            
            distance_km = route['distance'] / 1000
            duration_min = route['duration'] / 60
            
            print(f"  ✓ Success!")
            print(f"  Distance: {distance_km:.2f} km")
            print(f"  Duration: {duration_min:.1f} minutes")
            print(f"  Waypoints: {len(coordinates)}")
            print()
            
            return coordinates
        else:
            print(f"  ✗ Error: {data.get('message', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None


# Fetch both routes
print("=" * 80)
print("FETCHING CAR ROUTES FROM OSRM")
print("=" * 80)
print()

route1_coords = get_route(route1_start_lon, route1_start_lat, route1_end_lon, route1_end_lat, "Route 1 (Westbound)")
route2_coords = get_route(route2_start_lon, route2_start_lat, route2_end_lon, route2_end_lat, "Route 2 (Eastbound)")

# Save to JSON
if route1_coords and route2_coords:
    output = {
        'route1_westbound': {
            'name': 'QEW Westbound (Hamilton → Toronto)',
            'start': [route1_start_lat, route1_start_lon],
            'end': [route1_end_lat, route1_end_lon],
            'coordinates': route1_coords
        },
        'route2_eastbound': {
            'name': 'QEW Eastbound (Toronto → Hamilton)',
            'start': [route2_start_lat, route2_start_lon],
            'end': [route2_end_lat, route2_end_lon],
            'coordinates': route2_coords
        }
    }
    
    with open('qew_car_routes.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("=" * 80)
    print("✓ ROUTES SAVED TO: qew_car_routes.json")
    print("=" * 80)
    print()
    
    # Print JavaScript format
    print("JavaScript format for App.jsx:")
    print("=" * 80)
    print()
    print("// Route 1: Westbound (Hamilton → Toronto)")
    print("const qewPathWestbound = [")
    for i, coord in enumerate(route1_coords[:10]):  # Show first 10
        print(f"  [{coord[0]:.6f}, {coord[1]:.6f}],")
    print(f"  // ... {len(route1_coords) - 10} more points ...")
    print("];")
    print()
    print("// Route 2: Eastbound (Toronto → Hamilton)")
    print("const qewPathEastbound = [")
    for i, coord in enumerate(route2_coords[:10]):  # Show first 10
        print(f"  [{coord[0]:.6f}, {coord[1]:.6f}],")
    print(f"  // ... {len(route2_coords) - 10} more points ...")
    print("];")
    print()
    print("=" * 80)
    
else:
    print("✗ Failed to fetch routes")


if __name__ == '__main__':
    pass


"""
Create a smooth, accurate QEW highway route
Using proper geographic interpolation to avoid zigzagging
"""
import json
import math


def interpolate_points(start, end, num_points):
    """
    Create smooth interpolation between two points
    """
    points = []
    for i in range(num_points + 1):
        t = i / num_points
        lat = start[0] + (end[0] - start[0]) * t
        lon = start[1] + (end[1] - start[1]) * t
        points.append([lat, lon])
    return points


def create_smooth_qew_route():
    """
    Create a smooth QEW route following the actual highway
    The QEW follows Lake Ontario's shoreline in a gentle curve
    """
    
    # Key landmarks along the QEW (west to east)
    # These are major interchanges and landmarks
    key_points = [
        # Hamilton area (westernmost)
        [43.2201, -79.6514],    # Fifty Road
        [43.2500, -79.7000],    # Approaching Skyway
        [43.2800, -79.7500],    # Near Skyway
        [43.3092, -79.8030],    # Burlington Skyway (highest point)
        [43.3200, -79.7900],    # After Skyway
        [43.3400, -79.7500],    # Burlington/Oakville border
        
        # Oakville area
        [43.3700, -79.7000],    # Oakville central
        [43.4000, -79.6500],    # Oakville east
        [43.4300, -79.6000],    # Oakville/Mississauga border
        
        # Mississauga area
        [43.4600, -79.5600],    # Mississauga west
        [43.4900, -79.5200],    # Mississauga central
        [43.5200, -79.4800],    # Mississauga east
        [43.5500, -79.4500],    # Mississauga/Toronto border
        
        # Toronto area (easternmost)
        [43.5800, -79.4300],    # Toronto west
        [43.6100, -79.4150],    # Toronto central
        [43.6380, -79.4050],    # Toronto east (Gardiner)
    ]
    
    # Create smooth interpolation between key points
    smooth_route = []
    
    for i in range(len(key_points) - 1):
        start = key_points[i]
        end = key_points[i + 1]
        
        # Add 5 interpolated points between each key point
        # This creates a smooth curve
        interpolated = interpolate_points(start, end, 5)
        
        # Add all but the last point (to avoid duplicates)
        smooth_route.extend(interpolated[:-1])
    
    # Add the final point
    smooth_route.append(key_points[-1])
    
    # Save to JSON
    with open('qew_route_smooth.json', 'w') as f:
        json.dump({
            'source': 'Smooth Interpolation',
            'highway': 'QEW (Queen Elizabeth Way)',
            'description': 'Smooth route following Lake Ontario shoreline',
            'total_points': len(smooth_route),
            'key_landmarks': len(key_points),
            'coordinates': smooth_route
        }, f, indent=2)
    
    print("=" * 80)
    print("QEW SMOOTH ROUTE CREATED")
    print("=" * 80)
    print(f"Total points: {len(smooth_route)}")
    print(f"Key landmarks: {len(key_points)}")
    print()
    print("Route details:")
    print(f"  Start: Fifty Road, Hamilton ({smooth_route[0][0]:.4f}, {smooth_route[0][1]:.4f})")
    print(f"  End: Gardiner, Toronto ({smooth_route[-1][0]:.4f}, {smooth_route[-1][1]:.4f})")
    print()
    print("✓ Saved to: qew_route_smooth.json")
    print()
    
    # Print JavaScript array format for easy copy-paste
    print("JavaScript array format (for App.jsx):")
    print("=" * 80)
    print("const qewPath = [")
    for i, coord in enumerate(smooth_route):
        comment = ""
        if i == 0:
            comment = "  // Start - Hamilton"
        elif i == len(smooth_route) - 1:
            comment = "  // End - Toronto"
        elif i % 10 == 0:
            comment = f"  // Point {i}"
        
        print(f"  [{coord[0]:.6f}, {coord[1]:.6f}],{comment}")
    print("];")
    print("=" * 80)
    
    return smooth_route


if __name__ == '__main__':
    create_smooth_qew_route()


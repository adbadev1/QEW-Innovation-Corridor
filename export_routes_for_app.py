"""
Export the car routes in JavaScript format for App.jsx
"""
import json

# Load the routes
with open('qew_car_routes.json', 'r') as f:
    data = json.load(f)

route1 = data['route1_westbound']['coordinates']
route2 = data['route2_eastbound']['coordinates']

print("=" * 80)
print("QEW CAR ROUTES - READY FOR APP.JSX")
print("=" * 80)
print()
print(f"Route 1 (Westbound): {len(route1)} waypoints")
print(f"Route 2 (Eastbound): {len(route2)} waypoints")
print()
print("=" * 80)
print()

# Save to a JavaScript file
with open('qew_routes.js', 'w', encoding='utf-8') as f:
    f.write("// QEW Highway Routes - Both Directions\n")
    f.write("// Generated from OSRM car routing service\n")
    f.write("// These are actual driving routes along the QEW\n\n")

    f.write("// Route 1: Westbound (Hamilton to Toronto)\n")
    f.write("export const qewPathWestbound = [\n")
    for coord in route1:
        f.write(f"  [{coord[0]:.6f}, {coord[1]:.6f}],\n")
    f.write("];\n\n")

    f.write("// Route 2: Eastbound (Toronto to Hamilton)\n")
    f.write("export const qewPathEastbound = [\n")
    for coord in route2:
        f.write(f"  [{coord[0]:.6f}, {coord[1]:.6f}],\n")
    f.write("];\n")

print("✓ Saved to: qew_routes.js")
print()

# Also create a combined single-direction route (for simpler display)
print("Creating combined route (average of both directions)...")
print()

# For simplicity, we can just use Route 1 as the main route
with open('qew_route_single.js', 'w', encoding='utf-8') as f:
    f.write("// QEW Highway Route - Single Line (Westbound)\n")
    f.write("// Generated from OSRM car routing service\n\n")
    f.write("export const qewPath = [\n")
    for coord in route1:
        f.write(f"  [{coord[0]:.6f}, {coord[1]:.6f}],\n")
    f.write("];\n")

print("✓ Saved to: qew_route_single.js")
print()
print("=" * 80)
print("COPY THIS INTO App.jsx:")
print("=" * 80)
print()
print("// QEW Routes - Both directions")
print("const qewPathWestbound = [")
for i in range(min(5, len(route1))):
    print(f"  [{route1[i][0]:.6f}, {route1[i][1]:.6f}],")
print(f"  // ... {len(route1) - 5} more waypoints")
print("];")
print()
print("const qewPathEastbound = [")
for i in range(min(5, len(route2))):
    print(f"  [{route2[i][0]:.6f}, {route2[i][1]:.6f}],")
print(f"  // ... {len(route2) - 5} more waypoints")
print("];")
print()
print("// Then render both:")
print('<Polyline positions={qewPathWestbound} color="blue" weight={3} opacity={0.6} />')
print('<Polyline positions={qewPathEastbound} color="blue" weight={3} opacity={0.6} />')
print()
print("=" * 80)


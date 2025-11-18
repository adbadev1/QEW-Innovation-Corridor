/**
 * Geospatial Utility Functions
 * GPS calculations for V2X broadcast range determination
 */

/**
 * Calculate distance between two GPS coordinates using Haversine formula
 */
export function calculateDistance(lat1, lon1, lat2, lon2) {
  const R = 6371000;
  
  const phi1 = lat1 * Math.PI / 180;
  const phi2 = lat2 * Math.PI / 180;
  const deltaPhi = (lat2 - lat1) * Math.PI / 180;
  const deltaLambda = (lon2 - lon1) * Math.PI / 180;
  
  const a = Math.sin(deltaPhi / 2) * Math.sin(deltaPhi / 2) +
            Math.cos(phi1) * Math.cos(phi2) *
            Math.sin(deltaLambda / 2) * Math.sin(deltaLambda / 2);
  
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  
  return R * c;
}

/**
 * Check if vehicle is within broadcast radius
 */
export function isVehicleInBroadcastRange(vehicleCoords, workZone, radius = 1000) {
  if (!vehicleCoords || !workZone || vehicleCoords.length !== 2) {
    return false;
  }
  
  const [vehicleLat, vehicleLon] = vehicleCoords;
  const distance = calculateDistance(vehicleLat, vehicleLon, workZone.lat, workZone.lon);
  
  return distance <= radius;
}

/**
 * Format distance for display
 */
export function formatDistance(meters) {
  if (meters < 1000) {
    return Math.round(meters) + 'm';
  }
  return (meters / 1000).toFixed(1) + 'km';
}

/**
 * Get all vehicles within broadcast range
 */
export function getVehiclesInRange(vehicles, workZone, getVehicleCoordinates, radius = 1000) {
  return vehicles
    .map(vehicle => {
      const coords = getVehicleCoordinates(vehicle);
      if (!coords || coords.length < 2) return null;
      
      const [lat, lon] = coords;
      const distance = calculateDistance(lat, lon, workZone.lat, workZone.lon);
      
      if (distance <= radius) {
        return {
          vehicle,
          distance,
          coords: [lat, lon]
        };
      }
      return null;
    })
    .filter(Boolean)
    .sort((a, b) => a.distance - b.distance);
}

/**
 * Location Utilities for QEW Innovation Corridor
 *
 * Provides functions to:
 * - Calculate KM markers along the QEW corridor
 * - Map cameras to highway locations
 * - Generate location-aware AI analysis
 */

// QEW corridor reference points (based on actual camera coverage)
// Cameras span from Burlington (west) to Oakville/Mississauga (east)
const QEW_REFERENCE = {
  // Western terminus (Burlington area - westernmost camera)
  WEST: { lat: 43.336509, lon: -79.828291, km: 0, name: 'Burlington (West End)' },
  // Eastern terminus (Oakville/Mississauga area - easternmost camera)
  EAST: { lat: 43.579156, lon: -79.607964, km: 25, name: 'Oakville/Mississauga (East End)' }
};

/**
 * Calculate approximate KM marker for a camera location along QEW corridor
 * Uses linear interpolation based on longitude (QEW runs roughly east-west)
 *
 * @param {number} lat - Latitude
 * @param {number} lon - Longitude
 * @returns {number} Approximate KM marker (0 = West, 25 = East for camera coverage)
 */
export function calculateKmMarker(lat, lon) {
  const west = QEW_REFERENCE.WEST;
  const east = QEW_REFERENCE.EAST;

  // Calculate position ratio based on longitude (primary axis for QEW)
  const lonRange = east.lon - west.lon;
  const lonPosition = lon - west.lon;
  const ratio = lonPosition / lonRange;

  // KM = 0 at western cameras, 25 at eastern cameras
  const kmRange = east.km - west.km;
  const km = west.km + (ratio * kmRange);

  // Clamp to valid range and round to 1 decimal
  return Math.max(0, Math.min(25, km)).toFixed(1);
}

/**
 * Get nearest major exit/landmark for a KM marker
 *
 * @param {number} km - KM marker along corridor (camera coverage: 0-25)
 * @returns {string} Exit/landmark name
 */
export function getNearestExit(km) {
  const exits = [
    { km: 0, name: 'Burlington West' },
    { km: 2, name: 'Walkers Line' },
    { km: 4, name: 'Guelph Line' },
    { km: 6, name: 'Appleby Line' },
    { km: 8, name: 'Bronte Road' },
    { km: 10, name: 'Trafalgar Road' },
    { km: 12, name: 'Kerr Street' },
    { km: 14, name: 'Dorval Drive' },
    { km: 16, name: 'Winston Churchill Blvd' },
    { km: 18, name: 'Erin Mills Parkway' },
    { km: 20, name: 'Mississauga Road' },
    { km: 22, name: 'Cawthra Road' },
    { km: 24, name: 'Hurontario Street' },
    { km: 25, name: 'Dixie Road' }
  ];

  // Find closest exit
  let closest = exits[0];
  let minDistance = Math.abs(km - exits[0].km);

  for (const exit of exits) {
    const distance = Math.abs(km - exit.km);
    if (distance < minDistance) {
      minDistance = distance;
      closest = exit;
    }
  }

  return closest.name;
}

/**
 * Format camera location with KM marker and exit
 *
 * @param {Object} camera - Camera object with Location, Latitude, Longitude
 * @returns {string} Formatted location string
 */
export function formatCameraLocation(camera) {
  const km = calculateKmMarker(camera.Latitude, camera.Longitude);
  const exit = getNearestExit(parseFloat(km));

  return {
    km: parseFloat(km),
    kmFormatted: `KM ${km}`,
    exit: exit,
    fullLocation: `${camera.Location} (KM ${km}, near ${exit})`,
    shortLocation: `${camera.Location} @ KM ${km}`
  };
}

// NOTE: Real AI analysis is provided by Gemini 2.0 Flash
// See: src/services/autoWorkZoneAnalysis.js
// - Analyzes real camera images
// - Detects work zones, workers, equipment
// - Generates risk scores and safety recommendations
// - No mock/templated analysis - only real AI vision results

/**
 * Get cameras sorted by KM position (west to east)
 *
 * @param {Array} cameras - Array of camera objects
 * @returns {Array} Cameras sorted by KM position
 */
export function getCamerasByKm(cameras) {
  return cameras
    .map(camera => ({
      ...camera,
      location: formatCameraLocation(camera)
    }))
    .sort((a, b) => a.location.km - b.location.km);
}

/**
 * Extract real 511ON camera ID from SourceId field
 *
 * SourceId format: "468-QEW E/of MISSISSAUGA Rd"
 * Real Camera ID: 468
 *
 * @param {Object} camera - Camera object with SourceId field
 * @returns {Object} Camera IDs (real 511ON ID and internal ID)
 */
export function getCameraIds(camera) {
  // Extract real camera ID from SourceId (e.g., "468-QEW E/of MISSISSAUGA Rd" → 468)
  const realCameraId = camera.SourceId ? camera.SourceId.split('-')[0] : null;

  return {
    realId: realCameraId,           // Real 511ON camera ID (e.g., "468")
    internalId: camera.Id,          // Our internal database ID (e.g., 253)
    sourceId: camera.SourceId,      // Full SourceId string
    displayId: realCameraId || camera.Id  // Prefer real ID for display
  };
}

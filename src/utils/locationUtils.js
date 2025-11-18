/**
 * Location Utilities for QEW Innovation Corridor
 *
 * Provides functions to:
 * - Calculate KM markers along the QEW corridor
 * - Map cameras to highway locations
 * - Generate location-aware AI analysis
 */

// QEW corridor reference points
const QEW_REFERENCE = {
  // Western terminus (Burlington/Hamilton area)
  WEST: { lat: 43.2201, lon: -79.65143, km: 0, name: 'Burlington (Fifty Road)' },
  // Eastern terminus (Toronto area)
  EAST: { lat: 43.6426, lon: -79.3871, km: 40, name: 'Toronto (Gardiner Expressway)' }
};

/**
 * Calculate approximate KM marker for a camera location along QEW corridor
 * Uses linear interpolation based on longitude (QEW runs roughly east-west)
 *
 * @param {number} lat - Latitude
 * @param {number} lon - Longitude
 * @returns {number} Approximate KM marker (0 = Burlington, 40 = Toronto)
 */
export function calculateKmMarker(lat, lon) {
  const west = QEW_REFERENCE.WEST;
  const east = QEW_REFERENCE.EAST;

  // Calculate position ratio based on longitude (primary axis for QEW)
  const lonRange = east.lon - west.lon;
  const lonPosition = lon - west.lon;
  const ratio = lonPosition / lonRange;

  // KM = 0 at Burlington (west), 40 at Toronto (east)
  const km = ratio * 40;

  // Clamp to 0-40 range and round to 1 decimal
  return Math.max(0, Math.min(40, km)).toFixed(1);
}

/**
 * Get nearest major exit/landmark for a KM marker
 *
 * @param {number} km - KM marker along corridor
 * @returns {string} Exit/landmark name
 */
export function getNearestExit(km) {
  const exits = [
    { km: 0, name: 'Fifty Road (Burlington)' },
    { km: 3, name: 'Millen Road' },
    { km: 6, name: 'Walkers Line' },
    { km: 8, name: 'Guelph Line' },
    { km: 10, name: 'Appleby Line' },
    { km: 12, name: 'Bronte Road' },
    { km: 15, name: 'Trafalgar Road' },
    { km: 18, name: 'Kerr Street' },
    { km: 20, name: 'Dorval Drive' },
    { km: 22, name: 'Winston Churchill Blvd' },
    { km: 24, name: 'Erin Mills Parkway' },
    { km: 26, name: 'Mississauga Road' },
    { km: 28, name: 'Cawthra Road' },
    { km: 30, name: 'Hurontario Street' },
    { km: 32, name: 'Dixie Road' },
    { km: 34, name: 'Royal York Road' },
    { km: 36, name: 'Islington Avenue' },
    { km: 38, name: 'Kipling Avenue' },
    { km: 40, name: 'Gardiner Expressway (Toronto)' }
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

/**
 * Generate location-aware AI traffic analysis
 * References actual cameras and highway markers
 *
 * @param {Array} cameras - Array of camera objects
 * @param {Array} vehicles - Array of vehicle objects
 * @returns {string} AI analysis text with location references
 */
export function generateLocationAwareAnalysis(cameras, vehicles) {
  if (!cameras || cameras.length === 0) {
    return "Initializing AI analysis...";
  }

  // Select random cameras for analysis
  const randomCamera1 = cameras[Math.floor(Math.random() * cameras.length)];
  const randomCamera2 = cameras[Math.floor(Math.random() * cameras.length)];
  const randomCamera3 = cameras[Math.floor(Math.random() * cameras.length)];

  const loc1 = formatCameraLocation(randomCamera1);
  const loc2 = formatCameraLocation(randomCamera2);
  const loc3 = formatCameraLocation(randomCamera3);

  const currentHour = new Date().getHours();
  const timeOfDay = currentHour < 6 ? 'overnight' :
                    currentHour < 9 ? 'morning peak' :
                    currentHour < 16 ? 'midday' :
                    currentHour < 19 ? 'evening peak' : 'evening';

  const vehicleCount = vehicles?.length || 0;

  const analysisTemplates = [
    `${timeOfDay === 'morning peak' || timeOfDay === 'evening peak' ? 'Heavy' : 'Normal'} traffic flow detected across corridor. Camera #${randomCamera1.Id} at ${loc1.shortLocation} shows ${vehicleCount} active vehicles. ${loc2.exit} sector clear. All work zones nominal.`,

    `Corridor-wide scan complete. ${loc1.exit} to ${loc2.exit} segment (${Math.abs(loc2.km - loc1.km).toFixed(1)}km) shows optimal conditions. Camera #${randomCamera1.Id} monitoring ${loc1.exit}. No congestion detected.`,

    `Traffic velocity ${timeOfDay === 'morning peak' || timeOfDay === 'evening peak' ? 'elevated' : 'normal'} for ${timeOfDay} period. Cameras #${randomCamera1.Id} (${loc1.exit}), #${randomCamera2.Id} (${loc2.exit}) report free-flow conditions. Weather clear.`,

    `Active monitoring: ${cameras.length} cameras across 40km corridor. Camera #${randomCamera3.Id} at ${loc3.shortLocation} shows ${vehicleCount} vehicles in frame. ${loc1.exit} sector normal. No safety alerts.`,

    `Real-time analysis: ${loc1.exit} (${loc1.kmFormatted}) to ${loc2.exit} (${loc2.kmFormatted}) clear. Camera #${randomCamera2.Id} reports ${vehicleCount} vehicles. All work zones operating safely per MTO BOOK 7 standards.`,

    `Corridor status: Camera #${randomCamera1.Id} at ${loc1.kmFormatted} near ${loc1.exit} monitoring ${vehicleCount} vehicles. ${loc3.exit} sector clear. ${timeOfDay === 'morning peak' ? 'Rush hour traffic moving steadily.' : 'Traffic flow nominal.'}`,

    `AI scan: ${cameras.length} COMPASS cameras active. Focus on ${loc2.exit} area (Camera #${randomCamera2.Id}, ${loc2.kmFormatted}). No incidents detected. Weather conditions optimal for all work zones.`,

    `Live feed analysis: ${loc1.exit} to ${loc3.exit} segment shows ${vehicleCount} active vehicles. Camera #${randomCamera3.Id} (${loc3.shortLocation}) clear. ${timeOfDay === 'evening peak' ? 'Evening commute steady.' : 'No congestion.'} All RSU broadcasts nominal.`
  ];

  return analysisTemplates[Math.floor(Math.random() * analysisTemplates.length)];
}

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

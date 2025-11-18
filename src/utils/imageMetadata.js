/**
 * Image Metadata Utilities
 *
 * Extract and match geospatial/temporal features for synthetic testing
 */

/**
 * Get current corridor conditions (temporal context)
 *
 * @returns {Object} Current conditions
 */
export function getCurrentConditions() {
  const now = new Date();
  const hour = now.getHours();
  const month = now.getMonth(); // 0-11

  // Determine time of day
  let timeOfDay = 'afternoon';
  if (hour >= 5 && hour < 12) {
    timeOfDay = 'morning';
  } else if (hour >= 12 && hour < 17) {
    timeOfDay = 'afternoon';
  } else if (hour >= 17 && hour < 21) {
    timeOfDay = 'evening';
  } else {
    timeOfDay = 'night';
  }

  // Determine season (Northern Hemisphere)
  let season = 'summer';
  if (month >= 2 && month < 5) {
    season = 'spring'; // Mar, Apr, May
  } else if (month >= 5 && month < 8) {
    season = 'summer'; // Jun, Jul, Aug
  } else if (month >= 8 && month < 11) {
    season = 'fall'; // Sep, Oct, Nov
  } else {
    season = 'winter'; // Dec, Jan, Feb
  }

  // Simple weather heuristic (could be enhanced with real weather API)
  // For now, we'll use seasonal defaults
  let weather = 'clear';
  if (season === 'winter') {
    weather = Math.random() > 0.5 ? 'cloudy' : 'clear';
  } else if (season === 'fall' || season === 'spring') {
    weather = Math.random() > 0.6 ? 'cloudy' : 'clear';
  } else {
    weather = 'sunny';
  }

  return {
    timeOfDay,
    season,
    weather,
    hour,
    month,
    date: now.toISOString(),
    dateString: now.toLocaleDateString(),
    timeString: now.toLocaleTimeString()
  };
}

/**
 * Format conditions for display in UI
 *
 * @param {Object} conditions - Conditions object
 * @returns {string} Formatted string
 */
export function formatConditions(conditions) {
  const { timeOfDay, season, weather, timeString } = conditions;

  const weatherEmoji = {
    sunny: '☀️',
    clear: '🌤️',
    cloudy: '☁️',
    rainy: '🌧️',
    snowy: '❄️',
    overcast: '☁️'
  };

  const seasonEmoji = {
    spring: '🌸',
    summer: '☀️',
    fall: '🍂',
    winter: '❄️'
  };

  return `${weatherEmoji[weather] || '🌤️'} ${capitalize(weather)} | ${seasonEmoji[season] || '🌸'} ${capitalize(season)} | ${capitalize(timeOfDay)} (${timeString})`;
}

/**
 * Get search terms for image API based on conditions
 *
 * @param {Object} conditions - Conditions object
 * @returns {string} Search query
 */
export function getSearchTerms(conditions) {
  const { timeOfDay, weather } = conditions;

  const base = 'highway construction work zone';
  const weatherTerm = weather;
  const timeTerm = timeOfDay === 'night' ? 'night' : 'daytime';

  return `${base} ${weatherTerm} ${timeTerm}`;
}

/**
 * Select a random camera from available cameras
 *
 * @param {Array} cameras - Array of camera objects
 * @returns {Object} Selected camera
 */
export function selectRandomCamera(cameras) {
  if (!cameras || cameras.length === 0) {
    return null;
  }

  const randomIndex = Math.floor(Math.random() * cameras.length);
  return cameras[randomIndex];
}

/**
 * Create synthetic image metadata
 *
 * @param {Object} params - Parameters
 * @param {Object} params.image - Image object from search
 * @param {Object} params.camera - Selected camera
 * @param {Object} params.conditions - Current conditions
 * @returns {Object} Synthetic metadata
 */
export function createSyntheticMetadata(params) {
  const { image, camera, conditions } = params;

  return {
    synthetic: true,
    source: 'SYNTHETIC_TEST',
    imageId: image.id,
    cameraId: camera ? camera.Id : null,
    cameraLocation: camera ? camera.Location : 'Test Location',
    cameraLat: camera ? camera.Latitude : 43.3850,
    cameraLon: camera ? camera.Longitude : -79.7400,
    searchTerms: image.searchTerms,
    conditions: conditions,
    injectedAt: new Date().toISOString(),
    photographer: image.photographer,
    photoSource: image.source,
    description: image.description
  };
}

/**
 * Format camera info for display
 *
 * @param {Object} camera - Camera object
 * @returns {string} Formatted camera info
 */
export function formatCameraInfo(camera) {
  if (!camera) return 'No camera selected';

  return `Camera ${camera.Id}: ${camera.Location}`;
}

/**
 * Capitalize first letter of string
 *
 * @param {string} str - String to capitalize
 * @returns {string} Capitalized string
 */
function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

/**
 * Get random work zone scenario description
 * Used for generating realistic test scenarios
 *
 * @returns {string} Scenario description
 */
export function getRandomScenario() {
  const scenarios = [
    'Lane closure with active workers and equipment',
    'Barrier installation in progress',
    'Road resurfacing operation',
    'Bridge repair with reduced lanes',
    'Utility work near travel lanes',
    'Sign installation and maintenance',
    'Concrete pouring and finishing',
    'Pavement marking and striping',
    'Emergency pothole repair',
    'Median barrier construction'
  ];

  return scenarios[Math.floor(Math.random() * scenarios.length)];
}

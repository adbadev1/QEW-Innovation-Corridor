/**
 * Work Zone History Tracker
 *
 * Tracks cameras that have historically identified REAL work zones
 * through the camera collection and analysis system.
 *
 * Persisted to localStorage for long-term tracking across sessions.
 */

const STORAGE_KEY = 'qew_workzone_camera_history';

/**
 * Get all cameras that have detected work zones
 * @returns {Array<{cameraId: number, location: string, detectedAt: string, viewId: number}>}
 */
export function getWorkZoneCameras() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];

    const data = JSON.parse(stored);
    return Array.isArray(data) ? data : [];
  } catch (error) {
    console.error('[WorkZone History] Failed to load work zone cameras:', error);
    return [];
  }
}

/**
 * Add a camera to the work zone history
 * @param {number} cameraId - Camera ID
 * @param {string} location - Camera location description
 * @param {number} viewId - View ID
 * @param {Object} workZoneData - Additional work zone data (optional)
 */
export function addWorkZoneCamera(cameraId, location, viewId, workZoneData = {}) {
  try {
    const history = getWorkZoneCameras();

    // Check if this camera/view combo already exists
    const existingIndex = history.findIndex(
      item => item.cameraId === cameraId && item.viewId === viewId
    );

    const entry = {
      cameraId,
      location,
      viewId,
      detectedAt: new Date().toISOString(),
      riskScore: workZoneData.riskScore || null,
      workers: workZoneData.workers || null,
      vehicles: workZoneData.vehicles || null,
      equipment: workZoneData.equipment || null,
      lastUpdated: new Date().toISOString()
    };

    if (existingIndex >= 0) {
      // Update existing entry
      history[existingIndex] = {
        ...history[existingIndex],
        ...entry,
        firstDetectedAt: history[existingIndex].detectedAt, // Keep original detection time
        detectionCount: (history[existingIndex].detectionCount || 1) + 1
      };
    } else {
      // Add new entry
      history.push({
        ...entry,
        firstDetectedAt: entry.detectedAt,
        detectionCount: 1
      });
    }

    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
    console.log('[WorkZone History] Added camera to history:', { cameraId, location, viewId });

    return true;
  } catch (error) {
    console.error('[WorkZone History] Failed to add work zone camera:', error);
    return false;
  }
}

/**
 * Get unique camera IDs that have detected work zones
 * @returns {Array<number>} Array of camera IDs
 */
export function getWorkZoneCameraIds() {
  const history = getWorkZoneCameras();
  const uniqueIds = [...new Set(history.map(item => item.cameraId))];
  return uniqueIds;
}

/**
 * Check if a camera has detected work zones
 * @param {number} cameraId - Camera ID
 * @returns {boolean}
 */
export function hasDetectedWorkZone(cameraId) {
  const ids = getWorkZoneCameraIds();
  return ids.includes(cameraId);
}

/**
 * Get work zone history for a specific camera
 * @param {number} cameraId - Camera ID
 * @returns {Array} Array of work zone detections for this camera
 */
export function getCameraWorkZoneHistory(cameraId) {
  const history = getWorkZoneCameras();
  return history.filter(item => item.cameraId === cameraId);
}

/**
 * Clear all work zone history (for testing/reset)
 */
export function clearWorkZoneHistory() {
  try {
    localStorage.removeItem(STORAGE_KEY);
    console.log('[WorkZone History] History cleared');
    return true;
  } catch (error) {
    console.error('[WorkZone History] Failed to clear history:', error);
    return false;
  }
}

/**
 * Get summary statistics
 * @returns {Object} Summary statistics
 */
export function getWorkZoneStats() {
  const history = getWorkZoneCameras();
  const uniqueCameras = new Set(history.map(item => item.cameraId));
  const totalDetections = history.reduce((sum, item) => sum + (item.detectionCount || 1), 0);

  return {
    uniqueCameras: uniqueCameras.size,
    totalDetections,
    camerasWithWorkZones: history.length,
    lastDetection: history.length > 0
      ? history.reduce((latest, item) =>
          new Date(item.lastUpdated) > new Date(latest.lastUpdated) ? item : latest
        )
      : null
  };
}

/**
 * Get all work zones (alias for getWorkZoneCameras for compatibility)
 * @returns {Array} Array of work zone detections
 */
export function getAllWorkZones() {
  return getWorkZoneCameras();
}

/**
 * Get unique view IDs that have detected work zones
 * @returns {Array<number>} Array of view IDs (511ON Camera IDs)
 */
export function getWorkZoneViewIds() {
  const history = getWorkZoneCameras();
  const uniqueViewIds = [...new Set(history.map(item => item.viewId))];
  return uniqueViewIds;
}

/**
 * Check if a specific view has a work zone detected
 * @param {number} viewId - View ID (511ON Camera ID)
 * @returns {boolean}
 */
export function hasWorkZoneInView(viewId) {
  const viewIds = getWorkZoneViewIds();
  return viewIds.includes(viewId);
}

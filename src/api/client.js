/**
 * QEW Innovation Corridor - Frontend API Client
 * ==============================================
 *
 * Centralized API client for backend communication.
 * Connects React frontend to FastAPI backend.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Generic API request handler with error handling
 */
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;

  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  const config = { ...defaultOptions, ...options };

  try {
    const response = await fetch(url, config);

    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Unknown error' }));
      throw new Error(error.message || `HTTP ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
}

// =============================================================================
// CAMERAS API
// =============================================================================

/**
 * Get all cameras
 * @param {Object} params - Query parameters (skip, limit, active_only, has_direction)
 * @returns {Promise<Array>} List of cameras
 */
export async function getCameras(params = {}) {
  const query = new URLSearchParams(params).toString();
  return apiRequest(`/api/cameras${query ? `?${query}` : ''}`);
}

/**
 * Get specific camera by ID
 * @param {string} cameraId - Camera identifier
 * @returns {Promise<Object>} Camera object
 */
export async function getCamera(cameraId) {
  return apiRequest(`/api/cameras/${cameraId}`);
}

/**
 * Get camera statistics
 * @returns {Promise<Object>} Camera stats
 */
export async function getCameraStats() {
  return apiRequest('/api/cameras/stats/summary');
}

// =============================================================================
// WORK ZONES API
// =============================================================================

/**
 * Get all work zones
 * @param {Object} params - Query parameters (skip, limit, status, min_risk, hours)
 * @returns {Promise<Array>} List of work zones
 */
export async function getWorkZones(params = {}) {
  const query = new URLSearchParams(params).toString();
  return apiRequest(`/api/work-zones${query ? `?${query}` : ''}`);
}

/**
 * Get currently active work zones
 * @param {number} minRisk - Minimum risk score (default: 5)
 * @returns {Promise<Array>} Active work zones
 */
export async function getActiveWorkZones(minRisk = 5) {
  return apiRequest(`/api/work-zones/active?min_risk=${minRisk}`);
}

/**
 * Get work zone history
 * @param {Object} params - Query parameters (camera_id, days, skip, limit)
 * @returns {Promise<Array>} Historical work zones
 */
export async function getWorkZoneHistory(params = {}) {
  const query = new URLSearchParams(params).toString();
  return apiRequest(`/api/work-zones/history${query ? `?${query}` : ''}`);
}

/**
 * Get specific work zone by ID
 * @param {number} workZoneId - Work zone ID
 * @returns {Promise<Object>} Work zone object
 */
export async function getWorkZone(workZoneId) {
  return apiRequest(`/api/work-zones/${workZoneId}`);
}

/**
 * Create new work zone
 * @param {Object} workZoneData - Work zone data
 * @returns {Promise<Object>} Created work zone
 */
export async function createWorkZone(workZoneData) {
  return apiRequest('/api/work-zones', {
    method: 'POST',
    body: JSON.stringify(workZoneData),
  });
}

/**
 * Resolve work zone
 * @param {number} workZoneId - Work zone ID
 * @returns {Promise<Object>} Result message
 */
export async function resolveWorkZone(workZoneId) {
  return apiRequest(`/api/work-zones/${workZoneId}/resolve`, {
    method: 'PUT',
  });
}

/**
 * Get work zone statistics
 * @param {number} hours - Time window in hours (default: 24)
 * @returns {Promise<Object>} Work zone stats
 */
export async function getWorkZoneStats(hours = 24) {
  return apiRequest(`/api/work-zones/stats/summary?hours=${hours}`);
}

// =============================================================================
// COLLECTION API
// =============================================================================

/**
 * Start new camera collection run
 * @param {Object} params - Collection parameters
 * @returns {Promise<Object>} Collection run object
 */
export async function startCollection(params = {}) {
  return apiRequest('/api/collection/start', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

/**
 * Get collection run status
 * @param {string} collectionId - Collection ID
 * @returns {Promise<Object>} Collection status
 */
export async function getCollectionStatus(collectionId) {
  return apiRequest(`/api/collection/status/${collectionId}`);
}

/**
 * Trigger analysis on collected images
 * @param {string} collectionId - Collection ID
 * @param {number} minRiskThreshold - Minimum risk threshold
 * @returns {Promise<Object>} Analysis status
 */
export async function analyzeCollection(collectionId, minRiskThreshold = 5) {
  return apiRequest(`/api/collection/analyze/${collectionId}?min_risk_threshold=${minRiskThreshold}`, {
    method: 'POST',
  });
}

/**
 * Get collection history
 * @param {Object} params - Query parameters (skip, limit, status, days)
 * @returns {Promise<Array>} Collection runs
 */
export async function getCollectionHistory(params = {}) {
  const query = new URLSearchParams(params).toString();
  return apiRequest(`/api/collection/history${query ? `?${query}` : ''}`);
}

/**
 * Get latest collection run
 * @returns {Promise<Object>} Latest collection
 */
export async function getLatestCollection() {
  return apiRequest('/api/collection/latest');
}

/**
 * Get collection statistics
 * @param {number} days - Time window in days (default: 30)
 * @returns {Promise<Object>} Collection stats
 */
export async function getCollectionStats(days = 30) {
  return apiRequest(`/api/collection/stats/summary?days=${days}`);
}

// =============================================================================
// CAMERA DIRECTIONS API
// =============================================================================

/**
 * Get all camera directions
 * @param {Object} params - Query parameters (skip, limit, camera_id, confidence)
 * @returns {Promise<Array>} Camera directions
 */
export async function getCameraDirections(params = {}) {
  const query = new URLSearchParams(params).toString();
  return apiRequest(`/api/directions${query ? `?${query}` : ''}`);
}

/**
 * Get cameras with direction data
 * @param {Object} params - Query parameters (skip, limit, has_direction)
 * @returns {Promise<Array>} Cameras with directions
 */
export async function getCamerasWithDirections(params = {}) {
  const query = new URLSearchParams(params).toString();
  return apiRequest(`/api/directions/cameras${query ? `?${query}` : ''}`);
}

/**
 * Trigger camera direction analysis
 * @param {Object} params - Analysis parameters (camera_id, view_id, force_reanalysis)
 * @returns {Promise<Object>} Analysis status
 */
export async function analyzeCameraDirections(params = {}) {
  return apiRequest('/api/directions/analyze', {
    method: 'POST',
    body: JSON.stringify(params),
  });
}

/**
 * Create camera direction record
 * @param {Object} directionData - Direction data
 * @returns {Promise<Object>} Created direction record
 */
export async function createCameraDirection(directionData) {
  return apiRequest('/api/directions', {
    method: 'POST',
    body: JSON.stringify(directionData),
  });
}

/**
 * Get camera direction statistics
 * @returns {Promise<Object>} Direction stats
 */
export async function getDirectionStats() {
  return apiRequest('/api/directions/stats/summary');
}

// =============================================================================
// AI ANALYSIS API
// =============================================================================

/**
 * Analyze single image
 * @param {Object} analysisRequest - Image analysis request
 * @returns {Promise<Object>} Analysis result
 */
export async function analyzeImage(analysisRequest) {
  return apiRequest('/api/analysis/image', {
    method: 'POST',
    body: JSON.stringify(analysisRequest),
  });
}

/**
 * Upload and analyze image file
 * @param {File} file - Image file
 * @param {Object} params - Analysis parameters
 * @returns {Promise<Object>} Analysis result
 */
export async function uploadAndAnalyzeImage(file, params = {}) {
  const formData = new FormData();
  formData.append('file', file);

  if (params.camera_id) formData.append('camera_id', params.camera_id);
  if (params.model) formData.append('model', params.model);
  if (params.min_risk_threshold) formData.append('min_risk_threshold', params.min_risk_threshold);

  return apiRequest('/api/analysis/upload', {
    method: 'POST',
    body: formData,
    headers: {}, // Let browser set Content-Type for FormData
  });
}

/**
 * Batch analyze multiple images
 * @param {Object} batchRequest - Batch analysis request
 * @returns {Promise<Object>} Batch analysis result
 */
export async function analyzeBatch(batchRequest) {
  return apiRequest('/api/analysis/batch', {
    method: 'POST',
    body: JSON.stringify(batchRequest),
  });
}

/**
 * Get analysis history
 * @param {Object} params - Query parameters (skip, limit, camera_id, min_risk)
 * @returns {Promise<Array>} Analysis history
 */
export async function getAnalysisHistory(params = {}) {
  const query = new URLSearchParams(params).toString();
  return apiRequest(`/api/analysis/history${query ? `?${query}` : ''}`);
}

/**
 * Get analysis statistics
 * @returns {Promise<Object>} Analysis stats
 */
export async function getAnalysisStats() {
  return apiRequest('/api/analysis/stats/summary');
}

// =============================================================================
// HEALTH & STATUS API
// =============================================================================

/**
 * Check backend health
 * @returns {Promise<Object>} Health status
 */
export async function getHealth() {
  return apiRequest('/health');
}

/**
 * Get API root information
 * @returns {Promise<Object>} API info
 */
export async function getApiInfo() {
  return apiRequest('/');
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

/**
 * Check if backend is reachable
 * @returns {Promise<boolean>} True if backend is online
 */
export async function isBackendOnline() {
  try {
    await getHealth();
    return true;
  } catch (error) {
    return false;
  }
}

/**
 * Get API base URL
 * @returns {string} Base URL
 */
export function getApiBaseUrl() {
  return API_BASE_URL;
}

// Export all functions as default object
export default {
  // Cameras
  getCameras,
  getCamera,
  getCameraStats,

  // Work Zones
  getWorkZones,
  getActiveWorkZones,
  getWorkZoneHistory,
  getWorkZone,
  createWorkZone,
  resolveWorkZone,
  getWorkZoneStats,

  // Collection
  startCollection,
  getCollectionStatus,
  analyzeCollection,
  getCollectionHistory,
  getLatestCollection,
  getCollectionStats,

  // Camera Directions
  getCameraDirections,
  getCamerasWithDirections,
  analyzeCameraDirections,
  createCameraDirection,
  getDirectionStats,

  // AI Analysis
  analyzeImage,
  uploadAndAnalyzeImage,
  analyzeBatch,
  getAnalysisHistory,
  getAnalysisStats,

  // Health
  getHealth,
  getApiInfo,

  // Utilities
  isBackendOnline,
  getApiBaseUrl,
};

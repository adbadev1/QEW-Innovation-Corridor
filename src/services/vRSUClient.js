/**
 * vRSU Client Service
 * ===================
 *
 * Frontend client for Virtual RSU (vRSU) broadcast service.
 * Handles V2X message broadcasting to connected vehicles.
 *
 * Features:
 * - SAE J2735 message broadcasting
 * - Broadcast history tracking
 * - Real-time statistics
 * - Error handling and retry logic
 *
 * Author: ADBA Labs
 * Project: QEW Innovation Corridor
 */

// vRSU Service Configuration
const VRSU_SERVICE_URL = import.meta.env.VITE_VRSU_SERVICE_URL || 'http://localhost:8080';

/**
 * vRSU Client for V2X message broadcasting
 */
class VRSUClient {
  constructor(serviceUrl = VRSU_SERVICE_URL) {
    this.serviceUrl = serviceUrl;
    this.broadcastHistory = [];
    this.maxHistorySize = 100;
  }

  /**
   * Broadcast work zone alert to connected vehicles
   *
   * @param {Object} workZoneAnalysis - Work zone analysis from Gemini AI
   * @param {string} messageType - Message type: 'TIM' or 'RSA'
   * @param {string} priority - Priority: 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
   * @returns {Promise<Object>} Broadcast response
   */
  async broadcastAlert(workZoneAnalysis, messageType = 'TIM', priority = null) {
    try {
      // Auto-determine priority based on risk score if not specified
      if (!priority) {
        priority = this._determinePriority(workZoneAnalysis.riskScore);
      }

      // Prepare request payload
      const payload = {
        analysis: {
          camera_id: workZoneAnalysis.cameraId || 'UNKNOWN',
          latitude: workZoneAnalysis.lat || 0,
          longitude: workZoneAnalysis.lon || 0,
          elevation: workZoneAnalysis.elevation || null,
          risk_score: workZoneAnalysis.riskScore || 5,
          workers: workZoneAnalysis.workers || 0,
          vehicles: workZoneAnalysis.vehicles || 0,
          distance_to_zone: 500, // Default 500m
          hazards: workZoneAnalysis.hazards || [],
          violations: workZoneAnalysis.violations || [],
          confidence: workZoneAnalysis.confidence || 1.0
        },
        message_type: messageType,
        priority: priority
      };

      console.log(`🚨 Broadcasting ${messageType} message (Priority: ${priority})...`);
      console.log(`📍 Location: ${payload.analysis.latitude}, ${payload.analysis.longitude}`);
      console.log(`⚠️ Risk Score: ${payload.analysis.risk_score}/10`);

      // Call vRSU service API
      const response = await fetch(`${this.serviceUrl}/api/v1/broadcast`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload)
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP ${response.status}`);
      }

      const result = await response.json();

      // Add to local history
      this._addToHistory({
        ...result,
        localTimestamp: new Date().toISOString(),
        cameraId: payload.analysis.camera_id,
        riskScore: payload.analysis.risk_score
      });

      console.log(`✅ Broadcast successful! Message ID: ${result.message_id}`);
      console.log(`📏 Message size: ${result.message_size} bytes`);
      console.log(`📡 Status: ${result.broadcast_status}`);

      return result;

    } catch (error) {
      console.error('❌ Broadcast failed:', error.message);
      throw new Error(`vRSU broadcast failed: ${error.message}`);
    }
  }

  /**
   * Broadcast work zone alert if risk score is high enough
   *
   * @param {Object} workZoneAnalysis - Work zone analysis from Gemini AI
   * @param {number} threshold - Minimum risk score to broadcast (default: 5)
   * @returns {Promise<Object|null>} Broadcast response or null if below threshold
   */
  async broadcastIfHighRisk(workZoneAnalysis, threshold = 5) {
    if (workZoneAnalysis.riskScore < threshold) {
      console.log(`📊 Risk score ${workZoneAnalysis.riskScore}/10 below threshold ${threshold} - skipping broadcast`);
      return null;
    }

    return await this.broadcastAlert(workZoneAnalysis);
  }

  /**
   * Get recent broadcast history
   *
   * @param {number} limit - Number of broadcasts to return
   * @param {string} cameraId - Filter by camera ID (optional)
   * @returns {Promise<Array>} Array of broadcast records
   */
  async getBroadcastHistory(limit = 10, cameraId = null) {
    try {
      let url = `${this.serviceUrl}/api/v1/broadcasts?limit=${limit}`;
      if (cameraId) {
        url += `&camera_id=${cameraId}`;
      }

      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      return data.broadcasts || [];

    } catch (error) {
      console.error('Failed to fetch broadcast history:', error);
      // Return local history as fallback
      return this.broadcastHistory.slice(-limit);
    }
  }

  /**
   * Get broadcast statistics
   *
   * @returns {Promise<Object>} Broadcast statistics
   */
  async getStatistics() {
    try {
      const response = await fetch(`${this.serviceUrl}/api/v1/stats`);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      return await response.json();

    } catch (error) {
      console.error('Failed to fetch statistics:', error);
      // Return local statistics as fallback
      return this._calculateLocalStats();
    }
  }

  /**
   * Check if vRSU service is operational
   *
   * @returns {Promise<boolean>} True if service is healthy
   */
  async healthCheck() {
    try {
      const response = await fetch(`${this.serviceUrl}/`);
      if (!response.ok) return false;

      const data = await response.json();
      return data.status === 'operational';

    } catch (error) {
      console.error('vRSU health check failed:', error);
      return false;
    }
  }

  /**
   * Get local broadcast history (cached)
   *
   * @returns {Array} Local broadcast records
   */
  getLocalHistory() {
    return [...this.broadcastHistory];
  }

  /**
   * Clear local broadcast history
   */
  clearLocalHistory() {
    this.broadcastHistory = [];
  }

  // Private methods

  /**
   * Determine broadcast priority based on risk score
   *
   * @private
   * @param {number} riskScore - Risk score (1-10)
   * @returns {string} Priority level
   */
  _determinePriority(riskScore) {
    if (riskScore >= 9) return 'CRITICAL';
    if (riskScore >= 7) return 'HIGH';
    if (riskScore >= 5) return 'MEDIUM';
    return 'LOW';
  }

  /**
   * Add broadcast to local history
   *
   * @private
   * @param {Object} broadcast - Broadcast record
   */
  _addToHistory(broadcast) {
    this.broadcastHistory.push(broadcast);

    // Trim history if too large
    if (this.broadcastHistory.length > this.maxHistorySize) {
      this.broadcastHistory.shift();
    }
  }

  /**
   * Calculate statistics from local history
   *
   * @private
   * @returns {Object} Local statistics
   */
  _calculateLocalStats() {
    if (this.broadcastHistory.length === 0) {
      return {
        total_broadcasts: 0,
        tim_count: 0,
        rsa_count: 0,
        avg_risk_score: 0,
        avg_message_size: 0
      };
    }

    const total = this.broadcastHistory.length;
    const timCount = this.broadcastHistory.filter(b => b.message_type === 'TIM').length;
    const rsaCount = this.broadcastHistory.filter(b => b.message_type === 'RSA').length;
    const avgRisk = this.broadcastHistory.reduce((sum, b) => sum + (b.riskScore || 0), 0) / total;
    const avgSize = this.broadcastHistory.reduce((sum, b) => sum + (b.message_size || 0), 0) / total;

    return {
      total_broadcasts: total,
      tim_count: timCount,
      rsa_count: rsaCount,
      avg_risk_score: Math.round(avgRisk * 100) / 100,
      avg_message_size: Math.round(avgSize),
      last_broadcast: this.broadcastHistory[total - 1]?.timestamp
    };
  }
}

// Create singleton instance
const vrsuClient = new VRSUClient();

// Export client instance and class
export { vrsuClient, VRSUClient };

// Export convenience functions
export const broadcastWorkZoneAlert = (analysis, messageType, priority) =>
  vrsuClient.broadcastAlert(analysis, messageType, priority);

export const broadcastIfHighRisk = (analysis, threshold) =>
  vrsuClient.broadcastIfHighRisk(analysis, threshold);

export const getBroadcastHistory = (limit, cameraId) =>
  vrsuClient.getBroadcastHistory(limit, cameraId);

export const getVRSUStatistics = () =>
  vrsuClient.getStatistics();

export const checkVRSUHealth = () =>
  vrsuClient.healthCheck();

export default vrsuClient;

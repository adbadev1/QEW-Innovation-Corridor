// Risk Utility Functions - REAL DATA ONLY
// Used for AI-detected work zone risk analysis

/**
 * Get color styling for risk score (from Gemini AI analysis)
 * @param {number} score - Risk score from AI (0-10)
 * @returns {string} TailwindCSS classes
 */
export const getRiskColor = (score) => {
  if (score >= 7) return 'text-red-600 bg-red-50 border-red-200';
  if (score >= 4) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
  return 'text-green-600 bg-green-50 border-green-200';
};

/**
 * Get risk label for score (from Gemini AI analysis)
 * @param {number} score - Risk score from AI (0-10)
 * @returns {string} Risk label
 */
export const getRiskLabel = (score) => {
  if (score >= 7) return 'HIGH RISK';
  if (score >= 4) return 'MEDIUM RISK';
  return 'LOW RISK';
};

/**
 * Generate V2X alert message from real AI-detected work zone
 * @param {number} riskScore - Risk score from Gemini AI (0-10)
 * @param {Array} hazards - Array of detected hazards
 * @returns {string} V2X alert message for RSU broadcast
 */
export const generateV2XAlert = (riskScore, hazards) => {
  const priority = riskScore >= 7 ? 'HIGH_RISK' : riskScore >= 4 ? 'MEDIUM_RISK' : 'LOW_RISK';
  const speedLimit = riskScore >= 7 ? 60 : riskScore >= 4 ? 80 : 100;

  return `WORK_ZONE_HAZARD|${priority}|REDUCE_SPEED_${speedLimit}`;
};

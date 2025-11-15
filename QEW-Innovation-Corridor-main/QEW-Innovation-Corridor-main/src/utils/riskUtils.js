// Reused from work-zone-safety-analyzer.jsx
export const getRiskColor = (score) => {
  if (score >= 7) return 'text-red-600 bg-red-50 border-red-200';
  if (score >= 4) return 'text-yellow-600 bg-yellow-50 border-yellow-200';
  return 'text-green-600 bg-green-50 border-green-200';
};

export const getRiskLabel = (score) => {
  if (score >= 7) return 'HIGH RISK';
  if (score >= 4) return 'MEDIUM RISK';
  return 'LOW RISK';
};

export const generateMockBSM = (lat, lon) => {
  return {
    id: Math.random().toString(36).substr(2, 9),
    lat,
    lon,
    speed: Math.random() * 120, // km/h
    heading: 90 + (Math.random() - 0.5) * 20, // degrees
    timestamp: Date.now()
  };
};

export const generateV2XAlert = (riskScore, hazards) => {
  const priority = riskScore >= 7 ? 'HIGH_RISK' : riskScore >= 4 ? 'MEDIUM_RISK' : 'LOW_RISK';
  const speedLimit = riskScore >= 7 ? 60 : riskScore >= 4 ? 80 : 100;

  return `WORK_ZONE_HAZARD|${priority}|REDUCE_SPEED_${speedLimit}`;
};

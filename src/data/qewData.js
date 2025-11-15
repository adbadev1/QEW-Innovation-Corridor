// QEW Innovation Corridor 40km - Burlington to Toronto
export const QEW_ROUTE = {
  burlington: [43.3255, -79.7990],
  toronto: [43.6426, -79.3871],
  center: [43.48405, -79.59355],
  zoom: 11
};

// Mock COMPASS camera locations along QEW
export const COMPASS_CAMERAS = [
  { id: 'CAM_QEW_10', name: 'QEW @ KM 10', lat: 43.3255, lon: -79.7990, status: 'active' },
  { id: 'CAM_QEW_15', name: 'QEW @ KM 15', lat: 43.3580, lon: -79.7500, status: 'active' },
  { id: 'CAM_QEW_20', name: 'QEW @ KM 20', lat: 43.3900, lon: -79.7000, status: 'active' },
  { id: 'CAM_QEW_25', name: 'QEW @ KM 25', lat: 43.4220, lon: -79.6500, status: 'active' },
  { id: 'CAM_QEW_30', name: 'QEW @ KM 30', lat: 43.4540, lon: -79.6000, status: 'active' },
  { id: 'CAM_QEW_35', name: 'QEW @ KM 35', lat: 43.4860, lon: -79.5500, status: 'active' },
  { id: 'CAM_QEW_40', name: 'QEW @ KM 40', lat: 43.5180, lon: -79.5000, status: 'active' },
  { id: 'CAM_QEW_45', name: 'QEW @ KM 45', lat: 43.5500, lon: -79.4500, status: 'active' },
  { id: 'CAM_QEW_50', name: 'QEW @ KM 50', lat: 43.6426, lon: -79.3871, status: 'active' }
];

// Mock work zones along QEW
export const WORK_ZONES = [
  {
    id: 'WZ_001',
    name: 'QEW Work Zone - Burlington',
    lat: 43.3580,
    lon: -79.7500,
    riskScore: 8,
    workers: 4,
    vehicles: 2,
    equipment: 1,
    barriers: false,
    status: 'HIGH RISK',
    hazards: [
      'Workers within 2m of active traffic lane',
      'Approaching vehicle speed >80 km/h',
      'Missing advance warning signage'
    ],
    cameraId: 'CAM_QEW_15'
  },
  {
    id: 'WZ_002',
    name: 'QEW Work Zone - Oakville',
    lat: 43.4540,
    lon: -79.6000,
    riskScore: 5,
    workers: 2,
    vehicles: 1,
    equipment: 2,
    barriers: true,
    status: 'MEDIUM RISK',
    hazards: [
      'Equipment partially obstructing sight lines'
    ],
    cameraId: 'CAM_QEW_30'
  },
  {
    id: 'WZ_003',
    name: 'QEW Work Zone - Mississauga',
    lat: 43.5500,
    lon: -79.4500,
    riskScore: 2,
    workers: 3,
    vehicles: 0,
    equipment: 1,
    barriers: true,
    status: 'LOW RISK',
    hazards: [
      'Minor: Cones spaced 12m apart (10m recommended)'
    ],
    cameraId: 'CAM_QEW_45'
  }
];

// Mock traffic data for simulation
export const generateMockTrafficData = () => {
  const data = [];
  const now = Date.now();

  for (let i = 0; i < 20; i++) {
    data.push({
      time: new Date(now - (20 - i) * 60000).toLocaleTimeString(),
      avgSpeed: 80 + Math.random() * 20,
      volume: 200 + Math.random() * 100,
      incidents: Math.random() > 0.8 ? 1 : 0
    });
  }

  return data;
};

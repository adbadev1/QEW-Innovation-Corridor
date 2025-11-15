// QEW Innovation Corridor - Burlington to Toronto (Production Coordinates)
// Based on actual highway route along Lake Ontario
export const QEW_ROUTE = {
  burlington: [43.3300, -79.8000],  // Burlington - Highway 403 junction
  toronto: [43.6395, -79.3950],      // Toronto - Gardiner Expressway junction
  center: [43.4848, -79.5975],       // Center point for map display
  zoom: 11
};

// COMPASS camera locations along QEW (Actual highway landmarks)
// Positioned at key interchanges and monitoring points
export const COMPASS_CAMERAS = [
  { id: 'CAM_QEW_403', name: 'QEW @ Highway 403', lat: 43.3300, lon: -79.8000, status: 'active' },
  { id: 'CAM_QEW_GUELPH', name: 'QEW @ Guelph Line', lat: 43.3400, lon: -79.7900, status: 'active' },
  { id: 'CAM_QEW_BURLOAK', name: 'QEW @ Burloak Drive', lat: 43.3850, lon: -79.7400, status: 'active' },
  { id: 'CAM_QEW_TRAFALGAR', name: 'QEW @ Trafalgar Rd', lat: 43.4350, lon: -79.6850, status: 'active' },
  { id: 'CAM_QEW_THIRD', name: 'QEW @ Third Line', lat: 43.4550, lon: -79.6650, status: 'active' },
  { id: 'CAM_QEW_WINSTON', name: 'QEW @ Winston Churchill', lat: 43.4900, lon: -79.6300, status: 'active' },
  { id: 'CAM_QEW_HURONTARIO', name: 'QEW @ Hurontario St', lat: 43.5450, lon: -79.6100, status: 'active' },
  { id: 'CAM_QEW_DIXIE', name: 'QEW @ Dixie Rd', lat: 43.5900, lon: -79.5800, status: 'active' },
  { id: 'CAM_QEW_CAWTHRA', name: 'QEW @ Cawthra Rd', lat: 43.6100, lon: -79.5600, status: 'active' },
  { id: 'CAM_QEW_ETOBICOKE', name: 'QEW @ Etobicoke Creek', lat: 43.6250, lon: -79.5350, status: 'active' },
  { id: 'CAM_QEW_ISLINGTON', name: 'QEW @ Islington Ave', lat: 43.6350, lon: -79.5000, status: 'active' },
  { id: 'CAM_QEW_KIPLING', name: 'QEW @ Kipling Ave', lat: 43.6370, lon: -79.4650, status: 'active' },
  { id: 'CAM_QEW_PARKLAWN', name: 'QEW @ Park Lawn Rd', lat: 43.6380, lon: -79.4250, status: 'active' }
];

// Work zones along QEW at actual construction sites
export const WORK_ZONES = [
  {
    id: 'WZ_001',
    name: 'QEW Work Zone - Burloak Drive',
    lat: 43.3850,
    lon: -79.7400,
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
    cameraId: 'CAM_QEW_BURLOAK'
  },
  {
    id: 'WZ_002',
    name: 'QEW Work Zone - Hurontario St',
    lat: 43.5450,
    lon: -79.6100,
    riskScore: 5,
    workers: 2,
    vehicles: 1,
    equipment: 2,
    barriers: true,
    status: 'MEDIUM RISK',
    hazards: [
      'Equipment partially obstructing sight lines',
      'Single barrier configuration (double recommended)'
    ],
    cameraId: 'CAM_QEW_HURONTARIO'
  },
  {
    id: 'WZ_003',
    name: 'QEW Work Zone - Etobicoke Creek',
    lat: 43.6250,
    lon: -79.5350,
    riskScore: 2,
    workers: 3,
    vehicles: 0,
    equipment: 1,
    barriers: true,
    status: 'LOW RISK',
    hazards: [
      'Minor: Cones spaced 12m apart (10m recommended)'
    ],
    cameraId: 'CAM_QEW_ETOBICOKE'
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

// QEW Innovation Corridor - Burlington to Toronto (Real Coordinates)
// Based on actual MTO COMPASS camera locations along QEW
export const QEW_ROUTE = {
  burlington: [43.336509, -79.828291],  // Burlington - Highway 403/407 junction
  toronto: [43.6395, -79.3950],         // Toronto - Gardiner Expressway junction
  center: [43.450, -79.720],            // Center point for map display (adjusted for real cameras)
  zoom: 11
};

// COMPASS camera locations along QEW (Real MTO COMPASS camera coordinates)
// Source: MTO COMPASS System - camera_locations.geojson
// All 46 QEW cameras from Hamilton to Mississauga
export const COMPASS_CAMERAS = [
  { id: 'CAM_4', name: 'QEW at Burlington Skyway', lat: 43.30917, lon: -79.803, status: 'active', source: 'RWIS (MTO)' },
  { id: 'CAM_210', name: 'QEW West of Fifty Road', lat: 43.2201, lon: -79.65143, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_211', name: 'QEW near Millen Road', lat: 43.239493, lon: -79.716024, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_212', name: 'QEW near Grays Road', lat: 43.241952, lon: -79.736366, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_213', name: 'QEW near Centennial Parkway', lat: 43.246828, lon: -79.756794, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_214', name: 'QEW near Red Hill Valley Parkway', lat: 43.248234, lon: -79.761738, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_215', name: 'QEW near Nikola Tesla Boulevard', lat: 43.258518, lon: -79.767008, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_216', name: 'QEW near Woodward Avenue', lat: 43.264956, lon: -79.772243, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_217', name: 'QEW West of Eastport Drive', lat: 43.284453, lon: -79.787521, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_218', name: 'QEW East of Eastport Drive - Toronto Bound', lat: 43.294075, lon: -79.793444, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_219', name: 'QEW Burlington Skyway - Hamilton Side', lat: 43.301446, lon: -79.797735, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_220', name: 'QEW Burlington Skyway - Toronto Side', lat: 43.299637, lon: -79.797852, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_221', name: 'QEW Ramp to Northshore Boulevard', lat: 43.314687, lon: -79.805717, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_222', name: 'QEW East of Northshore Boulevard', lat: 43.316623, lon: -79.808464, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_224', name: 'QEW near Fairview Street', lat: 43.327831, lon: -79.824901, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_225', name: 'QEW near Highway 403/407 IC', lat: 43.336509, lon: -79.828291, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_226', name: 'QEW West of Brant Street', lat: 43.339974, lon: -79.824729, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_227', name: 'QEW East of Brant Street', lat: 43.342596, lon: -79.819322, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_228', name: 'QEW near Guelph Line', lat: 43.350991, lon: -79.804387, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_229', name: 'QEW East of Guelph Line', lat: 43.358979, lon: -79.795504, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_230', name: 'QEW near Walkers Line', lat: 43.365999, lon: -79.787822, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_231', name: 'QEW East of Walkers Line', lat: 43.37567, lon: -79.77705, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_232', name: 'QEW near Appleby Line', lat: 43.380567, lon: -79.771857, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_233', name: 'QEW East of Appleby Line', lat: 43.387741, lon: -79.763918, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_234', name: 'QEW near Burloak Drive', lat: 43.39482, lon: -79.756279, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_235', name: 'QEW East of Burloak Drive', lat: 43.402927, lon: -79.74761, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_236', name: 'QEW near Bronte Road', lat: 43.409256, lon: -79.740829, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_237', name: 'QEW East of Bronte Road', lat: 43.413839, lon: -79.735937, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_238', name: 'QEW near Third Line', lat: 43.423658, lon: -79.724908, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_239', name: 'QEW East of Third Line', lat: 43.432844, lon: -79.714764, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_240', name: 'QEW near Fourth Line', lat: 43.437966, lon: -79.709307, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_241', name: 'QEW near Dorval Drive', lat: 43.446158, lon: -79.699845, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_242', name: 'QEW East of Dorval Drive', lat: 43.453417, lon: -79.691777, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_223', name: 'QEW near Trafalgar Road', lat: 43.460956, lon: -79.683623, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_243', name: 'QEW near Royal Windsor Drive', lat: 43.473415, lon: -79.671822, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_244', name: 'QEW East of Royal Windsor Drive', lat: 43.481701, lon: -79.672352, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_245', name: 'QEW near Ford Drive', lat: 43.494589, lon: -79.672165, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_246', name: 'QEW near Highway 403 (Oakville)', lat: 43.501126, lon: -79.678602, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_247', name: 'QEW West of Winston Churchill Boulevard', lat: 43.504197, lon: -79.66958, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_1159', name: 'QEW near Winston Churchill Boulevard', lat: 43.509095, lon: -79.663153, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_249', name: 'QEW West of Erin Mills Parkway', lat: 43.516564, lon: -79.655514, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_250', name: 'QEW near Southbound Road/Erin Mills Parkway', lat: 43.523846, lon: -79.647446, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_251', name: 'QEW East of Erin Mills Parkway', lat: 43.535794, lon: -79.634228, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_5', name: 'QEW near Mississauga Road (2)', lat: 43.550471, lon: -79.617523, status: 'active', source: 'RWIS (MTO)' },
  { id: 'CAM_252', name: 'QEW near Mississauga Road (1)', lat: 43.552218, lon: -79.612513, status: 'active', source: 'COMPASS - Central' },
  { id: 'CAM_253', name: 'QEW East of Mississauga Road', lat: 43.558128, lon: -79.607964, status: 'active', source: 'COMPASS - Central' }
];

// Work zones along QEW at actual construction sites (aligned with real camera locations)
export const WORK_ZONES = [
  {
    id: 'WZ_001',
    name: 'QEW Work Zone - Burloak Drive',
    lat: 43.39482,
    lon: -79.756279,
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
    cameraId: 'CAM_234'
  },
  {
    id: 'WZ_002',
    name: 'QEW Work Zone - Winston Churchill',
    lat: 43.509095,
    lon: -79.663153,
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
    cameraId: 'CAM_1159'
  },
  {
    id: 'WZ_003',
    name: 'QEW Work Zone - Erin Mills Parkway',
    lat: 43.535794,
    lon: -79.634228,
    riskScore: 2,
    workers: 3,
    vehicles: 0,
    equipment: 1,
    barriers: true,
    status: 'LOW RISK',
    hazards: [
      'Minor: Cones spaced 12m apart (10m recommended)'
    ],
    cameraId: 'CAM_251'
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

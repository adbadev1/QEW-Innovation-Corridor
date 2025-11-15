import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Circle, Popup, Polyline } from 'react-leaflet';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';
import { Shield, Activity, AlertTriangle, Radio, Camera, Navigation } from 'lucide-react';
import L from 'leaflet';

import { getRiskColor, getRiskLabel, generateMockBSM, generateV2XAlert } from './utils/riskUtils';
import { QEW_ROUTE, COMPASS_CAMERAS, WORK_ZONES, generateMockTrafficData } from './data/qewData';
import WorkZoneAnalysisPanel from './components/WorkZoneAnalysisPanel';

// Fix Leaflet default icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom icons for different markers
const createCustomIcon = (color) => new L.Icon({
  iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const workZoneIcon = createCustomIcon('red');
const cameraIcon = createCustomIcon('blue');
const vehicleIcon = createCustomIcon('green');

function App() {
  const [vehicles, setVehicles] = useState([]);
  const [selectedWorkZone, setSelectedWorkZone] = useState(null);
  const [trafficData, setTrafficData] = useState(generateMockTrafficData());
  const [alerts, setAlerts] = useState([]);
  const [aiAnalysis, setAiAnalysis] = useState('');

  // Simulate vehicle movement along QEW
  useEffect(() => {
    const interval = setInterval(() => {
      // Generate new vehicles at random points along QEW
      const latRange = QEW_ROUTE.toronto[0] - QEW_ROUTE.burlington[0];
      const lonRange = QEW_ROUTE.toronto[1] - QEW_ROUTE.burlington[1];

      const newVehicle = generateMockBSM(
        QEW_ROUTE.burlington[0] + Math.random() * latRange,
        QEW_ROUTE.burlington[1] + Math.random() * lonRange
      );

      setVehicles(prev => [...prev.slice(-20), newVehicle]);

      // Update traffic data
      if (Math.random() > 0.7) {
        setTrafficData(generateMockTrafficData());
      }

      // Simulate AI analysis
      if (Math.random() > 0.8) {
        analyzeTrafficWithAI();
      }
    }, 3000);

    return () => clearInterval(interval);
  }, []);

  const analyzeTrafficWithAI = () => {
    const analyses = [
      "Traffic flow nominal across all 40km corridor. No congestion detected.",
      "Moderate congestion detected at KM 25 (Oakville). Recommending speed reduction.",
      "Work zone at KM 15 showing elevated risk. RSU alert activated.",
      "Heavy vehicle concentration near KM 40. Monitoring for queue formation.",
      "Weather conditions optimal. All work zones operating safely."
    ];

    setAiAnalysis(analyses[Math.floor(Math.random() * analyses.length)]);
  };

  const handleWorkZoneClick = (workZone) => {
    setSelectedWorkZone(workZone);

    // Generate alert if high risk
    if (workZone.riskScore >= 7) {
      const alert = {
        id: Date.now(),
        message: `HIGH RISK: ${workZone.name} - ${workZone.hazards[0]}`,
        rsuAlert: generateV2XAlert(workZone.riskScore, workZone.hazards),
        timestamp: new Date().toLocaleTimeString()
      };
      setAlerts(prev => [alert, ...prev.slice(0, 4)]);
    }
  };

  // QEW route polyline
  const qewPath = [
    QEW_ROUTE.burlington,
    [43.3580, -79.7500],
    [43.3900, -79.7000],
    [43.4220, -79.6500],
    [43.4540, -79.6000],
    [43.4860, -79.5500],
    [43.5180, -79.5000],
    [43.5500, -79.4500],
    QEW_ROUTE.toronto
  ];

  return (
    <div className="h-screen flex flex-col bg-gray-900">
      {/* Header */}
      <header className="bg-gradient-to-r from-indigo-600 to-blue-700 text-white p-4 shadow-lg">
        <div className="flex items-center justify-between max-w-full mx-auto">
          <div className="flex items-center space-x-3">
            <Shield className="w-10 h-10" />
            <div>
              <h1 className="text-2xl font-bold">QEW Innovation Corridor - Digital Twin</h1>
              <p className="text-sm text-blue-100">40km Burlington → Toronto | Live Traffic Management System</p>
            </div>
          </div>
          <div className="flex items-center space-x-6 text-sm">
            <div className="flex items-center space-x-2">
              <Camera className="w-5 h-5" />
              <span>{COMPASS_CAMERAS.length} Cameras Active</span>
            </div>
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5" />
              <span>{WORK_ZONES.length} Work Zones</span>
            </div>
            <div className="flex items-center space-x-2">
              <Navigation className="w-5 h-5" />
              <span>{vehicles.length} Vehicles Tracked</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Map - Left 70% */}
        <div className="w-2/3 relative">
          <MapContainer
            center={QEW_ROUTE.center}
            zoom={QEW_ROUTE.zoom}
            className="h-full w-full"
          >
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {/* QEW Route Polyline */}
            <Polyline positions={qewPath} color="blue" weight={4} opacity={0.6} />

            {/* COMPASS Cameras */}
            {COMPASS_CAMERAS.map(camera => (
              <Marker
                key={camera.id}
                position={[camera.lat, camera.lon]}
                icon={cameraIcon}
              >
                <Popup>
                  <div className="text-sm">
                    <strong>{camera.name}</strong><br />
                    Status: {camera.status}<br />
                    <span className="text-blue-600">COMPASS System</span>
                  </div>
                </Popup>
              </Marker>
            ))}

            {/* Work Zones */}
            {WORK_ZONES.map(zone => (
              <React.Fragment key={zone.id}>
                <Marker
                  position={[zone.lat, zone.lon]}
                  icon={workZoneIcon}
                  eventHandlers={{
                    click: () => handleWorkZoneClick(zone)
                  }}
                >
                  <Popup>
                    <div className="text-sm">
                      <strong>{zone.name}</strong><br />
                      Risk Score: <span className={zone.riskScore >= 7 ? 'text-red-600 font-bold' : 'text-yellow-600'}>{zone.riskScore}/10</span><br />
                      Workers: {zone.workers} | Vehicles: {zone.vehicles}<br />
                      <button
                        onClick={() => handleWorkZoneClick(zone)}
                        className="mt-2 bg-indigo-600 text-white px-3 py-1 rounded text-xs hover:bg-indigo-700"
                      >
                        View Details
                      </button>
                    </div>
                  </Popup>
                </Marker>
                {/* Risk zone circle */}
                <Circle
                  center={[zone.lat, zone.lon]}
                  radius={500}
                  pathOptions={{
                    color: zone.riskScore >= 7 ? 'red' : zone.riskScore >= 4 ? 'orange' : 'green',
                    fillColor: zone.riskScore >= 7 ? 'red' : zone.riskScore >= 4 ? 'orange' : 'green',
                    fillOpacity: 0.2
                  }}
                />
              </React.Fragment>
            ))}

            {/* Simulated Vehicles */}
            {vehicles.map(vehicle => (
              <Marker
                key={vehicle.id}
                position={[vehicle.lat, vehicle.lon]}
                icon={vehicleIcon}
              >
                <Popup>
                  <div className="text-sm">
                    Vehicle ID: {vehicle.id}<br />
                    Speed: {vehicle.speed.toFixed(0)} km/h<br />
                    Heading: {vehicle.heading.toFixed(0)}°
                  </div>
                </Popup>
              </Marker>
            ))}
          </MapContainer>
        </div>

        {/* Right Panel - 30% */}
        <div className="w-1/3 bg-gray-800 text-white overflow-y-auto">
          {/* AI Traffic Analyst */}
          <div className="p-6 border-b border-gray-700">
            <h2 className="text-xl font-bold mb-4 flex items-center">
              <Activity className="w-6 h-6 mr-2 text-indigo-400" />
              AI Traffic Analyst
            </h2>
            <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
              <p className="text-sm text-gray-300">
                {aiAnalysis || "Initializing AI analysis..."}
              </p>
              <p className="text-xs text-gray-500 mt-2">
                Powered by Claude 3.5 Sonnet
              </p>
            </div>
          </div>

          {/* Active Alerts */}
          <div className="p-6 border-b border-gray-700">
            <h3 className="text-lg font-semibold mb-3 flex items-center">
              <Radio className="w-5 h-5 mr-2 text-red-400" />
              Active RSU Broadcasts
            </h3>
            <div className="space-y-2">
              {alerts.length > 0 ? alerts.map(alert => (
                <div key={alert.id} className="bg-red-900/30 border border-red-600 p-3 rounded">
                  <p className="text-sm text-red-200">{alert.message}</p>
                  <p className="text-xs font-mono text-gray-400 mt-1">{alert.rsuAlert}</p>
                  <p className="text-xs text-gray-500 mt-1">{alert.timestamp}</p>
                </div>
              )) : (
                <p className="text-sm text-gray-500">No active alerts</p>
              )}
            </div>
          </div>

          {/* Traffic Flow Chart */}
          <div className="p-6 border-b border-gray-700">
            <h3 className="text-lg font-semibold mb-3">Traffic Flow (Last 20 min)</h3>
            <ResponsiveContainer width="100%" height={150}>
              <LineChart data={trafficData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="time" stroke="#9CA3AF" tick={{ fontSize: 10 }} />
                <YAxis stroke="#9CA3AF" tick={{ fontSize: 10 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                  labelStyle={{ color: '#E5E7EB' }}
                />
                <Line type="monotone" dataKey="avgSpeed" stroke="#3B82F6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Work Zone Details */}
          {selectedWorkZone && (
            <WorkZoneAnalysisPanel
              workZone={selectedWorkZone}
              onClose={() => setSelectedWorkZone(null)}
            />
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 text-center py-3 text-sm border-t border-gray-700">
        QEW Innovation Corridor Pilot | ADBA Labs | OVIN $150K Application | Powered by Claude AI
      </footer>
    </div>
  );
}

export default App;

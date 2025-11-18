import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Circle, Popup, Polyline } from 'react-leaflet';
import { Shield, AlertTriangle, Camera, Navigation } from 'lucide-react';
import L from 'leaflet';

import { getRiskColor, getRiskLabel, generateMockBSM, generateV2XAlert } from './utils/riskUtils';
import { QEW_ROUTE, WORK_ZONES, generateMockTrafficData } from './data/qewData';
import WorkZoneAnalysisPanel from './components/WorkZoneAnalysisPanel';
import CameraCollectionPanel from './components/CameraCollectionPanel';
import SyntheticTestingPanel from './components/SyntheticTestingPanel';
import MLValidationPanel from './components/MLValidationPanel';
import TrafficMonitoringPanel from './components/TrafficMonitoringPanel';
import { CollectionProvider } from './contexts/CollectionContext';
import { useV2X } from './contexts/V2XContext';
import { calculateDistance } from './utils/geoUtils';
import { generateLocationAwareAnalysis, formatCameraLocation } from './utils/locationUtils';
import { qewPathWestbound, qewPathEastbound } from './data/qewRoutes';

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
const vehicleIconOrange = createCustomIcon('orange');  // V2X alert - medium/high risk
const vehicleIconRed = createCustomIcon('red');        // V2X alert - critical risk

function App() {
  const [vehicles, setVehicles] = useState([]);
  const [selectedWorkZone, setSelectedWorkZone] = useState(null);
  const [trafficData, setTrafficData] = useState(generateMockTrafficData());
  const [alerts, setAlerts] = useState([]);
  const [aiAnalysis, setAiAnalysis] = useState('');
  const [cameras, setCameras] = useState([]);
  const [loadingCameras, setLoadingCameras] = useState(true);
  const vehiclesInitialized = React.useRef(false);

  // V2X Context for vehicle alert management
  const { checkVehicleAlerts, getVehicleAlerts, activeBroadcasts } = useV2X();

  // Load real camera data with images from database export
  useEffect(() => {
    const basePath = import.meta.env.BASE_URL || '/';
    fetch(`${basePath}camera_scraper/qew_cameras_with_images.json`)
      .then(r => r.json())
      .then(cameraData => {
        setCameras(cameraData);
        setLoadingCameras(false);
      })
      .catch(error => {
        console.error('Error loading camera data:', error);
        setLoadingCameras(false);
      });
  }, []);

  // Initialize 10 vehicles at random positions along the routes
  // Only initialize AFTER routes are loaded
  useEffect(() => {
    // Don't initialize until routes are loaded
    if (!qewPathWestbound || !qewPathEastbound || qewPathWestbound.length === 0 || qewPathEastbound.length === 0) {
      console.log('Waiting for routes to load before initializing vehicles...');
      return;
    }

    // Don't re-initialize if already initialized
    if (vehiclesInitialized.current) {
      console.log('Vehicles already initialized, skipping...');
      return;
    }

    console.log('Initializing 10 vehicles...');
    const initialVehicles = [];

    for (let i = 0; i < 10; i++) {
      // Randomly assign to westbound or eastbound
      const direction = Math.random() > 0.5 ? 'westbound' : 'eastbound';
      const routeLength = direction === 'westbound' ? qewPathWestbound.length : qewPathEastbound.length;

      // Spread vehicles evenly along the route with some randomness
      const basePosition = (i / 10) * routeLength;
      const randomOffset = (Math.random() - 0.5) * (routeLength / 10);
      const position = Math.max(0, Math.min(routeLength - 1, basePosition + randomOffset));

      initialVehicles.push({
        id: `VEH_${i + 1}`,
        position: position,
        direction: direction,
        speed: 70 + Math.random() * 40, // 70-110 km/h (varied speeds so they don't overlap)
        speedMultiplier: 0.8 + Math.random() * 0.4, // 0.8x to 1.2x speed variation
        spawnOffset: Math.random() * 100, // Unique spawn offset for each vehicle (0-100)
      });
    }

    console.log(`Initialized ${initialVehicles.length} vehicles`);
    vehiclesInitialized.current = true; // Mark as initialized
    setVehicles(initialVehicles);
  }, [qewPathWestbound, qewPathEastbound]); // Re-run when routes load

  // Move vehicles along the route (1 hour per direction)
  useEffect(() => {
    // Don't start interval until routes are loaded and vehicles are initialized
    if (!qewPathWestbound || !qewPathEastbound || !vehiclesInitialized.current) {
      console.log('Waiting for routes and vehicles before starting movement...');
      return;
    }

    console.log('Starting vehicle movement interval...');
    let updateCount = 0;

    const interval = setInterval(() => {
      updateCount++;
      if (updateCount % 10 === 0) { // Log every 10th update to reduce spam
        console.log(`Vehicle update #${updateCount}`);
      }

      setVehicles(prevVehicles => {
        if (!qewPathWestbound || !qewPathEastbound) {
          console.warn('Routes not loaded, skipping vehicle update');
          return prevVehicles; // Don't move if routes aren't loaded
        }

        if (prevVehicles.length === 0) {
          console.warn('No vehicles to update');
          return prevVehicles;
        }

        const totalWestbound = qewPathWestbound.length;
        const totalEastbound = qewPathEastbound.length;

        const updatedVehicles = prevVehicles.map(vehicle => {
          // Calculate movement speed
          // 1 hour = 3600 seconds = 3600000 ms
          // Update every 3000ms (3 seconds)
          // So we need to move: totalWaypoints / (3600000 / 3000) = totalWaypoints / 1200 per update
          const baseMovement = vehicle.direction === 'westbound'
            ? totalWestbound / 1200
            : totalEastbound / 1200;

          // Apply speed multiplier for variation
          const movementPerUpdate = baseMovement * (vehicle.speedMultiplier || 1.0);

          let newPosition = vehicle.position + movementPerUpdate;
          let newDirection = vehicle.direction;

          // Get current route length
          const currentRouteLength = vehicle.direction === 'westbound' ? totalWestbound : totalEastbound;

          // Check if reached end of current route - switch to other route
          if (newPosition >= currentRouteLength - 5) {
            // Switch direction (go to other side of highway)
            newDirection = vehicle.direction === 'westbound' ? 'eastbound' : 'westbound';

            // Calculate new route length
            const newRouteLen = newDirection === 'westbound' ? totalWestbound : totalEastbound;

            // Spawn at a RANDOM position each time (not the same spawnOffset)
            // Use a percentage of the route length to ensure it's valid
            const randomPercent = Math.random(); // 0.0 to 1.0
            newPosition = newRouteLen * randomPercent;

            console.log(`${vehicle.id} switched from ${vehicle.direction} to ${newDirection} at position ${newPosition.toFixed(2)} (${(randomPercent * 100).toFixed(1)}% of route)`);
          }

          // Safety check - ensure position is always valid
          const newRouteLength = newDirection === 'westbound' ? totalWestbound : totalEastbound;
          if (newPosition < 0) {
            console.warn(`${vehicle.id} position < 0, clamping to 0`);
            newPosition = 0;
          }
          if (newPosition >= newRouteLength - 1) {
            console.warn(`${vehicle.id} position >= route length, clamping`);
            newPosition = newRouteLength - 2;
          }

          // Validate the new position
          if (isNaN(newPosition)) {
            console.error(`${vehicle.id} has NaN position! Resetting to 0`);
            newPosition = 0;
          }

          const updatedVehicle = {
            ...vehicle,
            position: newPosition,
            direction: newDirection,
          };

          // Check V2X alerts for this vehicle
          const route = newDirection === 'westbound' ? qewPathWestbound : qewPathEastbound;
          if (route && route.length > 0) {
            const index = Math.floor(newPosition);
            if (index >= 0 && index < route.length - 1) {
              const fraction = newPosition - index;
              const current = route[index];
              const next = route[index + 1];
              if (current && next && current.length >= 2 && next.length >= 2) {
                const lat = current[0] + (next[0] - current[0]) * fraction;
                const lon = current[1] + (next[1] - current[1]) * fraction;
                if (!isNaN(lat) && !isNaN(lon)) {
                  checkVehicleAlerts(updatedVehicle.id, [lat, lon], calculateDistance);
                }
              }
            }
          }

          return updatedVehicle;
        });

        // Log count to detect disappearing vehicles
        if (updatedVehicles.length !== prevVehicles.length) {
          console.error(`VEHICLE COUNT CHANGED! Was ${prevVehicles.length}, now ${updatedVehicles.length}`);
        }

        return updatedVehicles;
      });
    }, 3000); // Update every 3 seconds

    return () => {
      console.log('Cleaning up vehicle movement interval');
      clearInterval(interval);
    };
  }, [qewPathWestbound, qewPathEastbound]); // Only restart when routes change, NOT when vehicles update

  // Debug: Log vehicle status every 30 seconds
  useEffect(() => {
    const debugInterval = setInterval(() => {
      console.log('=== VEHICLE STATUS ===');
      vehicles.forEach(v => {
        const coords = getVehicleCoordinates(v);
        const routeLength = v.direction === 'westbound' ? qewPathWestbound?.length : qewPathEastbound?.length;
        const progress = routeLength ? ((v.position / routeLength) * 100).toFixed(1) : 'N/A';
        console.log(`${v.id}: ${v.direction} @ ${v.position.toFixed(2)}/${routeLength} (${progress}%) - Coords: ${coords ? `[${coords[0].toFixed(4)}, ${coords[1].toFixed(4)}]` : 'NULL'}`);
      });
      console.log('=====================');
    }, 30000); // Every 30 seconds

    return () => clearInterval(debugInterval);
  }, [vehicles]);

  // Get current lat/lon for a vehicle based on its position
  const getVehicleCoordinates = (vehicle) => {
    const route = vehicle.direction === 'westbound' ? qewPathWestbound : qewPathEastbound;

    // Safety checks
    if (!route || route.length === 0) {
      console.warn(`Route not loaded for ${vehicle.id}`);
      return null; // Return null instead of default - will be filtered out
    }

    // Ensure position is valid
    let position = vehicle.position;
    if (isNaN(position) || position < 0) {
      position = 0;
    }
    if (position >= route.length) {
      position = route.length - 1;
    }

    const index = Math.floor(position);

    // Bounds checking
    if (index < 0) {
      return route[0];
    }

    if (index >= route.length - 1) {
      return route[route.length - 1];
    }

    // Interpolate between waypoints for smooth movement
    const fraction = position - index;
    const current = route[index];
    const next = route[index + 1];

    // Additional safety check
    if (!current || !next || current.length < 2 || next.length < 2) {
      console.warn(`Invalid waypoint data for ${vehicle.id} at index ${index}`);
      return route[Math.min(index, route.length - 1)] || route[0];
    }

    const lat = current[0] + (next[0] - current[0]) * fraction;
    const lon = current[1] + (next[1] - current[1]) * fraction;

    // Validate coordinates
    if (isNaN(lat) || isNaN(lon)) {
      console.warn(`Invalid coordinates for ${vehicle.id}: [${lat}, ${lon}]`);
      return route[index];
    }

    return [lat, lon];
  };

  // OLD VEHICLE GENERATION CODE - DISABLED
  // This was conflicting with our new vehicle movement system
  // Keeping traffic data and AI analysis updates only
  useEffect(() => {
    const interval = setInterval(() => {
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
    // Generate location-aware AI analysis using real camera positions
    const analysis = generateLocationAwareAnalysis(cameras, vehicles);
    setAiAnalysis(analysis);
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

  // QEW route polylines - ACTUAL CAR ROUTES from OSRM
  // qewPathWestbound and qewPathEastbound imported from './data/qewRoutes'
  // These are real driving routes fetched from OpenStreetMap routing service
  // Route 1: Westbound (Hamilton → Toronto) - 364 waypoints
  // Route 2: Eastbound (Toronto → Hamilton) - 316 waypoints

  return (
    <CollectionProvider cameras={cameras}>
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
              <span>{cameras.length} COMPASS Cameras</span>
            </div>
            <div className="flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5" />
              <span>AI Work Zone Detection</span>
            </div>
            <div className="flex items-center space-x-2">
              <Navigation className="w-5 h-5" />
              <span>{vehicles.length} Vehicles</span>
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

            {/* QEW Route Polylines - ACTUAL CAR ROUTES (Both Directions) */}
            {/* Westbound: Hamilton → Toronto (364 waypoints) */}
            <Polyline positions={qewPathWestbound} color="blue" weight={3} opacity={0.6} />

            {/* Eastbound: Toronto → Hamilton (316 waypoints) */}
            <Polyline positions={qewPathEastbound} color="blue" weight={3} opacity={0.6} />

            {/* Real QEW Cameras */}
            {cameras.map(camera => {
              // Get location metadata
              const location = formatCameraLocation(camera);

              return (
                <Marker
                  key={camera.Id}
                  position={[camera.Latitude, camera.Longitude]}
                  icon={cameraIcon}
                >
                  <Popup maxWidth={400} maxHeight={500}>
                    <div className="text-sm">
                      <strong className="text-base block mb-1">{camera.Location}</strong>
                      <div className="flex items-center space-x-2 text-xs mt-1">
                        <span className="bg-blue-100 text-blue-800 px-2 py-0.5 rounded font-semibold">
                          📍 {location.kmFormatted}
                        </span>
                        <span className="bg-green-100 text-green-800 px-2 py-0.5 rounded font-semibold">
                          🛣️ {location.exit}
                        </span>
                      </div>
                      <div className="mt-2 space-y-1 text-xs">
                        <div><strong>Camera ID:</strong> #{camera.Id}</div>
                        <div><strong>Source:</strong> {camera.Source}</div>
                        <div><strong>Coordinates:</strong> {camera.Latitude.toFixed(4)}, {camera.Longitude.toFixed(4)}</div>
                      </div>
                      <div className="mt-3 space-y-3 max-h-80 overflow-y-auto">
                        {camera.Views.map(view => {
                          const basePath = import.meta.env.BASE_URL || '/';

                          // Get last collected image for this view
                          const lastImage = view.Images && view.Images.length > 0
                            ? view.Images[view.Images.length - 1]
                            : null;

                          return (
                            <div key={view.Id} className="border-t pt-2 first:border-t-0 first:pt-0">
                              <div className="font-semibold text-gray-700 mb-2 text-xs">
                                📹 {view.Description || 'Camera View'}
                              </div>

                              {/* Last Collected Image Thumbnail */}
                              {lastImage && (
                                <div className="mb-2" id={`img-container-${view.Id}`}>
                                  <div className="text-[10px] text-gray-600 mb-1 font-semibold">Last Collected Image:</div>
                                  <img
                                    src={`${basePath}camera_scraper/${lastImage.path}`}
                                    alt="Last collected camera image"
                                    className="w-full rounded border border-gray-300"
                                    onError={(e) => {
                                      console.warn('Image file not found:', `${basePath}camera_scraper/${lastImage.path}`);
                                      // Hide the entire image container instead of showing error text
                                      const container = document.getElementById(`img-container-${view.Id}`);
                                      if (container) container.style.display = 'none';
                                    }}
                                    onLoad={(e) => {
                                      console.log('Image loaded successfully:', lastImage.path);
                                    }}
                                  />
                                  <div className="text-[9px] text-gray-500 mt-1">
                                    Captured: {new Date(lastImage.timestamp.replace(/(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})/, '$1-$2-$3T$4:$5:$6')).toLocaleString()}
                                  </div>
                                </div>
                              )}

                              {/* Live Camera Link */}
                              <a
                                href={view.Url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="block"
                              >
                                <div className="bg-blue-50 border-2 border-blue-200 rounded p-3 text-center hover:bg-blue-100 transition">
                                  <div className="text-blue-600 font-semibold mb-1">
                                    🎥 View Live Camera Feed
                                  </div>
                                  <div className="text-xs text-gray-600">
                                    Click to open 511ON live feed
                                  </div>
                                </div>
                              </a>
                            </div>
                          );
                        })}
                      </div>
                    </div>
                  </Popup>
                </Marker>
              );
            })}


            {/* Simulated Vehicles - Moving along the actual QEW routes */}
            {/* These vehicles move along real OSRM car routes (1 hour per direction) */}
            {qewPathWestbound && qewPathEastbound && vehicles.map((vehicle, index) => {
              // Validate vehicle object
              if (!vehicle || !vehicle.id) {
                console.error(`Invalid vehicle at index ${index}:`, vehicle);
                return null;
              }

              const coords = getVehicleCoordinates(vehicle);

              // Safety check - don't render if coords are invalid
              if (!coords || coords.length < 2) {
                console.warn(`${vehicle.id} has invalid coords:`, coords, `Position: ${vehicle.position}, Direction: ${vehicle.direction}`);
                // Return a placeholder marker at a default location instead of null
                // This prevents the vehicle from disappearing from the array
                return (
                  <Marker
                    key={vehicle.id}
                    position={[43.4848, -79.5975]} // Default center position
                    icon={vehicleIcon}
                    opacity={0.3}
                  >
                    <Popup>
                      <div className="text-sm">
                        <strong>{vehicle.id}</strong><br />
                        <span className="text-xs text-red-500">(ERROR - Invalid Position)</span><br />
                        Position: {vehicle.position}<br />
                        Direction: {vehicle.direction}
                      </div>
                    </Popup>
                  </Marker>
                );
              }

              // Get V2X alerts for this vehicle
              const vehicleAlerts = getVehicleAlerts(vehicle.id);
              const hasAlert = vehicleAlerts.length > 0;

              // Determine icon color based on highest urgency
              let vehicleMarkerIcon = vehicleIcon;
              if (hasAlert) {
                const highestUrgency = Math.max(...vehicleAlerts.map(a =>
                  a.urgency === 'critical' ? 3 : a.urgency === 'high' ? 2 : 1
                ));
                vehicleMarkerIcon = highestUrgency >= 3 ? vehicleIconRed : vehicleIconOrange;
              }

              return (
                <Marker
                  key={vehicle.id}
                  position={coords}
                  icon={vehicleMarkerIcon}
                >
                  <Popup>
                    <div className="text-sm">
                      <strong>{vehicle.id}</strong><br />
                      Speed: {vehicle.speed.toFixed(0)} km/h<br />
                      Direction: {vehicle.direction === 'westbound' ? 'Hamilton → Toronto' : 'Toronto → Hamilton'}<br />
                      Progress: {(() => {
                        const routeLength = vehicle.direction === 'westbound' ? qewPathWestbound?.length : qewPathEastbound?.length;
                        if (!routeLength || routeLength === 0) return '0.0';
                        return ((vehicle.position / routeLength) * 100).toFixed(1);
                      })()}%

                      {/* V2X ALERTS - SMS Style Notifications */}
                      {vehicleAlerts.length > 0 && (
                        <div style={{ marginTop: '12px', borderTop: '1px solid #ddd', paddingTop: '8px' }}>
                          <strong style={{ color: '#ea580c', display: 'block', marginBottom: '8px' }}>
                            📱 V2X ALERTS ({vehicleAlerts.length})
                          </strong>
                          {vehicleAlerts.map((alert, idx) => (
                            <div
                              key={idx}
                              style={{
                                marginTop: idx > 0 ? '8px' : '0',
                                padding: '8px',
                                borderRadius: '4px',
                                fontSize: '11px',
                                backgroundColor: alert.urgency === 'critical' ? '#fee2e2' :
                                                 alert.urgency === 'high' ? '#ffedd5' : '#fef3c7',
                                border: alert.urgency === 'critical' ? '1px solid #f87171' :
                                        alert.urgency === 'high' ? '1px solid #fb923c' : '1px solid #fbbf24',
                                color: '#000'
                              }}
                            >
                              <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
                                {alert.message}
                              </div>
                              <div style={{ fontSize: '10px', display: 'flex', justifyContent: 'space-between' }}>
                                <span>Distance: {alert.distance}m</span>
                                <span>Speed Limit: {alert.speedLimit} km/h</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </Popup>
                </Marker>
              );
            })}
          </MapContainer>
        </div>

        {/* Right Panel - 30% */}
        <div className="w-1/3 bg-gray-800 text-white overflow-y-auto">
          {/* Traffic Monitoring Panel - Persistent Collapsible */}
          <TrafficMonitoringPanel
            aiAnalysis={aiAnalysis}
            alerts={alerts}
            trafficData={trafficData}
          />

          {/* Camera Collection Panel - Persistent Collapsible */}
          <CameraCollectionPanel />

          {/* Synthetic Testing Panel - Persistent Collapsible */}
          <SyntheticTestingPanel cameras={cameras} />

          {/* ML Vision Model Validation Panel - Persistent Collapsible */}
          <MLValidationPanel cameras={cameras} />

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
    </CollectionProvider>
  );
}

export default App;

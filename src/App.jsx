import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import { Shield, Camera } from 'lucide-react';
import L from 'leaflet';

import { QEW_ROUTE } from './data/qewData';
import CameraCollectionPanel from './components/CameraCollectionPanel';
import SyntheticTestingPanel from './components/SyntheticTestingPanel';
import MLValidationPanel from './components/MLValidationPanel';
import TrafficMonitoringPanel from './components/TrafficMonitoringPanel';
import CameraSpotlightLayer from './components/CameraSpotlightLayer';
import { CollectionProvider, useCollection } from './contexts/CollectionContext';
import { formatCameraLocation, getCameraIds } from './utils/locationUtils';
import { qewPathWestbound, qewPathEastbound } from './data/qewRoutes';
import { generateRealTrafficData, generateRealAIAnalysis, generateRealRSUAlerts } from './utils/realTrafficData';
import { getAllWorkZones, getWorkZoneViewIds } from './utils/workZoneHistory';
import { mergeThumbnailsIntoCameras } from './services/thumbnailStorage';

// Fix Leaflet default icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom icon for cameras
const createCustomIcon = (color) => new L.Icon({
  iconUrl: `https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-${color}.png`,
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.3.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const normalCameraIcon = createCustomIcon('blue');
const workZoneCameraIcon = createCustomIcon('red');

// Main App component wrapped in CollectionProvider
function AppContent() {
  const [cameras, setCameras] = useState([]);
  const [loadingCameras, setLoadingCameras] = useState(true);
  const [workZoneViewIds, setWorkZoneViewIds] = useState([]);
  const [trafficData, setTrafficData] = useState([]);
  const [aiAnalysis, setAiAnalysis] = useState('');
  const [alerts, setAlerts] = useState([]);

  // Get REAL collection stats from CollectionContext
  const { stats: collectionStats } = useCollection();

  // Load REAL camera data from 511ON (collected via Camera Collection System)
  useEffect(() => {
    const loadCameras = () => {
      const basePath = import.meta.env.BASE_URL || '/';
      fetch(`${basePath}camera_scraper/qew_cameras_with_images.json`)
        .then(r => r.json())
        .then(cameraData => {
          console.log(`✅ Loaded ${cameraData.length} REAL cameras from 511ON`);

          // Merge latest thumbnails from collection runs
          const camerasWithThumbnails = mergeThumbnailsIntoCameras(cameraData);
          console.log(`✅ Merged latest thumbnails into camera data`);

          setCameras(camerasWithThumbnails);
          setLoadingCameras(false);
        })
        .catch(error => {
          console.error('Error loading camera data:', error);
          setLoadingCameras(false);
        });
    };

    // Initial load
    loadCameras();

    // Reload cameras every 10 seconds to pick up new thumbnails from collection
    const interval = setInterval(loadCameras, 10000);

    return () => clearInterval(interval);
  }, []);

  // Load and refresh work zone view IDs every 3 seconds
  useEffect(() => {
    const updateWorkZones = () => {
      const viewIds = getWorkZoneViewIds();
      setWorkZoneViewIds(viewIds);
      console.log(`✅ Updated work zone views: ${viewIds.length} views with work zones detected`);
    };

    // Initial load
    updateWorkZones();

    // Refresh every 3 seconds to pick up new work zone detections
    const interval = setInterval(updateWorkZones, 3000);

    return () => clearInterval(interval);
  }, []);

  // Update REAL traffic data and AI analysis every 5 seconds
  useEffect(() => {
    const updateRealData = () => {
      // Get REAL work zone history from localStorage
      const workZoneHistory = getAllWorkZones();

      // Generate REAL traffic data from actual collection stats
      const realTrafficData = generateRealTrafficData(collectionStats, workZoneHistory);
      setTrafficData(realTrafficData);

      // Generate REAL AI analysis from Gemini detections
      const realAIAnalysis = generateRealAIAnalysis(cameras.length, workZoneHistory, collectionStats);
      setAiAnalysis(realAIAnalysis);

      // Generate REAL RSU alerts from work zone detections
      const realAlerts = generateRealRSUAlerts(workZoneHistory);
      setAlerts(realAlerts);
    };

    // Initial update
    updateRealData();

    // Update every 5 seconds with fresh REAL data
    const interval = setInterval(updateRealData, 5000);

    return () => clearInterval(interval);
  }, [cameras.length, collectionStats]);

  return (
    <div className="h-screen flex flex-col bg-gray-900">
      {/* Header */}
      <header className="bg-gradient-to-r from-indigo-600 to-blue-700 text-white p-4 shadow-lg">
        <div className="flex items-center justify-between max-w-full mx-auto">
          <div className="flex items-center space-x-3">
            <Shield className="w-10 h-10" />
            <div>
              <h1 className="text-2xl font-bold">QEW Innovation Corridor - REAL DATA ONLY</h1>
              <p className="text-sm text-blue-100">40km Burlington → Toronto | Live 511ON Camera Feeds</p>
            </div>
          </div>
          <div className="flex items-center space-x-6 text-sm">
            <div className="flex items-center space-x-2">
              <Camera className="w-5 h-5" />
              <span>{cameras.length} Real 511ON Cameras</span>
            </div>
            <div className="bg-green-600 px-3 py-1 rounded-full text-xs font-bold">
              🟢 REAL STREAMING DATA
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

            {/* QEW Route Polylines - REAL OSRM Routes */}
            <Polyline positions={qewPathWestbound} color="blue" weight={3} opacity={0.6} />
            <Polyline positions={qewPathEastbound} color="blue" weight={3} opacity={0.6} />

            {/* Camera Direction Spotlights - Backend Integrated */}
            <CameraSpotlightLayer />

            {/* REAL 511ON Cameras */}
            {cameras.map(camera => {
              const location = formatCameraLocation(camera);
              const cameraIds = getCameraIds(camera);

              // Check if ANY view in this camera has a work zone detected
              const hasWorkZone = camera.Views && camera.Views.some(view =>
                workZoneViewIds.includes(view.Id)
              );

              return (
                <Marker
                  key={camera.Id}
                  position={[camera.Latitude, camera.Longitude]}
                  icon={hasWorkZone ? workZoneCameraIcon : normalCameraIcon}
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
                        <div><strong>511ON Camera ID:</strong> #{cameraIds.realId}</div>
                        {cameraIds.realId !== cameraIds.internalId.toString() && (
                          <div className="text-[10px] text-gray-500">Internal DB ID: #{cameraIds.internalId}</div>
                        )}
                        <div><strong>Source:</strong> {camera.Source}</div>
                        <div><strong>GPS Coordinates:</strong> {camera.Latitude.toFixed(6)}°N, {camera.Longitude.toFixed(6)}°W</div>
                      </div>
                      <div className="mt-3 space-y-3 max-h-80 overflow-y-auto">
                        {camera.Views.map(view => {
                          const basePath = import.meta.env.BASE_URL || '/';
                          const latestThumbnail = view.LatestImage; // From collection run thumbnails
                          const lastImage = view.Images && view.Images.length > 0
                            ? view.Images[view.Images.length - 1]
                            : null;

                          // Check if THIS specific view has a work zone detected
                          const viewHasWorkZone = workZoneViewIds.includes(view.Id);

                          return (
                            <div key={view.Id} className={`border-t pt-2 first:border-t-0 first:pt-0 ${viewHasWorkZone ? 'bg-red-50 p-2 rounded' : ''}`}>
                              <div className="font-semibold text-gray-700 mb-2 text-xs flex items-center justify-between">
                                <span>📹 {view.Description || 'Camera View'}</span>
                                <div className="flex items-center space-x-1">
                                  <span className="text-[10px] bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                                    511ON ID: #{view.Id}
                                  </span>
                                  {viewHasWorkZone && (
                                    <span className="text-[10px] bg-red-600 text-white px-2 py-0.5 rounded font-bold animate-pulse">
                                      🚧 WORK ZONE
                                    </span>
                                  )}
                                </div>
                              </div>

                              {/* LATEST Thumbnail from Collection Run */}
                              {latestThumbnail && (
                                <div className="mb-2">
                                  <div className="text-[10px] text-green-600 mb-1 font-semibold flex items-center">
                                    <span className="bg-green-100 px-1 rounded">🆕 LATEST FROM COLLECTION RUN</span>
                                  </div>
                                  <img
                                    src={latestThumbnail.dataUrl}
                                    alt="Latest from collection run"
                                    className="w-full rounded border-2 border-green-400"
                                  />
                                  <div className="text-[9px] text-green-600 mt-1 font-semibold">
                                    Captured: {new Date(latestThumbnail.timestamp).toLocaleString()}
                                  </div>
                                </div>
                              )}

                              {/* Archived Collected Image (if available) */}
                              {lastImage && !latestThumbnail && (
                                <div className="mb-2" id={`img-container-${view.Id}`}>
                                  <div className="text-[10px] text-gray-600 mb-1 font-semibold">Archived Image:</div>
                                  <img
                                    src={`${basePath}camera_scraper/${lastImage.path}`}
                                    alt="Archived camera image"
                                    className="w-full rounded border border-gray-300"
                                    onError={(e) => {
                                      const container = document.getElementById(`img-container-${view.Id}`);
                                      if (container) container.style.display = 'none';
                                    }}
                                  />
                                  <div className="text-[9px] text-gray-500 mt-1">
                                    Captured: {new Date(lastImage.timestamp.replace(/(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})/, '$1-$2-$3T$4:$5:$6')).toLocaleString()}
                                  </div>
                                </div>
                              )}

                              {/* REAL Live Camera Feed Link */}
                              <a href={view.Url} target="_blank" rel="noopener noreferrer" className="block">
                                <div className="bg-blue-50 border-2 border-blue-200 rounded p-3 text-center hover:bg-blue-100 transition">
                                  <div className="text-blue-600 font-semibold mb-1">
                                    🎥 View LIVE 511ON Feed
                                  </div>
                                  <div className="text-xs text-gray-600">
                                    Real-time camera stream
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
          </MapContainer>
        </div>

        {/* Right Panel - 30% */}
        <div className="w-1/3 bg-gray-800 text-white overflow-y-auto">
          {/* REAL DATA PANELS ONLY */}

          {/* Real Traffic Monitoring (real metrics from camera collections) */}
          <TrafficMonitoringPanel
            aiAnalysis={aiAnalysis}
            alerts={alerts}
            trafficData={trafficData}
          />

          {/* Real Camera Collection System */}
          <CameraCollectionPanel />

          {/* Real ML Vision Validation (Gemini 2.0 Flash analysis) */}
          <MLValidationPanel cameras={cameras} />

          {/* Real Synthetic Testing (uses real images) */}
          <SyntheticTestingPanel cameras={cameras} />
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 text-center py-3 text-sm border-t border-gray-700">
        🟢 REAL DATA ONLY | QEW Innovation Corridor | OVIN $150K Application | Powered by Claude AI & Gemini 2.0 Flash
      </footer>
    </div>
  );
}

// Wrapper component with CollectionProvider
function App() {
  const [cameras, setCameras] = useState([]);

  // Load cameras once at app level
  useEffect(() => {
    const basePath = import.meta.env.BASE_URL || '/';
    fetch(`${basePath}camera_scraper/qew_cameras_with_images.json`)
      .then(r => r.json())
      .then(cameraData => {
        setCameras(cameraData);
      })
      .catch(error => {
        console.error('Error loading camera data:', error);
      });
  }, []);

  return (
    <CollectionProvider cameras={cameras}>
      <AppContent />
    </CollectionProvider>
  );
}

export default App;

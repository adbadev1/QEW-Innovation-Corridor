import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import { Shield, Camera } from 'lucide-react';
import L from 'leaflet';

import { QEW_ROUTE } from './data/qewData';
import CameraCollectionPanel from './components/CameraCollectionPanel';
import SyntheticTestingPanel from './components/SyntheticTestingPanel';
import MLValidationPanel from './components/MLValidationPanel';
import TrafficMonitoringPanel from './components/TrafficMonitoringPanel';
import { CollectionProvider } from './contexts/CollectionContext';
import { formatCameraLocation, getCameraIds } from './utils/locationUtils';
import { qewPathWestbound, qewPathEastbound } from './data/qewRoutes';

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

const cameraIcon = createCustomIcon('blue');

function App() {
  const [cameras, setCameras] = useState([]);
  const [loadingCameras, setLoadingCameras] = useState(true);

  // Load REAL camera data from 511ON (collected via Camera Collection System)
  useEffect(() => {
    const basePath = import.meta.env.BASE_URL || '/';
    fetch(`${basePath}camera_scraper/qew_cameras_with_images.json`)
      .then(r => r.json())
      .then(cameraData => {
        console.log(`✅ Loaded ${cameraData.length} REAL cameras from 511ON`);
        setCameras(cameraData);
        setLoadingCameras(false);
      })
      .catch(error => {
        console.error('Error loading camera data:', error);
        setLoadingCameras(false);
      });
  }, []);

  return (
    <CollectionProvider cameras={cameras}>
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

            {/* REAL 511ON Cameras */}
            {cameras.map(camera => {
              const location = formatCameraLocation(camera);
              const cameraIds = getCameraIds(camera);

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
                          const lastImage = view.Images && view.Images.length > 0
                            ? view.Images[view.Images.length - 1]
                            : null;

                          return (
                            <div key={view.Id} className="border-t pt-2 first:border-t-0 first:pt-0">
                              <div className="font-semibold text-gray-700 mb-2 text-xs">
                                📹 {view.Description || 'Camera View'}
                              </div>

                              {/* REAL Collected Image Thumbnail */}
                              {lastImage && (
                                <div className="mb-2" id={`img-container-${view.Id}`}>
                                  <div className="text-[10px] text-gray-600 mb-1 font-semibold">Last Collected Image:</div>
                                  <img
                                    src={`${basePath}camera_scraper/${lastImage.path}`}
                                    alt="Real collected camera image"
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

          {/* Real Camera Collection System */}
          <CameraCollectionPanel />

          {/* Real Synthetic Testing (uses real images) */}
          <SyntheticTestingPanel cameras={cameras} />

          {/* Real ML Vision Validation (Gemini 2.0 Flash analysis) */}
          <MLValidationPanel cameras={cameras} />
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-400 text-center py-3 text-sm border-t border-gray-700">
        🟢 REAL DATA ONLY | QEW Innovation Corridor | OVIN $150K Application | Powered by Claude AI & Gemini 2.0 Flash
      </footer>
      </div>
    </CollectionProvider>
  );
}

export default App;

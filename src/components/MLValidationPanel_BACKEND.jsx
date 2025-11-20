import React, { useState, useEffect } from 'react';
import { Microscope, Camera, Loader, CheckCircle, AlertTriangle, Radio, ChevronDown, ChevronUp } from 'lucide-react';
import { getCurrentConditions, formatConditions } from '../utils/imageMetadata';
import { useV2X } from '../contexts/V2XContext';
import { getActiveWorkZones } from '../api/client';

/**
 * ML Vision Model Validation Panel - BACKEND INTEGRATED
 * Uses backend API for all work zone analysis
 *
 * REFACTORED: Now uses /api/work-zones endpoints instead of localStorage
 */
function MLValidationPanel({ cameras }) {
  const [isExpanded, setIsExpanded] = useState(() => {
    const saved = localStorage.getItem('mlValidationExpanded');
    return saved !== null ? saved === 'true' : true;
  });
  const [conditions, setConditions] = useState(null);
  const [selectedCamera, setSelectedCamera] = useState(null);
  const [selectedView, setSelectedView] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);
  const [imageUrl, setImageUrl] = useState(null);
  const [workZones, setWorkZones] = useState([]);
  const [workZoneStats, setWorkZoneStats] = useState({ total: 0, cameras: 0 });

  const { registerBroadcast } = useV2X();

  // Load active work zones from backend API
  useEffect(() => {
    const loadWorkZones = async () => {
      try {
        const zones = await getActiveWorkZones(5); // min_risk = 5
        setWorkZones(zones);

        // Calculate stats
        const uniqueCameras = new Set(zones.map(z => z.camera_id));
        setWorkZoneStats({
          total: zones.length,
          cameras: uniqueCameras.size
        });

        console.log('[MLValidationPanel] Loaded work zones from backend:', zones.length);
      } catch (err) {
        console.error('[MLValidationPanel] Failed to load work zones:', err);
      }
    };

    // Load immediately
    loadWorkZones();

    // Poll for changes every 5 seconds
    const interval = setInterval(loadWorkZones, 5000);

    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    localStorage.setItem('mlValidationExpanded', isExpanded.toString());
  }, [isExpanded]);

  // Filter cameras to only those with detected work zones
  const workZoneCameraIds = workZones.map(wz => wz.camera_id);
  const workZoneCameras = cameras.filter(camera =>
    workZoneCameraIds.includes(`C${camera.Id}`)
  );

  useEffect(() => {
    const currentConditions = getCurrentConditions();
    setConditions(currentConditions);

    // Select first camera with work zone detection
    if (workZoneCameras && workZoneCameras.length > 0) {
      setSelectedCamera(workZoneCameras[0]);
      if (workZoneCameras[0].Views && workZoneCameras[0].Views.length > 0) {
        setSelectedView(workZoneCameras[0].Views[0]);
      }
    }
  }, [cameras, workZones.length]);

  const handleAnalyzeCamera = async () => {
    if (!selectedCamera || !selectedView) {
      setError('Please select a camera and view');
      return;
    }

    setAnalyzing(true);
    setError(null);
    setAnalysisResult(null);
    setImageUrl(selectedView.Url);

    try {
      // Use backend API for image analysis
      const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

      // Analyze image using backend endpoint
      const response = await fetch(`${API_BASE_URL}/api/analysis/image`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image_url: selectedView.Url,
          camera_id: `C${selectedCamera.Id}`,
          latitude: selectedCamera.Latitude,
          longitude: selectedCamera.Longitude,
          location: selectedCamera.Location
        })
      });

      if (!response.ok) {
        throw new Error(`Backend API error: ${response.status}`);
      }

      const analysis = await response.json();

      if (!analysis.has_work_zone) {
        setError('No work zone detected. Camera shows normal traffic.');
        setAnalyzing(false);
        return;
      }

      // Format result for display
      const workZone = {
        id: analysis.work_zone_id || `WZ_${Date.now()}`,
        camera_id: `C${selectedCamera.Id}`,
        riskScore: analysis.risk_score,
        workers: analysis.workers,
        vehicles: analysis.vehicles,
        equipment: analysis.equipment,
        barriers: analysis.barriers,
        hazards: analysis.hazards || [],
        location: {
          lat: selectedCamera.Latitude,
          lon: selectedCamera.Longitude
        },
        realCamera: {
          synthetic: false,
          source: 'COMPASS',
          cameraId: selectedCamera.Id,
          viewId: selectedView.Id,
          cameraLocation: selectedCamera.Location,
          viewDescription: selectedView.Description,
          cameraLat: selectedCamera.Latitude,
          cameraLon: selectedCamera.Longitude,
          capturedAt: new Date().toISOString()
        }
      };

      setAnalysisResult(workZone);
      setAnalyzing(false);

      // Register V2X broadcast if needed
      if (workZone.riskScore >= 7) {
        try {
          const broadcast = await registerBroadcast({
            messageType: 'WORK_ZONE_ALERT',
            severity: 'high',
            location: workZone.location,
            details: `High-risk work zone detected at ${selectedCamera.Location}`
          });
          workZone.vrsuBroadcast = broadcast;
        } catch (err) {
          console.error('Failed to register V2X broadcast:', err);
        }
      }

    } catch (err) {
      console.error('Error analyzing camera:', err);
      setError(err.message || 'Failed to analyze camera image');
      setAnalyzing(false);
    }
  };

  const handleReset = () => {
    setAnalysisResult(null);
    setError(null);
    setImageUrl(null);
  };

  return (
    <div className="bg-gray-800 text-white border-b border-gray-700">
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-2 bg-gradient-to-r from-cyan-600 to-blue-700 flex items-center justify-between hover:from-cyan-700 hover:to-blue-800 transition"
      >
        <div className="flex items-center space-x-1.5">
          <Microscope className="w-4 h-4" />
          <div className="text-left">
            <h2 className="text-sm font-bold">ML Vision Model Validation</h2>
            <p className="text-[9px] text-cyan-100">
              {analysisResult ? '🟢 Analysis Complete' : analyzing ? '🟡 Processing' : '⚪ Ready'} • Backend API Integration
            </p>
          </div>
        </div>
        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {isExpanded && (
        <div className="flex flex-col max-h-[600px] overflow-y-auto">
          {/* Current Conditions */}
          {conditions && (
            <div className="p-3 bg-gray-900 border-b border-gray-700">
              <h3 className="text-xs font-semibold mb-2">Current Corridor Conditions</h3>
              <p className="text-[10px] text-gray-300">{formatConditions(conditions)}</p>
              <p className="text-[9px] text-gray-500 mt-1">
                Active work zones (from backend): {workZoneStats.cameras} cameras • {workZoneStats.total} detections
              </p>
            </div>
          )}

          {/* Camera Selection */}
          {!analysisResult && (
            <div className="p-3 border-b border-gray-700 space-y-2">
              {workZoneCameras.length === 0 ? (
                <div className="p-3 bg-yellow-900/30 border border-yellow-600 rounded">
                  <p className="text-xs text-yellow-200 font-semibold mb-1">⚠️ No Work Zones in Database</p>
                  <p className="text-[10px] text-yellow-300 leading-tight">
                    No work zones have been detected yet. Run the collection system or manually analyze cameras to populate the database.
                  </p>
                </div>
              ) : (
                <div>
                  <h3 className="text-xs font-semibold mb-1 flex items-center">
                    <Camera className="w-3 h-3 mr-1" />
                    Select REAL WORK ZONES (from Backend API)
                  </h3>
                  <select
                    value={selectedCamera ? selectedCamera.Id : ''}
                    onChange={(e) => {
                      const camera = workZoneCameras.find(c => c.Id === parseInt(e.target.value));
                      setSelectedCamera(camera);
                      if (camera && camera.Views && camera.Views.length > 0) {
                        setSelectedView(camera.Views[0]);
                      }
                    }}
                    className="w-full px-2 py-1 bg-gray-900 border border-gray-600 rounded text-[10px]"
                  >
                    {workZoneCameras.map(camera => {
                      const viewId = camera.Views && camera.Views[0] ? camera.Views[0].Id : '?';
                      return (
                        <option key={camera.Id} value={camera.Id}>
                          Camera #{viewId} - {camera.Location}
                        </option>
                      );
                    })}
                  </select>
                </div>
              )}

              {/* View Selection */}
              {selectedCamera && selectedCamera.Views && selectedCamera.Views.length > 1 && (
                <div>
                  <h3 className="text-xs font-semibold mb-1">Select View</h3>
                  <select
                    value={selectedView ? selectedView.Id : ''}
                    onChange={(e) => {
                      const view = selectedCamera.Views.find(v => v.Id === parseInt(e.target.value));
                      setSelectedView(view);
                    }}
                    className="w-full px-2 py-1 bg-gray-900 border border-gray-600 rounded text-[10px]"
                  >
                    {selectedCamera.Views.map(view => (
                      <option key={view.Id} value={view.Id}>
                        {view.Description || `View ${view.Id}`}
                      </option>
                    ))}
                  </select>
                </div>
              )}
            </div>
          )}

          {/* Analyze Button */}
          {!analysisResult && workZoneCameras.length > 0 && (
            <div className="p-3 border-b border-gray-700">
              <button
                onClick={handleAnalyzeCamera}
                disabled={analyzing}
                className="w-full py-2 rounded font-bold text-[10px] bg-cyan-600 hover:bg-cyan-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-1.5"
              >
                {analyzing ? (
                  <>
                    <Loader className="w-3 h-3 animate-spin" />
                    <span>Analyzing via Backend API...</span>
                  </>
                ) : (
                  <>
                    <Microscope className="w-3 h-3" />
                    <span>ANALYZE CAMERA FEED (Backend)</span>
                  </>
                )}
              </button>
            </div>
          )}

          {/* Error Display */}
          {error && (
            <div className="p-3 bg-red-900/30 border-l-4 border-red-600 mx-3 my-2">
              <p className="text-xs text-red-200">⚠️ {error}</p>
            </div>
          )}

          {/* Analysis Results */}
          {analysisResult && (
            <div className="flex-1 overflow-y-auto p-3 space-y-2">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-semibold flex items-center">
                  <CheckCircle className="w-3 h-3 mr-1 text-green-400" />
                  Analysis Complete (Backend API)
                </h3>
                <button
                  onClick={handleReset}
                  className="text-[9px] text-gray-400 hover:text-white"
                >
                  Test Another
                </button>
              </div>

              {/* Camera Image Thumbnail */}
              {imageUrl && (
                <div className="border border-cyan-600 rounded overflow-hidden">
                  <img
                    src={imageUrl}
                    alt="Camera feed"
                    className="w-full h-32 object-cover"
                    onError={(e) => {
                      e.target.style.display = 'none';
                    }}
                  />
                  <div className="p-1.5 bg-cyan-900/30">
                    <p className="text-[9px] text-cyan-300">Live COMPASS Camera Feed</p>
                  </div>
                </div>
              )}

              {/* Real Camera Badge */}
              <div className="p-2 bg-cyan-900/30 border border-cyan-600 rounded">
                <p className="text-xs font-bold text-cyan-200">🎥 REAL COMPASS CAMERA</p>
                <p className="text-[9px] text-cyan-300 mt-0.5">
                  Camera ID: {analysisResult.camera_id} • View: #{selectedView?.Id}
                </p>
                <p className="text-[9px] text-cyan-300">
                  Location: {selectedCamera?.Location}
                </p>
                <p className="text-[9px] text-cyan-300">
                  Analyzed via: Backend FastAPI
                </p>
              </div>

              {/* Risk Score */}
              <div className={`p-2 rounded border-2 ${
                analysisResult.riskScore >= 7 ? 'bg-red-900/30 border-red-600' :
                analysisResult.riskScore >= 5 ? 'bg-yellow-900/30 border-yellow-600' :
                'bg-green-900/30 border-green-600'
              }`}>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold">RISK SCORE</span>
                  <span className="text-2xl font-bold">{analysisResult.riskScore}/10</span>
                </div>
                <div className="text-[10px] font-semibold mt-1">
                  {analysisResult.riskScore >= 7 ? 'HIGH RISK' :
                   analysisResult.riskScore >= 5 ? 'MEDIUM RISK' : 'LOW RISK'}
                </div>
              </div>

              {/* Detection Stats */}
              <div className="grid grid-cols-2 gap-1.5">
                <div className="bg-blue-900/30 border border-blue-600 p-1.5 rounded">
                  <div className="text-[9px] text-blue-300 font-semibold">Workers</div>
                  <div className="text-lg font-bold text-blue-100">{analysisResult.workers || 0}</div>
                </div>
                <div className="bg-purple-900/30 border border-purple-600 p-1.5 rounded">
                  <div className="text-[9px] text-purple-300 font-semibold">Vehicles</div>
                  <div className="text-lg font-bold text-purple-100">{analysisResult.vehicles || 0}</div>
                </div>
                <div className="bg-orange-900/30 border border-orange-600 p-1.5 rounded">
                  <div className="text-[9px] text-orange-300 font-semibold">Equipment</div>
                  <div className="text-lg font-bold text-orange-100">{analysisResult.equipment || 0}</div>
                </div>
                <div className={`p-1.5 rounded border ${analysisResult.barriers ? 'bg-green-900/30 border-green-600' : 'bg-red-900/30 border-red-600'}`}>
                  <div className={`text-[9px] font-semibold ${analysisResult.barriers ? 'text-green-300' : 'text-red-300'}`}>
                    Barriers
                  </div>
                  <div className={`text-lg font-bold ${analysisResult.barriers ? 'text-green-100' : 'text-red-100'}`}>
                    {analysisResult.barriers ? 'YES' : 'NO'}
                  </div>
                </div>
              </div>

              {/* Hazards */}
              {analysisResult.hazards && analysisResult.hazards.length > 0 && (
                <div className="bg-red-900/30 border border-red-600 p-2 rounded">
                  <h5 className="text-xs font-bold text-red-200 mb-1 flex items-center">
                    <AlertTriangle className="w-3 h-3 mr-1" />
                    Hazards Detected
                  </h5>
                  <ul className="space-y-0.5">
                    {analysisResult.hazards.map((hazard, idx) => (
                      <li key={idx} className="text-[9px] text-red-300 leading-tight">• {hazard}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* V2X Broadcast */}
              {analysisResult.vrsuBroadcast && (
                <div className="p-2 rounded border bg-cyan-900/30 border-cyan-600">
                  <div className="flex items-center text-xs font-bold mb-1">
                    <Radio className="w-3 h-3 mr-1" />
                    V2X RSU Broadcast
                  </div>
                  <div className="text-[9px] text-cyan-300">
                    ✓ {analysisResult.vrsuBroadcast.messageType} message sent
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Footer */}
          <div className="p-1.5 bg-gray-900 border-t border-gray-700 text-[9px] text-gray-500 text-center">
            ML Model Validation • Backend API Integration • FastAPI Analysis
          </div>
        </div>
      )}
    </div>
  );
}

export default MLValidationPanel;

import React, { useState, useEffect } from 'react';
import { Beaker, Camera, Download, Loader, CheckCircle, AlertTriangle, Radio, ChevronDown, ChevronUp } from 'lucide-react';
import { searchWorkZoneImages, downloadImageAsFile } from '../services/imageSearchAPI';
import { getCurrentConditions, formatConditions, createSyntheticMetadata, formatCameraInfo, getRandomScenario } from '../utils/imageMetadata';
import { analyzeWorkZoneImage, formatWorkZoneForDashboard } from '../services/geminiVision';
import { useV2X } from '../contexts/V2XContext';

/**
 * Synthetic Testing Panel - Collapsible Persistent Dropdown
 *
 * FEATURES:
 * - Persistent collapsible dropdown (always visible in right panel)
 * - Test AI + V2X pipeline with synthetic work zone images
 * - Images fetched from web APIs matching current corridor conditions
 * - Expansion state persists across sessions
 */
function SyntheticTestingPanel({ cameras }) {
  const [isExpanded, setIsExpanded] = useState(() => {
    const saved = localStorage.getItem('syntheticTestingExpanded');
    return saved === 'true';
  });
  const [conditions, setConditions] = useState(null);
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [selectedImage, setSelectedImage] = useState(null);
  const [selectedCamera, setSelectedCamera] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);

  // V2X context for broadcast registration
  const { registerBroadcast } = useV2X();

  // Persist expansion state
  useEffect(() => {
    localStorage.setItem('syntheticTestingExpanded', isExpanded.toString());
  }, [isExpanded]);

  // Load current conditions on mount
  useEffect(() => {
    const currentConditions = getCurrentConditions();
    setConditions(currentConditions);

    // Auto-select first camera if available
    if (cameras && cameras.length > 0) {
      setSelectedCamera(cameras[0]);
    }
  }, [cameras]);

  // Generate test work zone images
  const handleGenerateImages = async () => {
    console.log('[SyntheticTestingPanel] Generate button clicked!');
    console.log('[SyntheticTestingPanel] Current conditions:', conditions);
    console.log('[SyntheticTestingPanel] Selected camera:', selectedCamera);

    if (!conditions || !selectedCamera) {
      console.error('[SyntheticTestingPanel] Missing conditions or camera');
      setError('Please select a camera first');
      return;
    }

    setLoading(true);
    setError(null);
    setImages([]);
    setSelectedImage(null);
    setAnalysisResult(null);

    try {
      // Determine camera direction from views
      // Most QEW cameras have "E" (East) or "W" (West) in their view descriptions
      let direction = 'eastbound'; // default
      if (selectedCamera.Views && selectedCamera.Views.length > 0) {
        const firstView = selectedCamera.Views[0].Description || '';
        if (firstView.includes('W') || firstView.toLowerCase().includes('west')) {
          direction = 'westbound';
        } else if (firstView.includes('E') || firstView.toLowerCase().includes('east')) {
          direction = 'eastbound';
        }
      }

      console.log('[SyntheticTestingPanel] Calling searchWorkZoneImages with:', {
        direction,
        weather: conditions.weather,
        timeOfDay: conditions.timeOfDay,
        season: conditions.season,
        limit: 8
      });

      const fetchedImages = await searchWorkZoneImages({
        direction: direction,
        weather: conditions.weather,
        timeOfDay: conditions.timeOfDay,
        season: conditions.season,
        limit: 8
      });

      console.log('[SyntheticTestingPanel] Received images:', fetchedImages);
      console.log('[SyntheticTestingPanel] Number of images:', fetchedImages.length);

      if (fetchedImages.length === 0) {
        console.error('[SyntheticTestingPanel] No images returned!');
        setError(`No geotagged construction images found in QEW corridor for ${direction}. Try again.`);
      } else {
        console.log('[SyntheticTestingPanel] Setting images state with', fetchedImages.length, 'images');
      }

      setImages(fetchedImages);
    } catch (err) {
      console.error('[SyntheticTestingPanel] Error fetching images:', err);
      setError(err.message || 'Failed to fetch images');
    } finally {
      setLoading(false);
      console.log('[SyntheticTestingPanel] Done - loading=false');
    }
  };

  // Inject and analyze selected image
  const handleInjectAndAnalyze = async () => {
    if (!selectedImage || !selectedCamera) {
      setError('Please select an image and camera');
      return;
    }

    setAnalyzing(true);
    setError(null);
    setAnalysisResult(null);

    try {
      // Download image as File object
      const imageFile = await downloadImageAsFile(selectedImage.url, `synthetic_${selectedImage.id}.jpg`);

      // Create synthetic metadata
      const syntheticMetadata = createSyntheticMetadata({
        image: selectedImage,
        camera: selectedCamera,
        conditions
      });

      // Analyze with Gemini AI (with synthetic flag)
      const analysis = await analyzeWorkZoneImage(imageFile, syntheticMetadata);

      if (analysis.error) {
        setError(analysis.message);
        setAnalyzing(false);
        return;
      }

      // Format for dashboard display and broadcast to vRSU
      const workZone = await formatWorkZoneForDashboard(
        analysis,
        `SYNTHETIC_${selectedCamera.Id}`,
        { lat: selectedCamera.Latitude, lon: selectedCamera.Longitude },
        registerBroadcast
      );

      if (!workZone) {
        setError('No work zone detected in this image. Try another image.');
        setAnalyzing(false);
        return;
      }

      // Add synthetic metadata to result
      workZone.synthetic = true;
      workZone.syntheticMetadata = syntheticMetadata;

      setAnalysisResult(workZone);
      setAnalyzing(false);

    } catch (err) {
      console.error('Error analyzing synthetic image:', err);
      setError(err.message || 'Failed to analyze image');
      setAnalyzing(false);
    }
  };

  // Reset to start over
  const handleReset = () => {
    setImages([]);
    setSelectedImage(null);
    setAnalysisResult(null);
    setError(null);
  };

  return (
    <div className="bg-gray-800 text-white border-b border-gray-700">
      {/* Collapsible Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-2 bg-gradient-to-r from-purple-600 to-pink-700 flex items-center justify-between hover:from-purple-700 hover:to-pink-800 transition"
      >
        <div className="flex items-center space-x-1.5">
          <Beaker className="w-4 h-4" />
          <div className="text-left">
            <h2 className="text-sm font-bold">Synthetic Testing Panel</h2>
            <p className="text-[9px] text-purple-100">
              {analysisResult ? '🟢 Test Complete' : loading || analyzing ? '🟡 Processing' : '⚪ Ready'} • {images.length} images • {selectedCamera ? selectedCamera.Location : 'No camera'}
            </p>
          </div>
        </div>
        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {/* Collapsible Content */}
      {isExpanded && (
        <div className="flex flex-col max-h-[600px]">{/* end of header section */}

      {/* Current Conditions */}
      {conditions && (
        <div className="p-3 bg-gray-900 border-b border-gray-700">
          <h3 className="text-xs font-semibold mb-2">Current Corridor Conditions</h3>
          <p className="text-[10px] text-gray-300">{formatConditions(conditions)}</p>
          <p className="text-[9px] text-gray-500 mt-1">Active cameras: {cameras.length}</p>
          {selectedCamera && (
            <>
              <p className="text-[9px] text-blue-400 mt-1">
                📍 Search area: Entire QEW Corridor (Burlington to Toronto, 40km)
              </p>
              <p className="text-[9px] text-purple-400">
                🧭 Direction: {selectedCamera.Views?.[0]?.Description?.includes('W') || selectedCamera.Views?.[0]?.Description?.toLowerCase().includes('west') ? 'Westbound (to Hamilton)' : 'Eastbound (to Toronto)'}
              </p>
              <p className="text-[9px] text-green-400">
                ⏰ Time match: ±2 hours from {conditions.timeString}
              </p>
            </>
          )}
        </div>
      )}

      {/* Camera Selection */}
      {!analysisResult && (
        <div className="p-3 border-b border-gray-700">
          <h3 className="text-xs font-semibold mb-2 flex items-center">
            <Camera className="w-3 h-3 mr-1" />
            Select Target Camera
          </h3>
          <select
            value={selectedCamera ? selectedCamera.Id : ''}
            onChange={(e) => {
              const camera = cameras.find(c => c.Id === parseInt(e.target.value));
              setSelectedCamera(camera);
            }}
            className="w-full px-2 py-1 bg-gray-900 border border-gray-600 rounded text-[10px]"
          >
            {cameras.map(camera => (
              <option key={camera.Id} value={camera.Id}>
                Camera {camera.Id}: {camera.Location}
              </option>
            ))}
          </select>
          {selectedCamera && (
            <p className="text-[9px] text-gray-400 mt-1">
              Lat: {selectedCamera.Latitude.toFixed(4)}, Lon: {selectedCamera.Longitude.toFixed(4)}
            </p>
          )}
        </div>
      )}

      {/* Generate Button */}
      {!images.length && !analysisResult && (
        <div className="p-3 border-b border-gray-700">
          <button
            onClick={handleGenerateImages}
            disabled={loading}
            className="w-full py-2 rounded font-bold text-[10px] bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-1.5"
          >
            {loading ? (
              <>
                <Loader className="w-3 h-3 animate-spin" />
                <span>Fetching Images...</span>
              </>
            ) : (
              <>
                <Beaker className="w-3 h-3" />
                <span>GENERATE TEST WORK ZONE</span>
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

      {/* Image Grid */}
      {images.length > 0 && !analysisResult && (
        <div className="flex-1 overflow-y-auto p-3">
          <div className="mb-2 flex items-center justify-between">
            <h3 className="text-xs font-semibold">Select Test Image ({images.length} found)</h3>
            <button
              onClick={handleReset}
              className="text-[9px] text-gray-400 hover:text-white"
            >
              Clear
            </button>
          </div>

          <div className="grid grid-cols-2 gap-2 mb-3">
            {images.map((image) => (
              <div
                key={image.id}
                onClick={() => setSelectedImage(image)}
                className={`cursor-pointer rounded border-2 overflow-hidden transition ${
                  selectedImage?.id === image.id
                    ? 'border-purple-500 ring-2 ring-purple-400'
                    : 'border-gray-600 hover:border-gray-500'
                }`}
              >
                <img
                  src={image.thumbnail}
                  alt={image.description}
                  className="w-full h-24 object-cover"
                />
                <div className="p-1.5 bg-gray-900">
                  <p className="text-[9px] text-gray-300 truncate" title={image.description}>
                    {image.description}
                  </p>
                  <p className="text-[8px] text-gray-500">by {image.photographer}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Inject Button */}
          {selectedImage && (
            <button
              onClick={handleInjectAndAnalyze}
              disabled={analyzing}
              className="w-full py-2 rounded font-bold text-[10px] bg-pink-600 hover:bg-pink-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-1.5"
            >
              {analyzing ? (
                <>
                  <Loader className="w-3 h-3 animate-spin" />
                  <span>Analyzing with Gemini AI...</span>
                </>
              ) : (
                <>
                  <Download className="w-3 h-3" />
                  <span>INJECT & ANALYZE</span>
                </>
              )}
            </button>
          )}
        </div>
      )}

      {/* Analysis Results */}
      {analysisResult && (
        <div className="flex-1 overflow-y-auto p-3 space-y-2">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-xs font-semibold flex items-center">
              <CheckCircle className="w-3 h-3 mr-1 text-green-400" />
              Analysis Complete
            </h3>
            <button
              onClick={handleReset}
              className="text-[9px] text-gray-400 hover:text-white"
            >
              Test Another
            </button>
          </div>

          {/* Synthetic Badge */}
          <div className="p-2 bg-purple-900/30 border border-purple-600 rounded">
            <p className="text-xs font-bold text-purple-200">🧪 SYNTHETIC TEST</p>
            <p className="text-[9px] text-purple-300 mt-0.5">
              Image Source: {analysisResult.syntheticMetadata.photoSource}
            </p>
            <p className="text-[9px] text-purple-300">
              Injected: {new Date(analysisResult.syntheticMetadata.injectedAt).toLocaleTimeString()}
            </p>
          </div>

          {/* Camera Info */}
          <div className="p-2 bg-gray-900 border border-gray-600 rounded">
            <p className="text-xs font-semibold">{formatCameraInfo(selectedCamera)}</p>
            <p className="text-[9px] text-gray-400 mt-0.5">
              Search: {analysisResult.syntheticMetadata.searchTerms}
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

          {/* vRSU Broadcast Status */}
          {analysisResult.vrsuBroadcast && (
            <div className={`p-2 rounded border ${
              analysisResult.vrsuBroadcast.success
                ? 'bg-cyan-900/30 border-cyan-600'
                : 'bg-yellow-900/30 border-yellow-600'
            }`}>
              <div className="flex items-center text-xs font-bold mb-1">
                <Radio className="w-3 h-3 mr-1" />
                V2X RSU Broadcast
              </div>
              {analysisResult.vrsuBroadcast.success ? (
                <div className="text-[9px] text-cyan-300">
                  ✓ {analysisResult.vrsuBroadcast.messageType} message sent
                  <br />
                  Message ID: {analysisResult.vrsuBroadcast.messageId}
                </div>
              ) : (
                <div className="text-[9px] text-yellow-300">
                  ⚠️ {analysisResult.vrsuBroadcast.error}
                </div>
              )}
            </div>
          )}

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

          {/* Watch Vehicles Note */}
          {analysisResult.vrsuBroadcast && analysisResult.vrsuBroadcast.success && (
            <div className="p-2 bg-green-900/30 border border-green-600 rounded">
              <p className="text-xs font-bold text-green-200">✓ Synthetic Test Complete!</p>
              <p className="text-[9px] text-green-300 mt-1">
                Watch the map - vehicles within 1km will receive V2X alerts and change color.
                Click a vehicle to see the SMS-style alert in its popup.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="p-1.5 bg-gray-900 border-t border-gray-700 text-[9px] text-gray-500 text-center">
        Synthetic Testing • Geotagged QEW Corridor Images • Direction + Time Matched (±2hrs) • No Real Data Modified
      </div>
        </div>
      )}
    </div>
  );
}

export default SyntheticTestingPanel;

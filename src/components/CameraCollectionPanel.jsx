import React, { useState, useEffect, useRef } from 'react';
import { Camera, Play, Square, Download, Clock, Settings, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

/**
 * Camera Collection Panel - Integrates camera image collection into Digital Twin Dashboard
 *
 * Replaces standalone PyQt6 GUI (qew_camera_gui.py) with React component
 * Features:
 * - Start/Stop scheduled collection
 * - Manual "Collect Now" button
 * - Collection settings (interval, images per camera)
 * - Real-time status log
 * - Progress tracking
 * - localStorage for settings persistence
 */
function CameraCollectionPanel({ cameras = [], onClose }) {
  // Settings state (persisted to localStorage)
  const [settings, setSettings] = useState(() => {
    const saved = localStorage.getItem('cameraCollectionSettings');
    return saved ? JSON.parse(saved) : {
      intervalHours: 1,
      intervalMinutes: 0,
      imagesPerCamera: 1,
      autoStart: false
    };
  });

  // Collection state
  const [isRunning, setIsRunning] = useState(false);
  const [isCollecting, setIsCollecting] = useState(false);
  const [statusLog, setStatusLog] = useState([]);
  const [nextCollectionTime, setNextCollectionTime] = useState(null);
  const [totalImages, setTotalImages] = useState(0);
  const [currentCamera, setCurrentCamera] = useState(null);
  const [currentProgress, setCurrentProgress] = useState(0);

  // Refs for timers
  const collectionTimerRef = useRef(null);
  const nextCollectionTimerRef = useRef(null);

  // Save settings to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('cameraCollectionSettings', JSON.stringify(settings));
  }, [settings]);

  // Calculate next collection time
  useEffect(() => {
    if (isRunning) {
      const intervalMs = (settings.intervalHours * 3600 + settings.intervalMinutes * 60) * 1000;
      const next = new Date(Date.now() + intervalMs);
      setNextCollectionTime(next);

      // Update next collection time every second for countdown
      nextCollectionTimerRef.current = setInterval(() => {
        setNextCollectionTime(new Date(Date.now() + intervalMs));
      }, 1000);

      return () => {
        if (nextCollectionTimerRef.current) {
          clearInterval(nextCollectionTimerRef.current);
        }
      };
    } else {
      setNextCollectionTime(null);
    }
  }, [isRunning, settings.intervalHours, settings.intervalMinutes]);

  // Log message to status log
  const logStatus = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setStatusLog(prev => [
      { timestamp, message, type },
      ...prev.slice(0, 49) // Keep last 50 messages
    ]);
  };

  // Start scheduled collection
  const startCollection = () => {
    if (cameras.length === 0) {
      logStatus('Error: No camera data loaded', 'error');
      return;
    }

    const intervalMs = (settings.intervalHours * 3600 + settings.intervalMinutes * 60) * 1000;

    if (intervalMs === 0) {
      logStatus('Error: Please set a collection interval greater than 0', 'error');
      return;
    }

    setIsRunning(true);
    logStatus(`Automatic collection started (every ${settings.intervalHours}h ${settings.intervalMinutes}m)`, 'success');

    // Run first collection immediately
    runCollection();

    // Set up interval for future collections
    collectionTimerRef.current = setInterval(() => {
      runCollection();
    }, intervalMs);
  };

  // Stop scheduled collection
  const stopCollection = () => {
    setIsRunning(false);
    if (collectionTimerRef.current) {
      clearInterval(collectionTimerRef.current);
      collectionTimerRef.current = null;
    }
    logStatus('Automatic collection stopped', 'info');
  };

  // Run camera image collection
  const runCollection = async () => {
    if (isCollecting) {
      logStatus('Previous collection still in progress, skipping...', 'warning');
      return;
    }

    setIsCollecting(true);
    setCurrentProgress(0);
    setTotalImages(0);

    logStatus(`Starting camera image collection (${cameras.length} cameras, ${settings.imagesPerCamera} images each)`, 'info');

    try {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
      const collectionId = `qew_collection_${timestamp}`;

      logStatus(`Collection ID: ${collectionId}`, 'info');

      let imagesCollected = 0;

      // Simulate collection process (in production, this would call backend API)
      for (let cameraIdx = 0; cameraIdx < cameras.length; cameraIdx++) {
        const camera = cameras[cameraIdx];
        setCurrentCamera(camera.Location || `Camera ${camera.Id}`);
        setCurrentProgress(Math.round(((cameraIdx + 1) / cameras.length) * 100));

        logStatus(`[${cameraIdx + 1}/${cameras.length}] ${camera.Location}`, 'info');

        // Collect images from each view
        const views = camera.Views || [];
        for (let viewIdx = 0; viewIdx < views.length; viewIdx++) {
          const view = views[viewIdx];

          for (let round = 0; round < settings.imagesPerCamera; round++) {
            // Simulate image download (in production, call backend API)
            await simulateImageDownload(camera.Id, view.Id, round + 1);
            imagesCollected++;
            setTotalImages(imagesCollected);
          }
        }
      }

      logStatus(`Collection complete! ${imagesCollected} images downloaded to collection: ${collectionId}`, 'success');
      logStatus('=' + '='.repeat(70), 'info');

    } catch (error) {
      logStatus(`Error during collection: ${error.message}`, 'error');
    } finally {
      setIsCollecting(false);
      setCurrentCamera(null);
      setCurrentProgress(0);
    }
  };

  // Simulate image download (replace with real API call in production)
  const simulateImageDownload = (cameraId, viewId, round) => {
    return new Promise(resolve => {
      setTimeout(resolve, 200); // Simulate 200ms download time
    });
  };

  // Manual collection (one-time)
  const handleManualCollection = () => {
    if (cameras.length === 0) {
      logStatus('Error: No camera data loaded', 'error');
      return;
    }

    if (isCollecting) {
      logStatus('Collection already in progress...', 'warning');
      return;
    }

    runCollection();
  };

  // Update settings
  const updateSetting = (key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
  };

  // Format next collection time
  const formatNextCollection = () => {
    if (!nextCollectionTime) return 'Not scheduled';

    const now = Date.now();
    const diff = nextCollectionTime.getTime() - now;

    if (diff < 0) return 'Now';

    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);

    return `${hours}h ${minutes}m ${seconds}s`;
  };

  return (
    <div className="h-full bg-gray-800 text-white flex flex-col">
      {/* Header */}
      <div className="p-4 bg-gradient-to-r from-indigo-600 to-blue-700 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <Camera className="w-6 h-6" />
          <h2 className="text-xl font-bold">Camera Collection System</h2>
        </div>
        <button
          onClick={onClose}
          className="text-white hover:text-gray-300"
        >
          ✕
        </button>
      </div>

      {/* Settings Section */}
      <div className="p-4 border-b border-gray-700">
        <h3 className="text-sm font-semibold mb-3 flex items-center">
          <Settings className="w-4 h-4 mr-2" />
          Collection Settings
        </h3>

        <div className="space-y-3">
          {/* Interval Settings */}
          <div className="flex items-center space-x-3">
            <label className="text-xs text-gray-400 w-20">Interval:</label>
            <div className="flex items-center space-x-2">
              <input
                type="number"
                min="0"
                max="23"
                value={settings.intervalHours}
                onChange={(e) => updateSetting('intervalHours', parseInt(e.target.value) || 0)}
                disabled={isRunning}
                className="w-16 px-2 py-1 bg-gray-900 border border-gray-600 rounded text-sm"
              />
              <span className="text-xs">hours</span>

              <input
                type="number"
                min="0"
                max="59"
                value={settings.intervalMinutes}
                onChange={(e) => updateSetting('intervalMinutes', parseInt(e.target.value) || 0)}
                disabled={isRunning}
                className="w-16 px-2 py-1 bg-gray-900 border border-gray-600 rounded text-sm"
              />
              <span className="text-xs">min</span>
            </div>
          </div>

          {/* Images Per Camera */}
          <div className="flex items-center space-x-3">
            <label className="text-xs text-gray-400 w-20">Images:</label>
            <input
              type="number"
              min="1"
              max="10"
              value={settings.imagesPerCamera}
              onChange={(e) => updateSetting('imagesPerCamera', parseInt(e.target.value) || 1)}
              disabled={isRunning}
              className="w-16 px-2 py-1 bg-gray-900 border border-gray-600 rounded text-sm"
            />
            <span className="text-xs">per camera</span>
          </div>

          {/* Camera Count */}
          <div className="flex items-center space-x-3">
            <label className="text-xs text-gray-400 w-20">Cameras:</label>
            <span className="text-sm font-semibold text-blue-400">{cameras.length}</span>
          </div>
        </div>
      </div>

      {/* Control Buttons */}
      <div className="p-4 border-b border-gray-700 space-y-2">
        {/* Start/Stop Button */}
        <button
          onClick={isRunning ? stopCollection : startCollection}
          disabled={isCollecting}
          className={`w-full py-3 rounded-lg font-bold text-sm flex items-center justify-center space-x-2 transition ${
            isRunning
              ? 'bg-red-600 hover:bg-red-700'
              : 'bg-green-600 hover:bg-green-700'
          } ${isCollecting ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {isRunning ? (
            <>
              <Square className="w-5 h-5" />
              <span>STOP COLLECTION</span>
            </>
          ) : (
            <>
              <Play className="w-5 h-5" />
              <span>START COLLECTION</span>
            </>
          )}
        </button>

        {/* Manual Collection Button */}
        <button
          onClick={handleManualCollection}
          disabled={isCollecting}
          className={`w-full py-3 rounded-lg font-bold text-sm flex items-center justify-center space-x-2 transition bg-blue-600 hover:bg-blue-700 ${
            isCollecting ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          <Download className="w-5 h-5" />
          <span>COLLECT NOW</span>
        </button>
      </div>

      {/* Status Info */}
      <div className="p-4 border-b border-gray-700 bg-gray-900">
        <div className="space-y-2 text-xs">
          {/* Next Collection Time */}
          {isRunning && (
            <div className="flex items-center justify-between">
              <span className="text-gray-400 flex items-center">
                <Clock className="w-4 h-4 mr-2" />
                Next Collection:
              </span>
              <span className="font-semibold text-blue-400">{formatNextCollection()}</span>
            </div>
          )}

          {/* Current Progress */}
          {isCollecting && (
            <>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Current Camera:</span>
                <span className="font-semibold text-yellow-400">{currentCamera}</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-gray-400">Progress:</span>
                <span className="font-semibold text-green-400">{currentProgress}%</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-gray-400">Images Collected:</span>
                <span className="font-semibold text-green-400">{totalImages}</span>
              </div>

              {/* Progress Bar */}
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${currentProgress}%` }}
                />
              </div>
            </>
          )}
        </div>
      </div>

      {/* Status Log */}
      <div className="flex-1 overflow-hidden flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <h3 className="text-sm font-semibold">Status Log</h3>
        </div>

        <div className="flex-1 overflow-y-auto p-4 bg-gray-900 font-mono text-xs space-y-1">
          {statusLog.length === 0 ? (
            <div className="text-gray-500 text-center py-8">
              No activity yet. Click "START COLLECTION" or "COLLECT NOW" to begin.
            </div>
          ) : (
            statusLog.map((log, idx) => (
              <div
                key={idx}
                className={`flex items-start space-x-2 ${
                  log.type === 'error' ? 'text-red-400' :
                  log.type === 'success' ? 'text-green-400' :
                  log.type === 'warning' ? 'text-yellow-400' :
                  'text-gray-300'
                }`}
              >
                <span className="text-gray-500 flex-shrink-0">[{log.timestamp}]</span>
                <span className="flex-1">{log.message}</span>
                {log.type === 'error' && <XCircle className="w-4 h-4 flex-shrink-0" />}
                {log.type === 'success' && <CheckCircle className="w-4 h-4 flex-shrink-0" />}
                {log.type === 'warning' && <AlertCircle className="w-4 h-4 flex-shrink-0" />}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Footer Info */}
      <div className="p-3 bg-gray-900 border-t border-gray-700 text-xs text-gray-500 text-center">
        Integrated Camera Collection System • Replaces standalone PyQt6 GUI
      </div>
    </div>
  );
}

export default CameraCollectionPanel;

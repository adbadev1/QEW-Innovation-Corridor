import React, { useEffect } from 'react';
import { Camera, Play, Square, Download, Clock, Settings, CheckCircle, XCircle, AlertCircle, Trash2, Info } from 'lucide-react';
import { useCollection } from '../contexts/CollectionContext';

/**
 * Camera Collection Panel - Integrates camera image collection into Digital Twin Dashboard
 *
 * NOW WITH PERSISTENT STATE:
 * - Logs persist across panel show/hide (session storage)
 * - Collection continues running even when panel is hidden
 * - Settings persist across browser sessions (local storage)
 * - Session tracking from START to END
 * - Full history grep/tail functionality
 */
function CameraCollectionPanel({ onClose }) {
  const {
    // Session info
    sessionId,
    sessionStartTime,
    getSessionUptime,

    // Settings
    settings,
    updateSetting,

    // Collection state
    isRunning,
    isCollecting,
    totalImages,
    currentCamera,
    currentProgress,
    nextCollectionTime,

    // Stats
    stats,

    // Logs
    statusLog,
    logStatus,
    clearLogs,

    // Actions
    startCollection,
    stopCollection,
    runCollection,

    // Data
    cameras
  } = useCollection();

  // Log when panel is opened
  useEffect(() => {
    logStatus(`─── Camera Collection Panel Opened ───`, 'info');
  }, []);

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
          <div>
            <h2 className="text-xl font-bold">Camera Collection System</h2>
            <p className="text-xs text-blue-100">Session persistent • Logs retained</p>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-white hover:text-gray-300 px-2 py-1 rounded hover:bg-white/10"
        >
          ✕
        </button>
      </div>

      {/* Session Info Bar */}
      <div className="p-3 bg-gray-900 border-b border-gray-700 text-xs">
        <div className="grid grid-cols-2 gap-2">
          <div className="flex items-center space-x-2">
            <Info className="w-4 h-4 text-blue-400" />
            <span className="text-gray-400">Session:</span>
            <span className="font-mono text-blue-400">{sessionId.slice(-8)}</span>
          </div>
          <div className="flex items-center space-x-2">
            <Clock className="w-4 h-4 text-green-400" />
            <span className="text-gray-400">Uptime:</span>
            <span className="font-mono text-green-400">{getSessionUptime()}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-gray-400">Started:</span>
            <span className="font-mono text-gray-300">{sessionStartTime.toLocaleTimeString()}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-gray-400">Collections:</span>
            <span className="font-mono text-yellow-400">{stats.collectionsThisSession}</span>
          </div>
        </div>
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
                className="w-16 px-2 py-1 bg-gray-900 border border-gray-600 rounded text-sm disabled:opacity-50"
              />
              <span className="text-xs">hours</span>

              <input
                type="number"
                min="0"
                max="59"
                value={settings.intervalMinutes}
                onChange={(e) => updateSetting('intervalMinutes', parseInt(e.target.value) || 0)}
                disabled={isRunning}
                className="w-16 px-2 py-1 bg-gray-900 border border-gray-600 rounded text-sm disabled:opacity-50"
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
              className="w-16 px-2 py-1 bg-gray-900 border border-gray-600 rounded text-sm disabled:opacity-50"
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
          onClick={runCollection}
          disabled={isCollecting}
          className={`w-full py-3 rounded-lg font-bold text-sm flex items-center justify-center space-x-2 transition bg-blue-600 hover:bg-blue-700 ${
            isCollecting ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          <Download className="w-5 h-5" />
          <span>COLLECT NOW</span>
        </button>

        {/* Clear Logs Button */}
        <button
          onClick={clearLogs}
          disabled={isCollecting}
          className="w-full py-2 rounded-lg font-semibold text-xs flex items-center justify-center space-x-2 transition bg-gray-700 hover:bg-gray-600"
        >
          <Trash2 className="w-4 h-4" />
          <span>CLEAR LOGS</span>
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
                <span className="font-semibold text-yellow-400 truncate max-w-[200px]" title={currentCamera}>
                  {currentCamera}
                </span>
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
              <div className="w-full bg-gray-700 rounded-full h-2 mt-2">
                <div
                  className="bg-green-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${currentProgress}%` }}
                />
              </div>
            </>
          )}

          {/* Session Stats */}
          {!isCollecting && stats.collectionsThisSession > 0 && (
            <div className="pt-2 border-t border-gray-700 space-y-1">
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Total Collections:</span>
                <span className="font-semibold text-purple-400">{stats.collectionsThisSession}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-400">Total Images:</span>
                <span className="font-semibold text-purple-400">{stats.totalImagesCollected}</span>
              </div>
              {stats.lastCollectionTime && (
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Last Collection:</span>
                  <span className="font-semibold text-gray-300">
                    {new Date(stats.lastCollectionTime).toLocaleTimeString()}
                  </span>
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Status Log */}
      <div className="flex-1 overflow-hidden flex flex-col">
        <div className="p-4 border-b border-gray-700 flex items-center justify-between">
          <h3 className="text-sm font-semibold">Session Log ({statusLog.length} entries)</h3>
          <span className="text-xs text-gray-500">Persistent since {sessionStartTime.toLocaleTimeString()}</span>
        </div>

        <div className="flex-1 overflow-y-auto p-4 bg-gray-900 font-mono text-xs space-y-1">
          {statusLog.length === 0 ? (
            <div className="text-gray-500 text-center py-8">
              <Info className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No activity yet.</p>
              <p className="text-xs mt-2">Click "START COLLECTION" or "COLLECT NOW" to begin.</p>
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
                <span className="text-gray-500 flex-shrink-0 w-20">[{log.timestamp}]</span>
                <span className="flex-1 break-words">{log.message}</span>
                {log.type === 'error' && <XCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />}
                {log.type === 'success' && <CheckCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />}
                {log.type === 'warning' && <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Footer Info */}
      <div className="p-3 bg-gray-900 border-t border-gray-700 text-xs text-gray-500 text-center">
        Session Persistent Collection System • Logs Retained • Collection Runs in Background
      </div>
    </div>
  );
}

export default CameraCollectionPanel;

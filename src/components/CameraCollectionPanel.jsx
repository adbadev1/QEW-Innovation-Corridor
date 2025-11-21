import React, { useEffect, useState } from 'react';
import { Camera, Play, Square, Download, Clock, Settings, CheckCircle, XCircle, AlertCircle, Trash2, Info, ChevronDown, ChevronUp } from 'lucide-react';
import { useCollection } from '../contexts/CollectionContext';

/**
 * Camera Collection Panel - Collapsible Persistent Dropdown
 *
 * FEATURES:
 * - Persistent collapsible dropdown (always visible in right panel)
 * - Logs persist across panel collapse/expand (session storage)
 * - Collection continues running even when panel is collapsed
 * - Settings persist across browser sessions (local storage)
 * - Session tracking from START to END
 * - Full history grep/tail functionality
 * - Verbose telemetry logging for all system events
 */
function CameraCollectionPanel() {
  const [isExpanded, setIsExpanded] = useState(() => {
    const saved = localStorage.getItem('cameraCollectionExpanded');
    return saved === 'true';
  });
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

  // Persist expansion state
  useEffect(() => {
    localStorage.setItem('cameraCollectionExpanded', isExpanded.toString());
  }, [isExpanded]);

  // Log when panel is first mounted
  useEffect(() => {
    logStatus(`─── Camera Collection Panel Mounted ───`, 'info');
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
    <div className="bg-gray-800 text-white border-b border-gray-700">
      {/* Collapsible Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full p-2 bg-gradient-to-r from-indigo-600 to-blue-700 flex items-center justify-between hover:from-indigo-700 hover:to-blue-800 transition"
      >
        <div className="flex items-center space-x-1.5">
          <Camera className="w-4 h-4" />
          <div className="text-left">
            <h2 className="text-sm font-bold">Camera Collection System</h2>
            <p className="text-[9px] text-blue-100">
              {isRunning ? '🟢 Running' : '⚪ Stopped'} • {stats.collectionsThisSession} collections • {statusLog.length} logs
            </p>
          </div>
        </div>
        {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {/* Collapsible Content */}
      {isExpanded && (
        <div className="flex flex-col max-h-[600px]">

      {/* Session Info Bar */}
      <div className="p-2 bg-gray-900 border-b border-gray-700 text-[10px]">
        <div className="grid grid-cols-2 gap-1.5">
          <div className="flex items-center space-x-1">
            <Info className="w-3 h-3 text-blue-400" />
            <span className="text-gray-400">Session:</span>
            <span className="font-mono text-blue-400">{sessionId.slice(-8)}</span>
          </div>
          <div className="flex items-center space-x-1">
            <Clock className="w-3 h-3 text-green-400" />
            <span className="text-gray-400">Uptime:</span>
            <span className="font-mono text-green-400">{getSessionUptime()}</span>
          </div>
          <div className="flex items-center space-x-1">
            <span className="text-gray-400">Started:</span>
            <span className="font-mono text-gray-300">{sessionStartTime.toLocaleTimeString()}</span>
          </div>
          <div className="flex items-center space-x-1">
            <span className="text-gray-400">Collections:</span>
            <span className="font-mono text-yellow-400">{stats.collectionsThisSession}</span>
          </div>
        </div>
      </div>

      {/* Settings Section */}
      <div className="p-2 border-b border-gray-700">
        <h3 className="text-xs font-semibold mb-2 flex items-center">
          <Settings className="w-3 h-3 mr-1" />
          Collection Settings
        </h3>

        <div className="space-y-2">
          {/* Interval Settings */}
          <div className="flex items-center space-x-2">
            <label className="text-[10px] text-gray-400 w-16">Interval:</label>
            <div className="flex items-center space-x-1.5">
              <input
                type="number"
                min="0"
                max="23"
                value={settings.intervalHours}
                onChange={(e) => updateSetting('intervalHours', parseInt(e.target.value) || 0)}
                disabled={isRunning}
                className="w-12 px-1.5 py-0.5 bg-gray-900 border border-gray-600 rounded text-[10px] disabled:opacity-50"
              />
              <span className="text-[10px]">h</span>

              <input
                type="number"
                min="0"
                max="59"
                value={settings.intervalMinutes}
                onChange={(e) => updateSetting('intervalMinutes', parseInt(e.target.value) || 0)}
                disabled={isRunning}
                className="w-12 px-1.5 py-0.5 bg-gray-900 border border-gray-600 rounded text-[10px] disabled:opacity-50"
              />
              <span className="text-[10px]">m</span>
            </div>
          </div>

          {/* Images Per Camera */}
          <div className="flex items-center space-x-2">
            <label className="text-[10px] text-gray-400 w-16">Images:</label>
            <input
              type="number"
              min="1"
              max="10"
              value={settings.imagesPerCamera}
              onChange={(e) => updateSetting('imagesPerCamera', parseInt(e.target.value) || 1)}
              disabled={isRunning}
              className="w-12 px-1.5 py-0.5 bg-gray-900 border border-gray-600 rounded text-[10px] disabled:opacity-50"
            />
            <span className="text-[10px]">per camera</span>
          </div>

          {/* AI Model Selection */}
          <div className="flex items-center space-x-2">
            <label className="text-[10px] text-gray-400 w-16">AI Model:</label>
            <select
              value={settings.aiModel || 'gemini'}
              onChange={(e) => updateSetting('aiModel', e.target.value)}
              disabled={isRunning}
              className="flex-1 px-1.5 py-0.5 bg-gray-900 border border-gray-600 rounded text-[10px] disabled:opacity-50"
            >
              <option value="gemini">Gemini 2.0 Flash (Fast, $0.0002/img)</option>
              <option value="claude">Claude 3.5 Sonnet (Accurate, $0.003/img)</option>
            </select>
          </div>

          {/* Camera Count */}
          <div className="flex items-center space-x-2">
            <label className="text-[10px] text-gray-400 w-16">Cameras:</label>
            <span className="text-xs font-semibold text-blue-400">{cameras.length}</span>
          </div>
        </div>
      </div>

      {/* Control Buttons */}
      <div className="p-2 border-b border-gray-700 space-y-1.5">
        {/* Start/Stop Button */}
        <button
          onClick={isRunning ? stopCollection : startCollection}
          disabled={isCollecting}
          className={`w-full py-1.5 rounded font-bold text-[10px] flex items-center justify-center space-x-1.5 transition ${
            isRunning
              ? 'bg-red-600 hover:bg-red-700'
              : 'bg-green-600 hover:bg-green-700'
          } ${isCollecting ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {isRunning ? (
            <>
              <Square className="w-3 h-3" />
              <span>STOP COLLECTION</span>
            </>
          ) : (
            <>
              <Play className="w-3 h-3" />
              <span>START COLLECTION</span>
            </>
          )}
        </button>

        {/* Manual Collection Button */}
        <button
          onClick={runCollection}
          disabled={isCollecting}
          className={`w-full py-1.5 rounded font-bold text-[10px] flex items-center justify-center space-x-1.5 transition bg-blue-600 hover:bg-blue-700 ${
            isCollecting ? 'opacity-50 cursor-not-allowed' : ''
          }`}
        >
          <Download className="w-3 h-3" />
          <span>COLLECT NOW</span>
        </button>

        {/* Clear Logs Button */}
        <button
          onClick={clearLogs}
          disabled={isCollecting}
          className="w-full py-1 rounded font-semibold text-[9px] flex items-center justify-center space-x-1 transition bg-gray-700 hover:bg-gray-600"
        >
          <Trash2 className="w-3 h-3" />
          <span>CLEAR LOGS</span>
        </button>
      </div>

      {/* Status Info */}
      <div className="p-2 border-b border-gray-700 bg-gray-900">
        <div className="space-y-1.5 text-[10px]">
          {/* Next Collection Time */}
          {isRunning && (
            <div className="flex items-center justify-between">
              <span className="text-gray-400 flex items-center">
                <Clock className="w-3 h-3 mr-1" />
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
                <span className="font-semibold text-yellow-400 truncate max-w-[150px]" title={currentCamera}>
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
              <div className="w-full bg-gray-700 rounded-full h-1.5 mt-1">
                <div
                  className="bg-green-500 h-1.5 rounded-full transition-all duration-300"
                  style={{ width: `${currentProgress}%` }}
                />
              </div>
            </>
          )}

          {/* Session Stats */}
          {!isCollecting && stats.collectionsThisSession > 0 && (
            <div className="pt-1.5 border-t border-gray-700 space-y-0.5">
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
        <div className="p-2 border-b border-gray-700 flex items-center justify-between">
          <h3 className="text-xs font-semibold">Session Log ({statusLog.length} entries)</h3>
          <span className="text-[9px] text-gray-500">Persistent since {sessionStartTime.toLocaleTimeString()}</span>
        </div>

        <div className="flex-1 overflow-y-auto p-2 bg-gray-900 font-mono text-[9px] space-y-0.5">
          {statusLog.length === 0 ? (
            <div className="text-gray-500 text-center py-4">
              <Info className="w-5 h-5 mx-auto mb-1.5 opacity-50" />
              <p className="text-[10px]">No activity yet.</p>
              <p className="text-[9px] mt-1">Click "START COLLECTION" or "COLLECT NOW" to begin.</p>
            </div>
          ) : (
            statusLog.map((log, idx) => (
              <div
                key={idx}
                className={`flex items-start space-x-1 leading-tight ${
                  log.type === 'error' ? 'text-red-400' :
                  log.type === 'success' ? 'text-green-400' :
                  log.type === 'warning' ? 'text-yellow-400' :
                  log.type === 'info' ? 'text-blue-300' :
                  'text-gray-300'
                } ${log.indent ? 'pl-3' : ''}`}
              >
                <span className="text-gray-500 flex-shrink-0 w-14 text-[8px]">[{log.timestamp}]</span>
                <span className="flex-1 break-words">{log.message}</span>
                {log.type === 'error' && <XCircle className="w-2.5 h-2.5 flex-shrink-0 mt-0.5" />}
                {log.type === 'success' && <CheckCircle className="w-2.5 h-2.5 flex-shrink-0 mt-0.5" />}
                {log.type === 'warning' && <AlertCircle className="w-2.5 h-2.5 flex-shrink-0 mt-0.5" />}
              </div>
            ))
          )}
        </div>
      </div>

        {/* Footer Info */}
        <div className="p-1.5 bg-gray-900 border-t border-gray-700 text-[9px] text-gray-500 text-center">
          Session Persistent Collection System • Logs Retained • Collection Runs in Background
        </div>
        </div>
      )}
    </div>
  );
}

export default CameraCollectionPanel;

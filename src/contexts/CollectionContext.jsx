import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';

/**
 * Collection Context - Persistent Camera Collection State Management
 *
 * Maintains collection state, logs, and settings across panel show/hide cycles.
 * Ensures logs and collection activity persist for the entire browser session.
 */

const CollectionContext = createContext(null);

export const useCollection = () => {
  const context = useContext(CollectionContext);
  if (!context) {
    throw new Error('useCollection must be used within CollectionProvider');
  }
  return context;
};

export const CollectionProvider = ({ children, cameras = [] }) => {
  // Session ID (created once per browser session, persists across page reloads)
  const [sessionId] = useState(() => {
    const stored = sessionStorage.getItem('collectionSessionId');
    if (stored) return stored;

    const newSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    sessionStorage.setItem('collectionSessionId', newSessionId);
    return newSessionId;
  });

  // Session start time (persists across page reloads)
  const [sessionStartTime] = useState(() => {
    const stored = sessionStorage.getItem('collectionSessionStart');
    if (stored) return new Date(stored);

    const startTime = new Date();
    sessionStorage.setItem('collectionSessionStart', startTime.toISOString());
    return startTime;
  });

  // Settings (persisted to localStorage)
  const [settings, setSettings] = useState(() => {
    const saved = localStorage.getItem('cameraCollectionSettings');
    return saved ? JSON.parse(saved) : {
      intervalHours: 1,
      intervalMinutes: 0,
      imagesPerCamera: 1,
      autoStart: false
    };
  });

  // Session logs (persisted to sessionStorage - cleared on browser close)
  const [statusLog, setStatusLog] = useState(() => {
    const saved = sessionStorage.getItem('collectionSessionLogs');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        return [];
      }
    }
    return [];
  });

  // Collection state (running, collecting, etc.)
  const [isRunning, setIsRunning] = useState(() => {
    const saved = sessionStorage.getItem('collectionIsRunning');
    return saved === 'true';
  });

  const [isCollecting, setIsCollecting] = useState(false);
  const [totalImages, setTotalImages] = useState(0);
  const [currentCamera, setCurrentCamera] = useState(null);
  const [currentProgress, setCurrentProgress] = useState(0);
  const [nextCollectionTime, setNextCollectionTime] = useState(null);

  // Collection statistics
  const [stats, setStats] = useState(() => {
    const saved = sessionStorage.getItem('collectionStats');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        return {
          totalCollections: 0,
          totalImagesCollected: 0,
          lastCollectionTime: null,
          collectionsThisSession: 0
        };
      }
    }
    return {
      totalCollections: 0,
      totalImagesCollected: 0,
      lastCollectionTime: null,
      collectionsThisSession: 0
    };
  });

  // Refs for timers
  const collectionTimerRef = useRef(null);
  const nextCollectionTimerRef = useRef(null);

  // Save settings to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('cameraCollectionSettings', JSON.stringify(settings));
  }, [settings]);

  // Save logs to sessionStorage whenever they change
  useEffect(() => {
    sessionStorage.setItem('collectionSessionLogs', JSON.stringify(statusLog));
  }, [statusLog]);

  // Save running state to sessionStorage
  useEffect(() => {
    sessionStorage.setItem('collectionIsRunning', isRunning.toString());
  }, [isRunning]);

  // Save stats to sessionStorage
  useEffect(() => {
    sessionStorage.setItem('collectionStats', JSON.stringify(stats));
  }, [stats]);

  // Log session info on first mount
  useEffect(() => {
    const sessionInfo = sessionStorage.getItem('collectionSessionInfoLogged');
    if (!sessionInfo) {
      logStatus(`════════════════════════════════════════════════════════════════════`, 'info');
      logStatus(`SESSION START: ${sessionStartTime.toLocaleString()}`, 'success');
      logStatus(`Session ID: ${sessionId}`, 'info');
      logStatus(`Cameras Available: ${cameras.length}`, 'info');
      logStatus(`════════════════════════════════════════════════════════════════════`, 'info');
      sessionStorage.setItem('collectionSessionInfoLogged', 'true');
    }
  }, []);

  // Restore collection timer if it was running
  useEffect(() => {
    if (isRunning && !collectionTimerRef.current) {
      const intervalMs = (settings.intervalHours * 3600 + settings.intervalMinutes * 60) * 1000;

      collectionTimerRef.current = setInterval(() => {
        runCollection();
      }, intervalMs);

      logStatus(`Automatic collection restored (every ${settings.intervalHours}h ${settings.intervalMinutes}m)`, 'info');
    }

    return () => {
      if (collectionTimerRef.current) {
        clearInterval(collectionTimerRef.current);
        collectionTimerRef.current = null;
      }
    };
  }, [isRunning, settings.intervalHours, settings.intervalMinutes]);

  // Calculate next collection time
  useEffect(() => {
    if (isRunning) {
      const intervalMs = (settings.intervalHours * 3600 + settings.intervalMinutes * 60) * 1000;
      const next = new Date(Date.now() + intervalMs);
      setNextCollectionTime(next);

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

  // Log message to status log (persisted across panel show/hide)
  const logStatus = useCallback((message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    const logEntry = { timestamp, message, type, sessionTime: Date.now() - sessionStartTime.getTime() };

    setStatusLog(prev => [
      logEntry,
      ...prev.slice(0, 499) // Keep last 500 messages (increased from 50)
    ]);
  }, [sessionStartTime]);

  // Start scheduled collection
  const startCollection = useCallback(() => {
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
    logStatus(`════════════════════════════════════════════════════════════════════`, 'info');
    logStatus(`AUTOMATIC COLLECTION STARTED`, 'success');
    logStatus(`Interval: ${settings.intervalHours} hours ${settings.intervalMinutes} minutes`, 'info');
    logStatus(`Images per camera: ${settings.imagesPerCamera}`, 'info');
    logStatus(`Total cameras: ${cameras.length}`, 'info');
    logStatus(`════════════════════════════════════════════════════════════════════`, 'info');

    // Run first collection immediately
    runCollection();

    // Set up interval for future collections
    collectionTimerRef.current = setInterval(() => {
      runCollection();
    }, intervalMs);
  }, [cameras, settings, logStatus]);

  // Stop scheduled collection
  const stopCollection = useCallback(() => {
    setIsRunning(false);
    if (collectionTimerRef.current) {
      clearInterval(collectionTimerRef.current);
      collectionTimerRef.current = null;
    }
    logStatus(`════════════════════════════════════════════════════════════════════`, 'info');
    logStatus(`AUTOMATIC COLLECTION STOPPED`, 'warning');
    logStatus(`════════════════════════════════════════════════════════════════════`, 'info');
  }, [logStatus]);

  // Run camera image collection
  const runCollection = useCallback(async () => {
    if (isCollecting) {
      logStatus('Previous collection still in progress, skipping...', 'warning');
      return;
    }

    setIsCollecting(true);
    setCurrentProgress(0);
    setTotalImages(0);

    const collectionNumber = stats.collectionsThisSession + 1;
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    const collectionId = `qew_collection_${timestamp}`;

    logStatus(``, 'info'); // Blank line for separation
    logStatus(`▶ COLLECTION #${collectionNumber} STARTED`, 'success');
    logStatus(`Collection ID: ${collectionId}`, 'info');
    logStatus(`Cameras: ${cameras.length} | Images per camera: ${settings.imagesPerCamera}`, 'info');

    try {
      let imagesCollected = 0;

      for (let cameraIdx = 0; cameraIdx < cameras.length; cameraIdx++) {
        const camera = cameras[cameraIdx];
        setCurrentCamera(camera.Location || `Camera ${camera.Id}`);
        setCurrentProgress(Math.round(((cameraIdx + 1) / cameras.length) * 100));

        logStatus(`[${cameraIdx + 1}/${cameras.length}] ${camera.Location}`, 'info');

        const views = camera.Views || [];
        for (let viewIdx = 0; viewIdx < views.length; viewIdx++) {
          const view = views[viewIdx];

          for (let round = 0; round < settings.imagesPerCamera; round++) {
            // Simulate image download (replace with real API call)
            await simulateImageDownload(camera.Id, view.Id, round + 1);
            imagesCollected++;
            setTotalImages(imagesCollected);
          }
        }
      }

      // Update stats
      setStats(prev => ({
        totalCollections: prev.totalCollections + 1,
        totalImagesCollected: prev.totalImagesCollected + imagesCollected,
        lastCollectionTime: new Date().toISOString(),
        collectionsThisSession: prev.collectionsThisSession + 1
      }));

      logStatus(`✓ COLLECTION #${collectionNumber} COMPLETE`, 'success');
      logStatus(`Images collected: ${imagesCollected} | Total this session: ${stats.totalImagesCollected + imagesCollected}`, 'success');
      logStatus(`Collection saved: ${collectionId}`, 'info');
      logStatus(`════════════════════════════════════════════════════════════════════`, 'info');

    } catch (error) {
      logStatus(`✗ COLLECTION #${collectionNumber} FAILED`, 'error');
      logStatus(`Error: ${error.message}`, 'error');
      logStatus(`════════════════════════════════════════════════════════════════════`, 'info');
    } finally {
      setIsCollecting(false);
      setCurrentCamera(null);
      setCurrentProgress(0);
    }
  }, [cameras, settings, isCollecting, stats, logStatus]);

  // Simulate image download
  const simulateImageDownload = (cameraId, viewId, round) => {
    return new Promise(resolve => {
      setTimeout(resolve, 200);
    });
  };

  // Update settings
  const updateSetting = useCallback((key, value) => {
    setSettings(prev => ({ ...prev, [key]: value }));
    logStatus(`Setting updated: ${key} = ${value}`, 'info');
  }, [logStatus]);

  // Clear session logs
  const clearLogs = useCallback(() => {
    setStatusLog([]);
    sessionStorage.removeItem('collectionSessionLogs');
    logStatus(`════════════════════════════════════════════════════════════════════`, 'info');
    logStatus(`LOGS CLEARED`, 'warning');
    logStatus(`Session ID: ${sessionId}`, 'info');
    logStatus(`════════════════════════════════════════════════════════════════════`, 'info');
  }, [sessionId, logStatus]);

  // Get session uptime
  const getSessionUptime = useCallback(() => {
    const uptimeMs = Date.now() - sessionStartTime.getTime();
    const hours = Math.floor(uptimeMs / (1000 * 60 * 60));
    const minutes = Math.floor((uptimeMs % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((uptimeMs % (1000 * 60)) / 1000);
    return `${hours}h ${minutes}m ${seconds}s`;
  }, [sessionStartTime]);

  const value = {
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
  };

  return (
    <CollectionContext.Provider value={value}>
      {children}
    </CollectionContext.Provider>
  );
};

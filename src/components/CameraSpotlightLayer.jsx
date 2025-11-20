import React, { useState, useEffect } from 'react';
import CameraSpotlight from './CameraSpotlight';

/**
 * CameraSpotlightLayer Component
 * Fetches camera direction data from backend API and renders spotlights for all cameras
 */
const CameraSpotlightLayer = () => {
  const [cameraDirections, setCameraDirections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch camera direction data from FastAPI backend
    const fetchCameraDirections = async () => {
      try {
        // Use backend API Gateway endpoint
        const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
        const response = await fetch(`${API_BASE_URL}/api/directions/cameras`);

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        console.log(`✅ Loaded ${data.length} cameras with direction data from backend`);
        setCameraDirections(data);
        setLoading(false);
      } catch (err) {
        console.error('❌ Error loading camera directions from backend:', err);
        console.warn('💡 Make sure backend is running: cd backend/api-gateway && python main.py');
        setError(err.message);
        setLoading(false);
      }
    };

    fetchCameraDirections();

    // Refresh camera directions every 30 seconds
    const interval = setInterval(fetchCameraDirections, 30000);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    console.log('⏳ Loading camera directions from backend...');
    return null;
  }

  if (error) {
    console.error('❌ Failed to load camera directions:', error);
    // Fail silently - don't break the map
    return null;
  }

  // Render spotlights for all cameras with direction data
  return (
    <>
      {cameraDirections.map((camera) => {
        // Only render if camera has heading data
        if (!camera.heading) {
          return null;
        }

        // Render spotlight for each direction view
        return camera.direction_views.map((view, viewIndex) => (
          <CameraSpotlight
            key={`spotlight-${camera.camera_id}-${viewIndex}`}
            latitude={camera.latitude}
            longitude={camera.longitude}
            heading={view.heading}
            color={getDirectionColor(view.direction)}
            opacity={0.25}
          />
        ));
      })}
    </>
  );
};

/**
 * Get spotlight color based on direction
 * @param {string} direction - Camera direction (N, NE, E, SE, S, SW, W, NW)
 * @returns {string} Hex color code
 */
function getDirectionColor(direction) {
  const colorMap = {
    'N': '#FFD700',  // Gold (North)
    'NE': '#FFA500', // Orange
    'E': '#FF6347',  // Tomato (East)
    'SE': '#FF1493', // Deep Pink
    'S': '#9370DB',  // Medium Purple (South)
    'SW': '#4169E1', // Royal Blue
    'W': '#20B2AA',  // Light Sea Green (West)
    'NW': '#32CD32'  // Lime Green
  };

  return colorMap[direction] || '#FFD700'; // Default to gold
}

export default CameraSpotlightLayer;

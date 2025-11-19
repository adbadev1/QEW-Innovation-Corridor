import React, { useState, useEffect } from 'react';
import CameraSpotlight from './CameraSpotlight';

/**
 * CameraSpotlightLayer Component
 * Fetches camera direction data and renders spotlights for all cameras
 */
const CameraSpotlightLayer = () => {
  const [cameraDirections, setCameraDirections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch camera direction data from FastAPI backend
    const fetchCameraDirections = async () => {
      try {
        // Use localhost:8000 for FastAPI backend
        const response = await fetch('http://localhost:8000/api/camera-directions/');
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        console.log(`✅ Loaded ${data.length} camera locations with direction data`);
        setCameraDirections(data);
        setLoading(false);
      } catch (err) {
        console.error('Error loading camera directions:', err);
        setError(err.message);
        setLoading(false);
      }
    };

    fetchCameraDirections();
  }, []);

  if (loading) {
    console.log('Loading camera directions...');
    return null;
  }

  if (error) {
    console.error('Failed to load camera directions:', error);
    return null;
  }

  // Render spotlights for all cameras
  return (
    <>
      {cameraDirections.map((location, locIndex) => (
        location.cameras.map((camera, camIndex) => (
          <CameraSpotlight
            key={`spotlight-${locIndex}-${camIndex}`}
            latitude={location.latitude}
            longitude={location.longitude}
            heading={camera.heading}
            color="#FFD700"  // Gold color for spotlight
            opacity={0.25}
          />
        ))
      ))}
    </>
  );
};

export default CameraSpotlightLayer;


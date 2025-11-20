import React from 'react';
import { Polygon, useMap } from 'react-leaflet';
import L from 'leaflet';

/**
 * CameraSpotlight Component
 * Renders a spotlight cone showing the direction a camera is facing
 *
 * @param {Object} props
 * @param {number} props.latitude - Camera latitude
 * @param {number} props.longitude - Camera longitude
 * @param {number} props.heading - Camera heading in degrees (0-360, 0=North)
 * @param {string} props.color - Spotlight color (default: yellow)
 * @param {number} props.opacity - Spotlight opacity (default: 0.3)
 */
const CameraSpotlight = ({
  latitude,
  longitude,
  heading,
  color = '#FFD700',
  opacity = 0.3
}) => {
  const map = useMap();

  // Calculate spotlight cone coordinates based on zoom level
  const getSpotlightCoordinates = () => {
    const zoom = map.getZoom();

    // Adjust cone size based on zoom level
    // Zoom 10: 100m, Zoom 12: 150m, Zoom 14: 200m, Zoom 16: 250m
    const baseLength = 100; // meters
    const zoomFactor = Math.pow(1.2, zoom - 10); // Exponential growth
    const coneLength = Math.min(baseLength * zoomFactor, 300); // Max 300m

    // Cone angle (total spread)
    const coneAngle = 45; // degrees (±22.5° from center)

    // Convert heading to radians (0° = North, clockwise)
    const headingRad = (heading * Math.PI) / 180;

    // Calculate left and right edges of cone
    const leftAngleRad = ((heading - coneAngle / 2) * Math.PI) / 180;
    const rightAngleRad = ((heading + coneAngle / 2) * Math.PI) / 180;

    // Earth radius in meters
    const earthRadius = 6371000;

    // Convert meters to degrees (approximate)
    const latOffset = (coneLength / earthRadius) * (180 / Math.PI);
    const lonOffset = (coneLength / (earthRadius * Math.cos((latitude * Math.PI) / 180))) * (180 / Math.PI);

    // Calculate end point of cone (center)
    const centerLat = latitude + latOffset * Math.cos(headingRad);
    const centerLon = longitude + lonOffset * Math.sin(headingRad);

    // Calculate left edge point
    const leftLat = latitude + latOffset * Math.cos(leftAngleRad);
    const leftLon = longitude + lonOffset * Math.sin(leftAngleRad);

    // Calculate right edge point
    const rightLat = latitude + latOffset * Math.cos(rightAngleRad);
    const rightLon = longitude + lonOffset * Math.sin(rightAngleRad);

    // Return polygon coordinates (triangle)
    return [
      [latitude, longitude],      // Camera position (origin)
      [leftLat, leftLon],          // Left edge
      [centerLat, centerLon],      // Center point (tip)
      [rightLat, rightLon],        // Right edge
      [latitude, longitude]        // Close the polygon
    ];
  };

  const coordinates = getSpotlightCoordinates();

  return (
    <Polygon
      positions={coordinates}
      pathOptions={{
        color: color,
        fillColor: color,
        fillOpacity: opacity,
        weight: 1,
        opacity: opacity + 0.2
      }}
    />
  );
};

export default CameraSpotlight;

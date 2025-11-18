/**
 * V2X Broadcast Context
 * Manages active vRSU broadcasts and vehicle alert subscriptions
 */

import React, { createContext, useContext, useState, useCallback } from 'react';

const V2XContext = createContext();

export function V2XProvider({ children }) {
  const [activeBroadcasts, setActiveBroadcasts] = useState([]);
  const [vehicleAlerts, setVehicleAlerts] = useState({});

  const registerBroadcast = useCallback((workZone, broadcastData) => {
    const broadcast = {
      id: workZone.id,
      workZone,
      messageType: broadcastData?.messageType || 'TIM',
      messageId: broadcastData?.messageId,
      timestamp: new Date().toISOString(),
      radius: 1000,
      expiresAt: new Date(Date.now() + 3600000).toISOString(),
      active: true
    };

    setActiveBroadcasts(prev => {
      const now = new Date();
      const active = prev.filter(b => new Date(b.expiresAt) > now);
      const existing = active.findIndex(b => b.id === broadcast.id);
      if (existing >= 0) {
        active[existing] = broadcast;
        return active;
      }
      return [...active, broadcast];
    });

    console.log('V2X Broadcast registered:', workZone.cameraId);
    return broadcast;
  }, []);

  const checkVehicleAlerts = useCallback((vehicleId, vehicleCoords, calculateDistance) => {
    const receivedAlerts = [];

    activeBroadcasts.forEach(broadcast => {
      if (!broadcast.active) return;
      
      const [vLat, vLon] = vehicleCoords;
      const distance = calculateDistance(
        vLat, vLon,
        broadcast.workZone.lat, broadcast.workZone.lon
      );

      if (distance <= broadcast.radius) {
        const alert = {
          broadcastId: broadcast.id,
          workZoneId: broadcast.workZone.id,
          messageType: broadcast.messageType,
          messageId: broadcast.messageId,
          cameraId: broadcast.workZone.cameraId,
          riskScore: broadcast.workZone.riskScore,
          distance: Math.round(distance),
          message: generateAlertMessage(broadcast.workZone, distance),
          receivedAt: new Date().toISOString(),
          speedLimit: getSpeedLimit(broadcast.workZone.riskScore),
          urgency: getUrgency(broadcast.workZone.riskScore)
        };
        
        receivedAlerts.push(alert);
      }
    });

    if (receivedAlerts.length > 0) {
      setVehicleAlerts(prev => ({
        ...prev,
        [vehicleId]: receivedAlerts
      }));
    } else {
      setVehicleAlerts(prev => {
        const updated = { ...prev };
        delete updated[vehicleId];
        return updated;
      });
    }

    return receivedAlerts;
  }, [activeBroadcasts]);

  const getVehicleAlerts = useCallback((vehicleId) => {
    return vehicleAlerts[vehicleId] || [];
  }, [vehicleAlerts]);

  const cleanupExpiredBroadcasts = useCallback(() => {
    const now = new Date();
    setActiveBroadcasts(prev => 
      prev.filter(b => new Date(b.expiresAt) > now)
    );
  }, []);

  const value = {
    activeBroadcasts,
    vehicleAlerts,
    registerBroadcast,
    checkVehicleAlerts,
    getVehicleAlerts,
    cleanupExpiredBroadcasts
  };

  return (
    <V2XContext.Provider value={value}>
      {children}
    </V2XContext.Provider>
  );
}

export function useV2X() {
  const context = useContext(V2XContext);
  if (!context) {
    throw new Error('useV2X must be used within V2XProvider');
  }
  return context;
}

function generateAlertMessage(workZone, distance) {
  const distanceText = distance < 1000 
    ? Math.round(distance) + 'm'
    : (distance / 1000).toFixed(1) + 'km';

  if (workZone.riskScore >= 9) {
    return 'CRITICAL: Work zone ' + distanceText + ' ahead. DANGER - Slow to 40 km/h.';
  } else if (workZone.riskScore >= 7) {
    return 'CAUTION: Work zone ' + distanceText + ' ahead. Reduce speed to 60 km/h.';
  } else if (workZone.riskScore >= 5) {
    return 'ADVISORY: Work zone ' + distanceText + ' ahead. Reduce speed to 60 km/h.';
  } else {
    return 'INFO: Work zone ' + distanceText + ' ahead. Maintain safe speed.';
  }
}

function getSpeedLimit(riskScore) {
  if (riskScore >= 9) return 40;
  if (riskScore >= 5) return 60;
  return 80;
}

function getUrgency(riskScore) {
  if (riskScore >= 9) return 'critical';
  if (riskScore >= 7) return 'high';
  if (riskScore >= 5) return 'medium';
  return 'low';
}

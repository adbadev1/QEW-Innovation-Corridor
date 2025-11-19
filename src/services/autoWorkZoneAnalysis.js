/**
 * Automatic Work Zone Analysis Service
 *
 * Automatically triggers Gemini AI analysis after camera image collection
 * Integrates with work zone history tracking system
 *
 * Workflow:
 * 1. Image uploaded to GCP Storage
 * 2. Gemini AI analyzes image
 * 3. If work zone detected → add to history
 * 4. Return analysis results
 */

import { analyzeWorkZoneImage, formatWorkZoneForDashboard } from './geminiVision';
import { blobToFile } from './gcpStorage';
import { addWorkZoneCamera } from '../utils/workZoneHistory';

/**
 * Analyze uploaded camera image for work zones
 * Automatically triggered after each image upload
 *
 * @param {Object} params - Analysis parameters
 * @param {Blob} params.imageBlob - Image blob data
 * @param {number} params.cameraId - Camera ID
 * @param {number} params.viewId - View ID
 * @param {string} params.cameraLocation - Camera location description
 * @param {number} params.latitude - Camera latitude
 * @param {number} params.longitude - Camera longitude
 * @param {string} params.collectionId - Collection ID
 * @param {string} params.gcpImageUrl - GCP Storage URL for the image
 * @param {Function} registerBroadcast - V2X broadcast registration callback (optional)
 * @returns {Promise<Object>} Analysis result
 */
export async function analyzeUploadedImage({
  imageBlob,
  cameraId,
  viewId,
  cameraLocation,
  latitude,
  longitude,
  collectionId,
  gcpImageUrl,
  registerBroadcast = null
}) {
  try {
    console.log(`[Auto Analysis] Starting analysis for Camera ${cameraId}, View ${viewId}`);

    // Convert blob to File for Gemini API
    const imageFile = blobToFile(imageBlob, `camera_${cameraId}_view_${viewId}.jpg`);

    // Create metadata for tracking
    const metadata = {
      synthetic: false,
      source: 'COMPASS',
      cameraId,
      viewId,
      cameraLocation,
      cameraLat: latitude,
      cameraLon: longitude,
      collectionId,
      gcpImageUrl,
      capturedAt: new Date().toISOString()
    };

    // Analyze with Gemini AI
    const analysis = await analyzeWorkZoneImage(imageFile, metadata);

    // Check for errors
    if (analysis.error) {
      console.error(`[Auto Analysis] Gemini error for Camera ${cameraId}:`, analysis.message);
      return {
        success: false,
        error: analysis.message,
        cameraId,
        viewId,
        hasWorkZone: false
      };
    }

    // Check if work zone detected
    if (!analysis.hasWorkZone) {
      console.log(`[Auto Analysis] No work zone detected - Camera ${cameraId} (confidence: ${(analysis.confidence * 100).toFixed(0)}%)`);
      return {
        success: true,
        hasWorkZone: false,
        confidence: analysis.confidence,
        cameraId,
        viewId,
        analysis
      };
    }

    console.log(`[Auto Analysis] 🚧 WORK ZONE DETECTED - Camera ${cameraId}`);
    console.log(`  ├─ Risk Score: ${analysis.riskScore}/10`);
    console.log(`  ├─ Workers: ${analysis.workers || 0}`);
    console.log(`  ├─ Vehicles: ${analysis.vehicles || 0}`);
    console.log(`  ├─ Confidence: ${(analysis.confidence * 100).toFixed(0)}%`);

    // Format for dashboard
    const workZone = await formatWorkZoneForDashboard(
      analysis,
      `CAMERA_${cameraId}`,
      { lat: latitude, lon: longitude },
      registerBroadcast
    );

    if (workZone) {
      // Add real camera metadata
      workZone.synthetic = false;
      workZone.realCamera = metadata;
      workZone.gcpImageUrl = gcpImageUrl;

      // Add to work zone history
      const added = addWorkZoneCamera(
        cameraId,
        cameraLocation,
        viewId,
        {
          riskScore: workZone.riskScore,
          workers: workZone.workers,
          vehicles: workZone.vehicles,
          equipment: workZone.equipment || 0,
          collectionId,
          gcpImageUrl
        }
      );

      if (added) {
        console.log(`[Auto Analysis] ✓ Added to work zone history: Camera ${cameraId}`);
      }

      return {
        success: true,
        hasWorkZone: true,
        workZone,
        cameraId,
        viewId,
        analysis
      };
    }

    return {
      success: true,
      hasWorkZone: false,
      cameraId,
      viewId,
      analysis
    };

  } catch (error) {
    console.error(`[Auto Analysis] Critical error for Camera ${cameraId}:`, error);
    return {
      success: false,
      error: error.message,
      cameraId,
      viewId,
      hasWorkZone: false
    };
  }
}

/**
 * Batch analyze multiple images from a collection
 *
 * @param {Array} images - Array of image objects with camera metadata
 * @param {Function} registerBroadcast - V2X broadcast registration callback
 * @param {Function} progressCallback - Progress update callback (optional)
 * @returns {Promise<Object>} Batch analysis results
 */
export async function batchAnalyzeCollection(images, registerBroadcast = null, progressCallback = null) {
  const results = {
    total: images.length,
    analyzed: 0,
    workZonesDetected: 0,
    errors: 0,
    workZones: [],
    errors: []
  };

  console.log(`[Auto Analysis] Starting batch analysis: ${images.length} images`);

  for (let i = 0; i < images.length; i++) {
    const image = images[i];

    try {
      const result = await analyzeUploadedImage({
        ...image,
        registerBroadcast
      });

      results.analyzed++;

      if (result.success && result.hasWorkZone) {
        results.workZonesDetected++;
        results.workZones.push(result.workZone);
      }

      if (!result.success) {
        results.errors++;
        results.errorsList.push({
          cameraId: image.cameraId,
          viewId: image.viewId,
          error: result.error
        });
      }

      // Update progress
      if (progressCallback) {
        progressCallback({
          current: i + 1,
          total: images.length,
          percentage: Math.round(((i + 1) / images.length) * 100),
          workZonesDetected: results.workZonesDetected
        });
      }

    } catch (error) {
      results.errors++;
      results.errorsList.push({
        cameraId: image.cameraId,
        viewId: image.viewId,
        error: error.message
      });
    }
  }

  console.log(`[Auto Analysis] Batch complete: ${results.workZonesDetected} work zones detected (${results.errors} errors)`);

  return results;
}

/**
 * Get analysis summary for logging
 * @param {Object} result - Analysis result
 * @returns {string} Formatted summary
 */
export function getAnalysisSummary(result) {
  if (!result.success) {
    return `❌ Error: ${result.error}`;
  }

  if (!result.hasWorkZone) {
    return `✓ No work zone (confidence: ${(result.confidence * 100).toFixed(0)}%)`;
  }

  const wz = result.workZone;
  return `🚧 Work Zone: Risk ${wz.riskScore}/10 | Workers: ${wz.workers} | Vehicles: ${wz.vehicles} | Barriers: ${wz.barriers ? 'YES' : 'NO'}`;
}

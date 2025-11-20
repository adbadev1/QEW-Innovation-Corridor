/**
 * Browser-compatible Scraped Image Analysis Module
 * Wrapper for autoWorkZoneAnalysis that works in browser context
 */

import { analyzeWorkZoneImage } from '../src/services/geminiVision.js';

/**
 * Get list of scraped images from manifest
 */
async function getScrapedImageList() {
  const basePath = window.location.origin + '/';

  try {
    const manifestUrl = `${basePath}camera_images/manifest.json`;
    console.log('[Auto Analysis] Loading manifest from:', manifestUrl);

    const response = await fetch(manifestUrl);
    if (!response.ok) {
      throw new Error(`Failed to load manifest: ${response.status}`);
    }

    const manifest = await response.json();
    console.log(`[Auto Analysis] ✅ Loaded manifest with ${manifest.length} images`);

    return manifest;
  } catch (error) {
    console.error('[Auto Analysis] ❌ Failed to load manifest:', error);
    return [];
  }
}

/**
 * Check if a view has already been analyzed
 */
function hasWorkZoneInView(viewId) {
  try {
    const history = JSON.parse(localStorage.getItem('qew_workzone_camera_history') || '[]');
    return history.some(item => item.viewId === viewId);
  } catch (error) {
    return false;
  }
}

/**
 * Add work zone to history
 */
function addWorkZoneCamera(cameraId, location, viewId, workZoneData = {}) {
  try {
    const history = JSON.parse(localStorage.getItem('qew_workzone_camera_history') || '[]');

    const entry = {
      cameraId,
      location,
      viewId,
      detectedAt: new Date().toISOString(),
      riskScore: workZoneData.riskScore || null,
      workers: workZoneData.workers || null,
      vehicles: workZoneData.vehicles || null,
      equipment: workZoneData.equipment || null,
      lastUpdated: new Date().toISOString(),
      gcpImageUrl: workZoneData.gcpImageUrl || null
    };

    // Check if exists
    const existingIndex = history.findIndex(
      item => item.cameraId === cameraId && item.viewId === viewId
    );

    if (existingIndex >= 0) {
      history[existingIndex] = {
        ...history[existingIndex],
        ...entry,
        firstDetectedAt: history[existingIndex].detectedAt,
        detectionCount: (history[existingIndex].detectionCount || 1) + 1
      };
    } else {
      history.push({
        ...entry,
        firstDetectedAt: entry.detectedAt,
        detectionCount: 1
      });
    }

    localStorage.setItem('qew_workzone_camera_history', JSON.stringify(history));
    console.log(`[Work Zone History] Added camera ${cameraId} to history`);

    return true;
  } catch (error) {
    console.error('[Work Zone History] Failed to add:', error);
    return false;
  }
}

/**
 * Auto-analyze scraped images
 */
export async function autoAnalyzeScrapedImages(cameras, progressCallback = null) {
  console.log('[Auto Analysis] 🚀 Starting analysis of scraped images...');

  const basePath = window.location.origin + '/';
  const results = {
    total: 0,
    analyzed: 0,
    workZonesDetected: 0,
    errors: 0,
    skipped: 0,
    details: []
  };

  // Get list of scraped images
  const imageFiles = await getScrapedImageList();
  console.log(`[Auto Analysis] Found ${imageFiles.length} scraped images`);

  results.total = imageFiles.length;

  for (let i = 0; i < imageFiles.length; i++) {
    const imageFile = imageFiles[i];
    const { cameraId, viewId, filename } = imageFile;

    try {
      // Find camera metadata
      const camera = cameras.find(c => c.Id === cameraId);
      if (!camera) {
        console.warn(`[Auto Analysis] ⚠️ Camera ${cameraId} not found in metadata`);
        results.skipped++;
        continue;
      }

      const view = camera.Views?.find(v => v.Id === viewId);
      if (!view) {
        console.warn(`[Auto Analysis] ⚠️ View ${viewId} not found for Camera ${cameraId}`);
        results.skipped++;
        continue;
      }

      // Skip if already analyzed
      if (hasWorkZoneInView(viewId)) {
        console.log(`[Auto Analysis] ⏭️ Skipping Camera ${cameraId} View ${viewId} (already analyzed)`);
        results.skipped++;
        continue;
      }

      // Fetch image from public directory
      const imageUrl = `${basePath}camera_images/${filename}`;
      console.log(`[Auto Analysis] 📥 Fetching: ${filename}`);

      const response = await fetch(imageUrl);
      if (!response.ok) {
        throw new Error(`Failed to fetch image: ${response.status}`);
      }

      const imageBlob = await response.blob();

      // Convert to File object
      const imageFileObj = new File([imageBlob], filename, { type: imageBlob.type });

      // Analyze with Gemini Vision API
      console.log(`[Auto Analysis] 🔍 Analyzing Camera ${cameraId} View ${viewId}...`);

      const metadata = {
        synthetic: false,
        source: 'COMPASS',
        cameraId,
        viewId,
        cameraLocation: camera.Location,
        cameraLat: camera.Latitude,
        cameraLon: camera.Longitude,
        collectionId: 'scraped_images',
        gcpImageUrl: imageUrl
      };

      const analysis = await analyzeWorkZoneImage(imageFileObj, metadata);

      results.analyzed++;

      if (analysis.success !== false && analysis.hasWorkZone) {
        results.workZonesDetected++;
        console.log(`[Auto Analysis] 🚧 WORK ZONE DETECTED - Camera ${cameraId} (Risk: ${analysis.riskScore}/10)`);

        // Add to history
        addWorkZoneCamera(
          cameraId,
          camera.Location,
          viewId,
          {
            riskScore: analysis.riskScore,
            workers: analysis.workers,
            vehicles: analysis.vehicles,
            equipment: analysis.equipment || 0,
            collectionId: 'scraped_images',
            gcpImageUrl: imageUrl
          }
        );
      }

      if (analysis.error) {
        results.errors++;
        console.error(`[Auto Analysis] ❌ Analysis failed for Camera ${cameraId}:`, analysis.message);
      }

      results.details.push({
        cameraId,
        viewId,
        filename,
        success: !analysis.error,
        hasWorkZone: analysis.hasWorkZone,
        riskScore: analysis.riskScore || 0
      });

      // Progress callback
      if (progressCallback) {
        progressCallback({
          current: i + 1,
          total: imageFiles.length,
          analyzed: results.analyzed,
          workZonesDetected: results.workZonesDetected,
          percentage: Math.round(((i + 1) / imageFiles.length) * 100),
          cameraId,
          viewId,
          hasWorkZone: analysis.hasWorkZone,
          complete: true
        });
      }

      // Small delay to avoid overwhelming the UI
      await new Promise(resolve => setTimeout(resolve, 500));

    } catch (error) {
      results.errors++;
      console.error(`[Auto Analysis] ❌ Error analyzing ${filename}:`, error);
      results.details.push({
        cameraId,
        viewId,
        filename,
        success: false,
        error: error.message
      });
    }
  }

  console.log('[Auto Analysis] ✅ Analysis complete!');
  console.log(`  ├─ Total images: ${results.total}`);
  console.log(`  ├─ Analyzed: ${results.analyzed}`);
  console.log(`  ├─ Work zones detected: ${results.workZonesDetected}`);
  console.log(`  ├─ Errors: ${results.errors}`);
  console.log(`  └─ Skipped: ${results.skipped}`);

  return results;
}

/**
 * Check status of scraped images
 */
export async function checkScrapedImagesStatus(cameras) {
  const imageFiles = await getScrapedImageList();

  const status = {
    totalImages: imageFiles.length,
    needsAnalysis: 0,
    alreadyAnalyzed: 0
  };

  for (const imageFile of imageFiles) {
    const { viewId } = imageFile;

    if (hasWorkZoneInView(viewId)) {
      status.alreadyAnalyzed++;
    } else {
      status.needsAnalysis++;
    }
  }

  console.log('[Auto Analysis] Status check:', status);

  return status;
}

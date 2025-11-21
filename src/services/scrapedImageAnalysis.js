/**
 * Scraped Image Analysis Service
 *
 * Automatically analyzes scraped camera images from /public/camera_images/
 * Triggers Gemini Vision API analysis and updates work zone history
 * Makes camera pins turn RED when work zones are detected
 *
 * WORKFLOW:
 * 1. Scan /public/camera_images/ for scraped JPEGs
 * 2. Load camera metadata from qew_cameras_with_images.json
 * 3. For each image, trigger Gemini Vision analysis
 * 4. Store results in localStorage (work zone history)
 * 5. Camera pins automatically turn RED via workZoneViewIds
 */

import { analyzeUploadedImage } from './autoWorkZoneAnalysis';
import { hasWorkZoneInView } from '../utils/workZoneHistory';

/**
 * Fetch and analyze all scraped camera images
 *
 * @param {Array} cameras - Camera metadata from qew_cameras_with_images.json
 * @param {Function} progressCallback - Optional progress callback
 * @returns {Promise<Object>} Analysis results
 */
export async function analyzeScrapedImages(cameras, progressCallback = null) {
  console.log('[Scraped Image Analysis] 🚀 Starting analysis of scraped images...');

  const basePath = import.meta.env.BASE_URL || '/';
  const results = {
    total: 0,
    analyzed: 0,
    workZonesDetected: 0,
    errors: 0,
    skipped: 0,
    details: []
  };

  // Get list of scraped images from public/camera_images/
  const imageFiles = await getScrapedImageList();
  console.log(`[Scraped Image Analysis] Found ${imageFiles.length} scraped images`);

  results.total = imageFiles.length;

  for (let i = 0; i < imageFiles.length; i++) {
    const imageFile = imageFiles[i];
    const { cameraId, viewId, filename } = imageFile;

    try {
      // Find camera metadata
      const camera = cameras.find(c => c.Id === cameraId);
      if (!camera) {
        console.warn(`[Scraped Image Analysis] ⚠️ Camera ${cameraId} not found in metadata`);
        results.skipped++;
        continue;
      }

      const view = camera.Views?.find(v => v.Id === viewId);
      if (!view) {
        console.warn(`[Scraped Image Analysis] ⚠️ View ${viewId} not found for Camera ${cameraId}`);
        results.skipped++;
        continue;
      }

      // Skip if already analyzed (check by view ID)
      if (hasWorkZoneInView(viewId)) {
        console.log(`[Scraped Image Analysis] ⏭️ Skipping Camera ${cameraId} View ${viewId} (already analyzed)`);
        results.skipped++;
        continue;
      }

      // Fetch image from public directory
      const imageUrl = `${basePath}camera_images/${filename}`;
      console.log(`[Scraped Image Analysis] 📥 Fetching: ${filename}`);

      const response = await fetch(imageUrl);
      if (!response.ok) {
        throw new Error(`Failed to fetch image: ${response.status}`);
      }

      const imageBlob = await response.blob();

      // Analyze with Gemini Vision API
      console.log(`[Scraped Image Analysis] 🔍 Analyzing Camera ${cameraId} View ${viewId}...`);

      const analysisResult = await analyzeUploadedImage({
        imageBlob,
        cameraId,
        viewId,
        cameraLocation: camera.Location,
        latitude: camera.Latitude,
        longitude: camera.Longitude,
        collectionId: 'scraped_images',
        gcpImageUrl: imageUrl
      });

      results.analyzed++;

      if (analysisResult.success && analysisResult.hasWorkZone) {
        results.workZonesDetected++;
        console.log(`[Scraped Image Analysis] 🚧 WORK ZONE DETECTED - Camera ${cameraId} (Risk: ${analysisResult.workZone.riskScore}/10)`);
      }

      if (!analysisResult.success) {
        results.errors++;
        console.error(`[Scraped Image Analysis] ❌ Analysis failed for Camera ${cameraId}:`, analysisResult.error);
      }

      results.details.push({
        cameraId,
        viewId,
        filename,
        success: analysisResult.success,
        hasWorkZone: analysisResult.hasWorkZone,
        riskScore: analysisResult.workZone?.riskScore || 0
      });

      // Progress callback
      if (progressCallback) {
        progressCallback({
          current: i + 1,
          total: imageFiles.length,
          analyzed: results.analyzed,
          workZonesDetected: results.workZonesDetected,
          percentage: Math.round(((i + 1) / imageFiles.length) * 100)
        });
      }

      // Small delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 1000));

    } catch (error) {
      results.errors++;
      console.error(`[Scraped Image Analysis] ❌ Error analyzing ${filename}:`, error);
      results.details.push({
        cameraId,
        viewId,
        filename,
        success: false,
        error: error.message
      });
    }
  }

  console.log('[Scraped Image Analysis] ✅ Analysis complete!');
  console.log(`  ├─ Total images: ${results.total}`);
  console.log(`  ├─ Analyzed: ${results.analyzed}`);
  console.log(`  ├─ Work zones detected: ${results.workZonesDetected}`);
  console.log(`  ├─ Errors: ${results.errors}`);
  console.log(`  └─ Skipped: ${results.skipped}`);

  // Generate comprehensive report
  const report = generateCollectionRunReport(results);
  saveCollectionRunReport(report);

  // Display report link
  console.log('\n' + '='.repeat(70));
  console.log('📊 COLLECTION RUN REPORT GENERATED');
  console.log('='.repeat(70));
  console.log('📄 View detailed report at: http://localhost:8200/collection-run-report.html');
  console.log('📥 Export options: JSON, CSV, or copy to clipboard');
  console.log('='.repeat(70) + '\n');

  return results;
}

/**
 * Get list of scraped images from manifest.json
 * The manifest is generated by the Python scraper or generate_manifest.py
 *
 * @returns {Promise<Array>} List of image metadata
 */
async function getScrapedImageList() {
  const basePath = import.meta.env.BASE_URL || '/';

  try {
    // Load manifest generated by Python scraper
    const manifestUrl = `${basePath}camera_images/manifest.json`;
    console.log('[Scraped Image Analysis] Loading manifest from:', manifestUrl);

    const response = await fetch(manifestUrl);
    if (!response.ok) {
      throw new Error(`Failed to load manifest: ${response.status}`);
    }

    const manifest = await response.json();
    console.log(`[Scraped Image Analysis] ✅ Loaded manifest with ${manifest.length} images`);

    return manifest;
  } catch (error) {
    console.error('[Scraped Image Analysis] ❌ Failed to load manifest:', error);
    console.warn('[Scraped Image Analysis] Falling back to empty list');
    return [];
  }
}

/**
 * Check if scraped images exist and need analysis
 *
 * @param {Array} cameras - Camera metadata
 * @returns {Promise<Object>} Status information
 */
export async function checkScrapedImagesStatus(cameras) {
  const imageFiles = await getScrapedImageList();

  const status = {
    totalImages: imageFiles.length,
    needsAnalysis: 0,
    alreadyAnalyzed: 0
  };

  for (const imageFile of imageFiles) {
    const { cameraId, viewId } = imageFile;

    if (hasWorkZoneInView(viewId)) {
      status.alreadyAnalyzed++;
    } else {
      status.needsAnalysis++;
    }
  }

  console.log('[Scraped Image Analysis] Status check:', status);

  return status;
}

/**
 * Auto-start analysis on app initialization
 * Call this from App.jsx on mount
 *
 * @param {Array} cameras - Camera metadata
 * @returns {Promise<void>}
 */
export async function autoAnalyzeScrapedImages(cameras) {
  // Check if analysis is needed
  const status = await checkScrapedImagesStatus(cameras);

  if (status.needsAnalysis === 0) {
    console.log('[Scraped Image Analysis] ✅ All scraped images already analyzed');
    return;
  }

  console.log(`[Scraped Image Analysis] 🚀 Starting auto-analysis of ${status.needsAnalysis} images`);

  // Start analysis in background
  analyzeScrapedImages(cameras, (progress) => {
    console.log(`[Scraped Image Analysis] Progress: ${progress.percentage}% (${progress.current}/${progress.total})`);
  }).then(results => {
    console.log('[Scraped Image Analysis] 🎉 Auto-analysis complete!', results);
  }).catch(error => {
    console.error('[Scraped Image Analysis] ❌ Auto-analysis failed:', error);
  });
}

/**
 * Generate comprehensive collection run report
 *
 * @param {Object} results - Analysis results
 * @returns {Object} Formatted report
 */
function generateCollectionRunReport(results) {
  // Get work zone history from localStorage
  const workZones = JSON.parse(localStorage.getItem('qew_workzone_camera_history') || '[]');

  // Calculate summary statistics
  const summary = {
    timestamp: new Date().toISOString(),
    runDate: new Date().toLocaleString(),
    totalImages: results.total,
    imagesAnalyzed: results.analyzed,
    imagesSkipped: results.skipped,
    errors: results.errors,
    workZonesDetected: results.workZonesDetected,
    successRate: results.total > 0 ? Math.round((results.analyzed / results.total) * 100) : 0,
    detectionRate: results.analyzed > 0 ? Math.round((results.workZonesDetected / results.analyzed) * 100) : 0
  };

  // Calculate risk statistics
  const riskStats = {
    highRisk: workZones.filter(wz => wz.riskScore >= 7).length,
    mediumRisk: workZones.filter(wz => wz.riskScore >= 4 && wz.riskScore < 7).length,
    lowRisk: workZones.filter(wz => wz.riskScore < 4).length,
    averageRiskScore: workZones.length > 0
      ? (workZones.reduce((sum, wz) => sum + wz.riskScore, 0) / workZones.length).toFixed(2)
      : 0,
    totalWorkers: workZones.reduce((sum, wz) => sum + (wz.workers || 0), 0),
    totalVehicles: workZones.reduce((sum, wz) => sum + (wz.vehicles || 0), 0)
  };

  // Breakdown by camera
  const cameraBreakdown = {};
  results.details.forEach(detail => {
    if (!cameraBreakdown[detail.cameraId]) {
      cameraBreakdown[detail.cameraId] = {
        cameraId: detail.cameraId,
        analyzed: 0,
        workZones: 0,
        errors: 0
      };
    }

    if (detail.success) {
      cameraBreakdown[detail.cameraId].analyzed++;
      if (detail.hasWorkZone) {
        cameraBreakdown[detail.cameraId].workZones++;
      }
    } else {
      cameraBreakdown[detail.cameraId].errors++;
    }
  });

  const report = {
    reportId: `run-${Date.now()}`,
    generatedAt: summary.timestamp,
    summary,
    riskStatistics: riskStats,
    cameraBreakdown: Object.values(cameraBreakdown),
    detectedWorkZones: workZones,
    detailedResults: results.details
  };

  return report;
}

/**
 * Save collection run report to localStorage
 *
 * @param {Object} report - Report to save
 */
function saveCollectionRunReport(report) {
  try {
    // Get existing reports
    const reports = JSON.parse(localStorage.getItem('qew_collection_run_reports') || '[]');

    // Add new report
    reports.push(report);

    // Keep only last 10 reports to avoid storage limits
    const recentReports = reports.slice(-10);

    // Save to localStorage
    localStorage.setItem('qew_collection_run_reports', JSON.stringify(recentReports));

    // Also save as "latest report" for quick access
    localStorage.setItem('qew_latest_collection_run', JSON.stringify(report));

    console.log(`[Scraped Image Analysis] 💾 Report saved (ID: ${report.reportId})`);
  } catch (error) {
    console.error('[Scraped Image Analysis] ❌ Failed to save report:', error);
  }
}

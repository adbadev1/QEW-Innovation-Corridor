// QEW Innovation Corridor - REAL DATA ONLY
// Burlington to Toronto (40km corridor)
export const QEW_ROUTE = {
  burlington: [43.3300, -79.8000],  // Burlington - Highway 403 junction
  toronto: [43.6395, -79.3950],      // Toronto - Gardiner Expressway junction
  center: [43.4848, -79.5975],       // Center point for map display
  zoom: 11
};

// NOTE: All camera data is REAL and loaded from:
// public/camera_scraper/qew_cameras_with_images.json
// - 46 real COMPASS cameras from 511ON
// - Real GPS coordinates
// - Real collected images
// - Real AI analysis from Gemini 2.0 Flash

// NOTE: All work zones are detected by REAL AI Vision analysis
// See: MLValidationPanel.jsx for Gemini 2.0 Flash detection results
// No mock/simulated work zones - only AI-detected from real camera images

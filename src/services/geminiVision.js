/**
 * Gemini Vision API Service
 *
 * AI-powered work zone safety analysis using Google Gemini 2.0 Flash
 * Analyzes highway camera images for MTO BOOK 7 compliance
 * Integrated with vRSU (Virtual Roadside Unit) for V2X broadcasting
 */

import { GoogleGenerativeAI } from '@google/generative-ai';
import { broadcastIfHighRisk } from './vRSUClient.js';

// Initialize Gemini API
const genAI = new GoogleGenerativeAI(import.meta.env.VITE_GEMINI_API_KEY);

/**
 * Convert File object to base64 string
 */
async function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => {
      const base64 = reader.result.split(',')[1]; // Remove data:image/jpeg;base64, prefix
      resolve(base64);
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

/**
 * Analyze work zone image for safety compliance
 *
 * @param {File} imageFile - JPEG/PNG image file from camera or upload
 * @param {Object} metadata - Optional metadata for tracking source (COMPASS vs SYNTHETIC)
 * @returns {Promise<Object>} Work zone analysis results
 */
export async function analyzeWorkZoneImage(imageFile, metadata = {}) {
  try {
    // Get Gemini model (use 2.0 Flash for speed, or 1.5 Pro for accuracy)
    const model = genAI.getGenerativeModel({
      model: import.meta.env.VITE_GEMINI_MODEL || 'gemini-2.0-flash-exp'
    });

    // Convert image to base64
    const imageBase64 = await fileToBase64(imageFile);

    // Construct the prompt for MTO BOOK 7 compliance analysis
    const prompt = `You are an MTO-certified work zone safety inspector analyzing this highway construction zone image.

Perform a comprehensive safety analysis following Ontario's MTO BOOK 7 standards (Ontario Traffic Manual - Temporary Conditions).

ANALYZE THE IMAGE FOR:

1. WORK ZONE PRESENCE
   - Is there an active construction work zone visible? (yes/no)
   - Confidence level (0-100%)

2. WORKER SAFETY ELEMENTS (if work zone present)
   - How many workers are visible?
   - Are they wearing high-visibility clothing? (fluorescent orange/yellow)
   - Are hard hats visible?
   - Distance of workers from active traffic lanes (meters estimate)
   - Are safety barriers present between workers and traffic?

3. TRAFFIC CONTROL DEVICES
   - Are advance warning signs visible?
   - Are channelizing devices present? (cones, barrels)
   - Is an arrow board visible?
   - Are reduced speed limit signs posted?

4. VEHICLE AND EQUIPMENT SAFETY
   - Are construction vehicles present?
   - Do vehicles have flashing amber lights?
   - Is shadow vehicle protecting workers?
   - Is equipment positioned safely?

5. RISK ASSESSMENT
   - Calculate risk score (1-10 scale)
     * 1-3: COMPLIANT (all safety measures present)
     * 4-6: MINOR NON-COMPLIANCE (1-2 issues)
     * 7-8: MAJOR NON-COMPLIANCE (multiple violations)
     * 9-10: CRITICAL VIOLATION (imminent danger)

6. MTO BOOK 7 COMPLIANCE
   - List any violations detected
   - Identify specific hazards

7. RECOMMENDATIONS
   - Immediate actions required (if risk score ≥ 7)
   - Long-term improvements

OUTPUT FORMAT (JSON only, no markdown):
{
  "hasWorkZone": boolean,
  "confidence": 0.0-1.0,
  "riskScore": 1-10,
  "workers": number,
  "vehicles": number,
  "barriers": boolean,
  "highVisClothing": boolean,
  "hardHats": boolean,
  "workerDistance": number (meters),
  "advanceWarnings": boolean,
  "arrowBoard": boolean,
  "flashingLights": boolean,
  "hazards": ["hazard1", "hazard2", ...],
  "violations": ["violation1", "violation2", ...],
  "mtoBookCompliance": boolean,
  "recommendations": ["action1", "action2", ...],
  "analysisTimestamp": ISO8601 string
}

Respond ONLY with valid JSON. No markdown, no code blocks, just raw JSON.`;

    // Call Gemini API with image and prompt
    const result = await model.generateContent([
      prompt,
      {
        inlineData: {
          mimeType: imageFile.type,
          data: imageBase64
        }
      }
    ]);

    const response = await result.response;
    const text = response.text();

    // Parse JSON response
    // Gemini sometimes wraps in ```json, so clean it
    const cleanedText = text
      .replace(/```json\n?/g, '')
      .replace(/```\n?/g, '')
      .trim();

    const analysis = JSON.parse(cleanedText);

    // Add metadata
    analysis.analysisTimestamp = new Date().toISOString();
    analysis.model = import.meta.env.VITE_GEMINI_MODEL || 'gemini-2.0-flash-exp';

    // Add source tracking (COMPASS real vs SYNTHETIC test)
    analysis.synthetic = metadata.synthetic || false;
    analysis.source = metadata.source || 'COMPASS';

    // Include full synthetic metadata if present
    if (metadata.synthetic && metadata) {
      analysis.syntheticMetadata = metadata;
    }

    return analysis;

  } catch (error) {
    console.error('Gemini Vision API Error:', error);

    // Return error response
    return {
      error: true,
      message: error.message || 'Failed to analyze image',
      hasWorkZone: false,
      riskScore: 0,
      confidence: 0
    };
  }
}

/**
 * Batch analyze multiple images (for backend processing)
 *
 * @param {Array<File>} imageFiles - Array of image files
 * @returns {Promise<Array<Object>>} Array of analysis results
 */
export async function batchAnalyzeWorkZones(imageFiles) {
  const results = [];

  for (const imageFile of imageFiles) {
    try {
      const analysis = await analyzeWorkZoneImage(imageFile);
      results.push({
        filename: imageFile.name,
        analysis
      });
    } catch (error) {
      results.push({
        filename: imageFile.name,
        error: error.message
      });
    }
  }

  return results;
}

/**
 * Generate V2X alert message from analysis
 *
 * @param {Object} analysis - Work zone analysis result
 * @param {Object} location - GPS coordinates {lat, lon}
 * @returns {Object} SAE J2735 compatible V2X alert
 */
export function generateV2XAlert(analysis, location) {
  if (!analysis.hasWorkZone) {
    return null;
  }

  let priority, message, speedLimit;

  if (analysis.riskScore >= 9) {
    priority = 'CRITICAL';
    message = 'DANGER: Work zone critical violation. SLOW TO 40 km/h. Workers very close to traffic.';
    speedLimit = 40;
  } else if (analysis.riskScore >= 7) {
    priority = 'MEDIUM';
    message = 'Caution: Work zone non-compliance detected. Reduce speed to 60 km/h. Workers present.';
    speedLimit = 60;
  } else if (analysis.riskScore >= 5) {
    priority = 'LOW';
    message = 'Work zone ahead - Reduced speed recommended';
    speedLimit = 60;
  } else {
    // Compliant work zone - optional informational message
    return null;
  }

  return {
    msgType: analysis.riskScore >= 7 ? 'RoadSideAlert' : 'TravelerInformation',
    priority,
    message,
    typeEvent: analysis.riskScore >= 7 ? 'workZoneHazard' : 'workZone',
    speedLimit,
    location: {
      lat: location.lat,
      lon: location.lon
    },
    distanceToZone: 500, // meters (estimated)
    urgency: analysis.riskScore >= 9 ? 'immediate' : 'normal',
    timestamp: new Date().toISOString()
  };
}

/**
 * Format analysis for display in dashboard
 *
 * NEW: Automatically broadcasts high-risk work zones to vRSU service
 *
 * @param {Object} analysis - Raw analysis from Gemini
 * @param {string} cameraId - Camera ID
 * @param {Object} location - GPS coordinates {lat, lon}
 * @param {Function} registerBroadcast - Optional V2X broadcast registration callback
 * @returns {Object} Formatted work zone object
 */
export async function formatWorkZoneForDashboard(analysis, cameraId, location, registerBroadcast = null) {
  if (!analysis.hasWorkZone) {
    return null;
  }

  const workZone = {
    id: `WZ_${cameraId}_${Date.now()}`,
    lat: location.lat,
    lon: location.lon,
    cameraId,
    riskScore: analysis.riskScore,
    status: analysis.riskScore >= 7 ? 'high-risk' : analysis.riskScore >= 5 ? 'medium-risk' : 'compliant',
    workers: analysis.workers,
    vehicles: analysis.vehicles,
    equipment: 0, // Not detected by current model
    barriers: analysis.barriers,
    hazards: analysis.hazards,
    violations: analysis.violations,
    recommendations: analysis.recommendations,
    mtoBookCompliance: analysis.mtoBookCompliance,
    confidence: analysis.confidence,
    detectedAt: analysis.analysisTimestamp,
    v2xAlert: generateV2XAlert(analysis, location),
    vrsuBroadcast: null, // Will be populated if broadcast succeeds
    // Source tracking (COMPASS real vs SYNTHETIC test)
    synthetic: analysis.synthetic || false,
    source: analysis.source || 'COMPASS'
  };

  // Include full synthetic metadata if present
  if (analysis.syntheticMetadata) {
    workZone.syntheticMetadata = analysis.syntheticMetadata;
  }

  // Automatically broadcast to vRSU if risk score >= 5
  // This triggers V2X messages to connected vehicles
  try {
    const broadcastResult = await broadcastIfHighRisk(workZone, 5);

    if (broadcastResult) {
      workZone.vrsuBroadcast = {
        success: true,
        messageId: broadcastResult.message_id,
        messageType: broadcastResult.message_type,
        timestamp: broadcastResult.timestamp,
        broadcastStatus: broadcastResult.broadcast_status
      };

      console.log(`📡 vRSU Broadcast: ${broadcastResult.message_type} message sent (ID: ${broadcastResult.message_id})`);

      // Register broadcast in V2X context so vehicles can receive alerts
      if (registerBroadcast && typeof registerBroadcast === 'function') {
        registerBroadcast(workZone, broadcastResult);
        console.log(`📡 V2X Context: Broadcast registered for vehicle alerts`);
      }
    } else {
      console.log(`📊 Work zone below broadcast threshold (risk: ${analysis.riskScore}/10)`);
    }
  } catch (error) {
    console.error('⚠️ vRSU broadcast failed:', error.message);
    workZone.vrsuBroadcast = {
      success: false,
      error: error.message
    };
  }

  return workZone;
}

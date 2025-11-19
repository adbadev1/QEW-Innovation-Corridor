/**
 * Diagnostic Tool: Test Gemini AI Detection on Specific Camera Images
 *
 * Tests camera images 465 and 468 to diagnose why visible construction zones
 * are not being detected by the work zone analysis system.
 */

import { GoogleGenerativeAI } from '@google/generative-ai';
import fs from 'fs';

// Read API key from .env file
function getApiKey() {
  try {
    const envContent = fs.readFileSync('.env', 'utf8');
    const match = envContent.match(/VITE_GEMINI_API_KEY=(.+)/);
    return match ? match[1].trim() : null;
  } catch (error) {
    console.error('❌ Could not read .env file');
    process.exit(1);
  }
}

const API_KEY = getApiKey();
if (!API_KEY) {
  console.error('❌ VITE_GEMINI_API_KEY not found in .env file');
  process.exit(1);
}

const genAI = new GoogleGenerativeAI(API_KEY);

async function analyzeImage(imagePath, cameraId) {
  console.log(`\n${'='.repeat(80)}`);
  console.log(`🔍 ANALYZING CAMERA ${cameraId}`);
  console.log(`   Image: ${imagePath}`);
  console.log(`${'='.repeat(80)}\n`);

  try {
    // Read image and convert to base64
    const imageBuffer = fs.readFileSync(imagePath);
    const imageBase64 = imageBuffer.toString('base64');

    // Get Gemini model
    const model = genAI.getGenerativeModel({
      model: 'gemini-2.0-flash-exp'
    });

    // Use the EXACT same prompt as production
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

    // Call Gemini API
    console.log('⏳ Calling Gemini API...\n');
    const startTime = Date.now();

    const result = await model.generateContent([
      prompt,
      {
        inlineData: {
          mimeType: 'image/jpeg',
          data: imageBase64
        }
      }
    ]);

    const response = await result.response;
    const text = response.text();
    const duration = Date.now() - startTime;

    // Parse JSON response
    const cleanedText = text
      .replace(/```json\n?/g, '')
      .replace(/```\n?/g, '')
      .trim();

    const analysis = JSON.parse(cleanedText);

    // Display results
    console.log(`✅ ANALYSIS COMPLETE (${duration}ms)\n`);
    console.log(`${'─'.repeat(80)}`);
    console.log(`📊 RESULTS:`);
    console.log(`${'─'.repeat(80)}\n`);

    console.log(`Work Zone Detected: ${analysis.hasWorkZone ? '🚧 YES' : '❌ NO'}`);
    console.log(`Confidence: ${(analysis.confidence * 100).toFixed(0)}%`);
    console.log(`Risk Score: ${analysis.riskScore}/10`);
    console.log(`Workers: ${analysis.workers || 0}`);
    console.log(`Vehicles: ${analysis.vehicles || 0}`);
    console.log(`Barriers: ${analysis.barriers ? 'YES' : 'NO'}`);
    console.log(`Flashing Lights: ${analysis.flashingLights ? 'YES' : 'NO'}`);
    console.log(`High-Vis Clothing: ${analysis.highVisClothing ? 'YES' : 'NO'}`);
    console.log(`MTO BOOK 7 Compliant: ${analysis.mtoBookCompliance ? 'YES' : 'NO'}`);

    if (analysis.hazards && analysis.hazards.length > 0) {
      console.log(`\n⚠️ HAZARDS DETECTED:`);
      analysis.hazards.forEach((hazard, i) => {
        console.log(`   ${i + 1}. ${hazard}`);
      });
    }

    if (analysis.violations && analysis.violations.length > 0) {
      console.log(`\n🚨 VIOLATIONS DETECTED:`);
      analysis.violations.forEach((violation, i) => {
        console.log(`   ${i + 1}. ${violation}`);
      });
    }

    if (analysis.recommendations && analysis.recommendations.length > 0) {
      console.log(`\n💡 RECOMMENDATIONS:`);
      analysis.recommendations.forEach((rec, i) => {
        console.log(`   ${i + 1}. ${rec}`);
      });
    }

    console.log(`\n${'─'.repeat(80)}`);
    console.log(`RAW JSON RESPONSE:`);
    console.log(`${'─'.repeat(80)}\n`);
    console.log(JSON.stringify(analysis, null, 2));
    console.log(`\n${'='.repeat(80)}\n`);

    return analysis;

  } catch (error) {
    console.error(`\n❌ ERROR ANALYZING CAMERA ${cameraId}:`, error.message);
    console.error(error);
    return null;
  }
}

// Run diagnostic tests
async function runDiagnostics() {
  console.log('\n');
  console.log('╔' + '═'.repeat(78) + '╗');
  console.log('║' + ' '.repeat(15) + 'GEMINI AI WORK ZONE DETECTION DIAGNOSTIC' + ' '.repeat(22) + '║');
  console.log('║' + ' '.repeat(20) + 'Camera 465 & 468 Analysis Test' + ' '.repeat(27) + '║');
  console.log('╚' + '═'.repeat(78) + '╝');

  // Test Camera 465 (Southdown Rd/Erin Mills Pkwy - visible construction)
  const result465 = await analyzeImage('/tmp/camera_465_test.jpg', '465');

  // Test Camera 468 (E/of Mississauga Rd - poor visibility)
  const result468 = await analyzeImage('/tmp/camera_468_test.jpg', '468');

  // Summary
  console.log('\n');
  console.log('╔' + '═'.repeat(78) + '╗');
  console.log('║' + ' '.repeat(30) + 'DIAGNOSTIC SUMMARY' + ' '.repeat(30) + '║');
  console.log('╚' + '═'.repeat(78) + '╝\n');

  if (result465) {
    console.log(`Camera 465: ${result465.hasWorkZone ? '✅ DETECTED' : '❌ NOT DETECTED'} (confidence: ${(result465.confidence * 100).toFixed(0)}%)`);
    if (!result465.hasWorkZone) {
      console.log(`   ⚠️ ISSUE: Human can see construction zone, but Gemini did not detect it`);
      console.log(`   📝 User report: Yellow barrier tape, orange lights, closed highway visible`);
    }
  }

  if (result468) {
    console.log(`Camera 468: ${result468.hasWorkZone ? '✅ DETECTED' : '❌ NOT DETECTED'} (confidence: ${(result468.confidence * 100).toFixed(0)}%)`);
    if (!result468.hasWorkZone) {
      console.log(`   ℹ️ Poor image quality (lens flare, low visibility) may affect detection`);
    }
  }

  console.log('\n');
}

// Execute diagnostics
runDiagnostics().catch(console.error);

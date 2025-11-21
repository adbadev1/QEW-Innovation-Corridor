#!/usr/bin/env node
/**
 * Real-time Auto-Analysis Monitor
 * Tracks progress by checking localStorage via browser automation
 */

const puppeteer = require('puppeteer');

async function monitorAnalysis() {
  console.log('🔍 Starting Auto-Analysis Monitor...\n');
  console.log('Dashboard: http://localhost:8200');
  console.log('Monitoring progress every 5 seconds...\n');

  let browser;
  try {
    browser = await puppeteer.launch({
      headless: false,
      defaultViewport: { width: 1920, height: 1080 }
    });

    const page = await browser.newPage();

    // Enable console logging from browser
    page.on('console', msg => {
      const text = msg.text();
      if (text.includes('[Auto Analysis]') ||
          text.includes('[Gemini Vision]') ||
          text.includes('[Rate Limiter]') ||
          text.includes('Work zone')) {
        console.log(`📝 ${text}`);
      }
    });

    // Navigate to dashboard
    console.log('📂 Loading dashboard...\n');
    await page.goto('http://localhost:8200', { waitUntil: 'networkidle0' });

    console.log('✅ Dashboard loaded\n');
    console.log('='.repeat(60));

    let lastCount = 0;
    let noChangeCount = 0;

    // Monitor progress
    while (true) {
      await new Promise(resolve => setTimeout(resolve, 5000));

      // Check localStorage
      const status = await page.evaluate(() => {
        const history = JSON.parse(localStorage.getItem('qew_workzone_camera_history') || '[]');
        const manifest = 50; // Known total from manifest.json

        return {
          workZones: history.length,
          total: manifest,
          percentage: Math.round((history.length / manifest) * 100),
          details: history.map(wz => ({
            cameraId: wz.cameraId,
            viewId: wz.viewId,
            location: wz.location,
            riskScore: wz.riskScore
          }))
        };
      });

      // Display progress
      console.clear();
      console.log('🚧 QEW Auto-Analysis Monitor\n');
      console.log('='.repeat(60));
      console.log(`📊 Progress: ${status.workZones}/50 images analyzed`);
      console.log(`🚧 Work Zones Detected: ${status.workZones}`);
      console.log(`📈 Percentage: ${status.percentage}%`);
      console.log('='.repeat(60));

      if (status.workZones > lastCount) {
        console.log(`\n✅ NEW WORK ZONE DETECTED! (Total: ${status.workZones})\n`);
        lastCount = status.workZones;
        noChangeCount = 0;
      } else {
        noChangeCount++;
      }

      // Show detected work zones
      if (status.details.length > 0) {
        console.log('\n🚧 Detected Work Zones:');
        console.log('-'.repeat(60));
        status.details.slice(-5).forEach(wz => {
          console.log(`  Camera ${wz.cameraId} (View ${wz.viewId}): ${wz.location}`);
          console.log(`    Risk Score: ${wz.riskScore}/10`);
        });
        if (status.details.length > 5) {
          console.log(`  ... and ${status.details.length - 5} more`);
        }
      }

      // Check if complete or stalled
      if (status.workZones >= 50) {
        console.log('\n' + '='.repeat(60));
        console.log('🎉 ANALYSIS COMPLETE!');
        console.log(`✅ Total Work Zones Detected: ${status.workZones}`);
        console.log('='.repeat(60));
        break;
      }

      if (noChangeCount >= 12) {
        console.log('\n⚠️ No progress for 60 seconds - analysis may be stalled');
        console.log('Check browser console for errors');
        break;
      }
    }

  } catch (error) {
    console.error('❌ Monitor error:', error.message);
  } finally {
    if (browser) {
      // await browser.close();
      console.log('\n📊 Browser left open for inspection');
    }
  }
}

monitorAnalysis().catch(console.error);

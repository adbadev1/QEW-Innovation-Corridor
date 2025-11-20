#!/usr/bin/env node
/**
 * Test Gemini API Quota Status
 * Verifies if upgrade to paid tier is active
 */

import { GoogleGenerativeAI } from '@google/generative-ai';

const apiKey = process.env.VITE_GEMINI_API_KEY || process.env.GEMINI_API_KEY;

if (!apiKey) {
  console.error('❌ No API key found.');
  console.error('Set VITE_GEMINI_API_KEY or GEMINI_API_KEY environment variable');
  process.exit(1);
}

console.log('🔍 Testing Gemini API quota status...\n');
console.log(`API Key: ${apiKey.substring(0, 10)}...${apiKey.substring(apiKey.length - 4)}\n`);

const genAI = new GoogleGenerativeAI(apiKey);

async function testModel(modelName) {
  try {
    console.log(`Testing ${modelName}...`);
    const model = genAI.getGenerativeModel({ model: modelName });

    const startTime = Date.now();
    const result = await model.generateContent('Reply with just the word SUCCESS');
    const duration = Date.now() - startTime;

    const response = await result.response;
    const text = response.text();

    console.log(`✅ ${modelName}: ${text.substring(0, 30)} (${duration}ms)\n`);
    return true;

  } catch (error) {
    if (error.message.includes('429')) {
      console.log(`⚠️  ${modelName}: RATE LIMIT (free tier quota)\n`);
      return false;
    } else if (error.message.includes('404')) {
      console.log(`❌ ${modelName}: Model not available\n`);
      return false;
    } else {
      console.log(`❌ ${modelName}: ${error.message}\n`);
      return false;
    }
  }
}

async function rapidFireTest() {
  console.log('🚀 RAPID FIRE TEST (15 requests in 10 seconds)\n');
  console.log('This tests if you have paid tier rate limits...\n');

  const model = genAI.getGenerativeModel({ model: 'gemini-1.5-flash' });
  let successCount = 0;
  let rateLimitHit = false;

  const startTime = Date.now();

  for (let i = 1; i <= 15; i++) {
    try {
      console.log(`Request ${i}/15...`);
      const result = await model.generateContent('Hi');
      await result.response;
      successCount++;
      console.log(`  ✅ Success\n`);
    } catch (error) {
      if (error.message.includes('429')) {
        rateLimitHit = true;
        console.log(`  ⚠️  Rate limit at request ${i}\n`);
        break;
      }
    }
  }

  const duration = Date.now() - startTime;

  console.log('\n' + '='.repeat(60));
  console.log('📊 RESULTS:');
  console.log('='.repeat(60));
  console.log(`Successful requests: ${successCount}/15`);
  console.log(`Time taken: ${(duration / 1000).toFixed(1)}s`);
  console.log(`Rate limit hit: ${rateLimitHit ? 'YES' : 'NO'}`);
  console.log('');

  if (successCount >= 15 && !rateLimitHit) {
    console.log('🎉 PAID TIER CONFIRMED!');
    console.log('   You have high rate limits (2000/min)');
    console.log('   Gemini analysis can continue without restrictions!');
  } else if (successCount >= 10 && rateLimitHit) {
    console.log('⚠️  FREE TIER DETECTED');
    console.log('   Rate limit: 10-15 requests/minute');
    console.log('   Upgrade needed for high-volume analysis');
  } else {
    console.log('❓ UNCLEAR - May need to check Google Cloud Console');
  }
  console.log('='.repeat(60));
}

async function main() {
  // Test individual models
  const models = ['gemini-2.0-flash-exp', 'gemini-1.5-flash'];

  console.log('📋 STEP 1: Test model availability\n');
  for (const modelName of models) {
    await testModel(modelName);
  }

  console.log('\n📋 STEP 2: Rapid fire test\n');
  await rapidFireTest();
}

main().catch(error => {
  console.error('\n❌ Test failed:', error.message);
  process.exit(1);
});

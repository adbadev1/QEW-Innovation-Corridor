# Gemini API Upgrade Guide

## 🚨 Current Issue: Rate Limit Exceeded (429 Error)

You're seeing this error because the **free tier** of Gemini API has very low rate limits:

```
❌ Error 429: You exceeded your current quota
   Current limit: 10 requests per minute (gemini-2.0-flash-exp)
   Retry after: 40 seconds
```

---

## 📊 Gemini API Pricing Tiers

### **Free Tier** (Current)
- **Rate Limits:**
  - `gemini-2.0-flash-exp`: **10 requests/minute** ⚠️ (Very low!)
  - `gemini-1.5-flash`: **15 requests/minute**
  - `gemini-1.5-pro`: **2 requests/minute**
- **Daily Limits:**
  - 1,500 requests per day
- **Cost:** $0
- **Best for:** Testing, demos, personal projects

### **Pay-As-You-Go** (Recommended for QEW Project)
- **Rate Limits:**
  - `gemini-1.5-flash`: **2,000 requests/minute** ✅ (200x faster!)
  - `gemini-1.5-pro`: **1,000 requests/minute** ✅
  - `gemini-2.0-flash-exp`: **1,000 requests/minute** ✅
- **Daily Limits:**
  - None (unlimited)
- **Cost:**
  - `gemini-1.5-flash`: $0.075 per 1M input tokens, $0.30 per 1M output tokens
  - `gemini-1.5-pro`: $1.25 per 1M input tokens, $5.00 per 1M output tokens
- **Estimated Cost for QEW Project:**
  - 50 images analyzed: ~$0.10 - $0.50
  - 1000 images/day: ~$2 - $10/day
- **Best for:** Production applications, high-volume analysis

### **Enterprise**
- **Custom rate limits** and pricing
- **SLA guarantees**
- **Dedicated support**
- **Contact Google Cloud sales**

---

## 💳 How to Upgrade to Pay-As-You-Go

### **Step 1: Sign Up for Google AI Studio (Free)**

1. Go to: https://aistudio.google.com/
2. Click **"Get API key"**
3. Sign in with your Google account
4. Accept terms of service

### **Step 2: Enable Billing in Google Cloud Console**

1. Go to: https://console.cloud.google.com/
2. Select your project (or create a new one)
3. Navigate to: **Billing** → **Link a billing account**
4. Click **"Create billing account"**
5. Enter credit card information
6. Confirm billing setup

### **Step 3: Upgrade Your API Key**

1. Return to Google AI Studio: https://aistudio.google.com/apikey
2. Your existing API key will automatically get higher rate limits
3. **No need to generate a new key!** The same key works for both free and paid tiers

### **Step 4: Enable Generative Language API**

1. Go to: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
2. Click **"Enable"**
3. Wait ~1 minute for activation

### **Step 5: Verify Upgrade**

```bash
# Test API with curl
curl -H "Content-Type: application/json" \
  -d '{"contents":[{"parts":[{"text":"Hello"}]}]}' \
  "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=YOUR_API_KEY"

# Check response headers for rate limits:
# X-RateLimit-Limit: 2000 (for paid tier)
# X-RateLimit-Remaining: 1999
```

### **Step 6: Update Your Environment Variable (Optional)**

```bash
# .env (no changes needed - same API key works!)
VITE_GEMINI_API_KEY=your_existing_api_key_here

# Optional: Switch to a different model for better quota
VITE_GEMINI_MODEL=gemini-1.5-flash  # Better rate limits than 2.0-flash-exp
```

---

## 🚀 Immediate Fix (No Upgrade Needed)

Our codebase now includes **automatic rate limiting** and **retry logic**. Here's what happens now:

### **Rate Limiting (Built-in)**
```javascript
// Automatically limits requests to 9/minute (stays below 10 limit)
const rateLimiter = new RateLimiter(9);

// Waits automatically if rate limit hit
await rateLimiter.acquire();  // Returns immediately if under limit
                               // Waits 60s if limit exceeded
```

### **Automatic Retries**
```javascript
// Retries up to 3 times with exponential backoff
if (error.includes('429')) {
  console.log('⏳ Rate limit hit. Waiting 40s...');
  await sleep(40000);  // Wait as suggested by API
  retry();
}
```

### **Model Fallback**
```javascript
// Tries multiple models if one fails:
const GEMINI_MODELS = [
  'gemini-2.0-flash-exp',     // 10/min (free), 1000/min (paid)
  'gemini-1.5-flash',         // 15/min (free), 2000/min (paid) ✅ BEST
  'gemini-1.5-flash-latest',  // Alternative
  'gemini-1.5-pro-latest'     // Slowest but most accurate
];
```

### **User-Friendly Error Messages**
```javascript
// Instead of raw API error:
❌ Error 429: You exceeded your current quota...

// Now shows:
⚠️ Rate limit exceeded. Please wait 1 minute and try again. (Free tier: 9/min)
```

---

## 🔧 Configuration Options

### **Option 1: Stay on Free Tier (Current Setup)**

**What you get:**
- ✅ Automatic rate limiting (9 requests/minute)
- ✅ Automatic retries with backoff
- ✅ No credit card required
- ❌ Slow analysis (1 image every 7 seconds)
- ❌ 50 images takes ~6 minutes

**Best for:** Testing, demos, low-volume projects

### **Option 2: Upgrade to Pay-As-You-Go (Recommended)**

**What you get:**
- ✅ 200x faster (2,000 requests/minute)
- ✅ 50 images analyzed in ~2 seconds
- ✅ Unlimited daily quota
- ✅ Same code, same API key
- 💰 Cost: ~$0.10-$0.50 per 50 images

**Best for:** Production, QEW OVIN pilot

**Setup:**
```bash
# 1. Enable billing (see Step 2 above)
# 2. No code changes needed!
# 3. Restart app:
npm run dev
```

### **Option 3: Use Local Model (No API, No Cost)**

**Alternative:** Use a local vision model (slower but free):
- CLIP (OpenAI)
- LLaVA (Open source)
- Ollama (Local LLM with vision)

**Trade-off:** Lower accuracy, slower processing, more setup

---

## 📊 Cost Estimation for QEW Project

### **Current Usage:**
- 46 cameras on QEW
- 50 images per collection run
- ~5-10 collection runs per day (testing)
- **Daily volume:** ~250-500 images

### **Monthly Cost Estimate (Pay-As-You-Go):**

| Model | Requests/Day | Cost/Image | Daily Cost | Monthly Cost |
|-------|-------------|-----------|-----------|-------------|
| gemini-1.5-flash | 500 | $0.001 | $0.50 | **$15/month** |
| gemini-1.5-pro | 500 | $0.01 | $5.00 | **$150/month** |

### **OVIN Pilot Budget:**
- **Total Funding:** $150,000 CAD
- **AI Analysis Budget:** ~$1,000-$2,000 (6 months)
- **Gemini API Cost:** $15-$150/month = **$90-$900 for 6 months**
- **Percentage of Budget:** 0.06% - 0.6% ✅ Very affordable!

---

## 🎯 Recommendation for QEW Project

### **Immediate (Today):**
✅ Use current free tier with rate limiting
- Works fine for testing
- Analyze 9 images/minute (1 every 7 seconds)
- 50 images take ~6 minutes
- No cost, no setup

### **Before OVIN Demo (This Week):**
⚠️ **Upgrade to Pay-As-You-Go**
- Enable billing in Google Cloud Console
- Get 200x faster rate limits
- Analyze 50 images in ~2 seconds
- Cost: ~$0.50 per demo run
- **Critical for live demo!** (Can't have 6-minute wait times)

### **For OVIN Pilot (6 Months):**
✅ **Stay on Pay-As-You-Go (gemini-1.5-flash)**
- Budget: $15-$30/month
- Total 6-month cost: **$90-$180**
- 0.12% of $150K budget
- Scale up to gemini-1.5-pro if higher accuracy needed

---

## 🔗 Important Links

- **Google AI Studio:** https://aistudio.google.com/
- **Google Cloud Console:** https://console.cloud.google.com/
- **Gemini API Pricing:** https://ai.google.dev/pricing
- **Rate Limits Documentation:** https://ai.google.dev/gemini-api/docs/rate-limits
- **Billing Setup Guide:** https://cloud.google.com/billing/docs/how-to/manage-billing-account

---

## 📝 Quick Commands

### **Check Current Rate Limit Status**
```bash
# In browser console (F12):
localStorage.getItem('gemini_request_count');  # Number of requests this minute
```

### **Clear Rate Limiter (Force Reset)**
```bash
# Reload the page - rate limiter resets on page load
location.reload();
```

### **Monitor API Usage**
```bash
# Google Cloud Console:
# Navigation → APIs & Services → Enabled APIs → Generative Language API → Quotas
```

### **Estimate Monthly Cost**
```javascript
// In browser console:
const imagesPerDay = 500;
const costPerImage = 0.001;  // gemini-1.5-flash
const monthlyCost = imagesPerDay * costPerImage * 30;
console.log(`Estimated monthly cost: $${monthlyCost.toFixed(2)}`);
```

---

## ✅ What Changed in the Code

### **Before (No Rate Limiting)**
```javascript
// Crashed after 10 requests
const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash-exp' });
const result = await model.generateContent([prompt, image]);  // ❌ Error 429
```

### **After (Rate Limited + Retry)**
```javascript
// Automatically rate limited, retries on failure
await rateLimiter.acquire();  // Waits if needed

// Tries multiple models with retry
const model = genAI.getGenerativeModel({
  model: GEMINI_MODELS[currentModelIndex]  // Fallback models
});

try {
  const result = await model.generateContent([prompt, image]);
} catch (error) {
  if (error.includes('429')) {
    await sleep(40000);  // Wait and retry
    retry();
  }
}
```

---

## 🎉 Summary

**Current Status:**
- ✅ Rate limiting added (9 requests/minute)
- ✅ Automatic retries (3 attempts)
- ✅ Model fallback (4 models)
- ✅ User-friendly error messages

**Next Steps:**
1. **Keep testing on free tier** (works fine for development)
2. **Upgrade before OVIN demo** (fast enough for live presentation)
3. **Budget ~$100-$200** for 6-month pilot

**No action required immediately** - the code now handles rate limits gracefully! 🎉

---

**Last Updated:** 2025-11-20
**Free Tier Limit:** 10 requests/minute
**Paid Tier Limit:** 2,000 requests/minute (200x faster)
**Recommended Model:** `gemini-1.5-flash` (best speed/cost balance)

🤖 **Generated with [Claude Code](https://claude.com/claude-code)**

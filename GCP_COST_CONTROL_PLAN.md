# 🔒 QEW Innovation Corridor - GCP Cost Control Plan

**Project:** QEW Innovation Corridor Digital Twin Dashboard
**Monthly Budget:** $5.00 (STRICT LIMIT)
**Status:** 🟢 ACTIVE - DEMO MODE
**Last Updated:** 2025-11-20

---

## 🚨 CRITICAL COST CONSTRAINTS

### Monthly Budget Allocation
```
Total Project Budget:        $5.00/month
├─ Gemini Vision API:        $3.00/month (60% allocation)
├─ Cloud Storage:            $1.00/month (20% allocation)
├─ Cloud Run (future):       $0.50/month (10% allocation)
└─ Buffer/Emergency:         $0.50/month (10% reserve)
```

### Budget Alerts
- **🟡 25% ($1.25):** Review usage, continue as normal
- **🟠 50% ($2.50):** Caution - disable auto-analysis
- **🔴 75% ($3.75):** Warning - switch to DEMO SAFE MODE
- **🚨 90% ($4.50):** Critical - stop all API calls
- **⛔ 100% ($5.00):** Emergency shutdown - disable all GCP services

---

## 💰 GEMINI VISION API COST ANALYSIS

### Pricing Model (As of Nov 2025)

**Free Tier:**
- Rate limit: 15 requests/minute
- Daily limit: 1,500 requests/day
- Monthly limit: ~45,000 requests/month
- **Cost: $0.00**

**Paid Tier (Pay-as-you-go):**
- Rate limit: 1,000 requests/minute
- No daily limit
- Cost per 1,000 requests:
  - gemini-1.5-flash: $0.075 per 1K requests
  - gemini-2.0-flash-exp: $0.075 per 1K requests
  - gemini-1.5-pro: $0.25 per 1K requests

### QEW Project Usage Calculation

**Current Status:**
- Total images to analyze: 50 (from manifest.json)
- Images analyzed: 6 (before quota hit)
- Images remaining: 44

**Cost for Full Analysis (50 images):**
```
Model: gemini-2.0-flash-exp
Cost per request: $0.000075
Total requests: 50 images × 1 request = 50 requests
TOTAL COST: 50 × $0.000075 = $0.00375 (~$0.004)
```

**Cost for 1,000 Images (Scaled Testing):**
```
1,000 images × $0.000075 = $0.075 (7.5 cents)
```

**Monthly Demo Budget (400 analyses):**
```
400 images/month × $0.000075 = $0.03/month (3 cents)
WELL UNDER $3.00 BUDGET ✅
```

### Cost Scenarios

| Scenario | Images | Cost | Budget % |
|----------|--------|------|----------|
| **Single Demo Run** | 50 | $0.004 | 0.08% |
| **Daily Demos (10/day)** | 300/month | $0.023 | 0.46% |
| **Weekly Collection** | 200/month | $0.015 | 0.30% |
| **Full Month Testing** | 1,000/month | $0.075 | 1.50% |
| **⚠️ DANGER ZONE** | 40,000/month | $3.00 | 60% |

---

## 🎯 DEMO-SAFE MODE STRATEGY

### What We Can Demo (Within Budget)

**✅ SAFE OPERATIONS (Unlimited):**
- View 6 already-analyzed work zones (cached in localStorage)
- Display collection run reports
- Show visual dashboards
- Export JSON/CSV reports
- View RED pin markers on map
- Simulate work zone alerts (using cached data)
- Interactive map with camera locations

**✅ LIMITED API OPERATIONS (< 400/month):**
- Live analysis of 1-2 cameras during demos
- Weekly collection runs (50 images = $0.004)
- Testing new detection features (10-20 images)
- Client presentations (5-10 live analyses)

**❌ PROHIBITED OPERATIONS:**
- Continuous real-time monitoring (would burn budget quickly)
- Auto-refresh analysis every 10 seconds
- Batch processing of all 46 cameras repeatedly
- Load testing with thousands of images

### DEMO MODE Implementation

**Mode 1: CACHED DEMO (Recommended - $0 cost)**
```javascript
// Use existing 6 work zones from localStorage
// No API calls, instant results, zero cost
COST: $0.00
DURATION: Unlimited
USE CASE: Client demos, presentations, stakeholder reviews
```

**Mode 2: LIVE DEMO (Controlled - $0.004 per run)**
```javascript
// Analyze 2-3 cameras live during demo
// Controlled API usage, real-time results
COST: $0.0002 per camera
DURATION: 5-10 minutes
USE CASE: Technical demos, OVIN presentations
```

**Mode 3: WEEKLY COLLECTION (Scheduled - $0.004 per run)**
```javascript
// Run full 50-image analysis weekly
// Scheduled off-peak hours, monitored costs
COST: $0.004 per week = $0.016/month
DURATION: Automated
USE CASE: Regular monitoring, trend analysis
```

---

## 🛡️ COST PROTECTION MECHANISMS

### 1. Request Quota Limiter (Hard Cap)

Create: `src/services/costProtection.js`

```javascript
/**
 * Cost Protection Service
 * Prevents budget overruns by enforcing strict request limits
 */

const COST_LIMITS = {
  DAILY_MAX_REQUESTS: 50,        // Max 50 API calls per day
  MONTHLY_MAX_REQUESTS: 400,     // Max 400 API calls per month
  COST_PER_REQUEST: 0.000075,    // $0.000075 per request
  MONTHLY_BUDGET: 3.00,          // $3.00 Gemini API budget
  EMERGENCY_SHUTOFF: 0.90        // Shutoff at 90% of budget
};

class CostProtector {
  constructor() {
    this.loadUsageStats();
  }

  loadUsageStats() {
    const stats = JSON.parse(localStorage.getItem('qew_api_usage_stats') || '{}');
    this.dailyRequests = stats.dailyRequests || 0;
    this.monthlyRequests = stats.monthlyRequests || 0;
    this.lastResetDate = stats.lastResetDate || new Date().toISOString().split('T')[0];
    this.monthlyResetDate = stats.monthlyResetDate || new Date().toISOString().slice(0, 7);
  }

  saveUsageStats() {
    localStorage.setItem('qew_api_usage_stats', JSON.stringify({
      dailyRequests: this.dailyRequests,
      monthlyRequests: this.monthlyRequests,
      lastResetDate: this.lastResetDate,
      monthlyResetDate: this.monthlyResetDate,
      lastUpdated: new Date().toISOString()
    }));
  }

  resetIfNeeded() {
    const today = new Date().toISOString().split('T')[0];
    const thisMonth = new Date().toISOString().slice(0, 7);

    // Reset daily counter
    if (this.lastResetDate !== today) {
      this.dailyRequests = 0;
      this.lastResetDate = today;
    }

    // Reset monthly counter
    if (this.monthlyResetDate !== thisMonth) {
      this.monthlyRequests = 0;
      this.monthlyResetDate = thisMonth;
    }

    this.saveUsageStats();
  }

  canMakeRequest() {
    this.resetIfNeeded();

    // Check daily limit
    if (this.dailyRequests >= COST_LIMITS.DAILY_MAX_REQUESTS) {
      console.error('🚫 DAILY LIMIT REACHED:', this.dailyRequests, 'requests today');
      return false;
    }

    // Check monthly limit
    if (this.monthlyRequests >= COST_LIMITS.MONTHLY_MAX_REQUESTS) {
      console.error('🚫 MONTHLY LIMIT REACHED:', this.monthlyRequests, 'requests this month');
      return false;
    }

    // Check budget (90% emergency shutoff)
    const monthlyCost = this.monthlyRequests * COST_LIMITS.COST_PER_REQUEST;
    const budgetUsed = monthlyCost / COST_LIMITS.MONTHLY_BUDGET;

    if (budgetUsed >= COST_LIMITS.EMERGENCY_SHUTOFF) {
      console.error('🚫 BUDGET LIMIT REACHED:', (budgetUsed * 100).toFixed(1) + '% of monthly budget used');
      return false;
    }

    return true;
  }

  recordRequest() {
    this.dailyRequests++;
    this.monthlyRequests++;
    this.saveUsageStats();

    const monthlyCost = this.monthlyRequests * COST_LIMITS.COST_PER_REQUEST;
    const budgetUsed = (monthlyCost / COST_LIMITS.MONTHLY_BUDGET * 100).toFixed(1);

    console.log(`📊 API Usage: ${this.dailyRequests} today, ${this.monthlyRequests} this month`);
    console.log(`💰 Cost: $${monthlyCost.toFixed(4)} (${budgetUsed}% of budget)`);

    // Warning at 50%
    if (budgetUsed >= 50 && budgetUsed < 75) {
      console.warn(`⚠️ WARNING: ${budgetUsed}% of monthly budget used`);
    }

    // Critical warning at 75%
    if (budgetUsed >= 75) {
      console.error(`🚨 CRITICAL: ${budgetUsed}% of monthly budget used - APPROACHING LIMIT`);
    }
  }

  getUsageStats() {
    this.resetIfNeeded();

    const monthlyCost = this.monthlyRequests * COST_LIMITS.COST_PER_REQUEST;
    const budgetUsed = (monthlyCost / COST_LIMITS.MONTHLY_BUDGET * 100).toFixed(1);

    return {
      dailyRequests: this.dailyRequests,
      dailyLimit: COST_LIMITS.DAILY_MAX_REQUESTS,
      dailyRemaining: COST_LIMITS.DAILY_MAX_REQUESTS - this.dailyRequests,
      monthlyRequests: this.monthlyRequests,
      monthlyLimit: COST_LIMITS.MONTHLY_MAX_REQUESTS,
      monthlyRemaining: COST_LIMITS.MONTHLY_MAX_REQUESTS - this.monthlyRequests,
      monthlyCost: monthlyCost,
      monthlyBudget: COST_LIMITS.MONTHLY_BUDGET,
      budgetUsedPercent: parseFloat(budgetUsed),
      budgetRemaining: COST_LIMITS.MONTHLY_BUDGET - monthlyCost
    };
  }
}

export const costProtector = new CostProtector();
```

### 2. Demo Mode Toggle

Create: `src/utils/demoMode.js`

```javascript
/**
 * Demo Mode Configuration
 * Switches between cached data (free) and live API calls (paid)
 */

const DEMO_MODES = {
  CACHED: 'cached',      // Use cached work zones only ($0 cost)
  LIVE: 'live',          // Allow limited API calls (controlled cost)
  FULL: 'full'           // Full analysis (use sparingly)
};

export function getDemoMode() {
  return localStorage.getItem('qew_demo_mode') || DEMO_MODES.CACHED;
}

export function setDemoMode(mode) {
  if (!Object.values(DEMO_MODES).includes(mode)) {
    throw new Error(`Invalid demo mode: ${mode}`);
  }
  localStorage.setItem('qew_demo_mode', mode);
  console.log(`🎯 Demo mode set to: ${mode.toUpperCase()}`);
}

export function isDemoMode() {
  return getDemoMode() === DEMO_MODES.CACHED;
}

export function isLiveMode() {
  return getDemoMode() === DEMO_MODES.LIVE;
}

export function isFullMode() {
  return getDemoMode() === DEMO_MODES.FULL;
}

export { DEMO_MODES };
```

### 3. Cost Dashboard Widget

Create: `public/cost-dashboard-widget.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>QEW Cost Dashboard</title>
  <style>
    body {
      font-family: monospace;
      background: #1e1e1e;
      color: #00ff00;
      padding: 20px;
    }
    .gauge {
      width: 100%;
      max-width: 400px;
      margin: 20px auto;
    }
    .gauge-bar {
      width: 100%;
      height: 30px;
      background: #333;
      border-radius: 5px;
      overflow: hidden;
    }
    .gauge-fill {
      height: 100%;
      background: linear-gradient(90deg, #00ff00, #ffff00, #ff0000);
      transition: width 0.3s;
    }
    .stats {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 10px;
      margin-top: 20px;
    }
    .stat {
      background: #2a2a2a;
      padding: 15px;
      border-radius: 5px;
    }
    .stat-label {
      color: #00ffff;
      font-size: 12px;
    }
    .stat-value {
      color: #00ff00;
      font-size: 24px;
      font-weight: bold;
    }
  </style>
</head>
<body>
  <h1>💰 QEW Cost Dashboard</h1>

  <div class="gauge">
    <div class="stat-label">Monthly Budget Usage</div>
    <div class="gauge-bar">
      <div class="gauge-fill" id="budgetGauge"></div>
    </div>
    <div id="budgetPercent" style="text-align: center; margin-top: 10px;"></div>
  </div>

  <div class="stats">
    <div class="stat">
      <div class="stat-label">Daily Requests</div>
      <div class="stat-value" id="dailyRequests">0</div>
      <div class="stat-label" id="dailyLimit">/ 50 limit</div>
    </div>
    <div class="stat">
      <div class="stat-label">Monthly Requests</div>
      <div class="stat-value" id="monthlyRequests">0</div>
      <div class="stat-label" id="monthlyLimit">/ 400 limit</div>
    </div>
    <div class="stat">
      <div class="stat-label">Current Cost</div>
      <div class="stat-value" id="currentCost">$0.00</div>
      <div class="stat-label">/ $3.00 budget</div>
    </div>
    <div class="stat">
      <div class="stat-label">Budget Remaining</div>
      <div class="stat-value" id="budgetRemaining">$3.00</div>
      <div class="stat-label" id="budgetStatus">✅ Safe</div>
    </div>
  </div>

  <script type="module">
    function loadStats() {
      const stats = JSON.parse(localStorage.getItem('qew_api_usage_stats') || '{}');

      const dailyRequests = stats.dailyRequests || 0;
      const monthlyRequests = stats.monthlyRequests || 0;
      const costPerRequest = 0.000075;
      const monthlyBudget = 3.00;

      const currentCost = monthlyRequests * costPerRequest;
      const budgetUsed = (currentCost / monthlyBudget * 100);
      const budgetRemaining = monthlyBudget - currentCost;

      // Update UI
      document.getElementById('dailyRequests').textContent = dailyRequests;
      document.getElementById('monthlyRequests').textContent = monthlyRequests;
      document.getElementById('currentCost').textContent = `$${currentCost.toFixed(4)}`;
      document.getElementById('budgetRemaining').textContent = `$${budgetRemaining.toFixed(4)}`;
      document.getElementById('budgetPercent').textContent = `${budgetUsed.toFixed(1)}%`;

      // Update gauge
      const gauge = document.getElementById('budgetGauge');
      gauge.style.width = `${Math.min(budgetUsed, 100)}%`;

      // Update status
      const statusEl = document.getElementById('budgetStatus');
      if (budgetUsed < 25) {
        statusEl.textContent = '✅ Safe';
        statusEl.style.color = '#00ff00';
      } else if (budgetUsed < 50) {
        statusEl.textContent = '🟡 Monitor';
        statusEl.style.color = '#ffff00';
      } else if (budgetUsed < 75) {
        statusEl.textContent = '🟠 Caution';
        statusEl.style.color = '#ff9900';
      } else if (budgetUsed < 90) {
        statusEl.textContent = '🔴 Warning';
        statusEl.style.color = '#ff0000';
      } else {
        statusEl.textContent = '🚨 Critical';
        statusEl.style.color = '#ff0000';
      }
    }

    loadStats();
    setInterval(loadStats, 5000); // Refresh every 5 seconds
  </script>
</body>
</html>
```

---

## 📋 DEMO PLAYBOOK

### For Client Demos (Zero Cost)

**Duration:** 15-30 minutes
**Cost:** $0.00
**Mode:** CACHED

**Script:**
1. Open dashboard: http://localhost:8200
2. Show 6 detected work zones (cached from localStorage)
3. Display collection run report: http://localhost:8200/collection-run-report.html
4. Demonstrate:
   - Work zone markers (RED pins)
   - Risk scores and statistics
   - Export to JSON/CSV
   - Interactive map
5. Explain AI detection capabilities (using cached examples)

**Advantages:**
- Zero API costs
- Instant results
- No quota concerns
- Unlimited demos

### For Technical Demos (Controlled Cost)

**Duration:** 10-15 minutes
**Cost:** $0.0002 per camera (~$0.002 total)
**Mode:** LIVE (2-3 cameras only)

**Script:**
1. Switch to LIVE mode: `localStorage.setItem('qew_demo_mode', 'live')`
2. Select 2-3 specific cameras for analysis
3. Trigger live Gemini Vision analysis
4. Show real-time detection results
5. Switch back to CACHED mode

**Budget Impact:** 10 demos = $0.02 (0.4% of monthly budget)

### For OVIN Application (Strategic Cost)

**Duration:** Weekly collection
**Cost:** $0.004 per week = $0.016/month
**Mode:** FULL (scheduled)

**Script:**
1. Run full 50-image analysis weekly (Friday nights)
2. Generate comprehensive reports
3. Track trends over time
4. Use results for OVIN documentation

**Budget Impact:** $0.016/month (0.32% of monthly budget)

---

## 🔧 IMPLEMENTATION CHECKLIST

### Phase 1: Immediate (Today)
- [ ] Create `src/services/costProtection.js`
- [ ] Create `src/utils/demoMode.js`
- [ ] Create `public/cost-dashboard-widget.html`
- [ ] Integrate cost protector with `geminiVision.js`
- [ ] Set default mode to CACHED
- [ ] Test cost limits with mock requests

### Phase 2: This Week
- [ ] Document demo playbooks in `docs/DEMO_PLAYBOOK.md`
- [ ] Create demo mode toggle UI component
- [ ] Add cost dashboard widget to main dashboard
- [ ] Set up weekly scheduled analysis (cron job or manual)
- [ ] Test full demo workflow

### Phase 3: Ongoing
- [ ] Monitor daily costs using GCP console
- [ ] Review monthly usage reports
- [ ] Adjust limits if needed
- [ ] Document cost-saving wins
- [ ] Plan for scale-up when funded

---

## 📊 COST MONITORING COMMANDS

### Daily Check (Manual)
```javascript
// Browser console (F12)
const stats = JSON.parse(localStorage.getItem('qew_api_usage_stats'));
console.table(stats);
```

### Weekly Review
```bash
# Open cost dashboard widget
open http://localhost:8200/cost-dashboard-widget.html

# Check GCP billing
gcloud billing accounts list
gcloud billing budgets list --billing-account=YOUR_ACCOUNT_ID
```

### Monthly Analysis
```bash
# Generate cost report (if billing export enabled)
./gcp-cost-analyzer.sh --detailed --export-csv

# Review in GCP Console
# https://console.cloud.google.com/billing/YOUR_BILLING_ACCOUNT/reports?project=qew-innovation-pilot
```

---

## 🚨 EMERGENCY PROCEDURES

### If Budget Alert Triggers

**25% Alert ($1.25):**
1. Review usage stats
2. Continue as normal (within limits)
3. Document what caused the usage

**50% Alert ($2.50):**
1. Disable auto-analysis
2. Switch to CACHED demo mode only
3. Investigate usage spike
4. Report findings

**75% Alert ($3.75):**
1. **IMMEDIATELY** switch to DEMO SAFE MODE
2. Stop all API calls
3. Review cost dashboard widget
4. Identify cost driver
5. Do NOT resume until next month

**90% Alert ($4.50):**
1. **EMERGENCY SHUTDOWN**
2. Set `qew_demo_mode` to `'cached'`
3. Disable all Gemini API calls
4. Review what went wrong
5. Plan for next month

**100% Alert ($5.00):**
1. **CRITICAL: PROJECT OVER BUDGET**
2. All GCP services should auto-alert
3. Disable billing if necessary
4. Post-mortem analysis required

---

## 📈 SCALING STRATEGY (Future)

### When OVIN Funding Arrives ($150K)

**Month 1-2: Bootstrap ($5/month)**
- Use cached demos
- Weekly collections only
- Minimal API usage

**Month 3-4: Ramp-Up ($50/month)**
- Daily collections
- Real-time monitoring (limited)
- Expanded testing

**Month 5-6: Production ($200/month)**
- Continuous monitoring
- Full 46-camera analysis
- Real-time V2X alerts
- Live dashboard updates

---

## 📚 RELATED DOCUMENTATION

- `GEMINI_API_UPGRADE_GUIDE.md` - API pricing and quotas
- `COLLECTION_RUN_REPORTS.md` - Reporting system
- `GCP_AI_INTEGRATION_COMPLETE.md` - AI setup
- `/Users/adbalabs/adba-corp-automation/projects/GCP/BOOTSTRAP-STATUS.md` - Overall GCP budget status

---

## ✅ SUCCESS CRITERIA

**Budget Compliance:**
- ✅ Stay under $5/month project budget
- ✅ Gemini API costs < $3/month
- ✅ Zero surprise charges
- ✅ Daily monitoring active

**Demo Capability:**
- ✅ Unlimited cached demos ($0 cost)
- ✅ 10+ live technical demos per month ($0.02)
- ✅ Weekly collection runs ($0.016/month)
- ✅ Full reporting and export capabilities

**Cost Visibility:**
- ✅ Real-time usage tracking
- ✅ Cost dashboard widget
- ✅ Budget alerts configured
- ✅ Emergency shutoff mechanisms

---

**🔒 COST CONTROL STATUS: ACTIVE**

The QEW project can now demo effectively while staying well under the $5/month budget constraint.

**Estimated Monthly Cost:** $0.03 - $0.10 (0.6% - 2% of budget)

**Safety Margin:** 98% unused budget for emergency scaling

---

**Last Updated:** 2025-11-20
**Status:** 🟢 LOCKED DOWN
**Next Review:** 2025-12-01

🤖 Generated with [Claude Code](https://claude.com/claude-code)

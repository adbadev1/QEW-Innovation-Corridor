/**
 * Cost Protection Service
 * Prevents budget overruns by enforcing strict request limits
 *
 * BUDGET CONSTRAINTS:
 * - Monthly Budget: $3.00 for Gemini API
 * - Daily Limit: 50 requests
 * - Monthly Limit: 400 requests
 * - Emergency Shutoff: 90% of budget
 *
 * INTEGRATION:
 * Import this service in geminiVision.js and check canMakeRequest()
 * before each API call.
 */

const COST_LIMITS = {
  DAILY_MAX_REQUESTS: 50,        // Max 50 API calls per day
  MONTHLY_MAX_REQUESTS: 400,     // Max 400 API calls per month
  COST_PER_REQUEST: 0.000075,    // $0.000075 per request (gemini-2.0-flash-exp)
  MONTHLY_BUDGET: 3.00,          // $3.00 Gemini API budget
  EMERGENCY_SHUTOFF: 0.90        // Shutoff at 90% of budget ($2.70)
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
      console.log('[Cost Protection] 🔄 Daily counter reset');
      this.dailyRequests = 0;
      this.lastResetDate = today;
    }

    // Reset monthly counter
    if (this.monthlyResetDate !== thisMonth) {
      console.log('[Cost Protection] 🔄 Monthly counter reset');
      this.monthlyRequests = 0;
      this.monthlyResetDate = thisMonth;
    }

    this.saveUsageStats();
  }

  canMakeRequest() {
    this.resetIfNeeded();

    // Check daily limit
    if (this.dailyRequests >= COST_LIMITS.DAILY_MAX_REQUESTS) {
      console.error('[Cost Protection] 🚫 DAILY LIMIT REACHED:', this.dailyRequests, 'requests today');
      console.error('[Cost Protection] ⏰ Reset at midnight. Switch to CACHED demo mode.');
      return false;
    }

    // Check monthly limit
    if (this.monthlyRequests >= COST_LIMITS.MONTHLY_MAX_REQUESTS) {
      console.error('[Cost Protection] 🚫 MONTHLY LIMIT REACHED:', this.monthlyRequests, 'requests this month');
      console.error('[Cost Protection] ⏰ Reset on 1st of next month. Use CACHED mode only.');
      return false;
    }

    // Check budget (90% emergency shutoff)
    const monthlyCost = this.monthlyRequests * COST_LIMITS.COST_PER_REQUEST;
    const budgetUsed = monthlyCost / COST_LIMITS.MONTHLY_BUDGET;

    if (budgetUsed >= COST_LIMITS.EMERGENCY_SHUTOFF) {
      console.error('[Cost Protection] 🚫 BUDGET LIMIT REACHED:', (budgetUsed * 100).toFixed(1) + '% of monthly budget used');
      console.error('[Cost Protection] 💰 Current cost: $' + monthlyCost.toFixed(4), '/ $' + COST_LIMITS.MONTHLY_BUDGET);
      console.error('[Cost Protection] 🚨 EMERGENCY SHUTOFF ACTIVATED - Switch to CACHED mode');
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

    console.log(`[Cost Protection] 📊 API Usage: ${this.dailyRequests} today, ${this.monthlyRequests} this month`);
    console.log(`[Cost Protection] 💰 Cost: $${monthlyCost.toFixed(4)} (${budgetUsed}% of $${COST_LIMITS.MONTHLY_BUDGET} budget)`);

    // Warning at 25%
    if (budgetUsed >= 25 && budgetUsed < 50) {
      console.warn(`[Cost Protection] 🟡 INFO: ${budgetUsed}% of monthly budget used - monitor usage`);
    }

    // Caution at 50%
    if (budgetUsed >= 50 && budgetUsed < 75) {
      console.warn(`[Cost Protection] 🟠 CAUTION: ${budgetUsed}% of monthly budget used - reduce API calls`);
    }

    // Warning at 75%
    if (budgetUsed >= 75 && budgetUsed < 90) {
      console.warn(`[Cost Protection] 🔴 WARNING: ${budgetUsed}% of monthly budget used - switch to CACHED mode soon`);
    }

    // Critical warning at 90%
    if (budgetUsed >= 90) {
      console.error(`[Cost Protection] 🚨 CRITICAL: ${budgetUsed}% of monthly budget used - APPROACHING LIMIT`);
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
      dailyPercentUsed: ((this.dailyRequests / COST_LIMITS.DAILY_MAX_REQUESTS) * 100).toFixed(1),
      monthlyRequests: this.monthlyRequests,
      monthlyLimit: COST_LIMITS.MONTHLY_MAX_REQUESTS,
      monthlyRemaining: COST_LIMITS.MONTHLY_MAX_REQUESTS - this.monthlyRequests,
      monthlyPercentUsed: ((this.monthlyRequests / COST_LIMITS.MONTHLY_MAX_REQUESTS) * 100).toFixed(1),
      monthlyCost: monthlyCost,
      monthlyBudget: COST_LIMITS.MONTHLY_BUDGET,
      budgetUsedPercent: parseFloat(budgetUsed),
      budgetRemaining: COST_LIMITS.MONTHLY_BUDGET - monthlyCost,
      status: this.getBudgetStatus(parseFloat(budgetUsed)),
      canMakeRequest: this.canMakeRequest()
    };
  }

  getBudgetStatus(budgetUsedPercent) {
    if (budgetUsedPercent < 25) return { level: 'safe', icon: '✅', message: 'Safe' };
    if (budgetUsedPercent < 50) return { level: 'info', icon: '🟡', message: 'Monitor' };
    if (budgetUsedPercent < 75) return { level: 'caution', icon: '🟠', message: 'Caution' };
    if (budgetUsedPercent < 90) return { level: 'warning', icon: '🔴', message: 'Warning' };
    return { level: 'critical', icon: '🚨', message: 'Critical' };
  }

  resetUsageStats() {
    console.warn('[Cost Protection] ⚠️ Resetting usage stats (ADMIN ONLY)');
    this.dailyRequests = 0;
    this.monthlyRequests = 0;
    this.lastResetDate = new Date().toISOString().split('T')[0];
    this.monthlyResetDate = new Date().toISOString().slice(0, 7);
    this.saveUsageStats();
  }

  printUsageReport() {
    const stats = this.getUsageStats();

    console.log('\n' + '='.repeat(60));
    console.log('💰 QEW COST PROTECTION - USAGE REPORT');
    console.log('='.repeat(60));
    console.log(`📅 Date: ${new Date().toLocaleString()}`);
    console.log('');
    console.log('DAILY USAGE:');
    console.log(`  Requests: ${stats.dailyRequests} / ${stats.dailyLimit} (${stats.dailyPercentUsed}%)`);
    console.log(`  Remaining: ${stats.dailyRemaining} requests`);
    console.log('');
    console.log('MONTHLY USAGE:');
    console.log(`  Requests: ${stats.monthlyRequests} / ${stats.monthlyLimit} (${stats.monthlyPercentUsed}%)`);
    console.log(`  Remaining: ${stats.monthlyRemaining} requests`);
    console.log(`  Cost: $${stats.monthlyCost.toFixed(4)} / $${stats.monthlyBudget}`);
    console.log(`  Budget Used: ${stats.budgetUsedPercent}%`);
    console.log(`  Budget Remaining: $${stats.budgetRemaining.toFixed(4)}`);
    console.log('');
    console.log(`STATUS: ${stats.status.icon} ${stats.status.message.toUpperCase()}`);
    console.log(`Can Make Request: ${stats.canMakeRequest ? '✅ YES' : '🚫 NO'}`);
    console.log('='.repeat(60) + '\n');
  }
}

// Singleton instance
export const costProtector = new CostProtector();

// Utility function for checking before API calls
export function canMakeAPIRequest() {
  return costProtector.canMakeRequest();
}

// Utility function for recording API calls
export function recordAPIRequest() {
  costProtector.recordRequest();
}

// Utility function for getting usage stats
export function getUsageStats() {
  return costProtector.getUsageStats();
}

// Print usage report to console
export function printCostReport() {
  costProtector.printUsageReport();
}

// Export for window debugging
if (typeof window !== 'undefined') {
  window.qewCostProtection = {
    getStats: () => costProtector.getUsageStats(),
    printReport: () => costProtector.printUsageReport(),
    canRequest: () => costProtector.canMakeRequest(),
    reset: () => costProtector.resetUsageStats() // ADMIN ONLY
  };
}

/**
 * Demo Mode Configuration
 * Switches between cached data (free) and live API calls (paid)
 *
 * MODES:
 * - CACHED: Use cached work zones only ($0 cost, unlimited demos)
 * - LIVE: Allow limited API calls (controlled cost, technical demos)
 * - FULL: Full analysis (use sparingly, scheduled runs only)
 *
 * USAGE:
 * import { getDemoMode, setDemoMode, DEMO_MODES } from './utils/demoMode';
 *
 * if (getDemoMode() === DEMO_MODES.CACHED) {
 *   // Use cached data only
 * } else if (getDemoMode() === DEMO_MODES.LIVE) {
 *   // Allow limited API calls
 * }
 */

export const DEMO_MODES = {
  CACHED: 'cached',      // Use cached work zones only ($0 cost)
  LIVE: 'live',          // Allow limited API calls (controlled cost)
  FULL: 'full'           // Full analysis (use sparingly)
};

const DEMO_MODE_DESCRIPTIONS = {
  cached: {
    name: 'CACHED Demo Mode',
    description: 'Uses cached work zone data from localStorage',
    cost: '$0.00',
    apiCalls: 'Disabled',
    useCase: 'Client demos, presentations, stakeholder reviews',
    icon: '💾',
    color: '#00ff00'
  },
  live: {
    name: 'LIVE Demo Mode',
    description: 'Allows limited API calls for real-time analysis',
    cost: '~$0.0002 per camera',
    apiCalls: 'Limited (2-3 cameras)',
    useCase: 'Technical demos, OVIN presentations',
    icon: '🎥',
    color: '#ffff00'
  },
  full: {
    name: 'FULL Analysis Mode',
    description: 'Complete analysis of all cameras',
    cost: '~$0.004 per run (50 images)',
    apiCalls: 'Unrestricted (within daily limits)',
    useCase: 'Weekly collections, testing, development',
    icon: '🚀',
    color: '#ff9900'
  }
};

/**
 * Get current demo mode
 * @returns {string} Current mode (cached|live|full)
 */
export function getDemoMode() {
  const mode = localStorage.getItem('qew_demo_mode');

  // Default to CACHED for cost safety (set directly to avoid recursion)
  if (!mode || !Object.values(DEMO_MODES).includes(mode)) {
    localStorage.setItem('qew_demo_mode', DEMO_MODES.CACHED);
    return DEMO_MODES.CACHED;
  }

  return mode;
}

/**
 * Set demo mode
 * @param {string} mode - Mode to set (cached|live|full)
 */
export function setDemoMode(mode) {
  if (!Object.values(DEMO_MODES).includes(mode)) {
    throw new Error(`Invalid demo mode: ${mode}. Must be one of: ${Object.values(DEMO_MODES).join(', ')}`);
  }

  const prevMode = localStorage.getItem('qew_demo_mode') || DEMO_MODES.CACHED;
  localStorage.setItem('qew_demo_mode', mode);

  const modeInfo = DEMO_MODE_DESCRIPTIONS[mode];

  console.log('\n' + '='.repeat(60));
  console.log(`${modeInfo.icon} DEMO MODE CHANGED`);
  console.log('='.repeat(60));
  console.log(`Previous Mode: ${prevMode.toUpperCase()}`);
  console.log(`New Mode: ${mode.toUpperCase()}`);
  console.log('');
  console.log(`Name: ${modeInfo.name}`);
  console.log(`Description: ${modeInfo.description}`);
  console.log(`Cost: ${modeInfo.cost}`);
  console.log(`API Calls: ${modeInfo.apiCalls}`);
  console.log(`Use Case: ${modeInfo.useCase}`);
  console.log('='.repeat(60) + '\n');

  // Store mode change history
  const history = JSON.parse(localStorage.getItem('qew_demo_mode_history') || '[]');
  history.push({
    timestamp: new Date().toISOString(),
    fromMode: prevMode,
    toMode: mode
  });
  // Keep last 50 mode changes
  localStorage.setItem('qew_demo_mode_history', JSON.stringify(history.slice(-50)));
}

/**
 * Check if in cached demo mode (zero cost)
 * @returns {boolean}
 */
export function isDemoMode() {
  return getDemoMode() === DEMO_MODES.CACHED;
}

/**
 * Check if in live demo mode (controlled cost)
 * @returns {boolean}
 */
export function isLiveMode() {
  return getDemoMode() === DEMO_MODES.LIVE;
}

/**
 * Check if in full analysis mode
 * @returns {boolean}
 */
export function isFullMode() {
  return getDemoMode() === DEMO_MODES.FULL;
}

/**
 * Check if API calls are allowed in current mode
 * @returns {boolean}
 */
export function canMakeAPICall() {
  const mode = getDemoMode();

  if (mode === DEMO_MODES.CACHED) {
    console.warn('[Demo Mode] 🚫 API calls disabled in CACHED mode');
    console.warn('[Demo Mode] 💡 Switch to LIVE or FULL mode to enable API calls');
    return false;
  }

  return true;
}

/**
 * Get mode description
 * @param {string} mode - Mode to describe
 * @returns {object} Mode description
 */
export function getModeDescription(mode = null) {
  const targetMode = mode || getDemoMode();
  return DEMO_MODE_DESCRIPTIONS[targetMode] || null;
}

/**
 * Print mode information to console
 */
export function printModeInfo() {
  const mode = getDemoMode();
  const modeInfo = DEMO_MODE_DESCRIPTIONS[mode];

  console.log('\n' + '='.repeat(60));
  console.log(`${modeInfo.icon} CURRENT DEMO MODE`);
  console.log('='.repeat(60));
  console.log(`Mode: ${mode.toUpperCase()}`);
  console.log(`Name: ${modeInfo.name}`);
  console.log(`Description: ${modeInfo.description}`);
  console.log(`Cost: ${modeInfo.cost}`);
  console.log(`API Calls: ${modeInfo.apiCalls}`);
  console.log(`Use Case: ${modeInfo.useCase}`);
  console.log('');
  console.log('AVAILABLE MODES:');
  Object.entries(DEMO_MODE_DESCRIPTIONS).forEach(([key, info]) => {
    const current = key === mode ? '→' : ' ';
    console.log(`  ${current} ${info.icon} ${key.toUpperCase()}: ${info.description}`);
  });
  console.log('');
  console.log('TO CHANGE MODE:');
  console.log(`  setDemoMode('cached')  // Zero cost, unlimited demos`);
  console.log(`  setDemoMode('live')    // Limited API calls`);
  console.log(`  setDemoMode('full')    // Full analysis`);
  console.log('='.repeat(60) + '\n');
}

/**
 * Get mode change history
 * @returns {array} History of mode changes
 */
export function getModeHistory() {
  return JSON.parse(localStorage.getItem('qew_demo_mode_history') || '[]');
}

/**
 * Clear mode history
 */
export function clearModeHistory() {
  localStorage.removeItem('qew_demo_mode_history');
  console.log('[Demo Mode] Mode history cleared');
}

/**
 * Get recommended mode based on use case
 * @param {string} useCase - Use case (client_demo|technical_demo|weekly_collection|development)
 * @returns {string} Recommended mode
 */
export function getRecommendedMode(useCase) {
  const recommendations = {
    client_demo: DEMO_MODES.CACHED,
    presentation: DEMO_MODES.CACHED,
    stakeholder_review: DEMO_MODES.CACHED,
    technical_demo: DEMO_MODES.LIVE,
    ovin_presentation: DEMO_MODES.LIVE,
    weekly_collection: DEMO_MODES.FULL,
    development: DEMO_MODES.FULL,
    testing: DEMO_MODES.FULL
  };

  return recommendations[useCase] || DEMO_MODES.CACHED;
}

// Export for window debugging
if (typeof window !== 'undefined') {
  window.qewDemoMode = {
    get: getDemoMode,
    set: setDemoMode,
    info: printModeInfo,
    history: getModeHistory,
    modes: DEMO_MODES,
    setCached: () => setDemoMode(DEMO_MODES.CACHED),
    setLive: () => setDemoMode(DEMO_MODES.LIVE),
    setFull: () => setDemoMode(DEMO_MODES.FULL)
  };

  console.log('[Demo Mode] 💡 Quick commands available:');
  console.log('  qewDemoMode.info()     // Show current mode');
  console.log('  qewDemoMode.setCached() // Switch to CACHED mode');
  console.log('  qewDemoMode.setLive()   // Switch to LIVE mode');
  console.log('  qewDemoMode.setFull()   // Switch to FULL mode');
}

// Initialize with safe default on first load (direct set to avoid recursion)
if (!localStorage.getItem('qew_demo_mode')) {
  console.log('[Demo Mode] ⚙️ Initializing with CACHED mode (zero cost)');
  localStorage.setItem('qew_demo_mode', DEMO_MODES.CACHED);
}

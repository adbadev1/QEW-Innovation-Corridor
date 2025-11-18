/**
 * Production-Grade Logging Utility
 *
 * Provides structured logging with multiple severity levels.
 * Logs are stored in sessionStorage for debugging and can be exported.
 *
 * Log Levels:
 * - DEBUG: Detailed information for debugging (development only)
 * - INFO: General informational messages
 * - WARN: Warning messages (non-critical issues)
 * - ERROR: Error messages (handled errors)
 * - CRITICAL: Critical errors (system failures)
 *
 * Features:
 * - Automatic timestamp and session tracking
 * - Persistent storage in sessionStorage
 * - Console output with color coding
 * - Export logs for support tickets
 * - Context tracking (component, function, user action)
 */

const LOG_LEVELS = {
  DEBUG: { value: 0, label: 'DEBUG', color: '#6B7280', icon: '🔍' },
  INFO: { value: 1, label: 'INFO', color: '#3B82F6', icon: 'ℹ️' },
  WARN: { value: 2, label: 'WARN', color: '#F59E0B', icon: '⚠️' },
  ERROR: { value: 3, label: 'ERROR', color: '#EF4444', icon: '❌' },
  CRITICAL: { value: 4, label: 'CRITICAL', color: '#DC2626', icon: '🚨' }
};

const IS_DEVELOPMENT = import.meta.env.DEV;
const MIN_LOG_LEVEL = IS_DEVELOPMENT ? LOG_LEVELS.DEBUG.value : LOG_LEVELS.INFO.value;
const MAX_STORED_LOGS = 1000;

class Logger {
  constructor() {
    this.sessionId = this.getOrCreateSessionId();
    this.startTime = Date.now();
    this.initializeStorage();
  }

  getOrCreateSessionId() {
    let sessionId = sessionStorage.getItem('logger_session_id');
    if (!sessionId) {
      sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
      sessionStorage.setItem('logger_session_id', sessionId);
    }
    return sessionId;
  }

  initializeStorage() {
    try {
      const existing = sessionStorage.getItem('app_logs');
      if (!existing) {
        sessionStorage.setItem('app_logs', JSON.stringify([]));
      }
    } catch (e) {
      console.warn('Logger: Unable to initialize sessionStorage:', e);
    }
  }

  formatTimestamp() {
    const now = new Date();
    return now.toISOString();
  }

  getUptime() {
    return Date.now() - this.startTime;
  }

  createLogEntry(level, message, context = {}) {
    return {
      timestamp: this.formatTimestamp(),
      uptime: this.getUptime(),
      sessionId: this.sessionId,
      level: level.label,
      message,
      context,
      userAgent: navigator.userAgent,
      url: window.location.href
    };
  }

  storeLog(logEntry) {
    try {
      const logs = JSON.parse(sessionStorage.getItem('app_logs') || '[]');
      logs.unshift(logEntry); // Most recent first
      const trimmedLogs = logs.slice(0, MAX_STORED_LOGS);
      sessionStorage.setItem('app_logs', JSON.stringify(trimmedLogs));
    } catch (e) {
      console.warn('Logger: Failed to store log:', e);
    }
  }

  outputToConsole(level, message, context) {
    const styles = `color: ${level.color}; font-weight: bold;`;
    const timestamp = new Date().toLocaleTimeString();
    const prefix = `${level.icon} [${timestamp}] [${level.label}]`;

    if (level.value >= LOG_LEVELS.ERROR.value) {
      console.error(`%c${prefix}`, styles, message, context);
    } else if (level.value === LOG_LEVELS.WARN.value) {
      console.warn(`%c${prefix}`, styles, message, context);
    } else {
      console.log(`%c${prefix}`, styles, message, context);
    }
  }

  log(level, message, context = {}) {
    // Filter by minimum log level
    if (level.value < MIN_LOG_LEVEL) {
      return;
    }

    // Create log entry
    const logEntry = this.createLogEntry(level, message, context);

    // Store in sessionStorage
    this.storeLog(logEntry);

    // Output to console
    this.outputToConsole(level, message, context);

    // Send to monitoring service if critical (production only)
    if (level.value >= LOG_LEVELS.CRITICAL.value && !IS_DEVELOPMENT) {
      this.reportToMonitoring(logEntry);
    }
  }

  debug(message, context = {}) {
    this.log(LOG_LEVELS.DEBUG, message, context);
  }

  info(message, context = {}) {
    this.log(LOG_LEVELS.INFO, message, context);
  }

  warn(message, context = {}) {
    this.log(LOG_LEVELS.WARN, message, context);
  }

  error(message, context = {}) {
    this.log(LOG_LEVELS.ERROR, message, context);
  }

  critical(message, context = {}) {
    this.log(LOG_LEVELS.CRITICAL, message, context);
  }

  reportToMonitoring(logEntry) {
    // TODO: Send to Sentry, LogRocket, or custom endpoint
    console.log('Would report to monitoring service:', logEntry);
  }

  // Export logs for debugging/support
  exportLogs() {
    try {
      const logs = JSON.parse(sessionStorage.getItem('app_logs') || '[]');
      return {
        sessionId: this.sessionId,
        exportTime: new Date().toISOString(),
        totalLogs: logs.length,
        logs
      };
    } catch (e) {
      console.error('Failed to export logs:', e);
      return null;
    }
  }

  // Download logs as JSON file
  downloadLogs() {
    const logsData = this.exportLogs();
    if (!logsData) return;

    const blob = new Blob([JSON.stringify(logsData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `qew-logs-${this.sessionId}-${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    this.info('Logs downloaded successfully', { fileName: a.download });
  }

  // Clear all stored logs
  clearLogs() {
    try {
      sessionStorage.removeItem('app_logs');
      sessionStorage.setItem('app_logs', JSON.stringify([]));
      this.info('All logs cleared');
    } catch (e) {
      console.error('Failed to clear logs:', e);
    }
  }

  // Get logs filtered by level
  getLogsByLevel(levelName) {
    try {
      const logs = JSON.parse(sessionStorage.getItem('app_logs') || '[]');
      return logs.filter(log => log.level === levelName);
    } catch (e) {
      console.error('Failed to filter logs:', e);
      return [];
    }
  }

  // Get logs within time range
  getLogsByTimeRange(startTime, endTime) {
    try {
      const logs = JSON.parse(sessionStorage.getItem('app_logs') || '[]');
      return logs.filter(log => {
        const logTime = new Date(log.timestamp).getTime();
        return logTime >= startTime && logTime <= endTime;
      });
    } catch (e) {
      console.error('Failed to filter logs by time:', e);
      return [];
    }
  }

  // Search logs by keyword
  searchLogs(keyword) {
    try {
      const logs = JSON.parse(sessionStorage.getItem('app_logs') || '[]');
      const lowerKeyword = keyword.toLowerCase();
      return logs.filter(log =>
        log.message.toLowerCase().includes(lowerKeyword) ||
        JSON.stringify(log.context).toLowerCase().includes(lowerKeyword)
      );
    } catch (e) {
      console.error('Failed to search logs:', e);
      return [];
    }
  }

  // Get system info for debugging
  getSystemInfo() {
    return {
      sessionId: this.sessionId,
      uptime: this.getUptime(),
      userAgent: navigator.userAgent,
      platform: navigator.platform,
      language: navigator.language,
      screenResolution: `${window.screen.width}x${window.screen.height}`,
      viewport: `${window.innerWidth}x${window.innerHeight}`,
      memory: performance.memory ? {
        usedJSHeapSize: performance.memory.usedJSHeapSize,
        totalJSHeapSize: performance.memory.totalJSHeapSize,
        jsHeapSizeLimit: performance.memory.jsHeapSizeLimit
      } : 'Not available',
      connection: navigator.connection ? {
        effectiveType: navigator.connection.effectiveType,
        downlink: navigator.connection.downlink,
        rtt: navigator.connection.rtt
      } : 'Not available'
    };
  }
}

// Create singleton instance
const logger = new Logger();

// Export convenience functions
export const debug = (message, context) => logger.debug(message, context);
export const info = (message, context) => logger.info(message, context);
export const warn = (message, context) => logger.warn(message, context);
export const error = (message, context) => logger.error(message, context);
export const critical = (message, context) => logger.critical(message, context);
export const exportLogs = () => logger.exportLogs();
export const downloadLogs = () => logger.downloadLogs();
export const clearLogs = () => logger.clearLogs();
export const getLogsByLevel = (level) => logger.getLogsByLevel(level);
export const getLogsByTimeRange = (start, end) => logger.getLogsByTimeRange(start, end);
export const searchLogs = (keyword) => logger.searchLogs(keyword);
export const getSystemInfo = () => logger.getSystemInfo();

export default logger;

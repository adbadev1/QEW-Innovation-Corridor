import { useState, useCallback, useEffect } from 'react';
import { error as logError, warn as logWarn, critical as logCritical } from '../utils/logger';

/**
 * useErrorTracking Hook
 *
 * Provides consistent error handling and tracking across components.
 *
 * Features:
 * - Automatic error logging
 * - Error state management
 * - Retry logic with exponential backoff
 * - Error recovery callbacks
 * - Network error detection
 * - User-friendly error messages
 *
 * Usage:
 * const { trackError, handleAsync, errors, clearError } = useErrorTracking('MyComponent');
 */

const ERROR_TYPES = {
  NETWORK: 'NETWORK',
  VALIDATION: 'VALIDATION',
  PERMISSION: 'PERMISSION',
  TIMEOUT: 'TIMEOUT',
  API: 'API',
  UNKNOWN: 'UNKNOWN'
};

const MAX_RETRIES = 3;
const INITIAL_RETRY_DELAY = 1000; // 1 second

export function useErrorTracking(componentName = 'UnknownComponent') {
  const [errors, setErrors] = useState([]);
  const [retryCount, setRetryCount] = useState({});

  // Add error to state
  const trackError = useCallback((error, context = {}) => {
    const errorType = categorizeError(error);
    const errorDetails = {
      id: Date.now() + Math.random(),
      timestamp: new Date().toISOString(),
      message: error.message || String(error),
      type: errorType,
      component: componentName,
      context,
      stack: error.stack,
      isCritical: errorType === ERROR_TYPES.NETWORK || errorType === ERROR_TYPES.API
    };

    setErrors(prev => [...prev, errorDetails]);

    // Log based on severity
    if (errorDetails.isCritical) {
      logCritical(errorDetails.message, {
        component: componentName,
        type: errorType,
        ...context
      });
    } else {
      logError(errorDetails.message, {
        component: componentName,
        type: errorType,
        ...context
      });
    }

    return errorDetails;
  }, [componentName]);

  // Clear specific error
  const clearError = useCallback((errorId) => {
    setErrors(prev => prev.filter(e => e.id !== errorId));
  }, []);

  // Clear all errors
  const clearAllErrors = useCallback(() => {
    setErrors([]);
  }, []);

  // Get user-friendly error message
  const getUserFriendlyMessage = useCallback((error) => {
    const errorType = categorizeError(error);

    const messages = {
      [ERROR_TYPES.NETWORK]: 'Network connection issue. Please check your internet connection and try again.',
      [ERROR_TYPES.VALIDATION]: 'Invalid input. Please check your data and try again.',
      [ERROR_TYPES.PERMISSION]: 'Permission denied. You may not have access to this resource.',
      [ERROR_TYPES.TIMEOUT]: 'Request timed out. The operation took too long. Please try again.',
      [ERROR_TYPES.API]: 'Server error. Our team has been notified. Please try again later.',
      [ERROR_TYPES.UNKNOWN]: 'An unexpected error occurred. Please try again or contact support.'
    };

    return messages[errorType] || messages[ERROR_TYPES.UNKNOWN];
  }, []);

  // Async operation wrapper with error tracking and retry
  const handleAsync = useCallback(async (
    asyncFn,
    options = {}
  ) => {
    const {
      retries = MAX_RETRIES,
      retryDelay = INITIAL_RETRY_DELAY,
      onError = null,
      onSuccess = null,
      context = {}
    } = options;

    const operationId = `${componentName}_${Date.now()}`;
    let lastError = null;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const result = await asyncFn();

        // Success - reset retry count
        setRetryCount(prev => ({ ...prev, [operationId]: 0 }));

        if (onSuccess) {
          onSuccess(result);
        }

        return { success: true, data: result, error: null };
      } catch (err) {
        lastError = err;
        const errorType = categorizeError(err);

        // Log retry attempt
        if (attempt < retries) {
          logWarn(`Operation failed, retry ${attempt + 1}/${retries}`, {
            component: componentName,
            error: err.message,
            type: errorType,
            ...context
          });

          // Exponential backoff
          const delay = retryDelay * Math.pow(2, attempt);
          await new Promise(resolve => setTimeout(resolve, delay));
        }
      }
    }

    // All retries exhausted
    const errorDetails = trackError(lastError, {
      ...context,
      retriesExhausted: true,
      attempts: retries + 1
    });

    if (onError) {
      onError(errorDetails);
    }

    return {
      success: false,
      data: null,
      error: errorDetails,
      userMessage: getUserFriendlyMessage(lastError)
    };
  }, [componentName, trackError, getUserFriendlyMessage]);

  // Check if there are critical errors
  const hasCriticalErrors = errors.some(e => e.isCritical);

  // Get latest error
  const latestError = errors.length > 0 ? errors[errors.length - 1] : null;

  // Auto-clear errors after 30 seconds
  useEffect(() => {
    if (errors.length === 0) return;

    const timer = setTimeout(() => {
      setErrors(prev => prev.filter(e => {
        const age = Date.now() - new Date(e.timestamp).getTime();
        return age < 30000; // Keep errors less than 30 seconds old
      }));
    }, 30000);

    return () => clearTimeout(timer);
  }, [errors]);

  return {
    errors,
    trackError,
    clearError,
    clearAllErrors,
    handleAsync,
    getUserFriendlyMessage,
    hasCriticalErrors,
    latestError
  };
}

// Helper: Categorize error type
function categorizeError(error) {
  const message = error.message?.toLowerCase() || String(error).toLowerCase();

  // Network errors
  if (
    message.includes('network') ||
    message.includes('fetch') ||
    message.includes('connection') ||
    error.name === 'NetworkError' ||
    error.name === 'TypeError' && message.includes('failed to fetch')
  ) {
    return ERROR_TYPES.NETWORK;
  }

  // Timeout errors
  if (message.includes('timeout') || error.name === 'TimeoutError') {
    return ERROR_TYPES.TIMEOUT;
  }

  // Validation errors
  if (
    message.includes('validation') ||
    message.includes('invalid') ||
    message.includes('required')
  ) {
    return ERROR_TYPES.VALIDATION;
  }

  // Permission errors
  if (
    message.includes('permission') ||
    message.includes('unauthorized') ||
    message.includes('forbidden') ||
    error.status === 401 ||
    error.status === 403
  ) {
    return ERROR_TYPES.PERMISSION;
  }

  // API errors
  if (
    error.status >= 400 ||
    message.includes('api') ||
    message.includes('server')
  ) {
    return ERROR_TYPES.API;
  }

  return ERROR_TYPES.UNKNOWN;
}

export { ERROR_TYPES };

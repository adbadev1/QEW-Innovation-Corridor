import React from 'react';
import { AlertTriangle, RefreshCcw, Home } from 'lucide-react';

/**
 * ErrorBoundary - Production-grade React Error Boundary
 *
 * Catches JavaScript errors anywhere in the child component tree,
 * logs those errors, and displays a fallback UI instead of crashing.
 *
 * Features:
 * - Detailed error logging with component stack trace
 * - User-friendly error display
 * - Recovery options (reload, home)
 * - Error reporting to monitoring service (extensible)
 */
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCount: 0
    };
  }

  static getDerivedStateFromError(error) {
    // Update state so the next render will show the fallback UI
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    const errorDetails = {
      message: error.toString(),
      stack: error.stack,
      componentStack: errorInfo.componentStack,
      timestamp: new Date().toISOString(),
      userAgent: navigator.userAgent,
      url: window.location.href
    };

    // Log to console in development
    console.error('🚨 ErrorBoundary caught an error:', errorDetails);

    // Update state with error details
    this.setState(prevState => ({
      error,
      errorInfo,
      errorCount: prevState.errorCount + 1
    }));

    // TODO: Send to error monitoring service (Sentry, LogRocket, etc.)
    this.reportErrorToService(errorDetails);

    // Store in sessionStorage for debugging
    try {
      const existingErrors = JSON.parse(sessionStorage.getItem('app_errors') || '[]');
      existingErrors.push(errorDetails);
      sessionStorage.setItem('app_errors', JSON.stringify(existingErrors.slice(-10))); // Keep last 10 errors
    } catch (e) {
      console.error('Failed to store error in sessionStorage:', e);
    }
  }

  reportErrorToService(errorDetails) {
    // Extensible error reporting
    // In production, send to Sentry, LogRocket, or custom endpoint
    if (process.env.NODE_ENV === 'production') {
      // Example: Sentry.captureException(errorDetails);
      console.log('Would report to monitoring service:', errorDetails);
    }
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
    window.location.href = '/QEW-Innovation-Corridor/';
  };

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      const { error, errorInfo, errorCount } = this.state;
      const isDevelopment = process.env.NODE_ENV === 'development';

      return (
        <div className="min-h-screen bg-gray-900 text-white flex items-center justify-center p-4">
          <div className="max-w-2xl w-full bg-gray-800 rounded-lg shadow-2xl overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-red-600 to-orange-600 p-6">
              <div className="flex items-center space-x-3">
                <AlertTriangle className="w-10 h-10 text-white" />
                <div>
                  <h1 className="text-2xl font-bold">Application Error</h1>
                  <p className="text-red-100 text-sm mt-1">
                    Something went wrong. Don't worry, we've logged this issue.
                  </p>
                </div>
              </div>
            </div>

            {/* Error Details */}
            <div className="p-6 space-y-4">
              {/* Error Count Warning */}
              {errorCount > 1 && (
                <div className="bg-yellow-900/30 border border-yellow-600 rounded p-3">
                  <p className="text-yellow-300 text-sm">
                    ⚠️ This error has occurred {errorCount} times. Please contact support if it persists.
                  </p>
                </div>
              )}

              {/* Error Message */}
              <div className="bg-gray-900 border border-gray-700 rounded p-4">
                <h3 className="text-sm font-semibold text-red-400 mb-2">Error Message:</h3>
                <p className="font-mono text-xs text-gray-300 break-words">
                  {error?.toString() || 'Unknown error'}
                </p>
              </div>

              {/* Development Details */}
              {isDevelopment && errorInfo && (
                <details className="bg-gray-900 border border-gray-700 rounded p-4">
                  <summary className="text-sm font-semibold text-orange-400 cursor-pointer">
                    Component Stack Trace (Development Only)
                  </summary>
                  <pre className="font-mono text-[10px] text-gray-400 mt-2 overflow-x-auto whitespace-pre-wrap">
                    {errorInfo.componentStack}
                  </pre>
                </details>
              )}

              {isDevelopment && error?.stack && (
                <details className="bg-gray-900 border border-gray-700 rounded p-4">
                  <summary className="text-sm font-semibold text-orange-400 cursor-pointer">
                    Full Stack Trace (Development Only)
                  </summary>
                  <pre className="font-mono text-[10px] text-gray-400 mt-2 overflow-x-auto whitespace-pre-wrap">
                    {error.stack}
                  </pre>
                </details>
              )}

              {/* Recovery Actions */}
              <div className="flex space-x-3 pt-2">
                <button
                  onClick={this.handleReset}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-lg transition flex items-center justify-center space-x-2"
                >
                  <RefreshCcw className="w-5 h-5" />
                  <span>Try Again</span>
                </button>
                <button
                  onClick={this.handleReload}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-3 rounded-lg transition flex items-center justify-center space-x-2"
                >
                  <RefreshCcw className="w-5 h-5" />
                  <span>Reload Page</span>
                </button>
                <button
                  onClick={this.handleGoHome}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 text-white font-semibold py-3 rounded-lg transition flex items-center justify-center space-x-2"
                >
                  <Home className="w-5 h-5" />
                  <span>Go Home</span>
                </button>
              </div>

              {/* Support Info */}
              <div className="bg-blue-900/30 border border-blue-600 rounded p-3 text-xs text-blue-200">
                <p className="font-semibold mb-1">Need Help?</p>
                <p>
                  If this error persists, please contact support at{' '}
                  <a href="mailto:adbalabs0101@gmail.com" className="underline">
                    adbalabs0101@gmail.com
                  </a>
                </p>
                <p className="mt-1 text-[10px] text-blue-300 font-mono">
                  Error ID: {Date.now()}-{Math.random().toString(36).substr(2, 9)}
                </p>
              </div>
            </div>

            {/* Footer */}
            <div className="bg-gray-900 border-t border-gray-700 p-4 text-center">
              <p className="text-xs text-gray-500">
                QEW Innovation Corridor Pilot | ADBA Labs
              </p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;

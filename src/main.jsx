import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { V2XProvider } from './contexts/V2XContext.jsx'
import ErrorBoundary from './components/ErrorBoundary.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <V2XProvider>
        <App />
      </V2XProvider>
    </ErrorBoundary>
  </React.StrictMode>,
)

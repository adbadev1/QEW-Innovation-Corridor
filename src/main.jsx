import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'
import { V2XProvider } from './contexts/V2XContext.jsx'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <V2XProvider>
      <App />
    </V2XProvider>
  </React.StrictMode>,
)

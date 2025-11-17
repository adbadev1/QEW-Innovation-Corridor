import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Port 8200 per universal_port_config.md
// See: /Users/adbalabs/config/universal_port_config.md
// - Port 3000: AVOID (React/Next.js conflicts)
// - New hackathon projects: Use 8200+ range
export default defineConfig({
  plugins: [react()],
  server: {
    port: 8200,
    open: true
  }
})

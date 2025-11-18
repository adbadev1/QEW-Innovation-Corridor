import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

// Port configuration per universal_port_config.md
// See: /Users/adbalabs/config/universal_port_config.md
// - Port 3000: AVOID (React/Next.js conflicts)
// - New hackathon projects: Use 8200+ range
// - Git worktrees: Each worktree uses custom port (8300, 8400, etc.)
export default defineConfig(({ mode }) => {
  // Load env file
  const env = loadEnv(mode, process.cwd(), '')

  // Get port from .env or default to 8200
  const port = parseInt(env.VITE_PORT || '8200', 10)

  return {
    plugins: [react()],
    base: '/QEW-Innovation-Corridor/',
    server: {
      port: port,
      strictPort: true,  // Fail if port is not available (no auto-increment)
      open: true
    }
  }
})

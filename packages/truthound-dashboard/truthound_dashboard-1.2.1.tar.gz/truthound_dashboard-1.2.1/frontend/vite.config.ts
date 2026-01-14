import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { intlayer } from 'vite-intlayer'
import path from 'path'

export default defineConfig(({ mode }) => ({
  plugins: [react(), intlayer()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8765',
        changeOrigin: true,
      },
    },
  },
  build: {
    // demo: Netlify (dist/), pip: backend static folder
    outDir: mode === 'demo' ? 'dist' : '../src/truthound_dashboard/static',
    emptyOutDir: true,
    sourcemap: false,
  },
  // pip: exclude mockServiceWorker.js, demo: include all
  publicDir: mode === 'pip' ? 'public-pip' : 'public',
}))

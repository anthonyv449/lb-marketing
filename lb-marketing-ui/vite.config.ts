import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from "path"

// Tailwind should be configured via PostCSS (postcss.config.js) and tailwind.config.js
// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  // Dev server proxy to forward API requests to backend to avoid CORS during development
  // In production, set VITE_API_URL environment variable instead
  server: {
    proxy: {
      // Proxy all API routes to backend
      '/posts': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      // Proxy OAuth routes
      '/oauth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      // Proxy social-profiles routes
      '/social-profiles': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      // Proxy authentication routes
      '/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      // Proxy other API routes (businesses, locations, campaigns, assets, etc.)
      '/businesses': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/locations': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/campaigns': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/assets': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/healthz': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
    }
  },
  // Build configuration
  build: {
    outDir: 'dist',
    sourcemap: false,
    minify: 'esbuild',
    rollupOptions: {
      output: {
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'ui-vendor': ['lucide-react'],
        },
      },
    },
  },
  // Preview server configuration (for testing production builds locally)
  preview: {
    port: 4173,
    host: true,
  },
})

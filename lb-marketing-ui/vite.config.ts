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
  server: {
    proxy: {
      // Proxy any request starting with /posts (and add other routes as needed)
      '/posts': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      // If you want to proxy all API routes under /api, use '/api': 'http://localhost:8000'
    }
  },
})

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
})

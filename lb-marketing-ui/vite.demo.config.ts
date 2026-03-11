import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  root: __dirname,
  build: {
    rollupOptions: {
      input: path.resolve(__dirname, "demo.html"),
    },
  },
  server: {
    port: 5174,
    open: "/demo.html",
  },
});

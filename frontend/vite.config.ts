import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from "tailwindcss";

// https://vitejs.dev/config/
export default defineConfig({
 base: "/",
 plugins: [react()],
 server: {
  port: 3000,
  strictPort: true,
  host: true,
  watch: {
    usePolling: true,
    interval: 1000
  }
 },
 css: {
  postcss: {
    plugins: [tailwindcss()],
  }
 }
});

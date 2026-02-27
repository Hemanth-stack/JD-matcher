import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    allowedHosts: ['jd-matcher.iamhemanth.in'],
    proxy: {
      '/api': process.env.VITE_BACKEND_URL ?? 'http://localhost:8080',
    },
  },
})

import react, { reactCompilerPreset } from '@vitejs/plugin-react'
import babel from '@rolldown/plugin-babel'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    babel({ presets: [reactCompilerPreset()] })
  ],
  server: {
    proxy: {
      // The study material viewer reads the processing service on port 8001.
      '/documents/summary': 'http://127.0.0.1:8001',
      '/documents/flashcards': 'http://127.0.0.1:8001',
    },
  },
})

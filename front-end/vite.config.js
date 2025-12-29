import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue({
    customElement: true
  })],
  build: {
    lib: {
      entry: './src/main.js',
      name: 'AiChatbot',
      fileName: 'chatbot'
    }
  },
  define: {
    'process.env': {},
    'process': { env: {} }
  }
})

import { defineConfig, loadEnv } from "vite";
import vue from '@vitejs/plugin-vue';
import { fileURLToPath, URL } from 'url';
import { resolve } from 'path';

export default defineConfig(({ mode }) => {
  // Load env variables
  const env = loadEnv(mode, process.cwd(), "VITE_");

  return {
    plugins: [vue()],
    base: env.VITE_BASE_URL || "/",
    server: {
      port: 8080,
      strictPort: true,
    },
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url))
      }
    },
    build: {
      sourcemap: false,
      cssCodeSplit: true,
      chunkSizeWarningLimit: 2000,
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor': ['vue', 'vue-router', 'axios'],
            'annotations': ['html2canvas', 'jspdf', 'html2pdf.js']
          }
        }
      }
    }
  };
});

import { defineConfig, loadEnv } from "vite";

export default defineConfig(({ mode }) => {
  // Load env variables
  const env = loadEnv(mode, process.cwd(), "VITE_");

  return {
    base: env.VITE_BASE_URL || "/",
    server: {
      port: 8080,
      strictPort: true,
    },
  };
});

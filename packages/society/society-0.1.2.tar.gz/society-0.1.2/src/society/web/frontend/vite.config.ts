import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const backendPort = process.env.SOCIETY_BACKEND_PORT || "8000";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      "/api": `http://localhost:${backendPort}`,
    },
  },
});

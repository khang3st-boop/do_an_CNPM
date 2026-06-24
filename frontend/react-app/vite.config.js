import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Proxy /api -> FastAPI backend (mặc định chạy ở localhost:8000)
// để giữ nguyên hành vi gọi fetch("/api/...") như code gốc, không cần
// đổi base URL trong api.js.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
});

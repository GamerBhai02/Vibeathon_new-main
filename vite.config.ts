import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// Try to import Replit plugins, but don't fail if they're missing (optional dependencies)
let runtimeErrorOverlay;
try {
  runtimeErrorOverlay = (await import("@replit/vite-plugin-runtime-error-modal")).default;
} catch {
  runtimeErrorOverlay = () => ({ name: 'runtime-error-overlay-stub' });
}

export default defineConfig({
  plugins: [
    react(),
    runtimeErrorOverlay(),
    ...(process.env.NODE_ENV !== "production" &&
    process.env.REPL_ID !== undefined
      ? await (async () => {
          try {
            const cartographer = await import("@replit/vite-plugin-cartographer");
            const devBanner = await import("@replit/vite-plugin-dev-banner");
            return [cartographer.cartographer(), devBanner.devBanner()];
          } catch (e) {
            console.log("Replit plugins not available (using minimal installation)");
            return [];
          }
        })()
      : []),
  ],
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "client", "src"),
      "@shared": path.resolve(import.meta.dirname, "shared"),
      "@assets": path.resolve(import.meta.dirname, "attached_assets"),
    },
  },
  root: path.resolve(import.meta.dirname, "client"),
  build: {
    outDir: path.resolve(import.meta.dirname, "dist/public"),
    emptyOutDir: true,
  },
  server: {
    fs: {
      strict: true,
      deny: ["**/.*"],
    },
  },
});

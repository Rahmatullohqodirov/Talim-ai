
import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), "");

  const API_URL = (
    env.VITE_API_URL || "https://talim-ai-backend.vercel.app"
  ).replace(/\/+$/, "");

  return {
    plugins: [
      react(),

      VitePWA({
        registerType: "autoUpdate",
        injectRegister: "auto",

        workbox: {
          globPatterns: ["**/*.{js,css,html,svg,png,ico}"],
          navigateFallback: "/index.html",

          runtimeCaching: [
            {
              urlPattern: ({ url, request }) =>
                request.method === "GET" &&
                url.pathname.startsWith("/api/v1/"),

              handler: "NetworkFirst",

              options: {
                cacheName: "talim-api-cache",
                networkTimeoutSeconds: 4,

                expiration: {
                  maxEntries: 200,
                  maxAgeSeconds: 60 * 60 * 24 * 7,
                },

                cacheableResponse: {
                  statuses: [0, 200],
                },
              },
            },
          ],
        },

        manifest: {
          name: "Talim",
          short_name: "Talim",
          description:
            "AI asosidagi til va matematika o'qitish platformasi",
          start_url: "/",
          display: "standalone",
          background_color: "#ffffff",
          theme_color: "#6d5ce8",

          icons: [
            {
              src: "/icon-192.png",
              sizes: "192x192",
              type: "image/png",
            },
            {
              src: "/icon-512.png",
              sizes: "512x512",
              type: "image/png",
            },
            {
              src: "/icon-maskable-512.png",
              sizes: "512x512",
              type: "image/png",
              purpose: "maskable",
            },
          ],
        },

        devOptions: {
          enabled: true,
        },
      }),
    ],

    server: {
      proxy: {
        "/api/v1": {
          target: API_URL,
          changeOrigin: true,
          secure: true,
        },
      },
    },
  };
});

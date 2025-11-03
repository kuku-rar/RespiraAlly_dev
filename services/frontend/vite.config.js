import { defineConfig, loadEnv } from "vite";
import react from "@vitejs/plugin-react";
import eslint from "vite-plugin-eslint";
import { resolve } from "path";
import { fileURLToPath, URL } from "node:url";

// https://vitejs.dev/config/
export default defineConfig(({ command, mode }) => {
  // --- 1. 環境設定與路徑解析 ---

  // 取得目前檔案的目錄路徑
  const __dirname = fileURLToPath(new URL(".", import.meta.url));
  const rootDir = resolve(__dirname, ".."); // <-- 指向專案根目錄

  // 🔥 載入環境變數
  // loadEnv 會從 process.env 讀取變數，並根據指定的 mode 和目錄來解析 .env 檔案
  // 第三個參數 '' 表示載入所有變數，但為了安全，建議維持預設的 'VITE_'
  const env = loadEnv(mode, rootDir, "");

  // 開發模式下，在終端機打印出重要的環境資訊，方便偵錯
  if (command === "serve") {
    console.log("🔧 Vite Config Initializing:", {
      mode,
      rootDir,
      vitePort: env.VITE_PORT,
      apiBaseUrl: env.VITE_API_BASE_URL,
      __dirname,
    });
  }

  // --- 2. 主要設定 ---

  return {
    // 設定專案的基礎公共路徑。'/' 表示根路徑，適用於標準的單頁應用 (SPA) 部署。
    base: "/",

    // --- 3. 插件 (Plugins) ---
    plugins: [
      // 啟用 React 插件，並整合 styled-jsx/babel 以提升 CSS-in-JS 效能
      react({
        babel: {
          plugins: [["styled-jsx/babel", { optimizeForSpeed: true }]],
        },
      }),
      // 僅在開發模式 (serve) 下啟用 ESLint 插件，用於即時程式碼品質檢查
      // 設定為非嚴格模式，警告和錯誤不會中斷開發伺服器
      ...(command === "serve"
        ? [
            eslint({
              failOnWarning: false,
              failOnError: false,
            }),
          ]
        : []),
    ],

    // --- 4. 路徑解析 (Resolve) ---
    resolve: {
      // 🔥 最佳實踐：防止 React 多版本衝突
      // `dedupe` 確保在整個專案中，指定的套件只會從一個地方被解析，避免因版本不一導致的錯誤。
      dedupe: ["react", "react-dom"],

      // 設定路徑別名，簡化 import 語句
      alias: {
        // 專案原始碼根目錄
        "@": resolve(__dirname, "./src"),

        // --- 共享模組 (Shared Modules) ---
        // 為了提高模組重用性，將共享資源設定高優先級別名
        "@shared": resolve(__dirname, "./src/shared"),
        "@shared/api": resolve(__dirname, "./src/shared/api"),
        "@shared/components": resolve(__dirname, "./src/shared/components"),
        "@shared/contexts": resolve(__dirname, "./src/shared/contexts"),
        "@shared/hooks": resolve(__dirname, "./src/shared/hooks"),
        "@shared/utils": resolve(__dirname, "./src/shared/utils"),
        "@shared/config": resolve(__dirname, "./src/shared/config.js"),

        // --- 多應用架構 (Multi-App Architecture) ---
        // 針對不同應用程式設定別名
        "@apps": resolve(__dirname, "./src/apps"),
        "@dashboard": resolve(__dirname, "./src/apps/dashboard"),
        "@liff-app": resolve(__dirname, "./src/apps/liff"),

        // --- 通用資源 (Common Resources) ---
        // 方便存取常用資源目錄
        "@assets": resolve(__dirname, "./src/assets"),
        "@styles": resolve(__dirname, "./src/styles"),
        "@pages": resolve(__dirname, "./src/pages"),

        // 🔥 最佳實踐：強制 React 使用專案根目錄的版本
        // 避免因不同路徑或依賴引入導致的多個 React 實例問題
        react: resolve(__dirname, "node_modules/react"),
        "react-dom": resolve(__dirname, "node_modules/react-dom"),
      },
    },

    // --- 5. 全域變數定義 (Define) ---
    // 在客戶端程式碼中注入全域常數
    define: {
      // 應用程式版本號，從 package.json 讀取
      __APP_VERSION__: JSON.stringify(env.npm_package_version || "1.0.0"),
      // 建置時間戳
      __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
    },

    // --- 6. 開發伺服器 (Server) ---
    server: {
      port: parseInt(env.VITE_PORT, 10) || 3000,
      host: "0.0.0.0", // 綁定所有網路介面
      strictPort: false,
      open: true, // 啟動時自動在瀏覽器中打開
      cors: true, // 啟用 CORS
      // 允許所有主機訪問（ngrok, 反向代理等）
      allowedHosts: [
        '.ngrok-free.app',
        '.ngrok.io',
        'localhost',
      ],
      // 為了在 Docker 環境中穩定觸發 HMR，啟用輪詢
      watch: {
        usePolling: true,
      },
      // 強制禁用瀏覽器快取，確保開發時總是載入最新的程式碼
      headers: {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        Pragma: "no-cache",
        Expires: "0",
      },
      // API 代理設定，解決開發時的跨域問題
      proxy: {
        "/api": {
          target: "http://web-app:5000", // 強制指向 Flask 後端服務
          changeOrigin: true, // 改變請求來源，使其看起來像是來自目標伺服器
          secure: false, // 後端 API 是 http，所以 secure 設定為 false
          rewrite: (path) => path, // 不重寫路徑
          // 監聽代理事件，提供詳細的日誌輸出，方便偵錯
          configure: (proxy) => {
            proxy.on("error", (err, req, res) => {
              console.error("🚨 Proxy Error:", err.message);
              if (!res.headersSent) {
                res.writeHead(500, { "Content-Type": "application/json" });
                res.end(JSON.stringify({
                  success: false,
                  error: { code: "PROXY_ERROR", message: "API proxy error. Check backend service." },
                }));
              }
            });
            proxy.on("proxyReq", (proxyReq, req) => {
              console.log(`🔄 [Proxy Req] ${req.method} ${req.url} -> ${proxyReq.path}`);
            });
            proxy.on("proxyRes", (proxyRes, req) => {
              const status = proxyRes.statusCode;
              const statusIcon = status >= 400 ? "❌" : status >= 300 ? "⚠️" : "✅";
              console.log(`${statusIcon} [Proxy Res] ${status}: ${req.url}`);
            });
          },
        },
      },
      // 熱模組替換 (HMR) 設定
      hmr: {
        overlay: true, // 在瀏覽器畫面上顯示錯誤覆蓋層
      },
    },

    // --- 7. 建置設定 (Build) ---
    build: {
      outDir: "dist", // 輸出目錄
      // 生產模式下不產生 sourcemap，其他模式下產生
      sourcemap: command === "build" && mode !== "production",
      minify: "esbuild", // 使用 esbuild 進行壓縮，速度更快
      // 設定建置目標，確保相容性
      target: ["es2020", "edge88", "firefox78", "chrome87", "safari14"],
      cssCodeSplit: true, // 啟用 CSS 程式碼分割
      cssMinify: true, // 壓縮 CSS

      rollupOptions: {
        output: {
          // --- 智慧化程式碼分割 (Code Splitting) ---
          manualChunks: (id) => {
            // 將大型或核心的 node_modules 分割成獨立的 chunk
            if (id.includes("node_modules")) {
              if (id.includes("recharts") || id.includes("d3")) return "vendor-charts";
              if (id.includes("@fullcalendar")) return "vendor-calendar";
              // 核心框架與常用庫合併為 vendor chunk
              return "vendor";
            }
            // 根據應用程式的進入點進行分割
            if (id.includes("/src/apps/dashboard/")) return "app-dashboard";
            if (id.includes("/src/apps/liff/")) return "app-liff";
            // 將共享模組打包成一個 chunk
            if (id.includes("/src/shared/")) return "shared";
          },

          // --- 檔案命名策略 ---
          // 確保檔案名稱帶有 hash，以利於快取管理
          entryFileNames: "js/[name]-[hash].js",
          chunkFileNames: "js/[name]-[hash].js",
          assetFileNames: (assetInfo) => {
            const ext = assetInfo.name.split(".").pop();
            if (/\.(png|jpe?g|gif|svg|webp|ico)$/.test(assetInfo.name)) return `images/[name]-[hash].${ext}`;
            if (/\.(woff2?|ttf|eot)$/.test(assetInfo.name)) return `fonts/[name]-[hash].${ext}`;
            if (/\.(css)$/.test(assetInfo.name)) return `css/[name]-[hash].${ext}`;
            return `assets/[name]-[hash].${ext}`;
          },
        },
        // 🔥 最佳實踐：永遠不要將 React 等核心庫外部化 (external)
        // 應由 Vite 自行打包，以確保 chunk 的穩定性和一致性
        external: [],
      },
      chunkSizeWarningLimit: 1000, // 將大 chunk 警告閾值提高到 1000KB
      // 模組預載入設定
      modulePreload: {
        polyfill: true,
      },
    },

    // --- 8. 依賴預構建 (Optimize Deps) ---
    // 優化大型或常用依賴，加快冷啟動速度
    optimizeDeps: {
      include: [
        "react",
        "react-dom",
        "react-router-dom",
        "@tanstack/react-query",
        "recharts",
        "dayjs",
        "clsx",
      ],
      exclude: [
        // 排除 @line/liff，因為其內部模組結構需要特殊處理
        "@line/liff",
      ],
    },

    // --- 9. CSS 設定 ---
    css: {
      devSourcemap: true, // 開發模式下啟用 CSS sourcemap
      modules: {
        localsConvention: "camelCase", // CSS Modules 使用駝峰命名
      },
    },

    // --- 10. 測試設定 (Vitest) ---
    test: {
      globals: true,
      environment: "jsdom", // 模擬 DOM 環境
      setupFiles: ["./src/setupTests.js"], // 測試設定檔案
    },
  };
});

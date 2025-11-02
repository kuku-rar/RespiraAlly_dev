import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import App from "./App";
import "./styles/index.css";

// 🧹 開發模式下清理 LIFF 緩存
if (import.meta.env.DEV) {
  // 清理任何舊的 LIFF SDK 引用
  if (typeof window !== "undefined" && window.liff) {
    console.log("🧹 清理舊的 LIFF SDK 引用");
    delete window.liff;
    window.liff = null;
  }
}

// 建立 QueryClient 實例
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 分鐘
      gcTime: 10 * 60 * 1000, // 10 分鐘 (原 cacheTime)
      retry: 3,
      refetchOnWindowFocus: false,
      refetchOnMount: true,
    },
    mutations: {
      retry: 1,
    },
  },
});

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      {import.meta.env.DEV && <ReactQueryDevtools initialIsOpen={false} />}
    </QueryClientProvider>
  </React.StrictMode>
);

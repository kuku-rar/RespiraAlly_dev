import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";

// 環境檢查 - 根據用戶的變數命名習慣
const isDevelopment = import.meta.env.DEV;
const disableLiff = import.meta.env.VITE_DISABLE_LIFF === "true";
const enableMock = import.meta.env.VITE_ENABLE_MOCK === "true";
const forceDevMode = import.meta.env.VITE_FORCE_DEV_MODE === "true";
const liffId = import.meta.env.VITE_LIFF_ID;

// LIFF SDK 動態載入
const loadLiffSDK = () => {
  return new Promise((resolve, reject) => {
    // 如果已經載入，直接返回
    if (window.liff) {
      resolve(window.liff);
      return;
    }

    // 動態載入 LIFF SDK
    const script = document.createElement("script");
    script.src = "https://static.line-scdn.net/liff/edge/2/sdk.js";
    script.onload = () => {
      if (window.liff) {
        resolve(window.liff);
      } else {
        reject(new Error("LIFF SDK 載入失敗"));
      }
    };
    script.onerror = () => reject(new Error("無法載入 LIFF SDK"));
    document.head.appendChild(script);
  });
};

export const useLIFF = () => {
  const location = useLocation();
  const isLiffRoute = location.pathname.startsWith("/liff");

  // 狀態管理
  const [state, setState] = useState({
    isLoggedIn: false,
    profile: null,
    isInClient: false,
    isReady: false,
    error: null,
    idToken: null,
    needsRegistration: false,
    authProcessing: false,
  });

  // LIFF 路由：根據環境決定使用 Mock 或真實 LIFF
  const useMockMode =
    isDevelopment || enableMock || disableLiff || forceDevMode;

  useEffect(() => {
    // 只在 LIFF 路由中初始化
    if (!isLiffRoute) {
      return;
    }
    const initializeLiff = async () => {
      setState((prev) => ({ ...prev, authProcessing: true, error: null }));

      try {
        if (useMockMode) {
          // 開發模式：使用 Mock 數據
          console.log("🎨 LIFF Mock 模式啟動", {
            isDevelopment,
            enableMock,
            disableLiff,
            forceDevMode,
            liffId,
          });
          setState({
            isLoggedIn: true,
            profile: {
              userId: "ui-dev-user",
              displayName: "UI 測試用戶",
              pictureUrl:
                "https://via.placeholder.com/200x200/4A90E2/FFFFFF?text=UI",
              statusMessage: "UI 開發中",
            },
            isInClient: false,
            isReady: true,
            error: null,
            idToken: "mock-token",
            needsRegistration: false,
            authProcessing: false,
          });
          return;
        }

        // 生產模式：真實 LIFF 初始化
        if (!liffId) {
          throw new Error("LIFF ID 未設定，請在環境變數中設定 VITE_LIFF_ID");
        }

        console.log("🔧 開始 LIFF 初始化，ID:", liffId);

        // 載入 LIFF SDK
        await loadLiffSDK();

        // 初始化 LIFF
        await window.liff.init({ liffId });

        console.log("✅ LIFF 初始化成功");

        // 檢查登入狀態
        const isLoggedIn = window.liff.isLoggedIn();
        const isInClient = window.liff.isInClient();

        if (!isLoggedIn) {
          // 未登入，導向 LINE 登入
          console.log("🔐 用戶未登入，導向 LINE 登入");
          setState((prev) => ({
            ...prev,
            isReady: true,
            isInClient,
            authProcessing: false,
          }));
          return;
        }

        // 已登入，取得用戶資料
        const profile = await window.liff.getProfile();
        const idToken = window.liff.getIDToken();

        console.log("👤 用戶已登入:", profile.displayName);

        setState({
          isLoggedIn: true,
          profile: {
            userId: profile.userId,
            displayName: profile.displayName,
            pictureUrl: profile.pictureUrl,
            statusMessage: profile.statusMessage,
          },
          isInClient,
          isReady: true,
          error: null,
          idToken,
          needsRegistration: false, // 可根據後端 API 檢查決定
          authProcessing: false,
        });
      } catch (error) {
        console.error("❌ LIFF 初始化失敗:", error);
        setState((prev) => ({
          ...prev,
          error: error.message,
          isReady: true,
          authProcessing: false,
        }));
      }
    };

    // 初始化 LIFF
    initializeLiff();
  }, [isLiffRoute, useMockMode]);

  // LIFF 功能函數
  const login = () => {
    if (useMockMode) {
      console.log("🎨 Mock 登入");
      return;
    }

    if (window.liff && !window.liff.isLoggedIn()) {
      window.liff.login();
    }
  };

  const logout = () => {
    if (useMockMode) {
      console.log("🎨 Mock 登出");
      window.location.reload();
      return;
    }

    if (window.liff && window.liff.isLoggedIn()) {
      window.liff.logout();
      window.location.reload();
    }
  };

  const handleRegisterSuccess = async (userData) => {
    console.log("✅ 用戶註冊成功:", userData);
    setState((prev) => ({ ...prev, needsRegistration: false }));
  };

  const getAccessToken = () => {
    if (useMockMode) {
      return "mock-access-token";
    }

    return window.liff && window.liff.isLoggedIn()
      ? window.liff.getAccessToken()
      : null;
  };

  const openExternalBrowser = (url) => {
    if (useMockMode || !window.liff || !window.liff.isInClient()) {
      window.open(url, "_blank");
      return;
    }

    window.liff.openExternalBrowser(url);
  };

  const closeWindow = () => {
    if (useMockMode) {
      console.log("🎨 Mock 關閉視窗");
      return;
    }

    if (window.liff && window.liff.isInClient()) {
      window.liff.closeWindow();
    } else {
      window.close();
    }
  };

  const shareMessage = async (messages) => {
    if (useMockMode) {
      console.log("🎨 Mock 分享訊息:", messages);
      return true;
    }

    if (!window.liff || !window.liff.isApiAvailable("shareTargetPicker")) {
      console.warn("分享功能不可用");
      return false;
    }

    try {
      await window.liff.shareTargetPicker(messages);
      return true;
    } catch (error) {
      console.error("分享失敗:", error);
      return false;
    }
  };

  // 如果不在 LIFF 路由中，返回空的實現（Dashboard 等其他路由）
  if (!isLiffRoute) {
    return {
      isLoggedIn: false,
      profile: null,
      isInClient: false,
      isReady: false,
      error: null,
      idToken: null,
      needsRegistration: false,
      authProcessing: false,
      login: () => console.log("非 LIFF 路由，忽略登入"),
      logout: () => console.log("非 LIFF 路由，忽略登出"),
      handleRegisterSuccess: () => console.log("非 LIFF 路由，忽略註冊"),
      getAccessToken: () => null,
      openExternalBrowser: (url) => window.open(url, "_blank"),
      closeWindow: () => console.log("非 LIFF 路由，忽略關閉"),
      shareMessage: () => Promise.resolve(false),
      isBackendAuthenticated: false,
      backendUser: null,
    };
  }

  return {
    ...state,
    login,
    logout,
    handleRegisterSuccess,
    getAccessToken,
    openExternalBrowser,
    closeWindow,
    shareMessage,
    // 後端認證狀態（可根據需要實現）
    isBackendAuthenticated: useMockMode ? true : !!state.idToken,
    backendUser: useMockMode
      ? {
          id: 1,
          first_name: "測試",
          last_name: "用戶",
        }
      : null,
  };
};

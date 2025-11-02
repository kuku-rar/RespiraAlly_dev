/* eslint-disable react-refresh/only-export-components */
import { createContext, useContext, useState, useEffect } from "react";
import { apiClient, setToken, clearToken } from "../api/client";
import { API_ENDPOINTS } from "../config";

const AuthContext = createContext({});

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  // 檢查現有 token 並驗證
  useEffect(() => {
    // 檢查是否強制開發模式自動登入（只有在環境變數明確設定時才啟用）
    if (import.meta.env.VITE_FORCE_DEV_MODE === "true") {
      setUser({
        id: "therapist_01",
        account: "therapist_01",
        first_name: "王",
        last_name: "小明",
        is_staff: true,
        is_admin: false,
      });
      setIsLoading(false);
      return;
    }

    const token =
      localStorage.getItem("token") || sessionStorage.getItem("token");
    if (token) {
      validateToken();
    } else {
      setIsLoading(false);
    }
  }, []);

  const validateToken = async () => {
    try {
      // TODO: 實作 token 驗證 API
      // const response = await apiClient.get('/auth/validate')
      // setUser(response.user)

      // 暫時模擬 - 測試用治療師帳號
      setUser({
        id: "therapist_01",
        account: "therapist_01",
        first_name: "王",
        last_name: "小明",
        is_staff: true,
        is_admin: false,
      });
    } catch {
      clearToken();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (credentials) => {
    try {
      const response = await apiClient.post(API_ENDPOINTS.LOGIN, credentials);

      // 處理後端的響應格式 { data: { token, user } }
      const { token, user } = response.data || response;

      setToken(token, credentials.remember);
      setUser(user);

      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const lineLogin = async (lineProfile) => {
    try {
      const response = await apiClient.post(
        API_ENDPOINTS.LINE_LOGIN,
        lineProfile
      );
      const { token, user } = response;

      setToken(token, true);
      setUser(user);

      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  };

  const logout = () => {
    clearToken();
    setUser(null);
    window.location.href = "/login";
  };

  const value = {
    user,
    isLoading,
    isAuthenticated: !!user,
    isStaff: user?.is_staff || false,
    isAdmin: user?.is_admin || false,
    login,
    lineLogin,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

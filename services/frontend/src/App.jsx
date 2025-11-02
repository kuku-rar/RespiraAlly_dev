import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Suspense, lazy } from "react";
import { AuthProvider } from "./shared/contexts/AuthContext";
import { ThemeProvider } from "./shared/contexts/ThemeContext";
import { AccessibilityProvider } from "./shared/contexts/AccessibilityContext";
import LoadingSpinner from "./shared/components/LoadingSpinner";

// 分離的應用路由
const LiffRoutes = lazy(() => import("./apps/liff/routes"));
const DashboardRoutes = lazy(() => import("./apps/dashboard/routes"));
const LoginPage = lazy(() => import("./pages/LoginPage"));

function App() {
  return (
    <BrowserRouter
      future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
    >
      <AuthProvider>
        <ThemeProvider>
          <AccessibilityProvider>
            <Suspense fallback={<LoadingSpinner fullScreen />}>
              <Routes>
                {/* 登入頁面 */}
                <Route path="/login" element={<LoginPage />} />

                {/* LIFF 應用 (病患端) */}
                <Route path="/liff/*" element={<LiffRoutes />} />

                {/* Dashboard 應用 (治療師端) */}
                <Route path="/dashboard/*" element={<DashboardRoutes />} />

                {/* 根路徑導向 - 開發模式直接到 Dashboard */}
                <Route
                  path="/"
                  element={<Navigate to="/dashboard" replace />}
                />

                {/* 404 處理 */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Suspense>
          </AccessibilityProvider>
        </ThemeProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;

import { lazy } from "react";
import { Routes, Route, Navigate } from "react-router-dom";

// LIFF 頁面
const PatientHome = lazy(() => import("./pages/PatientHome"));
const VoiceChat = lazy(() => import("./pages/VoiceChat"));
const CATForm = lazy(() => import("./pages/CATForm"));
const MMRCForm = lazy(() => import("./pages/MMRCForm"));
const DailyMetrics = lazy(() => import("./pages/DailyMetrics"));
const ThankYou = lazy(() => import("./pages/ThankYou"));
const RegisterPage = lazy(() => import("./pages/RegisterPage"));

const LiffRoutes = () => {
  return (
    <Routes>
      {/* LIFF 主頁 */}
      <Route path="/" element={<PatientHome />} />

      {/* 功能頁面 */}
      <Route path="/voice-chat" element={<VoiceChat />} />
      <Route path="/daily-metrics" element={<DailyMetrics />} />

      {/* 問卷頁面 */}
      <Route path="/questionnaire">
        <Route path="cat" element={<CATForm />} />
        <Route path="mmrc" element={<MMRCForm />} />
        <Route path="thankyou" element={<ThankYou />} />
      </Route>

      {/* 註冊頁面 */}
      <Route path="/register" element={<RegisterPage />} />

      {/* 預設導向 */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default LiffRoutes;

import { lazy } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import DashboardLayout from "./layouts/Layout";
import ProtectedRoute from "../../shared/components/ProtectedRoute";

// Dashboard 頁面
const OverviewPage = lazy(() => import("./pages/OverviewPage"));
const CasesPage = lazy(() => import("./pages/CasesPage"));
const PatientDetail = lazy(() => import("./pages/PatientDetail"));
const EducationPage = lazy(() => import("./pages/EducationPage"));
const TherapistTasksPage = lazy(() => import("./pages/TherapistTasksPage"));
const SettingsPage = lazy(() => import("./pages/SettingsPage"));

const DashboardRoutes = () => {
  return (
    <Routes>
      {/* Dashboard 需要治療師權限 */}
      <Route element={<ProtectedRoute requireStaff={true} />}>
        <Route element={<DashboardLayout />}>
          <Route index element={<Navigate to="overview" replace />} />
          <Route path="overview" element={<OverviewPage />} />

          <Route path="cases">
            <Route index element={<CasesPage />} />
            <Route path=":id" element={<PatientDetail />} />
          </Route>

          <Route path="education" element={<EducationPage />} />
          <Route path="tasks" element={<TherapistTasksPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Route>

      {/* 404 處理 */}
      <Route path="*" element={<Navigate to="overview" replace />} />
    </Routes>
  );
};

export default DashboardRoutes;

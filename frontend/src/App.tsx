import { Navigate, Route, Routes } from "react-router-dom";
import AppBar from "@/components/AppBar";
import LoginPage from "@/features/auth/LoginPage";
import DashboardPage from "@/features/reporting/DashboardPage";
import PrintersPage from "@/features/printers/PrintersPage";
import JobsPage from "@/features/jobs/JobsPage";
import QuotasPage from "@/features/quotas/QuotasPage";
import AlertsPage from "@/features/alerts/AlertsPage";
import DeveloperTokensPage from "@/features/developerTokens/DeveloperTokensPage";
import { useAuthStore } from "@/store/auth";

function Protected({ children }: { children: React.ReactNode }) {
  const token = useAuthStore((s) => s.accessToken);
  if (!token) return <Navigate to="/login" replace />;
  return <>{children}</>;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/*"
        element={
          <Protected>
            <AppBar />
            <Routes>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/printers" element={<PrintersPage />} />
              <Route path="/jobs" element={<JobsPage />} />
              <Route path="/quotas" element={<QuotasPage />} />
              <Route path="/alerts" element={<AlertsPage />} />
              <Route path="/developer-tokens" element={<DeveloperTokensPage />} />
            </Routes>
          </Protected>
        }
      />
    </Routes>
  );
}
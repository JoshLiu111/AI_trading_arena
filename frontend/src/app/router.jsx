import { lazy, Suspense } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { LoadingWrapper } from "@/ui";
import { Nav } from "@/ui";
import ErrorBoundary from "@/ui/ErrorBoundary";

// Lazy load routes for code splitting
const Home = lazy(() => {
  return import("@/pages/Home").catch((error) => {
    console.error("Failed to load Home:", error);
    throw error;
  });
});

const Dashboard = lazy(() => {
  return import("@/features/dashboard").then(module => ({ default: module.Dashboard })).catch((error) => {
    console.error("Failed to load Dashboard:", error);
    throw error;
  });
});

const StockDetail = lazy(() => import("@/pages/StockDetail"));
const AccountDetail = lazy(() => import("@/pages/AccountDetail"));
const LearnMore = lazy(() => import("@/pages/LearnMore"));

/**
 * React Router configuration with code splitting
 */
export function AppRouter({ children }) {
  return (
    <Router>
      <ErrorBoundary>
        <Nav />
        <Suspense fallback={<LoadingWrapper loading={true} />}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/stock/:ticker" element={<StockDetail />} />
          <Route path="/account/:accountId" element={<AccountDetail />} />
          <Route path="/learn-more" element={<LearnMore />} />
        </Routes>
        </Suspense>
        {children}
      </ErrorBoundary>
    </Router>
  );
}


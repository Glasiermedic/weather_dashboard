import React, { Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./layout/Layout";

// Lazy main pages
const LandingPage = lazy(() => import("./pages/LandingPage"));
const WeatherDashboard = lazy(() => import("./pages/WeatherDashboard"));
const About = lazy(() => import("./pages/About"));
const Results = lazy(() => import("./pages/Results"));

// Lazy tab panels for Results
const MlResultsTab = lazy(() => import("./pages/results/MlResultsTab"));
const EtlResultsTab = lazy(() => import("./pages/results/EtlResultsTab"));
const WaveResultsTab = lazy(() => import("./pages/results/WaveResultsTab"));
const MaintenanceResultsTab = lazy(
  () => import("./pages/results/MaintenanceResultsTab")
);

function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div className="app-main">Loading…</div>}>
        <Routes>
          {/* Layout = shared shell (header + navbar + sidebar) */}
          <Route element={<Layout />}>
            {/* "/" → Landing page */}
            <Route index element={<LandingPage />} />

            {/* "/stations" → Weather dashboard */}
            <Route path="/stations" element={<WeatherDashboard />} />

            {/* About page */}
            <Route path="/about" element={<About />} />

            {/* Results with nested tab routes */}
            <Route path="/results" element={<Results />}>
              <Route index element={<MlResultsTab />} />
              <Route path="etl" element={<EtlResultsTab />} />
              <Route path="wave" element={<WaveResultsTab />} />
              <Route path="maintenance" element={<MaintenanceResultsTab />} />
            </Route>
          </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;

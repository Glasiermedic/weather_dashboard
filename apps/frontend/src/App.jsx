// src/App.jsx
import React, { Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./layout/Layout";

// 🔹 Lazy-loaded pages (code-splitting)
const WeatherDashboard = lazy(() => import("./pages/WeatherDashboard"));
const Results = lazy(() => import("./pages/Results"));
const About = lazy(() => import("./pages/About"));

function App() {
  return (
    <BrowserRouter>
      {/* Suspense shows a fallback while lazy chunks load */}
      <Suspense fallback={<div className="app-main">Loading...</div>}>
        <Routes>
          {/* Layout is the shared shell (header + sidebar + glasier theme) */}
          <Route element={<Layout />}>
            {/* index = "/" → main landing page / dashboard */}
            <Route index element={<WeatherDashboard />} />

            {/* Results page for roadmap/tabs/etc. */}
            <Route path="/results" element={<Results />} />

            {/* About page (this will also match your sidebar /about link) */}
            <Route path="/about" element={<About />} />
          </Route>
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}

export default App;

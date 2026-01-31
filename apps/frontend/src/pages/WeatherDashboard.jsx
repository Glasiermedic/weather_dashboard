// src/pages/WeatherDashboard.jsx
import React from "react";

function WeatherDashboard() {
  return (
    <div>
      <h1 className="landing-page-title">Weather Dashboard</h1>
      <p className="landing-page-subtitle">
        Explore hourly conditions, wave energy signals, and buoy health across the Glasier network.
      </p>

      {/* Top: summary strip */}
      <section className="landing-section">
        <div className="landing-section-text">
          <h2>Key Summaries</h2>
          <p>
            This area will surface your key metrics: current buoy status, average power generation, and
            upcoming maintenance risk.
          </p>
        </div>
      </section>

      {/* Bottom: adaptive grid for charts/summaries/controls */}
      <section className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 p-4">
        <div className="rounded-xl border border-slate-200 bg-white shadow-sm p-4">
          <h2 className="text-sm font-semibold text-slate-800 mb-2">Charts</h2>
          <p className="text-slate-600 mb-3">
            Slot for time series charts (temperature, precipitation, wind gust, power, etc.).
          </p>
          <ul className="list-disc pl-5 text-slate-700 space-y-1">
            <li>Hourly temperature</li>
            <li>Wave height &amp; power density</li>
            <li>Buoy health trend</li>
          </ul>
          <div className="mt-4 h-64 rounded-lg bg-slate-50" />
        </div>

        <div className="rounded-xl border border-slate-200 bg-white shadow-sm p-4">
          <h2 className="text-sm font-semibold text-slate-800 mb-2">Selectors &amp; Filters</h2>
          <p className="text-slate-600 mb-3">
            Slot for station/buoy selectors, time range controls, model selection, and other inputs
            that drive the charts.
          </p>
          <div className="space-y-3">
            <div className="h-10 rounded-lg bg-slate-50" />
            <div className="h-10 rounded-lg bg-slate-50" />
            <div className="h-10 rounded-lg bg-slate-50" />
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white shadow-sm p-4">
          <h2 className="text-sm font-semibold text-slate-800 mb-2">Buoy Health</h2>
          <p className="text-slate-600 mb-3">
            Slot for alerts, last-seen timestamps, battery trends, and offline warnings.
          </p>
          <div className="h-64 rounded-lg bg-slate-50" />
        </div>
      </section>
    </div>
  );
}

export default WeatherDashboard;

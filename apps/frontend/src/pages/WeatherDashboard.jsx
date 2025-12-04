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

      {/* Bottom: two-column “slots” for charts & selectors */}
      <div className="landing-sections">
        <section className="landing-section">
          <div className="landing-section-col">
            <div className="landing-section-text">
              <h2>Charts</h2>
              <p>
                Slot for time series charts (temperature, precipitation, wind gust, power, etc.).
              </p>
              <ul>
                <li>Hourly temperature</li>
                <li>Wave height &amp; power density</li>
                <li>Buoy health trend</li>
              </ul>
            </div>
          </div>
          <div className="landing-section-col">
            <div className="landing-section-text">
              <h2>Selectors &amp; Filters</h2>
              <p>
                Slot for station/buoy selectors, time range controls, model selection, and other inputs
                that drive the charts.
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default WeatherDashboard;

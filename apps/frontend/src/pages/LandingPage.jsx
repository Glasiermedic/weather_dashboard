// src/pages/LandingPage.jsx
import React from "react";
import CircleLink from "../components/CircleLink";

import weatherIcon from "../assets/Weather Data_transparent.png";
import buoyIcon from "../assets/Buoy Analytics_transparent.png";
import mlIcon from "../assets/Machine Learning_transparent.png";

function LandingPage() {
  return (
    <div>
      <h1 className="landing-page-title">Landing Page</h1>
      <p className="landing-page-subtitle">
        A static preview of the Glasier layout with logo, glacier theme, left nav,
        and circular portal links.
      </p>

      <div className="landing-sections">
        <section className="landing-section">
          <div className="landing-section-col">
            <CircleLink to="/stations" src={weatherIcon} alt="Stations & Buoys" />
          </div>
          <div className="landing-section-col">
            <div className="landing-section-text">
              <h2>Stations &amp; Buoys</h2>
              <p>
                Explore coastal, buoy, and land-based stations—coverage, health,
                and real-time conditions along the Glasier network.
              </p>
            </div>
          </div>
        </section>

        <section className="landing-section landing-section-right">
          <div className="landing-section-col">
            <div className="landing-section-text">
              <h2>Wave Energy &amp; Power Experiments</h2>
              <p>
                Visualize wave height, period, and power density to support
                ocean energy experiments and planning.
              </p>
            </div>
          </div>
          <div className="landing-section-col">
            <CircleLink
              to="/wave-energy"
              src={buoyIcon}
              alt="Wave Energy"
            />
          </div>
        </section>

        <section className="landing-section">
          <div className="landing-section-col">
            <CircleLink
              to="/ml/hourly-forecasts"
              src={mlIcon}
              alt="ML Forecasts"
            />
          </div>
          <div className="landing-section-col">
            <div className="landing-section-text">
              <h2>ML Forecasts</h2>
              <p>
                Forecast hourly temperature, wind, precipitation, power generation,
                and buoy maintenance risk using Glasier’s ML stack.
              </p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

export default LandingPage;

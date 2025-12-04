// src/pages/About.jsx
import React from "react";

function About() {
  return (
    <div>
      <h1 className="landing-page-title">About Glasier Weather</h1>
      <p className="landing-page-subtitle">
        Why this project exists, what it’s aiming to do, and the values behind it.
      </p>

      <div className="landing-sections">
        <section className="landing-section">
          <div className="landing-section-text">
            <h2>Mission</h2>
            <p>
              Glasier Weather brings together real-world ocean buoys, personal weather stations,
              airport data, and machine learning to support decisions around wave energy, forecasting,
              and system reliability. It’s a place where telemetry, analytics, and design all meet.
            </p>
          </div>
        </section>

        <section className="landing-section landing-section-right">
          <div className="landing-section-text">
            <h2>Faith Integration</h2>
            <p>
              “By wisdom a house is built, and through understanding it is established;
              through knowledge its rooms are filled with rare and beautiful treasures.”
            </p>
            <p>
              This project treats data, models, and tools as part of that “house”—built with wisdom,
              established with understanding, and filled with meaningful insights rather than noise.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}

export default About;

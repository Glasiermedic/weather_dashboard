// apps/frontend/src/pages/results/WaveResultsTab.jsx
import React from "react";

function WaveResultsTab() {
  return (
    <section className="results-tabpanel">
      <h2>Wave Energy Experiments</h2>
      <p>
        This panel will visualize metrics that matter to Panthalassa and
        other wave-energy consumers: wave height, period, direction, and
        estimated power.
      </p>
      <ul>
        <li>Recent wave power estimates per buoy</li>
        <li>Experiment runs and scenarios</li>
        <li>Links to drill-down views in the Wave Energy page</li>
      </ul>
    </section>
  );
}

export default WaveResultsTab;

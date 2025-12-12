// apps/frontend/src/pages/results/EtlResultsTab.jsx
import React from "react";

function EtlResultsTab() {
  return (
    <section className="results-tabpanel">
      <h2>ETL &amp; Data Freshness</h2>
      <p>
        This panel will track your ETL pipelines: when they ran, how long
        they took, and whether each step succeeded.
      </p>
      <ul>
        <li>Last successful run time per pipeline</li>
        <li>Lag between raw feeds and gold tables</li>
        <li>Alerts or warnings for stale data</li>
      </ul>
    </section>
  );
}

export default EtlResultsTab;

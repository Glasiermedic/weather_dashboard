import React from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";

const RESULTS_TABS = [
  { to: "/results", label: "ML Models", end: true },
  { to: "/results/etl", label: "ETL & Freshness" },
  { to: "/results/wave", label: "Wave Energy" },
  { to: "/results/maintenance", label: "Buoy Maintenance" },
];

function Results() {
  const location = useLocation();

  return (
    <div>
      <h1 className="landing-page-title">Results &amp; Roadmap</h1>
      <p className="landing-page-subtitle">
        View model performance, data freshness, wave energy experiments, and
        buoy maintenance insights in one place.
      </p>

      {/* Faith Integration: keep it as a subtle supporting line */}
      <p className="landing-page-subtitle" style={{ fontSize: "0.85rem" }}>
        “Trust in the Lord with all your heart and lean not on your own
        understanding; in all your ways submit to him, and he will make your
        paths straight.”
      </p>

      {/* Tab navigation using NavLink */}
      <div className="results-tabs" role="tablist">
        {RESULTS_TABS.map((tab) => (
          <NavLink
            key={tab.to}
            to={tab.to}
            end={tab.end}
            className={({ isActive }) =>
              "results-tab" + (isActive ? " active" : "")
            }
            role="tab"
            aria-selected={
              location.pathname === tab.to ||
              (tab.end && location.pathname === "/results" && tab.to === "/results")
            }
          >
            {tab.label}
          </NavLink>
        ))}
      </div>

      {/* Nested route content for the active tab */}
      <Outlet />
    </div>
  );
}

export default Results;

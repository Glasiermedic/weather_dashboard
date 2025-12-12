// apps/frontend/src/components/Navbar.jsx
import React from "react";
import { NavLink } from "react-router-dom";
import NavIcon from "./NavIcon";

// 🔹 Round transparent icons in apps/frontend/src/assets
// (filenames taken from your uploads – keep them if they match)
import stationsIcon from "../assets/Weather Data_transparent.png";
import waveIcon from "../assets/Buoy Analytics_transparent.png";
import mlIcon from "../assets/Machine Learning_transparent.png";
import resultsIcon from "../assets/Results_transparent.png";

// Default nav items for the main Glasier shell
const DEFAULT_NAV_ITEMS = [
  { to: "/", label: "Home", end: true, icon: null },           // text-only for now
  { to: "/stations", label: "Stations", icon: stationsIcon },
  { to: "/wave-energy", label: "Wave Energy", icon: waveIcon },
  { to: "/results", label: "Results", icon: resultsIcon },
  { to: "/ml/hourly-forecasts", label: "ML Forecasts", icon: mlIcon },
];

function Navbar({ items = DEFAULT_NAV_ITEMS }) {
  return (
    <nav className="app-top-nav">
      {items.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.end}
          className={({ isActive }) =>
            "top-nav-link" + (isActive ? " active" : "")
          }
        >
          <NavIcon icon={item.icon} label={item.label} />
        </NavLink>
      ))}
    </nav>
  );
}

export default Navbar;
export { DEFAULT_NAV_ITEMS };

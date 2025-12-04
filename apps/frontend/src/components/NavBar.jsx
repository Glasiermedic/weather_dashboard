// components/Navbar.jsx
import React from "react";
import { NavLink } from "react-router-dom";

const TOP_NAV_ITEMS = [
  { to: "/", label: "Home", end: true },
  { to: "/stations", label: "Stations" },
  { to: "/wave-energy", label: "Wave Energy" },
  { to: "/ml/hourly-forecasts", label: "ML Forecasts" },
];

function Navbar() {
  return (
    <nav className="app-top-nav">
      {TOP_NAV_ITEMS.map((item) => (
        <NavLink
          key={item.to}
          to={item.to}
          end={item.end}
          className={({ isActive }) =>
            "top-nav-link" + (isActive ? " active" : "")
          }
        >
          {item.label}
        </NavLink>
      ))}
    </nav>
  );
}

export default Navbar;

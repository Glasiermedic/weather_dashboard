// src/layout/Layout.jsx
import React from "react";
import { Outlet } from "react-router-dom";
import glasierLogo from "../assets/optimized/Glasier Data Logo.webp";
import Navbar from "../components/Navbar";
import Sidebar from "../components/Sidebar";

function Layout() {
  return (
    <div className="app-root">
      <header className="app-header">
        <div className="app-header-left">
          <img
            src={glasierLogo}
            alt="Glasier Data"
            className="app-logo-image"
          />
          <span className="app-name">Glasier Weather Observatory</span>
        </div>

        {/* Top navigation bar */}
        <Navbar />

        <div className="app-header-right">
          <span className="app-status">
            ETL: <span className="status-dot status-ok" /> OK
          </span>
          <span className="user-chip">WR</span>
        </div>
      </header>

      <div className="app-body">
        {/* Left sidebar navigation */}
        <Sidebar />

        {/* Main routed content */}
        <main className="app-main">
          <Outlet />
        </main>
      </div>
    </div>
  );
}

export default Layout;

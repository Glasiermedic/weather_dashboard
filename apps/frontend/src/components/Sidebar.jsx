// src/components/Sidebar.jsx
import React from "react";
import { NavLink } from "react-router-dom";

const DEFAULT_PROFILE_ITEMS = [
  { to: "/about", label: "About Me" },
  { to: "/mission", label: "Mission" },
];

const DEFAULT_LINK_ITEMS = [
  { href: "https://glasierdata.atlassian.net", label: "Jira" },
  { href: "https://github.com/Glasiermedic", label: "GitHub" },
];

function Sidebar({
  profileItems = DEFAULT_PROFILE_ITEMS,
  linkItems = DEFAULT_LINK_ITEMS,
}) {
  return (
    <aside className="app-sidebar">
      {/* Profile section */}
      <div className="sidebar-section">
        <div className="sidebar-section-title">Profile</div>
        {profileItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className="sidebar-link"
          >
            {item.label}
          </NavLink>
        ))}
      </div>

      {/* Links section */}
      <div className="sidebar-section">
        <div className="sidebar-section-title">Links</div>
        {linkItems.map((item) => (
          <a
            key={item.href}
            href={item.href}
            target="_blank"
            rel="noreferrer"
            className="sidebar-link sidebar-link-external"
          >
            {item.label}
          </a>
        ))}
      </div>
    </aside>
  );
}

export default Sidebar;
export { DEFAULT_PROFILE_ITEMS, DEFAULT_LINK_ITEMS };

// apps/frontend/src/components/NavIcon.jsx
import React from "react";

/**
 * NavIcon is a tiny presentational component used inside Navbar.
 * It renders the round icon + label in a consistent Glasier style.
 */
function NavIcon({ icon, label }) {
  return (
    <span className="top-nav-item">
      {icon && (
        <img
          src={icon}
          alt=""
          className="top-nav-icon"
          aria-hidden="true"
        />
      )}
      <span className="top-nav-label">{label}</span>
    </span>
  );
}

export default NavIcon;
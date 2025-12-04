// src/components/CircleLink.jsx
import React from "react";
import { Link } from "react-router-dom";

function CircleLink({ to, src, alt }) {
  return (
    <Link to={to} className="circle-link" aria-label={alt}>
      <div className="circle-link-inner">
        <img src={src} alt={alt} className="circle-link-image" />
      </div>
    </Link>
  );
}

export default CircleLink;

import React from "react";
import { Link } from "react-router-dom";
import ebeLogo from "../assets/ebe-logo-dark.jpg";
import "./ebe.css";

function Ebe() {
  return (
    <main className="ebe-page">
      <section className="ebe-hero" aria-labelledby="ebe-title">
        <div className="ebe-glow ebe-glow-one" aria-hidden="true" />
        <div className="ebe-glow ebe-glow-two" aria-hidden="true" />

        <div className="ebe-logo-frame">
          <img className="ebe-logo" src={ebeLogo} alt="Ebe logo" />
        </div>

        <p className="ebe-kicker">Something thoughtful is taking shape</p>
        <h1 id="ebe-title">Ebe is under construction</h1>
        <p className="ebe-description">
          Ebe will be a personal thought engine—a place to capture ideas,
          connect memories and observations, and develop them into stories,
          songs, plans, and other meaningful creative work.
        </p>

        <div className="ebe-status" role="status">
          <span className="ebe-status-dot" aria-hidden="true" />
          Building the first experience
        </div>

        <Link className="ebe-home-link" to="/">
          Return to Glasier Data
        </Link>
      </section>
    </main>
  );
}

export default Ebe;

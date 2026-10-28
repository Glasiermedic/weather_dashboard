import React from 'react';
import { Link } from 'react-router-dom';
import './Music.css';

export default function Music() {
  return (
    <div className="music-page">
      <section className="music-hero" aria-labelledby="music-heading">
        <img
          className="music-hero-image"
          src="/images/jesus-faith-songwriter-cover.jpg"
          alt="A faith-centered songwriter working at a piano surrounded by family photographs and song notes"
        />
        <div className="music-hero-shade" />
        <div className="music-hero-copy">
          <p className="music-eyebrow music-eyebrow-light">WESLEY ROLFSON / ORIGINAL MUSIC</p>
          <h1 id="music-heading">Songs that point beyond the noise.</h1>
          <p>Honest songwriting about faith, family, purpose, redemption, and the people God sees.</p>
        </div>
      </section>

      <section className="music-section" aria-labelledby="featured-release">
        <div className="music-section-heading">
          <p className="music-eyebrow">FEATURED RELEASE</p>
          <h2 id="featured-release">More Road Ahead</h2>
          <p>A six-song demo collection about perseverance, connection, and hope for the journey still unfolding.</p>
          <Link className="music-button" to="/music/more-road-ahead">Explore the album</Link>
        </div>
        <Link className="music-cover-link" to="/music/more-road-ahead" aria-label="Explore More Road Ahead">
          <img className="music-cover" src="/images/more-road-ahead.jpg" alt="More Road Ahead album cover" />
        </Link>
      </section>

      <section className="music-statement" aria-labelledby="about-wesley">
        <p className="music-eyebrow">ABOUT THE SONGWRITER</p>
        <h2 id="about-wesley">Writing what I know. Trusting God with what I don’t.</h2>
        <p>Wesley Rolfson writes story-led songs grounded in faith, family, grief, service, and hope. These demo recordings preserve the heart and direction of each song while leaving room for the road ahead.</p>
        <p className="music-contact">Artist contact: <a href="mailto:rolfson.data@gmail.com">rolfson.data@gmail.com</a></p>
      </section>
    </div>
  );
}


import React from 'react';
import { Link } from 'react-router-dom';
import './Music.css';

export default function Music() {
  return (
    <section className="music-page">
      <p className="music-eyebrow">GLASIER DATA / ORIGINAL MUSIC</p>
      <h1>Stories worth singing.</h1>
      <p className="music-lead">Original songwriting exploring family, faith, perseverance, and the roads that shape us.</p>
      <div className="music-panel">
        <p className="music-eyebrow">FEATURED RELEASE</p>
        <h2>More Road Ahead</h2>
        <p>A collection of original songs about the moments, relationships, and journeys that matter.</p>
        <Link className="music-button" to="/music/more-road-ahead">Explore the album</Link>
      </div>
      <div className="music-panel music-panel-secondary">
        <h2>About the music</h2>
        <p>These songs begin with original writing and creative direction. Current demo recordings may use AI-assisted performances, with future human-performed recordings planned.</p>
      </div>
    </section>
  );
}

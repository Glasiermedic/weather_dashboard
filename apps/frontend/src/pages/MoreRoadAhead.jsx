import React from "react";
import { Link } from "react-router-dom";
import albumArt from "../assets/optimized/more-road-ahead.jpg";
import "./music.css";

const spotifyAlbumId = "75AlWQPHTO9YS7puVXA8zF";
const tracks = [
  ["More Road Ahead", "7:28"],
  ["Soul Behind the Signal", "7:07"],
  ["Peaches N Lilies", "5:04"],
  ["Just Out of Reach", "4:14"],
  ["Except Jesus' Seat", "4:51"],
  ["Re-Tuning Hope", "3:38"],
];

function MoreRoadAhead() {
  return (
    <article className="music-page album-page">
      <Link to="/music" className="music-back">
        ← Wesley Rolfson music
      </Link>

      <header className="album-header">
        <img
          className="album-art"
          src={albumArt}
          alt="More Road Ahead album cover"
        />
        <div className="album-intro">
          <p className="music-eyebrow">DEMO ALBUM / 2026</p>
          <h1>More Road Ahead</h1>
          <p className="music-lead">
            Six original songs about the journeys we take, the people who
            travel beside us, and the hope that keeps calling us forward.
          </p>
          <dl className="album-meta">
            <div>
              <dt>Artist</dt>
              <dd>Wesley Rolfson</dd>
            </div>
            <div>
              <dt>Released</dt>
              <dd>October 22, 2026</dd>
            </div>
            <div>
              <dt>Label</dt>
              <dd>Wesley Rolfson – DataDad</dd>
            </div>
            <div>
              <dt>UPC</dt>
              <dd>037557719796</dd>
            </div>
            <div>
              <dt>Artist contact</dt>
              <dd>
                <a href="mailto:rolfson.data@gmail.com">
                  rolfson.data@gmail.com
                </a>
              </dd>
            </div>
          </dl>
        </div>
      </header>

      <section className="music-panel" aria-labelledby="listen-heading">
        <p className="music-eyebrow">LISTEN</p>
        <h2 id="listen-heading">Stream More Road Ahead</h2>
        <iframe
          className="spotify-embed"
          title="More Road Ahead by Wesley Rolfson on Spotify"
          src={`https://open.spotify.com/embed/album/${spotifyAlbumId}?utm_source=generator&theme=0`}
          allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture"
          loading="lazy"
        />
      </section>

      <section className="track-section" aria-labelledby="track-listing">
        <p className="music-eyebrow">SIX SONGS / 32 MINUTES</p>
        <h2 id="track-listing">Track listing</h2>
        <ol className="track-list">
          {tracks.map(([title, duration]) => (
            <li key={title}>
              <span>{title}</span>
              <time>{duration}</time>
            </li>
          ))}
        </ol>
      </section>

      <section className="music-statement album-note">
        <p className="music-eyebrow">ABOUT THE RECORD</p>
        <h2>A demo shaped by faith, family, and the long view.</h2>
        <p>
          More Road Ahead is a songwriter’s demo: a first recorded home for
          six original songs and the stories behind them.
        </p>
      </section>
    </article>
  );
}

export default MoreRoadAhead;


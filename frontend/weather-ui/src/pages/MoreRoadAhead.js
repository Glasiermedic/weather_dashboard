import React from 'react';
import { Link } from 'react-router-dom';
import './Music.css';

// Add the verified Spotify album URL here when available.
const spotifyAlbumUrl = 'https://open.spotify.com/album/75AlWQPHTO9YS7puVXA8zF';

function getSpotifyEmbedUrl(url) {
  const match = url.match(/^https:\/\/open\.spotify\.com\/album\/([A-Za-z0-9]+)(?:[/?#]|$)/);
  return match ? `https://open.spotify.com/embed/album/${match[1]}` : null;
}

export default function MoreRoadAhead() {
  const embedUrl = getSpotifyEmbedUrl(spotifyAlbumUrl);
  return (
    <article className="music-page">
      <Link to="/music" className="music-back">← All music</Link>
      <p className="music-eyebrow">ALBUM / ORIGINAL SONGS</p>
      <h1>More Road Ahead</h1>
      <p className="music-lead">Songs about the journeys we take and the people who travel them with us.</p>
      <div className="music-panel">
        <h2>Listen to the album</h2>
        {embedUrl ? (
          <iframe title="More Road Ahead on Spotify" src={embedUrl} width="100%" height="352" style={{ border: 0, borderRadius: 12 }} allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy" />
        ) : (
          <p>Spotify player coming soon. The album is available on Spotify; the verified album link will be added here.</p>
        )}
      </div>
      <div className="music-panel music-panel-secondary">
        <h2>Behind the songs</h2>
        <p>Original songwriting and storytelling, presented in demo recordings. Performance and production credits will be published alongside verified release details.</p>
      </div>
    </article>
  );
}

// src/pages/HomePage.js
import { Link } from 'react-router-dom';

function Homepage() {
  const cardStyle = {
    borderRadius: '1rem',
    padding: '1.5rem',
    background: '#f9f9f9',
    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
    textAlign: 'center',
    flex: 1,
    margin: '1rem'
  };

  const iconStyle = {
    fontSize: '2rem',
    marginBottom: '0.5rem'
  };

  return (
    <div style={{ maxWidth: '900px', margin: '2rem auto', textAlign: 'center' }}>
      <h1>Welcome to My Projects Hub</h1>
      <p style={{ fontSize: '1.1rem', color: '#555', marginBottom: '2rem' }}>
        Hello! This is a collection of interactive tools and visualizations I've built using Python, React, and real-world APIs.
      </p>
      <div style={{ display: 'flex', flexWrap: 'wrap', justifyContent: 'center' }}>
        <div style={{ ...cardStyle, background: '#e6f7ff' }}>
          <div style={iconStyle}>🌤️</div>
          <h3>Weather Dashboard</h3>
          <p>Real-time weather data, charts and summaries from local PWS sensors.</p>
          <Link to="/weather">Explore →</Link>
        </div>
        <div style={{ ...cardStyle, background: '#eaffea' }}>
          <div style={iconStyle}>📊</div>
          <h3>Awtowbotz</h3>
          <p>A market intelligence simulator with synthetic data and dashboards.</p>
          <Link to="/awtowbotz">Explore →</Link>
        </div>
        <div style={{ ...cardStyle, background: '#fff3e6' }}>
          <div style={iconStyle}>🎸🛹</div>
          <h3>SkateTone Forge</h3>
          <p>Music-powered skate park-animation! Upload a song to generate ramps.</p>
          <Link to="/skatestone">Explore →</Link>
        </div>
      </div>
    </div>
  );
}

export default Homepage;

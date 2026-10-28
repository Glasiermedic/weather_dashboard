import { Link } from 'react-router-dom';

function Navbar() {
  return (
    <nav style={{ padding: '1rem', background: '#f0f0f0', display: 'flex', flexWrap: 'wrap', gap: '1rem' }}>
      <Link to="/">Home</Link>
      <Link to="/weather">Weather Dashboard</Link>
      <Link to="/awtowbotz">Awtowbotz</Link>
      <Link to="/skatestone">SkateTone Forge</Link>
      <Link to="/music">Music</Link>
    </nav>
  );
}

export default Navbar;

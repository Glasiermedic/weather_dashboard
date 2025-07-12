import { Link } from 'react-router-dom';

function Navbar() {
  return (
    <nav style={{ padding: '1rem', background: '#f0f0f0' }}>
      <Link to="/" style={{ marginRight: '1rem' }}>Home</Link>
      <Link to="/weather" style={{ marginRight: '1rem' }}>Weather Dashboard</Link>
      <Link to="/awtowbotz" style={{ marginRight: '1rem' }}>Awtowbotz</Link>
      <Link to="/skatestone">SkateTone Forge</Link>
    </nav>
  );
}

export default Navbar;

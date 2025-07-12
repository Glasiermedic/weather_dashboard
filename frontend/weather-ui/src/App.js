import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Homepage from './pages/Homepage';
import WeatherDashboard from './pages/WeatherDashboard';
import AwtowbotzPage from './pages/AwtowbotzPage';
import SkateToneForge from './pages/SkateToneForge';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Homepage />} />
          <Route path="weather" element={<WeatherDashboard />} />
          <Route path="awtowbotz" element={<AwtowbotzPage />} />
          <Route path="skatestone" element={<SkateToneForge />} />
        </Route>
      </Routes>
    </Router>
  );
}

export default App;

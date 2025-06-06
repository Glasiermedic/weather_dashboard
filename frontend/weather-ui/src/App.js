// src/App.js
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import WeatherDashboard from './WeatherDashboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<h1>Homepage</h1>} />
        <Route path="/weather" element={<WeatherDashboard />} />
      </Routes>
    </Router>
  );
}

export default App;

import React from 'react';
import {
  createBrowserRouter,
  RouterProvider,
  Route,
  createRoutesFromElements,
} from 'react-router-dom';

import Layout from './components/Layout';
import Homepage from './pages/Homepage';
import WeatherDashboard from './pages/WeatherDashboard';
import AwtowbotzDashboard from './pages/AwtowbotzDashboard';
import SkateToneForge from './pages/SkateToneForge';

const router = createBrowserRouter(
  createRoutesFromElements(
    <Route path="/" element={<Layout />}>
      <Route index element={<Homepage />} />
      <Route path="weather" element={<WeatherDashboard />} />
      <Route path="awtowbotz" element={<AwtowbotzDashboard />} />
      <Route path="skatestone" element={<SkateToneForge />} />
    </Route>
  ),
  {
    future: {
      v7_startTransition: true,
      v7_relativeSplatPath: true,
    },
  }
);

function App() {
  return <RouterProvider router={router} />;
}

export default App;

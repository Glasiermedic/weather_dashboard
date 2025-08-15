import React from 'react';
import SummaryCards from './components/SummaryCards'; //dependent on the config.js and .env working on fixing the issues
import RegionChart from './components/RegionChart';
import TopRepsList from './components/TopRepsList'
import SalesWindow from './components/SalesWindow';
import './Awtowbotz.css';

function Awtobotz(){
  return (
    <div style={{ padding: '2rem', fontFamily: 'Arial, sans-serif' }}>
      <h1>aw-tow-botz-co: Transformer Co Sales Dashboard</h1>
        <SalesWindow />
        <SummaryCards />
        <RegionChart />
        <TopRepsList />
    </div>
  );
}

export default Awtowbotz;
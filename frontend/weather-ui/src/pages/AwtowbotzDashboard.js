import React from 'react';
import SalesSummary from '../components/SalesSummary';
import RegionChart from '../components/SalesByRegionChart';
import TopRepsList from '../components/TopRepsTable';
import SalesWindow from '../components/archived_SalesWindow';
import '../Awtowbotz.css';

const AwtowbotzDashboard = () => {
  // setting inline style: the font, a fall back font and padding inside the container
  // Creating a dashboard title
  // adding the four components of our dashboard


  return (
      <div style={{ padding: '2rem', fontfamily: 'Arial, sans-serif'}}>
        <h1>Awtowbotz Transformer Co: Sales Dashboard</h1>

        <SalesWindow />
        <SalesSummary />
        <SalesByRegionChart />
        <TopRepsTable />
      </div>
  );
};

export default AwtowbotzDashboard;
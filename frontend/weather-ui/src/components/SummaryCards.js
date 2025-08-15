import React, { useEffect, useState } from 'react';
import axios from 'axios';
import BASE_URL from '../config';

function SummaryCards() {
  const [summary, setSummary] = useState(null);

  useEffect(() => {
    console.log("📡 REACT_APP_API_BASE_URL in use:", BASE_URL);

    axios.get(`${BASE_URL}/api/sales_summary`)
      .then(res => {
        console.log("✅ Sales summary response:", res.data);
        setSummary(res.data);
      })
      .catch(err => {
        console.error('❌ Error fetching sales summary:', err.message || err);
      });
  }, []);

  if (!summary) return <p>Loading summary...</p>;

  return (
    <div style={containerStyle}>
      <div style={cardStyle}>
        <h4 style={labelStyle}>Total Revenue</h4>
        <p style={valueStyle}>${summary.total_revenue.toLocaleString()}</p>
      </div>
      <div style={cardStyle}>
        <h4 style={labelStyle}>Avg Unit Price</h4>
        <p style={valueStyle}>${summary.avg_unit_price.toFixed(2)}</p>
      </div>
      <div style={cardStyle}>
        <h4 style={labelStyle}>Top Product</h4>
        <p style={valueStyle}>{summary.top_product}</p>
      </div>
    </div>
  );
}

const containerStyle = {
  display: 'flex',
  gap: '2rem',
  justifyContent: 'center',
  margin: '2rem auto',
  maxWidth: '900px'
};

const cardStyle = {
  flex: 1,
  backgroundColor: '#ffffff',
  padding: '1.5rem',
  borderRadius: '0.5rem',
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.05)',
  textAlign: 'center'
};

const labelStyle = {
  fontSize: '1rem',
  color: '#6b7280',
  marginBottom: '0.25rem'
};

const valueStyle = {
  fontSize: '1.75rem',
  fontWeight: '600',
  color: '#1f2937'
};

export default SummaryCards;

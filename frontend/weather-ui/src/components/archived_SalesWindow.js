import React, { useEffect, useState } from 'react';
import axios from 'axios';
import BASE_URL from '../config';

function SalesWindow() {
  const [data, setData] = useState(null);

  useEffect(() => {
    axios.get(`${BASE_URL}/api/sales_window_summary`)
      .then(res => setData(res.data))
      .catch(err => console.error('❌ Error fetching sales window summary:', err));
  }, []);

  if (!data) return <p style={loadingStyle}>Loading daily & monthly summary...</p>;

  return (
    <div style={containerStyle}>
      <div style={sectionStyle}>
        <h3 style={headerStyle}>📅 Today</h3>
        <p style={valueStyle}>
          Revenue: ${data.today?.total_revenue != null ? data.today.total_revenue.toLocaleString() : '0'}
        </p>
        <p style={valueStyle}>
          Avg Unit Price: ${data.today?.avg_unit_price != null ? data.today.avg_unit_price.toFixed(2) : '0.00'}
        </p>
        <p style={valueStyle}>
          Transactions: {data.today?.transactions ?? '0'}
        </p>
      </div>
      <div style={sectionStyle}>
        <h3 style={headerStyle}>📆 This Month</h3>
        <p style={valueStyle}>
          Revenue: ${data.month?.total_revenue != null ? data.month.total_revenue.toLocaleString() : '0'}
        </p>
        <p style={valueStyle}>
          Avg Unit Price: ${data.month?.avg_unit_price != null ? data.month.avg_unit_price.toFixed(2) : '0.00'}
        </p>
        <p style={valueStyle}>
          Transactions: {data.month?.transactions ?? '0'}
        </p>
      </div>
    </div>
  );
}

const containerStyle = {
  display: 'flex',
  justifyContent: 'space-around',
  padding: '2rem',
  backgroundColor: '#f9fafb',
  borderRadius: '1rem',
  marginBottom: '2rem'
};

const sectionStyle = {
  flex: 1,
  margin: '0 1rem',
  backgroundColor: '#ffffff',
  padding: '1.5rem',
  borderRadius: '0.75rem',
  boxShadow: '0 4px 12px rgba(0, 0, 0, 0.06)',
  textAlign: 'center'
};

const headerStyle = {
  fontSize: '1.25rem',
  fontWeight: '700',
  marginBottom: '1rem',
  color: '#1f2937'
};

const valueStyle = {
  fontSize: '1.1rem',
  margin: '0.25rem 0',
  color: '#374151'
};

const loadingStyle = {
  textAlign: 'center',
  padding: '2rem',
  fontSize: '1.25rem',
  color: '#9ca3af'
};

export default archived_SalesWindow;

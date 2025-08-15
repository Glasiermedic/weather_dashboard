import React, { useEffect, useState } from 'react';
import axios from 'axios';
import BASE_URL from '../config';

function TopRepsList() {
  const [reps, setReps] = useState([]);

  useEffect(() => {
    axios.get(`${BASE_URL}/api/top_reps`)
      .then(res => setReps(res.data))
      .catch(err => console.error('❌ Error fetching top results:', err));
  }, []);

  if (!reps.length) return <p style={loadingStyle}>Loading top reps...</p>;

  return (
    <div style={containerStyle}>
      <h3 style={headerStyle}>🏆 Top Sales Reps – YTD</h3>
      <table style={tableStyle}>
        <thead>
          <tr>
            <th>Rep</th>
            <th>Transactions</th>
            <th>Units Sold</th>
            <th>Total Sales</th>
          </tr>
        </thead>
        <tbody>
          {reps.map(rep => (
            <tr key={rep.sales_rep}>
              <td>{rep.sales_rep}</td>
              <td>{rep.num_sales}</td>
              <td>{rep.total_units}</td>
              <td>${rep.total_sales.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

const containerStyle = {
  backgroundColor: '#ffffff',
  padding: '2rem',
  borderRadius: '1rem',
  boxShadow: '0 10px 20px rgba(0, 0, 0, 0.06)',
  marginBottom: '2.5rem'
};

const headerStyle = {
  fontSize: '1.5rem',
  fontWeight: '700',
  marginBottom: '1rem',
  color: '#111827',
  textAlign: 'center'
};

const tableStyle = {
  width: '100%',
  borderCollapse: 'collapse',
  fontSize: '1rem'
};

const loadingStyle = {
  textAlign: 'center',
  padding: '2rem',
  fontSize: '1.25rem',
  color: '#9ca3af'
};

export default TopRepsList;
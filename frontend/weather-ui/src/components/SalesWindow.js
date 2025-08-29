import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

function SalesWindow() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API_BASE}/api/sales_window_summary`)
      .then((res) => {
        setData(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("❌ Error fetching sales window summary:", err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <p className="loading-text">Loading sales window...</p>;

  return (
    <div className="sales-window-container">
      <div className="sales-window-card">
        <h3>📅 Today</h3>
        <p>Revenue: ${data.today?.total_revenue?.toLocaleString() ?? '0'}</p>
        <p>Avg Unit Price: ${data.today?.avg_unit_price?.toFixed(2) ?? '0.00'}</p>
        <p>Transactions: {data.today?.transactions ?? 0}</p>
      </div>

      <div className="sales-window-card">
        <h3>📆 This Month</h3>
        <p>Revenue: ${data.month?.total_revenue?.toLocaleString() ?? '0'}</p>
        <p>Avg Unit Price: ${data.month?.avg_unit_price?.toFixed(2) ?? '0.00'}</p>
        <p>Transactions: {data.month?.transactions ?? 0}</p>
      </div>
    </div>
  );
}

export default SalesWindow;

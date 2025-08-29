
import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

function SalesSummary() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API_BASE}/api/sales_summary`)
      .then((res) => {
        setSummary(res.data);
        setLoading(false);
      })
      .catch((err) => {
        console.error("❌ Error fetching sales summary:", err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <p className="loading-text">Loading sales summary...</p>;

  return (
    <div className="sales-summary-card">
      <h2>📊 Sales Summary</h2>
      <p>Total Revenue: ${summary?.total_revenue?.toLocaleString() ?? '0'}</p>
      <p>Average Unit Price: ${summary?.avg_unit_price?.toFixed(2) ?? '0.00'}</p>
      <p>Top Product: {summary?.top_product ?? '—'}</p>
    </div>
  );
}

export default SalesSummary;

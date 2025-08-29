
import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

function TopRepsTable() {
  const [topReps, setTopReps] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API_BASE}/api/top_reps`)
      .then(res => {
        setTopReps(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("❌ Error fetching top results:", err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <p className="loading-text">Loading top sales reps...</p>;

  return (
    <div className="top-reps-table">
      <h3>🏆 Top Performing Sales Reps</h3>
      <table>
        <thead>
          <tr>
            <th>Sales Rep</th>
            <th># Sales</th>
            <th>Units Sold</th>
            <th>Total Sales</th>
          </tr>
        </thead>
        <tbody>
          {topReps.map((rep, index) => (
            <tr key={index}>
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

export default TopRepsTable;

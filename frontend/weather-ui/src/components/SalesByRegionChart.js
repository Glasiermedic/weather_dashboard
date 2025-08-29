
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Bar } from 'react-chartjs-2';

const API_BASE = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

function SalesByRegionChart() {
  const [regionData, setRegionData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${API_BASE}/api/sales_by_region`)
      .then(res => {
        setRegionData(res.data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Error fetching region data:", err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <p className="loading-text">Loading regional sales data...</p>;

  const chartData = {
    labels: regionData.map(entry => entry.region),
    datasets: [
      {
        label: 'Sales by Region',
        data: regionData.map(entry => entry.total_sales),
        backgroundColor: '#3B82F6'
      }
    ]
  };

  const options = {
    responsive: true,
    plugins: {
      legend: { display: false },
      title: { display: true, text: 'Total Sales by Region' }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: { callback: (val) => `$${val.toLocaleString()}` }
      }
    }
  };

  return (
    <div className="chart-container">
      <Bar data={chartData} options={options} />
    </div>
  );
}

export default SalesByRegionChart;

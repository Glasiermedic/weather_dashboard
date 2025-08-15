import React, { useEffect, useState } from 'react';
import axios from 'axios';
import BASE_URL from '../config';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend);


function RegionChart() {
  const [chartData, setChartData] = useState(null);

  useEffect(() => {
    axios.get(`${BASE_URL}/api/sales_by_region`)
      .then(res => {
        const labels = res.data.map(item => item.region);
        const data = res.data.map(item => item.total_sales);
        setChartData({
          labels,
          datasets: [{
            label: 'Sales by Region',
            data,
            backgroundColor: '#60a5fa',
            borderRadius: 8,
            barThickness: 36
          }]
        });
      })
      .catch(err => console.error('Error fetching region data:', err));
  }, []);

  if (!chartData) return <p style={loadingStyle}>Loading region sales chart...</p>;

  return (
    <div style={containerStyle}>
      <h3 style={headerStyle}>📊 Sales by Region</h3>
      <div style={{ padding: '0 1rem' }}>
        <Bar data={chartData} options={chartOptions} />
      </div>
    </div>
  );
}

const containerStyle = {
  backgroundColor: '#ffffff',
  padding: '2.5rem 2rem',
  borderRadius: '1.25rem',
  boxShadow: '0 12px 28px rgba(0,0,0,0.08)',
  marginBottom: '2.5rem',
  maxWidth: '100%',
  marginLeft: 'auto',
  marginRight: 'auto'
};

const headerStyle = {
  fontSize: '1.875rem',
  fontWeight: '800',
  marginBottom: '1.5rem',
  textAlign: 'center',
  color: '#111827'
};

const loadingStyle = {
  textAlign: 'center',
  padding: '2.5rem',
  fontSize: '1.375rem',
  color: '#9ca3af'
};

const chartOptions = {
  responsive: true,
  plugins: {
    legend: { display: false },
    title: { display: false },
    tooltip: {
      callbacks: {
        label: function (context) {
          return `$${context.raw.toLocaleString()}`;
        }
      }
    }
  },
  scales: {
    y: {
      ticks: {
        callback: function (value) {
          return `$${value.toLocaleString()}`;
        },
        color: '#6b7280',
        font: { size: 14 }
      },
      grid: { color: '#e5e7eb' }
    },
    x: {
      ticks: {
        color: '#6b7280',
        font: { size: 14 }
      },
      grid: { display: false }
    }
  }
};

export default RegionChart;

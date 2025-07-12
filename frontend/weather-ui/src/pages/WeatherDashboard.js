import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

const API_BASE = "https://weather-dashboard-hqpk.onrender.com";

const stations = {
  propdada: 'Propeller Sensor',
  dustprop: 'Dust Sensor'
};

const stationColors = {
  propdada: 'blue',
  dustprop: 'red'
};

const timeRanges = {
  '1d': 'Today',
  '7d': 'Last 7 Days',
  '30d': 'Last 30 Days',
  'ytd': 'Year to Date'
};

const metricOptions = {
  temp_avg: "average temp",
  temp_low: "low temp",
  temp_high: "high temp",
  humidity_avg: "average humidity",
  wind_speed_high: "high wind",
  wind_speed_low: "low wind",
  wind_speed_avg: "average wind",
  wind_gust_max: "max wind gust",
  dew_point_avg: "average dewpoint",
  windchill_Avg: "average wind chill",
  heatindex_Avg: "ave heat index",
  pressure_Trend: "pressure trend",
  solar_rad_max: "solar radiation",
  uv_max: "UV",
  //precipRate: "precipitation rate",
  precip_total: "total precip"
};

const spinnerStyle = {
  width: "1.5rem",
  height: "1.5rem",
  border: "3px solid #ccc",
  borderTop: "3px solid #333",
  borderRadius: "50%",
  animation: "spin 1s linear infinite",
  margin: "0.5rem auto"
};

const fadeInStyle = {
  animation: "fadein 0.4s ease-in"
};

function WeatherDashboard() {
  const [selectedStations, setSelectedStations] = useState(['propdada']);
  const [selectedPeriod, setSelectedPeriod] = useState('30d');
  const [selectedMetric, setSelectedMetric] = useState('temp_avg');
  const [graphSeries, setGraphSeries] = useState({});
  const [currentData, setCurrentData] = useState({});
  const [isLoadingCurrent, setIsLoadingCurrent] = useState(false);

  const fetchAll = async () => {
    const newGraphs = {};
    const newCurrent = {};
    setIsLoadingCurrent(true);

    await Promise.all(
      selectedStations.map(async (station) => {
        try {
          const [graphRes, currentRes] = await Promise.all([
            axios.get(`${API_BASE}/api/graph_data?station_id=${station}&period=${selectedPeriod}&column=${selectedMetric}`),
            axios.get(`${API_BASE}/api/current_data_live?station_id=${station}`)
          ]);
          newGraphs[station] = graphRes.data;
          newCurrent[station] = currentRes.data;
        } catch (err) {
          console.error(`Fetch failed for ${station}:`, err.message);
          if (err.response) {
            console.error("Response data:", err.response.data);
            console.error("Status:", err.response.status);
          } else if (err.request) {
            console.error("Request made but no response:", err.request);
          } else {
            console.error("Error setting up request:", err.message);
          }
        }
      })
    );

    setGraphSeries(newGraphs);
    setCurrentData(newCurrent);
    setIsLoadingCurrent(false);
  };

  useEffect(() => {
    fetchAll();
  }, [selectedStations, selectedPeriod, selectedMetric]);

  const toggleStation = (stationId) => {
    setSelectedStations((prev) =>
      prev.includes(stationId)
        ? prev.filter((id) => id !== stationId)
        : [...prev, stationId]
    );
  };

  const nowData = () => {
    const count = selectedStations.length;
    const total = { temp: 0, humidity: 0, wind_speed: 0, precip: 0, timestamp: null, fallback: false };

    selectedStations.forEach((id) => {
      const s = currentData[id];
      if (s) {
        total.temp += s.temp || 0;
        total.humidity += s.humidity || 0;
        total.wind_speed += s.wind_speed || 0;
        total.precip += s.precip || 0;
        total.timestamp = s.timestamp;
        total.fallback = s.fallback || total.fallback;
      }
    });

    return count === 0 ? null : {
      temp: (total.temp / count).toFixed(1),
      humidity: (total.humidity / count).toFixed(1),
      wind_speed: (total.wind_speed / count).toFixed(1),
      precip: total.precip.toFixed(2),
      timestamp: total.timestamp,
      fallback: total.fallback
    };
  };

  const now = nowData();

  return (
  <div style={{ padding: "2rem" }}>
    <h2>Weather Dashboard</h2>

    <div style={{ marginBottom: "1rem" }}>
      <strong>Stations:</strong>{" "}
      {Object.entries(stations).map(([id, label]) => (
        <label key={id} style={{ marginRight: "1rem" }}>
          <input
            type="checkbox"
            checked={selectedStations.includes(id)}
            onChange={() => toggleStation(id)}
          />{" "}
          {label}
        </label>
      ))}
    </div>

    <div style={{ marginBottom: "1rem" }}>
      <label style={{ marginRight: "1rem" }}>
        <strong>Time Range:</strong>{" "}
        <select value={selectedPeriod} onChange={(e) => setSelectedPeriod(e.target.value)}>
          {Object.entries(timeRanges).map(([val, label]) => (
            <option key={val} value={val}>
              {label}
            </option>
          ))}
        </select>
      </label>

      <label>
        <strong>Metric:</strong>{" "}
        <select value={selectedMetric} onChange={(e) => setSelectedMetric(e.target.value)}>
          {Object.entries(metricOptions).map(([val, label]) => (
            <option key={val} value={val}>
              {label}
            </option>
          ))}
        </select>
      </label>
    </div>

    <div style={{ marginBottom: "1.5rem" }}>
      <strong>Right Now:</strong>
      {isLoadingCurrent ? (
        <div style={spinnerStyle}></div>
      ) : now ? (
        <div style={fadeInStyle}>
          Temp: {now.temp}°F | Humidity: {now.humidity}% | Wind: {now.wind_speed} mph | Precip: {now.precip}" <br />
          <small>As of {now.timestamp} {now.fallback && "(from fallback data)"}</small>
        </div>
      ) : (
        <div>— No live data available —</div>
      )}
    </div>

    <div>
      <Line
        data={{
          labels: graphSeries[selectedStations[0]]?.labels || [],
          datasets: selectedStations.map((id) => ({
            label: stations[id],
            data: graphSeries[id]?.data || [],
            borderColor: stationColors[id],
            fill: false
          }))
        }}
        options={{
          responsive: true,
          plugins: {
            legend: { position: "bottom" },
            title: {
              display: true,
              text: `Trend: ${metricOptions[selectedMetric] || selectedMetric}`
            }
          }
        }}
      />
    </div>
  </div>
);

}

export default WeatherDashboard;

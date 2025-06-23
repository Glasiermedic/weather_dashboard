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
  windchillAvg: "average wind chill",
  heatindexAvg: "ave heat index",
  pressureTrend: "pressure trend",
  solar_rad_max: "solar radiation",
  uv_max: "UV",
  precipRate: "precipitation rate",
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
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshMessage, setRefreshMessage] = useState("");

  const fetchAll = async () => {
    const newGraphs = {};
    const newCurrent = {};
    setIsLoadingCurrent(true);

    await Promise.all(
      selectedStations.map(async (station) => {
        try {
          const [graphRes, currentRes] = await Promise.all([
            axios.get(`http://localhost:5000/api/graph_data?station_id=${station}&period=${selectedPeriod}&column=${selectedMetric}`),
            axios.get(`http://localhost:5000/api/current_data_live?station_id=${station}`)
          ]);
          newGraphs[station] = graphRes.data;
          newCurrent[station] = currentRes.data;
        } catch (err) {
          console.error(`Fetch failed for ${station}:`, err);
        }
      })
    );

    setGraphSeries(newGraphs);
    setCurrentData(newCurrent);
    setIsLoadingCurrent(false);
  };

  const refreshSummaries = async () => {
    setIsRefreshing(true);
    setRefreshMessage("");

    try {
      const response = await axios.get(`http://localhost:5000/api/generate_summary?period=${selectedPeriod}`);
      setRefreshMessage("✅ Summaries refreshed successfully.");
      console.log("Summary results:", response.data);
    } catch (error) {
      console.error("❌ Error refreshing summaries:", error);
      setRefreshMessage("❌ Failed to refresh summaries.");
    }

    setIsRefreshing(false);
  };

  // eslint-disable-next-line react-hooks/exhaustive-deps
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

      {/* Station Selector */}
      <div style={{ border: "1px solid #ccc", padding: "1rem", marginBottom: "1rem" }}>
        <h4>Select Stations</h4>
        {Object.entries(stations).map(([id, label]) => (
          <label key={id} style={{ display: "block", marginBottom: "0.5rem" }}>
            <input
              type="checkbox"
              checked={selectedStations.includes(id)}
              onChange={() => toggleStation(id)}
              style={{ marginRight: "0.5rem" }}
            />
            <span style={{ color: stationColors[id] }}>{label}</span>
          </label>
        ))}
      </div>

      {/* Time Range Selector */}
      <div style={{ marginBottom: "1rem" }}>
        <label htmlFor="range-select" style={{ fontWeight: "bold", marginRight: "0.5rem" }}>
          Select Time Range:
        </label>
        <select
          id="range-select"
          value={selectedPeriod}
          onChange={(e) => setSelectedPeriod(e.target.value)}
        >
          {Object.entries(timeRanges).map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
      </div>

      {/* Metric Selector */}
      <div style={{ marginBottom: "2rem" }}>
        <label htmlFor="metric-select" style={{ fontWeight: "bold", marginRight: "0.5rem" }}>
          Select Metric:
        </label>
        <select
          id="metric-select"
          value={selectedMetric}
          onChange={(e) => setSelectedMetric(e.target.value)}
        >
          {Object.entries(metricOptions).map(([value, label]) => (
            <option key={value} value={value}>{label}</option>
          ))}
        </select>
      </div>

      {/* Right Now Section */}
      <div style={{ marginBottom: "2rem", background: "#f3f3f3", padding: "1rem", borderRadius: "0.5rem" }}>
        <h3>
          Right Now
          {now?.timestamp && (
            <span style={{ fontSize: "1rem", fontWeight: "normal", marginLeft: "1rem" }}>
              (as of {new Date(now.timestamp).toLocaleString("en-US", { timeZone: "America/Los_Angeles" })})
            </span>
          )}
        </h3>

        {isLoadingCurrent ? (
          <div style={spinnerStyle}></div>
        ) : now ? (
          <div style={fadeInStyle}>
            <ul>
              <li>Temperature: {now.temp}°F</li>
              <li>Humidity: {now.humidity}%</li>
              <li>Wind Speed: {now.wind_speed} mph</li>
              <li>Precipitation: {now.precip} in</li>
              {now.fallback && (
                <li style={{ color: "gray", fontStyle: "italic" }}>Data shown from local DB (live unavailable)</li>
              )}
            </ul>
            <button onClick={fetchAll} style={{ marginTop: "0.5rem" }}>Refresh</button>
          </div>
        ) : (
          <p><em>No current data available.</em></p>
        )}
      </div>

      {/* Refresh Summaries Section */}
      <div style={{ marginBottom: "2rem", borderTop: "1px solid #ccc", paddingTop: "1rem" }}>
        <h4>Backend Summary Tools</h4>
        <button onClick={refreshSummaries} disabled={isRefreshing}>
          {isRefreshing ? "Refreshing..." : "Refresh Backend Summaries"}
        </button>
        {refreshMessage && (
          <div style={{ marginTop: "0.5rem", fontStyle: "italic" }}>{refreshMessage}</div>
        )}
      </div>

      {/* Graph Section */}
      <h3>{metricOptions[selectedMetric]} Trend</h3>
      {Object.keys(graphSeries).length > 0 ? (() => {
        const allLabelsSet = new Set();
        selectedStations.forEach((id) => {
          graphSeries[id]?.labels?.forEach((label) => allLabelsSet.add(label));
        });
        const allLabels = Array.from(allLabelsSet).sort();

        const datasets = selectedStations
          .filter((id) => graphSeries[id])
          .map((id) => {
            const dataMap = {};
            graphSeries[id].labels.forEach((label, idx) => {
              dataMap[label] = graphSeries[id].data[idx];
            });

            const alignedData = allLabels.map((label) =>
              dataMap.hasOwnProperty(label) ? dataMap[label] : null
            );

            return {
              label: stations[id],
              data: alignedData,
              borderColor: stationColors[id],
              fill: false,
              tension: 0.1
            };
          });

        return (
          <Line
            data={{
              labels: allLabels,
              datasets: datasets
            }}
          />
        );
      })() : (
        <p>Loading graph...</p>
      )}

      {/* Inline CSS Keyframes */}
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        @keyframes fadein {
          from { opacity: 0; }
          to { opacity: 1; }
        }
      `}</style>
    </div>
  );
}

export default WeatherDashboard;

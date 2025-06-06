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
  const [summaries, setSummaries] = useState({});
  const [graphSeries, setGraphSeries] = useState({});
  const [currentData, setCurrentData] = useState({});
  const [isLoadingCurrent, setIsLoadingCurrent] = useState(false);

  const fetchAll = async () => {
    const newSummaries = {};
    const newGraphs = {};
    const newCurrent = {};
    setIsLoadingCurrent(true);

    await Promise.all(
      selectedStations.map(async (station) => {
        try {
          const [summaryRes, graphRes, currentRes] = await Promise.all([
            axios.get(`http://localhost:5000/api/summary_data?station_id=${station}&period=${selectedPeriod}`),
            axios.get(`http://localhost:5000/api/graph_data?station_id=${station}&period=${selectedPeriod}&column=temp_avg`),
            axios.get(`http://localhost:5000/api/current_data_live?station_id=${station}`)
          ]);
          newSummaries[station] = summaryRes.data;
          newGraphs[station] = graphRes.data;
          newCurrent[station] = currentRes.data;
        } catch (err) {
          console.error(`Fetch failed for ${station}:`, err);
        }
      })
    );

    setSummaries(newSummaries);
    setGraphSeries(newGraphs);
    setCurrentData(newCurrent);
    setIsLoadingCurrent(false);
  };

  useEffect(() => {
  fetchAll(); // fetch once on load or when station/time range changes
}, [selectedStations, selectedPeriod]);


  const toggleStation = (stationId) => {
    setSelectedStations((prev) =>
      prev.includes(stationId)
        ? prev.filter((id) => id !== stationId)
        : [...prev, stationId]
    );
  };

  const combinedSummary = () => {
    const count = selectedStations.length;
    const total = { temp_avg: 0, humidity_avg: 0, wind_speed_avg: 0, precip_total: 0 };

    selectedStations.forEach((id) => {
      const s = summaries[id];
      if (s) {
        total.temp_avg += s.temp_avg || 0;
        total.humidity_avg += s.humidity_avg || 0;
        total.wind_speed_avg += s.wind_speed_avg || 0;
        total.precip_total += s.precip_total || 0;
      }
    });

    return count === 0 ? null : {
      temp_avg: (total.temp_avg / count).toFixed(1),
      humidity_avg: (total.humidity_avg / count).toFixed(1),
      wind_speed_avg: (total.wind_speed_avg / count).toFixed(1),
      precip_total: total.precip_total.toFixed(2)
    };
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

  const summary = combinedSummary();
  const now = nowData();

  const allLabelsSet = new Set();
  selectedStations.forEach((id) => {
    graphSeries[id]?.labels?.forEach((label) => allLabelsSet.add(label));
  });
  const allLabels = Array.from(allLabelsSet).sort();

  return (
    <div style={{ padding: "2rem" }}>
      <h2>Weather Dashboard</h2>

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

      <div style={{ marginBottom: "1.5rem" }}>
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

      <div style={{ marginBottom: "2rem", background: "#f3f3f3", padding: "1rem", borderRadius: "0.5rem" }}>
        <h3>
          Right Now
          {now?.timestamp && (
            <span style={{ fontSize: "1rem", fontWeight: "normal", marginLeft: "1rem" }}>
              (as of {new Date(now.timestamp).toLocaleString("en-US", { timeZone: "America/Los_Angeles", timeZoneName: "short" })})
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
            </ul>
            <small style={{ color: now.fallback ? "#c00" : "#555" }}>
              {now.fallback ? "Data shown from local DB (live unavailable)" : "Live data"}
            </small>
          </div>
        ) : (
          <p><em>No current data available.</em></p>
        )}
        <button onClick={fetchAll} style={{ marginTop: "0.5rem" }}>Refresh</button>
      </div>

      <h3>Summary ({timeRanges[selectedPeriod]})</h3>
      {summary ? (
        <ul>
          <li>Temp Avg: {summary.temp_avg}</li>
          <li>Humidity Avg: {summary.humidity_avg}</li>
          <li>Wind Speed Avg: {summary.wind_speed_avg}</li>
          <li>Precip Total: {summary.precip_total}</li>
        </ul>
      ) : (
        <p>Loading summary...</p>
      )}

      <h3>Temperature Trend</h3>
      {Object.keys(graphSeries).length > 0 ? (
        <Line
          data={{
            labels: allLabels,
            datasets: selectedStations
              .filter((id) => graphSeries[id])
              .map((id) => {
                const stationLabels = graphSeries[id].labels;
                const stationData = graphSeries[id].data;
                const dataMap = {};
                stationLabels.forEach((label, i) => {
                  dataMap[label] = stationData[i];
                });
                return {
                  label: stations[id],
                  data: allLabels.map((label) => dataMap[label] ?? null),
                  borderColor: stationColors[id],
                  fill: false,
                  tension: 0.1
                };
              })
          }}
        />
      ) : (
        <p>Loading graph...</p>
      )}

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

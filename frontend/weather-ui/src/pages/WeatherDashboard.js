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

const stationColors = {
  KORMCMIN127: 'blue',
  KORMCMIN133: 'red'
};

const metricLabels = {
  temp_avg: "average temp",
  temp_low: "low temp",
  temp_high: "high temp",
  humidity_avg: "average humidity",
  wind_speed_high: "high wind",
  wind_speed_low: "low wind",
  wind_speed_avg: "average wind",
  wind_gust_max: "max wind gust",
  dew_point_avg: "average dewpoint",
  windchill_avg: "average wind chill",
  heatindex_avg: "ave heat index",
  pressure_trend: "pressure trend",
  solar_rad_max: "solar radiation",
  uv_max: "UV",
  precip_total: "total precip"
};

function WeatherDashboard() {
  const [selectedStations, setSelectedStations] = useState(['KORMCMIN127']);
  const [selectedPeriod, setSelectedPeriod] = useState('30d');
  const [selectedMetric, setSelectedMetric] = useState('temp_avg');
  const [tableStation, setTableStation] = useState('KORMCMIN127');

  const [graphSeries, setGraphSeries] = useState({});
  const [currentData, setCurrentData] = useState({});
  const [availableMetrics, setAvailableMetrics] = useState([]);

  const [tableData, setTableData] = useState([]);
  const [tableColumns, setTableColumns] = useState([]);

  const [isLoadingGraph, setIsLoadingGraph] = useState(false);
  const [isLoadingCurrent, setIsLoadingCurrent] = useState(false);
  const [isLoadingTable, setIsLoadingTable] = useState(false);

  const fetchGraphAndCurrent = async () => {
    setIsLoadingGraph(true);
    setIsLoadingCurrent(true);

    const newGraphs = {};
    const newCurrent = {};

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
        }
      })
    );

    setGraphSeries(newGraphs);
    setCurrentData(newCurrent);
    setIsLoadingGraph(false);
    setIsLoadingCurrent(false);
  };

  const fetchTable = async () => {
    setIsLoadingTable(true);
    try {
      const res = await axios.get(`${API_BASE}/api/table_data?station_id=${tableStation}`);
      const rows = res.data?.rows || [];
      setTableData(rows);

     const hiddenColumns = new Set(['day'
                                                      , 'humidity_max'
                                                      , 'humidity_min'
                                                      , 'hour'
                                                      , 'pressure_max'
                                                      , 'pressure_min'
                                                      , 'temp_max'
                                                      , 'temp_min'
                                                      , 'wind_speed_max'
                                                      , 'wind_speed_min'
                                                      ,'solar_rad_max'
                                                      , 'uv_max']);
const allColumns = new Set();

rows.forEach(row => {
  Object.keys(row).forEach(key => {
    if (!hiddenColumns.has(key)) {
      allColumns.add(key);
    }
  });
});

setTableColumns(Array.from(allColumns));

    } catch (err) {
      console.error(`Failed to load table data for ${tableStation}:`, err.message);
    }
    setIsLoadingTable(false);
  };

  useEffect(() => {
    axios.get(`${API_BASE}/api/debug/weather_daily_columns`)
      .then((res) => {
        const cols = res.data.columns || [];
        setAvailableMetrics(cols.filter(col => col !== 'station_id' && col !== 'date' && col !== 'local_time'));
      });
  }, []);

  useEffect(() => {
    fetchGraphAndCurrent();
  }, [selectedStations, selectedPeriod, selectedMetric]);

  useEffect(() => {
    fetchTable();
  }, [tableStation]);

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
    <div className="dashboard-container">
      <h2>Weather Dashboard</h2>

      <div className="dashboard-controls">
        <div>
          <label>Stations (for Graph + Now):</label><br />
          <select multiple value={selectedStations} onChange={(e) => setSelectedStations(Array.from(e.target.selectedOptions, opt => opt.value))}>
            <option value="KORMCMIN127">KORMCMIN127</option>
            <option value="KORMCMIN133">KORMCMIN133</option>
          </select>
        </div>

        <div>
          <label>Metric:</label><br />
          <select value={selectedMetric} onChange={(e) => setSelectedMetric(e.target.value)}>
            {availableMetrics.map(metric => (
              <option key={metric} value={metric}>{metricLabels[metric] || metric}</option>
            ))}
          </select>
        </div>

        <div>
          <label>Period:</label><br />
          <select value={selectedPeriod} onChange={(e) => setSelectedPeriod(e.target.value)}>
            <option value="1d">1 Day</option>
            <option value="7d">7 Days</option>
            <option value="30d">30 Days</option>
            <option value="ytd">Year to Date</option>
          </select>
        </div>

        <div>
          <label>Table Station:</label><br />
          <select value={tableStation} onChange={(e) => setTableStation(e.target.value)}>
            <option value="KORMCMIN127">KORMCMIN127</option>
            <option value="KORMCMIN133">KORMCMIN133</option>
          </select>
        </div>
      </div>

      {now && (
        <div className="dashboard-now">
          <p><strong>Right Now</strong> ({now.timestamp})</p>
          <p>🌡 Temp: {now.temp} °F</p>
          <p>💧 Humidity: {now.humidity} %</p>
          <p>💨 Wind: {now.wind_speed} mph</p>
          <p>🌧 Precip: {now.precip} in</p>
          {now.fallback && <p className="fallback-warning">⚠️ Data fallback in use</p>}
        </div>
      )}

      <div className="dashboard-graph">
        <h3>Graph</h3>
        <div className="graph-container">
          <Line data={{
            labels: graphSeries[selectedStations[0]]?.timestamps || [],
            datasets: selectedStations.map(station => ({
              label: `${station} - ${metricLabels[selectedMetric] || selectedMetric}`,
              data: graphSeries[station]?.values || [],
              borderColor: stationColors[station] || 'gray',
              backgroundColor: 'transparent',
              pointRadius: 0,
              borderWidth: 2
            }))
          }} options={{
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: true }, title: { display: false } },
            scales: {
              x: { display: true, title: { display: true, text: 'Time' } },
              y: { display: true, title: { display: true, text: metricLabels[selectedMetric] || selectedMetric } }
            }
          }} />
        </div>
      </div>

      {tableData.length > 0 ? (
        <div className="dashboard-table">
          <h3>Last 48 Hours Data ({tableStation})</h3>
          <table>
            <thead>
              <tr>
                {tableColumns.map(col => (
                  <th key={col}>{col}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {tableData.map((row, i) => (
                <tr key={i}>
                  {tableColumns.map(col => (
                    <td key={col}>{Number.isNaN(row[col]) ? '—' : row[col] ?? ''}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <p>No recent 48-hour data available for {tableStation}</p>
      )}
    </div>
  );
}

export default WeatherDashboard;

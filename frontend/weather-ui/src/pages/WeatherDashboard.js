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

const spinnerStyle = {
  width: "1.5rem",
  height: "1.5rem",
  border: "3px solid #ccc",
  borderTop: "3px solid #333",
  borderRadius: "50%",
  animation: "spin 1s linear infinite",
  margin: "0.5rem auto"
};

function WeatherDashboard() {
  const [selectedStations, setSelectedStations] = useState(['KORMCMIN127']);
  const [selectedPeriod, setSelectedPeriod] = useState('30d');
  const [selectedMetric, setSelectedMetric] = useState('temp_avg');
  const [graphSeries, setGraphSeries] = useState({});
  const [currentData, setCurrentData] = useState({});
  const [isLoadingCurrent, setIsLoadingCurrent] = useState(false);
  const [isLoadingGraph, setIsLoadingGraph] = useState(false);
  const [availableMetrics, setAvailableMetrics] = useState([]);

  const fetchAll = async () => {
    const newGraphs = {};
    const newCurrent = {};
    setIsLoadingCurrent(true);
    setIsLoadingGraph(true);

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
    setIsLoadingGraph(false);
  };

  useEffect(() => {
    axios.get(`${API_BASE}/api/debug/weather_daily_columns`)
        .then((res) => {
          const cols = res.data.columns || [];
          setAvailableMetrics(cols.filter(col => col !== 'station_id' && col !== 'date' && col !== 'local_time'));
        })
        .catch((err) => {
          console.error("Failed to load metric columns:", err.message);
        });
  }, []);

  useEffect(() => {
    fetchAll();
  }, [selectedStations, selectedPeriod, selectedMetric]);

  const nowData = () => {
    const count = selectedStations.length;
    const total = {temp: 0, humidity: 0, wind_speed: 0, precip: 0, timestamp: null, fallback: false};

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

  const chartData = {
  labels: graphSeries[selectedStations[0]]?.timestamps || [],
  datasets: selectedStations.map((stationId) => ({
    label: stationId,
    data: graphSeries[stationId]?.values || [],
    borderColor: stationColors[stationId] || 'gray',
    backgroundColor: stationColors[stationId] || 'gray',
    fill: false,
    tension: 0.4
  }))
};


  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {position: 'top'},
      title: {display: true, text: metricLabels[selectedMetric] || selectedMetric}
    }
  };

  return (
      <div style={{padding: "2rem"}}>
        <h2>Weather Dashboard</h2>
        {isLoadingGraph && <div style={spinnerStyle}></div>}
        {/* Right Now Section (Optional) */}
        {now && (
            <div>
              <p><strong>Right Now</strong> ({now.timestamp})</p>
              <p>🌡 Temp: {now.temp} °F</p>
              <p>💧 Humidity: {now.humidity} %</p>
              <p>💨 Wind: {now.wind_speed} mph</p>
              <p>🌧 Precip: {now.precip} in</p>
              {now.fallback && <p style={{color: "orange"}}>⚠️ Data fallback in use</p>}
            </div>
        )}

        {/* Graphs for each station */}
        {Object.entries(graphSeries).map(([station, series]) => {
          if (!series || !Array.isArray(series.timestamps)) {
            return <div key={station}>⚠️ No data for {station}</div>;
          }

          const chartData = {
            labels: series.timestamps,
            datasets: [
              {
                label: `${station} - ${metricLabels[selectedMetric] || selectedMetric}`,
                data: series.values,
                borderColor: stationColors[station] || 'gray',
                backgroundColor: 'transparent',
                pointRadius: 0,
                borderWidth: 2
              }
            ]
          };

          const options = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {display: true},
              title: {display: false}
            },
            scales: {
              x: {display: true, title: {display: true, text: 'Time'}},
              y: {display: true, title: {display: true, text: metricLabels[selectedMetric] || selectedMetric}}
            }
          };

          return (
              <div key={station} style={{margin: '2rem 0', height: '300px'}}>
                <Line data={chartData} options={options}/>
              </div>
          );
        })}
      </div>
  );
}

  export default WeatherDashboard;


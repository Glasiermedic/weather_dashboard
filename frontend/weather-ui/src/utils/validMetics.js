const validMetrics = {
  // 🌡️ Temperature
  "average temp": { column: "temp_avg", tables: ["weather_hourly", "weather_daily"] },
  "low temp":     { column: "temp_min", tables: ["weather_hourly"] },
  "high temp":    { column: "temp_max", tables: ["weather_hourly"] },
  "temp low":     { column: "temp_low", tables: ["weather_daily"] },
  "temp high":    { column: "temp_high", tables: ["weather_daily"] },

  // 💧 Humidity
  "average humidity": { column: "humidity_avg", tables: ["weather_hourly", "weather_daily"] },
  "low humidity":     { column: "humidity_min", tables: ["weather_hourly", "weather_daily"] },
  "high humidity":    { column: "humidity_max", tables: ["weather_hourly", "weather_daily"] },

  // 🌬️ Wind Speed
  "average wind": { column: "wind_speed_avg", tables: ["weather_hourly", "weather_daily"] },
  "low wind":     { column: "wind_speed_min", tables: ["weather_hourly"] },
  "high wind":    { column: "wind_speed_max", tables: ["weather_hourly"] },
  "wind low":     { column: "wind_speed_low", tables: ["weather_daily"] },
  "wind high":    { column: "wind_speed_high", tables: ["weather_daily"] },

  // 🌪️ Wind Gust
  "max wind gust": { column: "wind_gust_max", tables: ["weather_hourly", "weather_daily"] },

  // 🌫️ Dew Point
  "average dewpoint": { column: "dew_point_avg", tables: ["weather_hourly", "weather_daily"] },

  // ❄️ Wind Chill
  "average wind chill": { column: "windchill_avg", tables: ["weather_hourly", "weather_daily"] },

  // 🔥 Heat Index
  "ave heat index": { column: "heatindex_avg", tables: ["weather_hourly", "weather_daily"] },

  // 📉 Pressure
  "pressure avg":    { column: "pressure_avg", tables: ["weather_hourly", "weather_daily"] },
  "pressure min":    { column: "pressure_min", tables: ["weather_hourly", "weather_daily"] },
  "pressure max":    { column: "pressure_max", tables: ["weather_hourly", "weather_daily"] },
  "pressure trend":  { column: "pressure_trend", tables: ["weather_daily"] },
  "pressuretrend":   { column: "pressuretrend", tables: ["weather_daily"] }, // included for redundancy

  // ☀️ Solar Radiation
  "solar radiation": { column: "solar_rad_max", tables: ["weather_hourly", "weather_daily"] },

  // 🌞 UV
  "UV": { column: "uv_max", tables: ["weather_hourly", "weather_daily"] },

  // 🌧️ Precipitation
  "total precip":       { column: "precip_total", tables: ["weather_hourly", "weather_daily"] },
  "precipitation rate": { column: "precip_rate", tables: ["weather_raw"] }, // fallback only
};

export default validMetrics;

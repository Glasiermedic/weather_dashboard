import sqlite3
import os

# Path to your database
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data_exports", "weather.db"))

# Connect and create tables if they don't exist
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Table for 5-minute raw data (last 48 hours)
cursor.execute("""
CREATE TABLE IF NOT EXISTS weather_raw (
    station_id TEXT,
    local_time TEXT,
    temp REAL,
    humidity REAL,
    wind_speed REAL,
    wind_gust REAL,
    dew_point REAL,
    windchill REAL,
    heatindex REAL,
    pressure REAL,
    precip_rate REAL,
    precip_total REAL,
    solar_radiation REAL,
    uv REAL
)
""")

# Table for hourly averages (last 7 days)
cursor.execute("""
CREATE TABLE IF NOT EXISTS weather_hourly (
    station_id TEXT,
    hour TEXT,
    temp_avg REAL,
    humidity_avg REAL,
    wind_speed_avg REAL,
    wind_gust_max REAL,
    dew_point_avg REAL,
    windchill_avg REAL,
    heatindex_avg REAL,
    pressure_avg REAL,
    precip_total REAL,
    solar_rad_max REAL,
    uv_max REAL
)
""")

# Table for daily aggregates (up to 2 years)
cursor.execute("""
CREATE TABLE IF NOT EXISTS weather_daily (
    station_id TEXT,
    date TEXT,
    temp_avg REAL,
    temp_high REAL,
    temp_low REAL,
    humidity_avg REAL,
    wind_speed_avg REAL,
    wind_speed_high REAL,
    wind_speed_low REAL,
    wind_gust_max REAL,
    dew_point_avg REAL,
    windchill_avg REAL,
    heatindex_avg REAL,
    pressure_max REAL,
    pressure_min REAL,
    pressure_trend REAL,
    precip_total REAL,
    solar_rad_max REAL,
    uv_max REAL
)
""")

conn.commit()
conn.close()

print("Weather tables checked/created successfully.")

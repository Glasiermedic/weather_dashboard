import sqlite3
import os

DB_PATH = os.path.join("..", "data_exports", "weather.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS weather_raw;")
cursor.execute("DROP TABLE IF EXISTS weather_hourly;")
cursor.execute("DROP TABLE IF EXISTS weather_daily;")
cursor.execute(CREATE TABLE weather_raw (
    station_id TEXT,
    local_time TIMESTAMP,
    avg_humidity REAL,
    avg_temp REAL,
    dewpt REAL,
    feelslike REAL,
    heatindex REAL,
    humidity REAL,
    precip_hrly REAL,
    pressure REAL,
    solar_radiation REAL,
    temp REAL,
    uv REAL,
    wind_dir TEXT,
    wind_gust REAL,
    wind_speed REAL,
    windchill REAL
);)

print("✅ Tables dropped.")

conn.commit()
conn.close()

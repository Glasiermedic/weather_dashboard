import sqlite3
import os

# Correct path relative to your current script location
DB_PATH = os.path.join("..", "..", "data_exports", "weather.db")

schema = """
DROP TABLE IF EXISTS weather_raw;

CREATE TABLE weather_raw (
    station_id TEXT,
    local_time TEXT,
    temp_avg REAL,
    temp_high REAL,
    temp_low REAL,
    humidity_avg REAL,
    wind_speed_avg REAL,
    wind_speed_high REAL,
    wind_speed_low REAL,
    wind_gust_max REAL,
    dew_point_avg REAL,
    windchillAvg REAL,
    heatindexAvg REAL,
    pressureTrend REAL,
    solar_rad_max REAL,
    uv_max REAL,
    precipRate REAL,
    precip_total REAL
);
"""

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.executescript(schema)
conn.commit()
conn.close()

print("✅ weather_raw table recreated successfully.")

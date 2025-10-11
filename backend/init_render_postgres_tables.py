
import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Connect to the PostgreSQL database
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cursor = conn.cursor()

# Drop existing tables if they exist
cursor.execute("DROP TABLE IF EXISTS weather_raw;")
cursor.execute("DROP TABLE IF EXISTS weather_hourly;")
cursor.execute("DROP TABLE IF EXISTS weather_daily;")

# Recreate weather_raw table
cursor.execute("""
CREATE TABLE weather_raw (
    avg_dewpt REAL,
    avg_heat_indx REAL,
    avg_humidity REAL,
    avg_temp REAL,
    avg_wnd_chill REAL,
    avg_wnd_dir REAL,
    avg_wnd_gust REAL,
    avg_wnd_spd REAL,
    dewpt_max REAL,
    dewpt_min REAL,
    epoch BIGINT,
    heat_index_max REAL,
    heat_index_min REAL,
    humidity_max REAL,
    humidity_min REAL,
    lat REAL,
    local_time TIMESTAMP,
    lon REAL,
    precip_rate REAL,
    pressure_max REAL,
    pressure_min REAL,
    pressure_trend REAL,
    qcStatus TEXT,
    solar_rad_max REAL,
    station_id TEXT,
    temp_max REAL,
    temp_min REAL,
    total_precip REAL,
    tz TEXT,
    utc_time TEXT,
    uv_max REAL,
    wnd_chill_max REAL,
    wnd_chill_min REAL,
    wnd_gust_max REAL,
    wnd_gust_min REAL,
    wnd_spd_max REAL,
    wnd_spd_min REAL
)
""")

# Recreate weather_hourly table
cursor.execute("""
CREATE TABLE weather_hourly (
    station_id TEXT,
    hour TEXT,
    temp_avg REAL,
    temp_min REAL,
    temp_max REAL,
    humidity_avg REAL,
    humidity_min REAL,
    humidity_max REAL,
    wind_speed_avg REAL,
    wind_speed_min REAL,
    wind_speed_max REAL,
    wind_gust_max REAL,
    dew_point_avg REAL,
    windchill_avg REAL,
    heatindex_avg REAL,
    pressure_avg REAL,
    pressure_min REAL,
    pressure_max REAL,
    precip_total REAL,
    solar_rad_max REAL,
    uv_max REAL
)
""")

# Recreate weather_daily table
cursor.execute("""
CREATE TABLE weather_daily (
    station_id TEXT,
    date TEXT,
    temp_avg REAL,
    temp_low REAL,
    temp_high REAL,
    humidity_avg REAL,
    humidity_min REAL,
    humidity_max REAL,
    wind_speed_avg REAL,
    wind_speed_low REAL,
    wind_speed_high REAL,
    wind_gust_max REAL,
    dew_point_avg REAL,
    windchill_avg REAL,
    heatindex_avg REAL,
    pressure_avg REAL,
    pressure_min REAL,
    pressure_max REAL,
    pressure_trend REAL,
    precip_total REAL,
    solar_rad_max REAL,
    uv_max REAL
)
""")

# Finalize and close
conn.commit()
cursor.close()
conn.close()

print("✅ PostgreSQL weather tables created successfully.")

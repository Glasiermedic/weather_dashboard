import sqlite3
import os

# Correct path to the database file
DB_PATH = os.path.join("..", "..", "data_exports", "weather.db")

def create_weather_hourly_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Drop the table if it already exists (be cautious: this will erase existing data)
    cursor.execute("DROP TABLE IF EXISTS weather_hourly")

    # Create the weather_hourly table with full schema
    cursor.execute("""
        CREATE TABLE weather_hourly (
            station_id TEXT,
            local_time TEXT,
            temp_avg REAL,
            temp_low REAL,
            temp_high REAL,
            humidity_avg REAL,
            wind_speed_high REAL,
            wind_speed_low REAL,
            wind_speed_avg REAL,
            wind_gust_max REAL,
            dew_point_avg REAL,
            windchillAvg REAL,
            heatindexAvg REAL,
            pressureTrend REAL,
            solar_rad_max REAL,
            uv_max REAL,
            precipRate REAL,
            precip_total REAL
        )
    """)

    conn.commit()
    conn.close()
    print("✅ weather_hourly table created successfully.")

if __name__ == "__main__":
    create_weather_hourly_table()


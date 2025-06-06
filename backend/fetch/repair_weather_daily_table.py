import sqlite3
import os

# Define database path
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data_exports", "weather.db"))

def repair_weather_daily_table():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("🧹 Dropping and recreating 'weather_daily' table...")

    cursor.execute("DROP TABLE IF EXISTS weather_daily")

    cursor.execute("""
        CREATE TABLE weather_daily (
            station_id TEXT,
            local_date TEXT,
            temp_avg REAL,
            temp_low REAL,
            temp_high REAL,
            humidity_avg REAL,
            wind_speed_avg REAL,
            wind_speed_low REAL,
            wind_speed_high REAL,
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
    print("✅ 'weather_daily' table has been reset successfully.")

if __name__ == "__main__":
    repair_weather_daily_table()

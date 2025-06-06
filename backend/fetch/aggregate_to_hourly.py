import sqlite3
from datetime import datetime
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data_exports", "weather.db"))

def aggregate_hourly():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT station_id FROM weather_raw")
    stations = [row[0] for row in cursor.fetchall()]

    for station in stations:
        print(f"\n🔁 Aggregating for station: {station}")
        cursor.execute("""
            SELECT DISTINCT substr(local_time, 1, 13) AS hour
            FROM weather_raw
            WHERE station_id = ?
              AND substr(local_time, 1, 13) NOT IN (
                  SELECT substr(local_time, 1, 13) FROM weather_hourly WHERE station_id = ?
              )
            ORDER BY hour
        """, (station, station))
        hours = [row[0] for row in cursor.fetchall()]

        for hour_prefix in hours:
            cursor.execute("""
                SELECT * FROM weather_raw
                WHERE station_id = ?
                  AND substr(local_time, 1, 13) = ?
            """, (station, hour_prefix))
            rows = cursor.fetchall()
            if not rows:
                continue

            # Convert to DataFrame for easy aggregation
            import pandas as pd
            df = pd.DataFrame(rows, columns=[
                'station_id', 'local_time', 'temp', 'humidity', 'wind_speed',
                'wind_gust', 'dew_point', 'windchill', 'heatindex', 'pressure',
                'precip_rate', 'precip_total', 'solar_radiation', 'uv'
            ])

            agg_row = {
                'station_id': station,
                'local_time': hour_prefix + ":00",  # e.g., 2025-06-06 15:00
                'temp_avg': df['temp'].mean(),
                'humidity_avg': df['humidity'].mean(),
                'wind_speed_avg': df['wind_speed'].mean(),
                'wind_gust_max': df['wind_gust'].max(),
                'dew_point_avg': df['dew_point'].mean(),
                'windchill_avg': df['windchill'].mean(),
                'heatindex_avg': df['heatindex'].mean(),
                'pressure_avg': df['pressure'].mean(),
                'precip_total': df['precip_total'].sum(),
                'solar_rad_max': df['solar_radiation'].max(),
                'uv_max': df['uv'].max()
            }

            cursor.execute("""
                INSERT INTO weather_hourly (
                    station_id, local_time, temp_avg, humidity_avg, wind_speed_avg,
                    wind_gust_max, dew_point_avg, windchill_avg, heatindex_avg,
                    pressure_avg, precip_total, solar_rad_max, uv_max
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(agg_row.values()))

        conn.commit()

    conn.close()
    print("✅ Hourly aggregation complete.")

# === Main ===
if __name__ == "__main__":
    aggregate_hourly()

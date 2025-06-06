import sqlite3
from datetime import datetime
import os
import pandas as pd

# Correct relative path to database
DB_PATH = os.path.join("..", "..", "data_exports", "weather.db")

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

            df = pd.DataFrame(rows, columns=[
                "station_id", "local_time",
                "temp_avg", "temp_low", "temp_high",
                "humidity_avg", "wind_speed_high", "wind_speed_low", "wind_speed_avg",
                "wind_gust_max", "dew_point_avg", "windchillAvg", "heatindexAvg",
                "pressureTrend", "solar_rad_max", "uv_max", "precipRate", "precip_total"
            ])

            agg_row = {
                'station_id': station,
                'local_time': hour_prefix + ":00",
                'temp_avg': df['temp_avg'].mean(),
                'temp_low': df['temp_low'].min(),
                'temp_high': df['temp_high'].max(),
                'humidity_avg': df['humidity_avg'].mean(),
                'wind_speed_high': df['wind_speed_high'].max(),
                'wind_speed_low': df['wind_speed_low'].min(),
                'wind_speed_avg': df['wind_speed_avg'].mean(),
                'wind_gust_max': df['wind_gust_max'].max(),
                'dew_point_avg': df['dew_point_avg'].mean(),
                'windchillAvg': df['windchillAvg'].mean(),
                'heatindexAvg': df['heatindexAvg'].mean(),
                'pressureTrend': df['pressureTrend'].mean(),
                'solar_rad_max': df['solar_rad_max'].max(),
                'uv_max': df['uv_max'].max(),
                'precipRate': df['precipRate'].mean(),
                'precip_total': df['precip_total'].sum()
            }

            cursor.execute("""
                INSERT INTO weather_hourly (
                    station_id, local_time, temp_avg, temp_low, temp_high,
                    humidity_avg, wind_speed_high, wind_speed_low, wind_speed_avg,
                    wind_gust_max, dew_point_avg, windchillAvg, heatindexAvg,
                    pressureTrend, solar_rad_max, uv_max, precipRate, precip_total
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(agg_row.values()))

        conn.commit()

    conn.close()
    print("✅ Hourly aggregation complete.")

if __name__ == "__main__":
    aggregate_hourly()

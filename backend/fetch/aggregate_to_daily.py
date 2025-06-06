import sqlite3
import pandas as pd
from datetime import datetime
import os

# Correct path to the database
DB_PATH = os.path.join("..", "..", "data_exports", "weather.db")

def aggregate_daily():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT station_id FROM weather_hourly")
    stations = [row[0] for row in cursor.fetchall()]

    for station in stations:
        print(f"🔁 Aggregating daily for station: {station}")
        cursor.execute("""
            SELECT DISTINCT substr(local_time, 1, 10) AS day
            FROM weather_hourly
            WHERE station_id = ?
              AND substr(local_time, 1, 10) NOT IN (
                  SELECT substr(local_date, 1, 10) FROM weather_daily WHERE station_id = ?
              )
            ORDER BY day
        """, (station, station))
        days = [row[0] for row in cursor.fetchall()]

        for day in days:
            cursor.execute("""
                SELECT * FROM weather_hourly
                WHERE station_id = ?
                  AND substr(local_time, 1, 10) = ?
            """, (station, day))
            rows = cursor.fetchall()
            if not rows:
                continue

            df = pd.DataFrame(rows, columns=[
                "station_id", "local_time", "temp_avg", "temp_low", "temp_high",
                "humidity_avg", "wind_speed_high", "wind_speed_low", "wind_speed_avg",
                "wind_gust_max", "dew_point_avg", "windchillAvg", "heatindexAvg",
                "pressureTrend", "solar_rad_max", "uv_max", "precipRate", "precip_total"
            ])

            daily = {
                'station_id': station,
                'local_date': day,
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
                INSERT INTO weather_daily (
                    station_id, local_date, temp_avg, temp_low, temp_high,
                    humidity_avg, wind_speed_high, wind_speed_low, wind_speed_avg,
                    wind_gust_max, dew_point_avg, windchillAvg, heatindexAvg,
                    pressureTrend, solar_rad_max, uv_max, precipRate, precip_total
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, tuple(daily.values()))

        conn.commit()

    conn.close()
    print("✅ Daily aggregation complete.")

if __name__ == "__main__":
    aggregate_daily()

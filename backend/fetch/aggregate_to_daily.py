# backend/fetch/aggregate_to_daily.py
import os
import sqlite3
import pandas as pd
from datetime import datetime
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data_exports", "weather.db"))



def create_daily_table_if_needed(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather_daily (
            station_id TEXT,
            local_date TEXT,
            temp_avg REAL,
            humidity_avg REAL,
            wind_speed_avg REAL,
            precip_total REAL,
            PRIMARY KEY (station_id, local_date)
        )
    """)
    conn.commit()

def aggregate_daily():
    conn = sqlite3.connect(DB_PATH)
    create_daily_table_if_needed(conn)

    stations = pd.read_sql("SELECT DISTINCT station_id FROM weather_hourly", conn)["station_id"]

    for station_id in stations:
        print(f"🔁 Aggregating daily for station: {station_id}")

        df = pd.read_sql(f"""
            SELECT * FROM weather_hourly
            WHERE station_id = ?
        """, conn, params=(station_id,))

        if df.empty:
            continue

        df["local_time"] = pd.to_datetime(df["local_time"])
        df["local_date"] = df["local_time"].dt.date

        daily = df.groupby("local_date").agg({
            "temp_avg": "mean",
            "humidity_avg": "mean",
            "wind_speed_avg": "mean",
            "precip_total": "sum"
        }).reset_index()

        daily["station_id"] = station_id
        daily["local_date"] = daily["local_date"].astype(str)

        daily.to_sql("weather_daily", conn, if_exists="append", index=False)

    print("✅ Daily aggregation complete.")
    conn.close()

if __name__ == "__main__":
    aggregate_daily()

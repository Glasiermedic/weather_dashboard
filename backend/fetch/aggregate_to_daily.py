import os
import sqlite3
import pandas as pd
from pathlib import Path

# Setup paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # goes from fetch → backend
DB_PATH = os.path.join(BASE_DIR, "data_exports", "weather.db")

def aggregate_daily():
    conn = sqlite3.connect(DB_PATH)

    try:
        df = pd.read_sql_query("SELECT * FROM weather_hourly", conn)
    except Exception as e:
        print(f"❌ Failed to read weather_hourly: {e}")
        conn.close()
        return

    if df.empty:
        print("⚠️ No data found in weather_hourly.")
        conn.close()
        return

    df["local_time"] = pd.to_datetime(df["local_time"])
    df["local_date"] = df["local_time"].dt.date

    group_cols = ["station_id", "local_date"]
    available = set(df.columns)

    # Define metrics to aggregate if present
    metrics = {
        "temp": "mean",
        "humidity": "mean",
        "wind_speed": ["mean", "min", "max"],
        "wind_gust": "max",
        "dew_point": "mean",
        "windchill": "mean",
        "heatindex": "mean",
        "pressure": "mean",
        "solar_rad": "max",
        "uv": "max",
        "precip_rate": "mean",
        "precip_total": "sum"
    }

    # Only include available columns
    safe_metrics = {
        col: agg for col, agg in metrics.items() if col in available
    }

    if not safe_metrics:
        print("❌ No matching columns available to aggregate.")
        conn.close()
        return

    agg_df = df.groupby(group_cols).agg(safe_metrics).reset_index()

    # Flatten MultiIndex columns
    agg_df.columns = ["_".join(col).strip("_") if isinstance(col, tuple) else col for col in agg_df.columns]

    # Rename for consistency with rest of app
    rename_map = {
        "temp_mean": "temp_avg",
        "humidity_mean": "humidity_avg",
        "wind_speed_mean": "wind_speed_avg",
        "wind_speed_min": "wind_speed_low",
        "wind_speed_max": "wind_speed_high",
        "wind_gust_max": "wind_gust_max",
        "dew_point_mean": "dew_point_avg",
        "windchill_mean": "windchillAvg",
        "heatindex_mean": "heatindexAvg",
        "pressure_mean": "pressureTrend",
        "solar_rad_max": "solar_rad_max",
        "uv_max": "uv_max",
        "precip_rate_mean": "precipRate",
        "precip_total_sum": "precip_total"
    }

    agg_df.rename(columns=rename_map, inplace=True)

    # Write to DB
    agg_df.to_sql("weather_daily", conn, if_exists="replace", index=False)
    conn.close()
    print("✅ Aggregated daily data saved to weather_daily.")

if __name__ == "__main__":
    aggregate_daily()
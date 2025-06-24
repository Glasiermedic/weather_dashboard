import os
import pandas as pd
from sqlalchemy import create_engine

engine = create_engine("postgresql+psycopg2://username:password@host:port/dbname")
df = pd.read_sql("SELECT * FROM weather_raw", engine)
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_pg_connection():
    return psycopg2.connect(DATABASE_URL)

def main():
    with get_pg_connection() as conn:
        df = pd.read_sql_query("SELECT * FROM weather_raw", conn)

    if df.empty:
        print("No data in weather_raw table.")
        return

    df["local_time"] = pd.to_datetime(df["local_time"])
    df["date"] = df["local_time"].dt.date

    # Group and aggregate
    agg = df.groupby(["station_id", "date"]).agg({
        "avg_temp": ["mean", "min", "max"],
        "avg_humidity": ["mean", "min", "max"],
        "avg_wnd_spd": ["mean", "min", "max"],
        "avg_wnd_gust": "max",
        "avg_dewpt": "mean",
        "avg_wnd_chill": "mean",
        "avg_heat_indx": "mean",
        "pressure_trend": "mean",
        "pressure_max": "max",
        "pressure_min": "min",
        "total_precip": "sum",
        "solar_rad_max": "max",
        "uv_max": "max"
    })

    agg.columns = [
        "temp_avg", "temp_low", "temp_high",
        "humidity_avg", "humidity_min", "humidity_max",
        "wind_speed_avg", "wind_speed_low", "wind_speed_high",
        "wind_gust_max", "dew_point_avg", "windchill_avg",
        "heatindex_avg", "pressureTrend", "pressure_max",
        "pressure_min", "precip_total", "solar_rad_max", "uv_max"
    ]
    agg = agg.reset_index()

    with get_pg_connection() as conn:
        with conn.cursor() as cur:
            for _, row in agg.iterrows():
                cur.execute("""
                    INSERT INTO weather_daily (
                        station_id, date,
                        temp_avg, temp_low, temp_high,
                        humidity_avg, humidity_min, humidity_max,
                        wind_speed_avg, wind_speed_low, wind_speed_high,
                        wind_gust_max, dew_point_avg, windchill_avg, heatindex_avg,
                        pressureTrend, pressure_max, pressure_min,
                        precip_total, solar_rad_max, uv_max
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (station_id, date) DO NOTHING
                """, tuple(row))

            conn.commit()

    print("✅ Daily aggregation complete and inserted into weather_daily.")

if __name__ == "__main__":
    main()

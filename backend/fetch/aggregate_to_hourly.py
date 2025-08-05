import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

def main():
    # Read data from PostgreSQL
    df = pd.read_sql("SELECT * FROM weather_raw", engine)

    if df.empty:
        print("No data in weather_raw table.")
        return

    # Convert to datetime and extract hour
    df["local_time"] = pd.to_datetime(df["local_time"])
    df["hour"] = df["local_time"].dt.floor("H")

    # Group and aggregate
    agg = df.groupby(["station_id", "hour"]).agg({
        "avg_temp": ["mean", "min", "max"],
        "avg_humidity": ["mean", "min", "max"],
        "avg_wnd_spd": ["mean", "min", "max"],
        "avg_wnd_gust": "max",
        "avg_dewpt": "mean",
        "avg_wnd_chill": "mean",
        "avg_heat_indx": "mean",
        "pressure_max": "max",
        "pressure_min": "min",
        "pressure_trend": "mean",
        "total_precip": "sum",
        "solar_rad_max": "max",
        "uv_max": "max"
    })

    # Rename columns
    agg.columns = [
        "temp_avg", "temp_min", "temp_max",
        "humidity_avg", "humidity_min", "humidity_max",
        "wind_speed_avg", "wind_speed_min", "wind_speed_max",
        "wind_gust_max", "dew_point_avg", "windchill_avg",
        "heatindex_avg", "pressure_max", "pressure_min",
        "pressure_avg", "precip_total", "solar_rad_max", "uv_max"
    ]
    agg = agg.reset_index()

    agg["day"] = agg["hour"].dt.strftime("%Y-%m-%d")
    agg["local_time"] = agg["hour"]

    # Insert aggregated data into weather_hourly
    with engine.begin() as conn:
        for _, row in agg.iterrows():
            conn.execute(text("""
                INSERT INTO weather_hourly (
                    station_id, hour, local_time, day, 
                    temp_avg, temp_min, temp_max,
                    humidity_avg, humidity_min, humidity_max,
                    wind_speed_avg, wind_speed_min, wind_speed_max,
                    wind_gust_max, dew_point_avg, windchill_avg, heatindex_avg,
                    pressure_max, pressure_min, pressure_avg,
                    precip_total, solar_rad_max, uv_max
                )
                VALUES (
                    :station_id, :hour, :local_time, :day,
                    :temp_avg, :temp_min, :temp_max,
                    :humidity_avg, :humidity_min, :humidity_max,
                    :wind_speed_avg, :wind_speed_min, :wind_speed_max,
                    :wind_gust_max, :dew_point_avg, :windchill_avg, :heatindex_avg,
                    :pressure_max, :pressure_min, :pressure_avg,
                    :precip_total, :solar_rad_max, :uv_max
                )
                ON CONFLICT (station_id, hour) DO UPDATE
                SET
                local_time = EXCLUDED.local_time,
                day = EXCLUDED.day,
                temp_avg = EXCLUDED.temp_avg,
                temp_min = EXCLUDED.temp_min,
                temp_max = EXCLUDED.temp_max,
                humidity_avg = EXCLUDED.humidity_avg,
                humidity_min = EXCLUDED.humidity_min,
                humidity_max = EXCLUDED.humidity_max,
                wind_speed_avg = EXCLUDED.wind_speed_avg,
                wind_speed_min = EXCLUDED.wind_speed_min,
                wind_speed_max = EXCLUDED.wind_speed_max,
                wind_gust_max = EXCLUDED.wind_gust_max,
                dew_point_avg = EXCLUDED.dew_point_avg,
                windchill_avg = EXCLUDED.windchill_avg,
                heatindex_avg = EXCLUDED.heatindex_avg,
                pressure_max = EXCLUDED.pressure_max,
                pressure_min = EXCLUDED.pressure_min,
                pressure_avg = EXCLUDED.pressure_avg,
                precip_total = EXCLUDED.precip_total,
                solar_rad_max = EXCLUDED.solar_rad_max,
                uv_max = EXCLUDED.uv_max
            """), row_dict)

    print("✅ Hourly aggregation complete and inserted into weather_hourly.")

if __name__ == "__main__":
    main()

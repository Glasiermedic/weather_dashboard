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
    # Read weather_raw into DataFrame
    df = pd.read_sql("SELECT * FROM weather_raw", engine)

    if df.empty:
        print("No data in weather_raw table.")
        return

    # Parse and extract date
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

    # Rename columns
    agg.columns = [
        "temp_avg", "temp_low", "temp_high",
        "humidity_avg", "humidity_min", "humidity_max",
        "wind_speed_avg", "wind_speed_low", "wind_speed_high",
        "wind_gust_max", "dew_point_avg", "windchill_avg",
        "heatindex_avg", "pressureTrend", "pressure_max",
        "pressure_min", "precip_total", "solar_rad_max", "uv_max"
    ]
    agg = agg.reset_index()

    agg["local_time"] = pd.to_datetime(agg["date"])
    agg["day"] = agg["date"].astype(str)

    # Insert using SQLAlchemy
    with engine.begin() as conn:
        for _, row in agg.iterrows():
            row_dict = row.to_dict()

            # Normalize 'date'
            if isinstance(row_dict.get("date"), pd.Timestamp):
                row_dict["date"] = row_dict["date"].date()
            elif isinstance(row_dict.get("date"), str):
                row_dict["date"] = pd.to_datetime(row_dict["date"]).date()

            # Ensure 'local_time' exists and is datetime
            if "local_time" not in row_dict or pd.isna(row_dict["local_time"]):
                row_dict["local_time"] = pd.to_datetime(row_dict["date"])

            # Ensure 'day' is a string version of date
            row_dict["day"] = row_dict["local_time"].strftime("%Y-%m-%d")

            # Debug print (optional)
            print(
                f"⬇️ Inserting row with station_id {row_dict['station_id']}, date {row_dict['date']}, local_time {row_dict['local_time']}, day {row_dict['day']}")

            # Insert
            conn.execute(text("""
                INSERT INTO weather_daily (
                    station_id, date, local_time, day,
                    temp_avg, temp_low, temp_high,
                    humidity_avg, humidity_min, humidity_max,
                    wind_speed_avg, wind_speed_low, wind_speed_high,
                    wind_gust_max, dew_point_avg, windchill_avg, heatindex_avg,
                    pressureTrend, pressure_max, pressure_min,
                    precip_total, solar_rad_max, uv_max
                )
                VALUES (
                    :station_id, :date, :local_time, :day,
                    :temp_avg, :temp_low, :temp_high,
                    :humidity_avg, :humidity_min, :humidity_max,
                    :wind_speed_avg, :wind_speed_low, :wind_speed_high,
                    :wind_gust_max, :dew_point_avg, :windchill_avg, :heatindex_avg,
                    :pressureTrend, :pressure_max, :pressure_min,
                    :precip_total, :solar_rad_max, :uv_max
                )
                ON CONFLICT (station_id, date) DO UPDATE
                SET local_time = EXCLUDED.local_time,
                    day = EXCLUDED.day,
                    temp_avg = EXCLUDED.temp_avg,
                    temp_low = EXCLUDED.temp_low,
                    temp_high = EXCLUDED.temp_high,
                    humidity_avg = EXCLUDED.humidity_avg,
                    humidity_min = EXCLUDED.humidity_min,
                    humidity_max = EXCLUDED.humidity_max,
                    wind_speed_avg = EXCLUDED.wind_speed_avg,
                    wind_speed_low = EXCLUDED.wind_speed_low,
                    wind_speed_high = EXCLUDED.wind_speed_high,
                    wind_gust_max = EXCLUDED.wind_gust_max,
                    dew_point_avg = EXCLUDED.dew_point_avg,
                    windchill_avg = EXCLUDED.windchill_avg,
                    heatindex_avg = EXCLUDED.heatindex_avg,
                    pressureTrend = EXCLUDED.pressureTrend,
                    pressure_max = EXCLUDED.pressure_max,
                    pressure_min = EXCLUDED.pressure_min,
                    precip_total = EXCLUDED.precip_total,
                    solar_rad_max = EXCLUDED.solar_rad_max,
                    uv_max = EXCLUDED.uv_max
            """), row_dict)

    print("✅ Daily aggregation complete and inserted into weather_daily.")

if __name__ == "__main__":
    main()
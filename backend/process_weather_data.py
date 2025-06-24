import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()  # Load .env if running locally

DATABASE_URL = os.getenv("DATABASE_URL")

# SQLAlchemy engine
engine = create_engine(DATABASE_URL)

def load_weather_data(station_id, date_str):
    path = os.path.join("..", "data", station_id, f"{date_str}.json")
    if not os.path.exists(path):
        return None
    try:
        df = pd.read_json(path)
        df["station_id"] = station_id
        return df
    except Exception as e:
        print(f"❌ Error loading {path}: {e}")
        return None

def insert_dataframe(df, table_name):
    try:
        df.to_sql(table_name, engine, if_exists="append", index=False, method="multi")
        print(f"✅ Inserted {len(df)} rows into {table_name}")
    except Exception as e:
        print(f"❌ Error inserting into {table_name}: {e}")

def process_raw(df):
    # Normalize columns (this assumes the JSON is already flattened)
    df = df.rename(columns={
        "imperial.temp": "temp",
        "imperial.windSpeed": "wind_speed",
        "imperial.precipRate": "precipRate"
    })
    df["local_time"] = pd.to_datetime(df["obsTimeLocal"])
    return df[["station_id", "local_time", "temp", "humidity", "wind_speed", "precipRate"]]

def aggregate_hourly(df):
    df["hour"] = df["local_time"].dt.strftime("%Y-%m-%d %H:00:00")
    return df.groupby(["station_id", "hour"]).agg({
        "temp": ["mean", "min", "max"],
        "humidity": ["mean", "min", "max"],
        "wind_speed": ["mean", "min", "max"],
        "precipRate": "sum"
    }).reset_index()

def aggregate_daily(df):
    df["date"] = df["local_time"].dt.date
    return df.groupby(["station_id", "date"]).agg({
        "temp": ["mean", "min", "max"],
        "humidity": ["mean", "min", "max"],
        "wind_speed": ["mean", "min", "max"],
        "precipRate": "sum"
    }).reset_index()

def flatten_columns(df):
    df.columns = ["_".join(col) if isinstance(col, tuple) else col for col in df.columns]
    return df

def run_all():
    stations = ["dustprop", "propdada"]
    dates = pd.date_range(end=pd.Timestamp.today(), periods=3).strftime("%Y%m%d")

    for station in stations:
        for date_str in dates:
            raw_df = load_weather_data(station, date_str)
            if raw_df is None:
                continue

            processed = process_raw(raw_df)
            insert_dataframe(processed, "weather_raw")

            hourly = flatten_columns(aggregate_hourly(processed))
            insert_dataframe(hourly, "weather_hourly")

            daily = flatten_columns(aggregate_daily(processed))
            insert_dataframe(daily, "weather_daily")
def main():
    print("✅ ETL process_weather_data.py ran successfully")
    run_all()
if __name__ == "__main__":
    main()

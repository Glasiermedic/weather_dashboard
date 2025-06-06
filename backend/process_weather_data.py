import os
import json
import pandas as pd
import sqlite3
from datetime import datetime

# Always resolve base paths from the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BASE_INPUT = os.path.join(project_root, "data")
BASE_OUTPUT = os.path.join(project_root, "data_exports")
DB_FILENAME = "weather.db"

os.makedirs(BASE_OUTPUT, exist_ok=True)

def process_station(alias_folder):
    input_path = os.path.join(BASE_INPUT, alias_folder)
    output_path = os.path.join(BASE_OUTPUT, alias_folder)
    os.makedirs(output_path, exist_ok=True)

    all_records = []

    for file in os.listdir(input_path):
        if file.endswith(".json"):
            file_path = os.path.join(input_path, file)
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    observations = data.get("observations", [])
                    for obs in observations:
                        flat = {**obs, **obs.get("imperial", {}), **obs.get("metric", {})}
                        flat.pop("imperial", None)
                        flat.pop("metric", None)
                        flat["station_id"] = alias_folder
                        all_records.append(flat)
            except Exception as e:
                print(f" Error reading {file}: {e}")

    if not all_records:
        print(f" No data found for {alias_folder}")
        return None

    df = pd.DataFrame(all_records)

    if 'obsTimeLocal' in df.columns:
        df['obsTimeLocal'] = pd.to_datetime(df['obsTimeLocal'], errors='coerce')

    rename_map = {
        'obsTimeLocal': 'local_time',
        'obsTimeUtc': 'utc_time',
        'tempAvg': 'temp_avg',
        'tempHigh': 'temp_high',
        'tempLow': 'temp_low',
        'humidityAvg': 'humidity_avg',
        'humidityHigh': 'humidity_high',
        'humidityLow': 'humidity_low',
        'windspeedAvg': 'wind_speed_avg',
        'windspeedHigh': 'wind_speed_high',
        'windspeedLow': 'wind_speed_low',
        'precipTotal': 'precip_total',
        'solarRadiationHigh': 'solar_rad_max',
        'uvHigh': 'uv_max',
        'dewptAvg': 'dew_point_avg',
        'heatindexHigh': 'heat_index_high',
        'heatindexLow': 'heat_index_low',
        'windgustHigh': 'wind_gust_max',
        'qcStatus': 'quality_control',
        'lat': 'latitude',
        'lon': 'longitude'
    }
    df.rename(columns=rename_map, inplace=True)

    # Add year/month columns for grouping
    df['year'] = df['local_time'].dt.year
    df['month'] = df['local_time'].dt.month

    # Save monthly CSVs
    grouped = df.groupby(['year', 'month'])
    for (year, month), group in grouped:
        filename = f"{alias_folder}_{year}_{month:02}.csv"
        filepath = os.path.join(output_path, filename)
        group.to_csv(filepath, index=False)
        print(f" Saved CSV: {filepath}")

    return df

# === Main Routine ===
if __name__ == "__main__":
    station_dirs = [d for d in os.listdir(BASE_INPUT) if os.path.isdir(os.path.join(BASE_INPUT, d))]
    all_frames = []

    for alias in station_dirs:
        df = process_station(alias)
        if df is not None:
            all_frames.append(df)

    # Future-proof: exclude empty/all-NaN frames before concatenating
    non_empty_frames = [
        df.dropna(axis=1, how="all")  # Remove all-NA columns
        for df in all_frames
        if not df.empty and not df.dropna(axis=1, how="all").empty
    ]

    if non_empty_frames:
        full_df = pd.concat(non_empty_frames, ignore_index=True)
        db_path = os.path.join(BASE_OUTPUT, DB_FILENAME)
        conn = sqlite3.connect(db_path)
        full_df.to_sql("weather", conn, if_exists="replace", index=False)
        conn.close()
        print(f" SQLite database saved to: {db_path}")
    else:
        print(" No valid dataframes to combine — skipping database creation.")

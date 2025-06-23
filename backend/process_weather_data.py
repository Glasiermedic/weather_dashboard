import os
import sqlite3
import pandas as pd
from datetime import datetime

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/
DB_PATH = os.path.join(BASE_DIR, "data_exports", "weather.db")

# Connect to DB and read raw data
def load_raw_data():
    print("📦 Connecting to DB...")
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT * FROM weather_raw", conn, parse_dates=["local_time"])
        if df.empty:
            print("⚠️ No data in weather_raw table.")
        return df
    finally:
        conn.close()

# Basic aggregation
def process_data(df):
    if df.empty:
        return pd.DataFrame()

    print(f"📊 Columns in df: {df.columns.tolist()}")

    df["local_time"] = pd.to_datetime(df["local_time"])
    df["local_time"] = df["local_time"].dt.floor("h")

    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    group_cols = ["station_id", "local_time"]

    summary_df = df.groupby(group_cols)[numeric_cols].mean().reset_index()

    return summary_df

# Save to SQLite
def save_summary(df):
    if df.empty:
        print("⚠️ No data to save.")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        df.to_sql("weather_hourly", conn, if_exists="replace", index=False)
        print("✅ Saved processed data to 'weather_hourly' table.")
    finally:
        conn.close()

# Main
def main():
    raw_df = load_raw_data()
    if raw_df.empty:
        return

    summary_df = process_data(raw_df)
    save_summary(summary_df)

if __name__ == "__main__":
    main()

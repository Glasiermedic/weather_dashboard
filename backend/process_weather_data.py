import sqlite3
import pandas as pd
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Path setup
BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data_exports" / "weather.db"

def summarize_by_period(df: pd.DataFrame, period: str) -> pd.DataFrame:
    if df.empty:
        logging.warning("DataFrame is empty. Skipping summary.")
        return pd.DataFrame()

    try:
        df['local_time'] = pd.to_datetime(df['local_time'], errors='coerce')
        df = df.dropna(subset=['local_time'])

        if period == "7d":
            df = df[df['local_time'] >= pd.Timestamp.now() - pd.Timedelta(days=7)]
        elif period == "30d":
            df = df[df['local_time'] >= pd.Timestamp.now() - pd.Timedelta(days=30)]
        elif period == "ytd":
            df = df[df['local_time'].dt.year == pd.Timestamp.now().year]

    except Exception as e:
        logging.error(f"Error during time filtering: {e}")
        return pd.DataFrame()

    return df

def create_summary(df: pd.DataFrame) -> dict:
    if df.empty:
        logging.warning("No data to summarize.")
        return {}

    def safe_mean(col):
        return round(df[col].mean(), 2) if col in df.columns else None

    def safe_max(col):
        return round(df[col].max(), 2) if col in df.columns else None

    def safe_min(col):
        return round(df[col].min(), 2) if col in df.columns else None

    summary = {
        "temp_avg": safe_mean("temp_avg"),
        "temp_low": safe_min("temp_low"),
        "temp_high": safe_max("temp_high"),
        "humidity_avg": safe_mean("humidity_avg"),
        "wind_speed_high": safe_max("wind_speed_high"),
        "wind_speed_low": safe_min("wind_speed_low"),
        "wind_speed_avg": safe_mean("wind_speed_avg"),
        "wind_gust_max": safe_max("wind_gust_max"),
        "dew_point_avg": safe_mean("dew_point_avg"),
        "windchillAvg": safe_mean("windchillAvg"),
        "heatindexAvg": safe_mean("heatindexAvg"),
        "pressureTrend": safe_mean("pressureTrend"),
        "solar_rad_max": safe_max("solar_rad_max"),
        "uv_max": safe_max("uv_max"),
        "precipRate": safe_mean("precipRate"),
        "precip_total": safe_mean("precip_total"),
    }
    return summary

if __name__ == "__main__":
    station_id = "dustprop"
    period = "7d"

    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(f"SELECT * FROM weather_hourly WHERE station_id = ?", conn, params=(station_id,))
        conn.close()
    except Exception as e:
        logging.error(f"Failed to load data: {e}")
        df = pd.DataFrame()

    df_filtered = summarize_by_period(df, period)
    summary = create_summary(df_filtered)

    for key, value in summary.items():
        logging.info(f"{key}: {value}")

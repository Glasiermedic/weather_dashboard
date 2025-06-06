import os
import requests
import sqlite3
from datetime import datetime
from dotenv import load_dotenv

# Load env vars
load_dotenv()
API_KEY = os.getenv("WEATHER_API_KEY")
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data_exports", "weather.db"))

# Add your station IDs here
STATION_IDS = {
    "propdada": "KORMCMIN133",
    "dustprop": "KORMCMIN127"
}

def fetch_5min_data(station_id):
    url = "https://api.weather.com/v2/pws/observations/all/1day"
    params = {
        "stationId": station_id,
        "format": "json",
        "units": "e",
        "apiKey": API_KEY
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json().get("observations", [])

def insert_new_data(station_key, observations):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    count_inserted = 0

    for obs in observations:
        timestamp = obs["obsTimeLocal"]

        cursor.execute("SELECT COUNT(*) FROM weather_raw WHERE station_id = ? AND local_time = ?", (station_key, timestamp))
        if cursor.fetchone()[0] > 0:
            continue

        imp = obs.get("imperial", {})
        row = (
            station_key,
            timestamp,
            imp.get("tempAvg"),
            obs.get("humidityAvg"),
            imp.get("windspeedAvg"),
            imp.get("windgustHigh"),
            imp.get("dewptAvg"),
            imp.get("windchillAvg"),
            imp.get("heatindexAvg"),
            imp.get("pressureMax"),
            imp.get("precipRate"),
            imp.get("precipTotal"),
            obs.get("solarRadiationHigh"),
            obs.get("uvHigh"),
        )

        cursor.execute("""
        INSERT INTO weather_raw (
            station_id, local_time, temp, humidity, wind_speed, wind_gust, dew_point,
            windchill, heatindex, pressure, precip_rate, precip_total,
            solar_radiation, uv
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, row)
        count_inserted += 1

    conn.commit()
    conn.close()
    print(f"✅ {station_key}: {count_inserted} new rows inserted")

# === Main ===
if __name__ == "__main__":
    for key, pws_id in STATION_IDS.items():
        print(f"\n⏳ Fetching {key} ({pws_id})...")
        try:
            data = fetch_5min_data(pws_id)
            insert_new_data(key, data)
        except Exception as e:
            print(f"❌ {key} failed: {e}")

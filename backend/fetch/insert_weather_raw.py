import sqlite3
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data_exports", "weather.db"))
JSON_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data_exports", "1day.json"))

def load_json():
    with open(JSON_PATH, "r") as f:
        return json.load(f)

def insert_raw_data(data):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    observations = data.get("observations", [])
    inserted_count = 0

    for obs in observations:
        try:
            station_id = obs.get("stationID")
            local_time = obs.get("obsTimeLocal")
            imp = obs.get("imperial", {})

            cursor.execute("""
                INSERT OR IGNORE INTO weather_raw (
                    station_id, local_time, temp, humidity, wind_speed, wind_gust,
                    dew_point, windchill, heatindex, pressure, precip_rate,
                    precip_total, solar_radiation, uv
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                station_id,
                local_time,
                imp.get("temp"),
                obs.get("humidity"),
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
            ))
            inserted_count += 1
        except Exception as e:
            print(f"⚠️ Skipping malformed observation: {e}")

    conn.commit()
    conn.close()
    print(f"✅ Inserted {inserted_count} rows into weather_raw.")

if __name__ == "__main__":
    json_data = load_json()
    insert_raw_data(json_data)

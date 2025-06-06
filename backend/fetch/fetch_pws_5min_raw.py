import requests
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Correct path to the database
DB_PATH = os.path.join("..", "..", "data_exports", "weather.db")
API_KEY = os.getenv("WEATHER_API_KEY")

stations = {
    "propdada": "KORMCMIN133",
    "dustprop": "KORMCMIN127"
}

def fetch_and_store(station_id, pws_id):
    print(f"\n⏳ Fetching {station_id} ({pws_id})...")
    try:
        url = (
            f"https://api.weather.com/v2/pws/observations/all/1day"
            f"?stationId={pws_id}&format=json&units=e&apiKey={API_KEY}"
        )
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        observations = data.get("observations", [])

        if not observations:
            print(f"⚠️ No data returned for {station_id}")
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        inserted_count = 0
        for obs in observations:
            local_time = obs.get("obsTimeLocal")
            values = obs.get("imperial", {})

            cursor.execute("""
                SELECT 1 FROM weather_raw WHERE station_id = ? AND local_time = ?
            """, (station_id, local_time))
            if cursor.fetchone():
                continue  # Already exists

            cursor.execute("""
                INSERT INTO weather_raw (
                    station_id, local_time,
                    temp_avg, temp_low, temp_high,
                    humidity_avg, wind_speed_high, wind_speed_low, wind_speed_avg,
                    wind_gust_max, dew_point_avg, windchillAvg, heatindexAvg,
                    pressureTrend, solar_rad_max, uv_max, precipRate, precip_total
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                station_id, local_time,
                values.get("temp"), values.get("tempLow"), values.get("tempHigh"),
                values.get("humidity"), values.get("windSpeed"), values.get("windSpeed"), values.get("windSpeed"),
                values.get("windGust"), values.get("dewpt"), values.get("windChill"), values.get("heatIndex"),
                obs.get("pressureTrend"), obs.get("solarRadiationHigh"), obs.get("uvHigh"),
                values.get("precipRate"), values.get("precipTotal")
            ))
            inserted_count += 1

        conn.commit()
        conn.close()
        print(f"✅ {station_id}: {inserted_count} new rows inserted")

    except Exception as e:
        print(f"❌ Error fetching {station_id}: {e}")

def main():
    for station_id, pws_id in stations.items():
        fetch_and_store(station_id, pws_id)

if __name__ == "__main__":
    main()

import os
import requests
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def fetch_station_data(station_id, alias, start_date, end_date, base_output=None):
    # 🔧 Set base_output to "weather_dashboard/data/" regardless of current location
    if base_output is None:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        base_output = os.path.join(project_root, "data")

    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        print("❌ WEATHER_API_KEY missing in .env")
        return

    output_dir = os.path.join(base_output, alias)
    os.makedirs(output_dir, exist_ok=True)

    delta = timedelta(days=31)
    current_start = start_date

    while current_start < end_date:
        current_end = min(current_start + delta - timedelta(days=1), end_date)
        start_str = current_start.strftime("%Y%m%d")
        end_str = current_end.strftime("%Y%m%d")
        file_name = f"{station_id}_{start_str}_{end_str}.json"
        file_path = os.path.join(output_dir, file_name)

        print(f"\n🔍 Checking {alias} ({station_id}) for {start_str} to {end_str}")
        if os.path.exists(file_path):
            print(f"✅ Skipping {file_name}, already exists.")
        else:
            url = (
                f"https://api.weather.com/v2/pws/history/hourly?"
                f"stationId={station_id}&format=json&units=e"
                f"&startDate={start_str}&endDate={end_str}&apiKey={api_key}"
            )
            print(f"➡️ Requesting: {url}")

            try:
                response = requests.get(url)
                print(f"📡 Status Code: {response.status_code}")

                if response.status_code == 200:
                    data = response.json()
                    obs = data.get("observations", [])
                    if obs:
                        with open(file_path, "w") as f:
                            json.dump(data, f, indent=2)
                        print(f"✅ Data saved: {file_name}")
                    else:
                        print(f"⚠️ No observations in response — skipping save.")
                elif response.status_code == 204:
                    print(f"❌ No data available (204 No Content)")
                elif response.status_code == 401:
                    print(f"❌ Unauthorized (401). Check your API key.")
                elif response.status_code == 403:
                    print(f"❌ Forbidden (403). API key might lack permissions.")
                else:
                    print(f"❌ Error {response.status_code}: {response.text}")
            except Exception as e:
                print(f"❌ Exception occurred: {e}")

        current_start += delta

# === Run script for multiple stations ===
if __name__ == "__main__":
    station_map = {
        "KORMCMIN133": "propdada",
        "KORMCMIN127": "dustprop"
    }

    start = datetime.now() - timedelta(days=365)
    end = datetime.now()

    for station_id, alias in station_map.items():
        fetch_station_data(station_id, alias, start, end)

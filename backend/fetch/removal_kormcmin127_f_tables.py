import sqlite3
import os

# Adjust path if needed
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data_exports", "weather.db"))
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Remove from all relevant tables
tables = ["weather_raw", "weather_hourly", "weather_daily", "weather"]
for table in tables:
    try:
        cursor.execute(f"DELETE FROM {table} WHERE station_id = 'KORMCMIN127'")
        print(f"✅ Deleted from {table}")
    except Exception as e:
        print(f"⚠️ Skipped {table}: {e}")

conn.commit()
conn.close()

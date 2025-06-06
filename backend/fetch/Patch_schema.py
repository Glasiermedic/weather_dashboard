import sqlite3
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data_exports", "weather.db"))
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE weather_hourly ADD COLUMN local_time TEXT;")
    print("✅ Added 'local_time' column to weather_hourly")
except sqlite3.OperationalError:
    print("ℹ️ 'local_time' column already exists")

conn.commit()
conn.close()

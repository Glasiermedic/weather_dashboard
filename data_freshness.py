import sqlite3

conn = sqlite3.connect("data_exports/weather.db")
cursor = conn.cursor()

timestamp_columns = {
    "weather_raw": "local_time",
    "weather_hourly": "local_time",
    "weather_daily": "local_date"
}

for table, time_col in timestamp_columns.items():
    print(f"\nLatest from {table}:")
    try:
        cursor.execute(f"SELECT station_id, MAX({time_col}) FROM {table} GROUP BY station_id")
        for row in cursor.fetchall():
            print(row)
    except Exception as e:
        print(f"❌ Error reading {table}: {e}")

conn.close()

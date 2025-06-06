import sqlite3

DB_PATH = "../data_exports/weather.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    SELECT station_id, MAX(local_time)
    FROM weather
    GROUP BY station_id;
""")

results = cursor.fetchall()
for station_id, max_time in results:
    print(f"{station_id}: Latest timestamp = {max_time}")

conn.close()

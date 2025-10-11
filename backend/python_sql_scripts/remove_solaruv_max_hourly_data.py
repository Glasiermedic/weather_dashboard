import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()
conn = psycopg2.connect(os.getenv("DATABASE_URL"))
cur = conn.cursor()

cur.execute("""
    ALTER TABLE weather_hourly
    DROP COLUMN IF EXISTS solar_rad_max,
    DROP COLUMN IF EXISTS uv_max;
""")

conn.commit()
cur.close()
conn.close()
print("Columns removed.")

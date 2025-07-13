import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Load DB connection string from .env
DATABASE_URL = os.getenv("DATABASE_URL")

def fetch_latest_weather_raw(station_id="propdada"):
    query = """
        SELECT * FROM weather_raw
        WHERE station_id = %s
        ORDER BY local_time DESC
        LIMIT 1;
    """
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            df = pd.read_sql_query(query, conn, params=(station_id,))
            if df.empty:
                print("⚠️ No data found.")
            else:
                print("✅ Latest record:")
                print(df.T)  # Transposed for easier column viewing
    except Exception as e:
        print(f"❌ Error fetching data: {e}")

def list_station_ids():
    query = "SELECT DISTINCT station_id FROM weather_raw;"
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            df = pd.read_sql_query(query, conn)
            print("Available station IDs in weather_raw:")
            print(df)
    except Exception as e:
        print(f"❌ Error fetching station IDs: {e}")

if __name__ == "__main__":
    fetch_latest_weather_raw("KORMCMIN127")
    list_station_ids()


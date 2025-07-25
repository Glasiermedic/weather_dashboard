import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__),"..", ".."))
ENV_PATH = os.path.join(ROOT_DIR, ".env")
load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in .env")

engine = create_engine(DATABASE_URL)

def run_query(sql, params=None):
    """Executes a SQL query and prints each row as a dictionary."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql), params or {})
            rows = result.mappings().all()  # <-- Fix is here
            if not rows:
                print("⚠️ No rows returned.")
            for row in rows:
                print(dict(row))
    except Exception as e:
        print(f"❌ Query failed: {e}")

def main():
    print("📊 Running custom query...\n")

    # 🔧 Example 1: check recent hourly data
    run_query("""
        SELECT 'weather_hourly' AS table_name, column_name FROM information_schema.columns WHERE table_name = 'weather_hourly'
        UNION ALL
        SELECT 'weather_daily' AS table_name, column_name FROM information_schema.columns WHERE table_name = 'weather_daily'
        UNION ALL
        SELECT 'weather_raw' AS table_name, column_name FROM information_schema.columns WHERE table_name = 'weather_raw';
        ;
    """)

    # 👇 You can add other queries below as needed

if __name__ == "__main__":
    main()
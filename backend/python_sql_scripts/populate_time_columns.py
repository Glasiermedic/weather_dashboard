import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATH = os.path.join(ROOT_DIR, ".env")
load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def add_column_if_not_exists(table, column, dtype):
    sql = f"""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name='{table}' AND column_name='{column}'
        ) THEN
            ALTER TABLE {table} ADD COLUMN {column} {dtype};
        END IF;
    END
    $$;
    """
    print(f"➕ Ensuring column: {table}.{column}")
    try:
        raw_conn = engine.raw_connection()
        try:
            cur = raw_conn.cursor()
            cur.execute(sql)
            raw_conn.commit()
            cur.close()
            print(f"✅ Column {table}.{column} added or already exists.")
        finally:
            raw_conn.close()
    except Exception as e:
        print(f"❌ Failed to add column {table}.{column}: {e}")


def run_update(label, sql):
    print(f"🔧 Updating: {label}")
    try:
        with engine.connect() as conn:
            conn.execute(text(sql))
        print(f"✅ {label} updated.")
    except Exception as e:
        print(f"❌ Failed to update {label}: {e}")

def main():
    print("📌 Ensuring columns exist...\n")

    add_column_if_not_exists("weather_raw", "hour", "TIMESTAMP")
    add_column_if_not_exists("weather_raw", "day", "DATE")

    add_column_if_not_exists("weather_hourly", "local_time", "TIMESTAMP")
    add_column_if_not_exists("weather_hourly", "day", "DATE")

    add_column_if_not_exists("weather_daily", "local_time", "TIMESTAMP")
    add_column_if_not_exists("weather_daily", "day", "DATE")

    print("\n📌 Populating new time fields...\n")

    run_update("weather_raw.hour",
        "UPDATE weather_raw SET hour = date_trunc('hour', local_time) WHERE hour IS NULL;"
    )
    run_update("weather_raw.day",
        "UPDATE weather_raw SET day = local_time::date WHERE day IS NULL;"
    )

    run_update("weather_hourly.local_time",
               "UPDATE weather_hourly SET local_time = hour::timestamp WHERE local_time IS NULL;"
               )
    run_update("weather_hourly.day",
        "UPDATE weather_hourly SET day = hour::date WHERE day IS NULL;"
    )

    run_update("weather_daily.local_time",
        "UPDATE weather_daily SET local_time = date_trunc('day', date) WHERE local_time IS NULL;"
    )
    run_update("weather_daily.day",
        "UPDATE weather_daily SET day = date::date WHERE day IS NULL;"
    )

    print("\n✅ All updates complete.")

if __name__ == "__main__":
    main()

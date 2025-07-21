# backend/update_schema_add_time_columns.py

import os
from dotenv import load_dotenv
import sqlalchemy
import pandas as pd
from sqlalchemy import create_engine, text

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATH = os.path.join(ROOT_DIR, ".env")
load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def add_columns_if_missing(table, columns_with_types):
    with engine.connect() as conn:
        existing_cols = pd.read_sql(f"SELECT * FROM {table} LIMIT 1", conn).columns.tolist()
        for col, sql_type in columns_with_types.items():
            if col not in existing_cols:
                print(f"🛠 Adding '{col}' to {table}...")
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {sql_type};"))
            else:
                print(f"✅ '{col}' already exists in {table}")

def main():
    print("🔧 Updating schema...")
    add_columns_if_missing("weather_raw", {
        "hour": "TIMESTAMP",
        "day": "DATE"
    })
    add_columns_if_missing("weather_hourly", {
        "local_time": "TIMESTAMP",
        "day": "DATE"
    })
    add_columns_if_missing("weather_daily", {
        "local_time": "TIMESTAMP",
        "day": "DATE"
    })
    print("✅ Schema update complete.")

if __name__ == "__main__":
    main()

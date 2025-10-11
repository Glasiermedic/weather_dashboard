import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATH = os.path.join(ROOT_DIR, ".env")
load_dotenv(dotenv_path=ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")
assert DATABASE_URL, "DATABASE_URL not found in environment"

TABLES = ["weather_raw", "weather_hourly", "weather_daily"]
OUTPUT_DIR = os.path.join(ROOT_DIR, "reports")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_pg_connection():
    return psycopg2.connect(DATABASE_URL)

def inspect_table(table_name):
    print(f"🔍 Inspecting table: {table_name}")
    with get_pg_connection() as conn:
        df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 500", conn)

    rows = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        example = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
        rows.append({"column": col, "dtype": dtype, "example": example})

    report_df = pd.DataFrame(rows)
    output_path = os.path.join(OUTPUT_DIR, f"{table_name}_columns.csv")
    report_df.to_csv(output_path, index=False)
    print(f"✅ Saved to {output_path}")

if __name__ == "__main__":
    for table in TABLES:
        try:
            inspect_table(table)
        except Exception as e:
            print(f"❌ Error with {table}: {e}")

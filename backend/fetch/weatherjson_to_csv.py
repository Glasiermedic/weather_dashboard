import os
import json
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Paths
MAPPING_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "full_weather_json_fields.csv"))
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))

# PostgreSQL connection
DATABASE_URL = os.getenv("DATABASE_URL")

def load_field_mapping(path):
    df = pd.read_csv(path)
    print("CSV columns:", df.columns)
    return {row["Source Field (from JSON)"]: row["Suggested DB Column Name"] for _, row in df.iterrows()}

def extract_observations(json_path, field_map):
    with open(json_path, "r") as f:
        data = json.load(f)

    obs = data.get("observations", [])
    if not obs:
        logging.warning(f"⚠️ No observations found in {json_path}")
        return pd.DataFrame()

    rows = []
    for record in obs:
        flat = {
            "station_id": record.get("stationID"),
            "local_time": record.get("obsTimeLocal"),
        }
        for json_key, db_column in field_map.items():
            if json_key.startswith("imperial."):
                nested_key = json_key.split(".", 1)[1]
                flat[db_column] = record.get("imperial", {}).get(nested_key)
            else:
                flat[db_column] = record.get(json_key)
        rows.append(flat)

    return pd.DataFrame(rows)

def main():
    logging.info(f"📁 Reading JSON files from: {os.path.abspath(DATA_DIR)}")

    if not os.path.exists(MAPPING_FILE):
        logging.error(f"❌ Field mapping file not found: {MAPPING_FILE}")
        return

    field_map = load_field_mapping(MAPPING_FILE)
    all_dfs = []

    for subfolder in os.listdir(DATA_DIR):
        folder_path = os.path.join(DATA_DIR, subfolder)
        if not os.path.isdir(folder_path):
            continue

        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                json_path = os.path.join(folder_path, filename)
                df = extract_observations(json_path, field_map)
                if not df.empty:
                    all_dfs.append(df)

    if not all_dfs:
        logging.warning("⚠️ No data to save.")
        return

    combined_df = pd.concat(all_dfs, ignore_index=True)
    combined_df["local_time"] = pd.to_datetime(combined_df["local_time"])
    combined_df = combined_df.drop_duplicates(subset=["station_id", "local_time"])

    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                columns = combined_df.columns.tolist()
                values = [tuple(x) for x in combined_df.to_numpy()]
                insert_query = f"""
                    INSERT INTO weather_raw ({', '.join(columns)}) VALUES %s
                    ON CONFLICT (station_id, local_time) DO NOTHING
                """
                execute_values(cur, insert_query, values)
        logging.info("✅ Conversion complete and saved to PostgreSQL.")
    except Exception as e:
        logging.error(f"❌ Failed to insert into PostgreSQL: {e}")

if __name__ == "__main__":
    main()

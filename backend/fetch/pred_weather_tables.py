#!/usr/bin/env python3
import os, uuid, math
import pandas as pd
from ndbc_api import NdbcApi
from google.cloud import bigquery

# -------------------- CONFIG --------------------
# Set these in your environment or edit here:
BQ_PROJECT   = os.getenv("BQ_PROJECT", "aw-tow-botz-co")
BQ_DATASET   = os.getenv("BQ_DATASET", "regional_weatherdata")
# Target tables
BQ_TABLE_AIR   = os.getenv("BQ_TABLE_AIR",   "pacific_ocean_air")
BQ_TABLE_WATER = os.getenv("BQ_TABLE_WATER", "pacific_ocean_water")
BQ_TABLE_AIRPORT = os.getenv("BQ_TABLE_AIRPORT", "pwn_airport") # you'll create this table soon
BQ_TABEL_HIGH_ALT = os.getenv("BQ_HIGH_ALT") # you'll create this table soon

# Buoy fetch window & stations
OCEAN_STATIONS = ['46050', '46015', '46027', '46059']
AIRPORT_STATIONS = ['KMMV', 'KEUG', 'KDLS', 'KONP', 'K6S2', 'KSLE', 'KPDX', 'KALW' ]
AIR_COLS   = ['WDIR', 'WSPD', 'GST', 'PRES', 'ATMP', 'DEWP']
OCEAN_COLS = ['WVHT', 'DPD', 'APD', 'MWD', 'WTMP', 'VIS', 'PTDY', 'TIDE']
START = '2025-01-01'
END   = '2025-09-01'

# Keep only records around :10 past the hour for ocean
TARGET_MINUTE    = 10
MINUTE_TOLERANCE = "0min"   # use "2min" if you want to keep 09..11 too

# -------------------- HELPERS --------------------
def _setup_gcp_creds_from_json_env():
    """If GOOGLE_APPLICATION_CREDENTIALS_JSON is set, write to a temp file for the SDK."""
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON") and not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        import tempfile
        path = tempfile.NamedTemporaryFile(delete=False, suffix=".json").name
        with open(path, "w", encoding="utf-8") as f:
            f.write(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = path

def _bq_client():
    _setup_gcp_creds_from_json_env()
    return bigquery.Client(project=BQ_PROJECT)

def _full_table_id(table_name: str) -> str:
    return f"{BQ_PROJECT}.{BQ_DATASET2}.{table_name}"

def _reset_multiindex(df: pd.DataFrame) -> pd.DataFrame:
    """MultiIndex -> columns: time_utc, station_id, … (forcing UTC)."""
    if df is None or df.empty:
        return pd.DataFrame(columns=["time_utc","station_id"])
    out = df.reset_index().rename(columns={"timestamp": "time_utc"})
    out["time_utc"] = pd.to_datetime(out["time_utc"], utc=True, errors="coerce")
    return out

def _filter_to_minute(df: pd.DataFrame, minute: int = 10, tolerance: str = "0min") -> pd.DataFrame:
    """Keep only rows where timestamp is ~ HH:{minute} (± tolerance)."""
    if df.empty:
        return df
    ts = pd.DatetimeIndex(df.index.get_level_values(0))
    target = ts.floor('H') + pd.to_timedelta(minute, unit='m')
    tol = pd.Timedelta(tolerance)
    mask = (ts >= target - tol) & (ts <= target + tol)
    return df[mask]

def _merge_upsert_df(client: bigquery.Client, table_id: str, df: pd.DataFrame, key_cols=("station_id","time_utc")):
    """
    Idempotent write: write to staging then MERGE on key_cols.
    Drops any df columns that don't exist in the table schema.
    """
    if df is None or df.empty:
        print(f"({table_id}) nothing to write.")
        return

    table = client.get_table(table_id)
    table_cols = [f.name for f in table.schema]

    # keep only known columns
    cols = [c for c in df.columns if c in table_cols]
    if not cols:
        raise ValueError(f"No overlapping columns with {table_id}. Table has: {table_cols}")

    df = df[cols].copy()

    # auto-fill ingested_at if present in schema
    if "ingested_at" in table_cols and "ingested_at" not in df.columns:
        df["ingested_at"] = pd.Timestamp.utcnow()
        cols.append("ingested_at")

    # ensure timestamps are timestamps
    for c in cols:
        if c.lower().endswith("time") or c.lower().endswith("utc") or c.lower().endswith("_ts"):
            try:
                df[c] = pd.to_datetime(df[c], utc=True, errors="coerce")
            except Exception:
                pass
        elif c not in ("station_id",):
            # best-effort numeric coercion for metric columns
            if df[c].dtype == "object":
                df[c] = pd.to_numeric(df[c], errors="coerce")

    # write to staging
    staging = f"{BQ_PROJECT}.{BQ_DATASET2}._stg_{table.table_id}_{uuid.uuid4().hex[:8]}"
    bigquery.LoadJobConfig  # just to make linters happy
    client.load_table_from_dataframe(df, staging,
        job_config=bigquery.LoadJobConfig(write_disposition="WRITE_TRUNCATE")
    ).result()

    # MERGE
    can_merge = all(k in cols for k in key_cols)
    if can_merge:
        key_match = " AND ".join([f"T.{k}=S.{k}" for k in key_cols])
        update_cols = [c for c in cols if c not in key_cols]
        set_clause = ", ".join([f"{c}=S.{c}" for c in update_cols]) if update_cols else ""
        insert_cols = ", ".join(cols)
        insert_vals = ", ".join([f"S.{c}" for c in cols])
        merge_sql = f"""
        MERGE `{table_id}` T
        USING `{staging}` S
        ON {key_match}
        {"WHEN MATCHED THEN UPDATE SET " + set_clause if set_clause else ""}
        WHEN NOT MATCHED THEN INSERT ({insert_cols}) VALUES ({insert_vals});
        """
        client.query(merge_sql).result()
    else:
        client.query(f"INSERT INTO `{table_id}` SELECT * FROM `{staging}`").result()

    client.delete_table(staging, not_found_ok=True)
    print(f"✅ wrote {len(df)} rows -> {table_id}")

# -------------------- FETCH + WRITE --------------------
def main():
    client = _bq_client()
    api = NdbcApi()

    # 1) Pull buoys
    air_df = api.get_data(
        station_ids=OCEAN_STATIONS,
        modes=['stdmet', 'cwind'],
        start_time=START, end_time=END,
        cols=AIR_COLS
    )

    ocean_df = api.get_data(
        station_ids=OCEAN_STATIONS,
        modes=['stdmet', 'cwind'],
        start_time=START, end_time=END,
        cols=OCEAN_COLS
    )

    # 2) Filter ocean to HH:10 (± tolerance)
    ocean_10_df = _filter_to_minute(ocean_df, minute=TARGET_MINUTE, tolerance=MINUTE_TOLERANCE)

    # 3) Flatten to columns BigQuery can ingest
    air_out   = _reset_multiindex(air_df)
    ocean_out = _reset_multiindex(ocean_10_df)

    # 4) Upsert to your two tables
    air_table_id   = _full_table_id(BQ_TABLE_AIR)     # regional_weatherdata.pacific_ocean_air
    water_table_id = _full_table_id(BQ_TABLE_WATER)   # regional_weatherdata.pacific_ocean_water

    # Ensure we only try to write columns that exist in the target tables.
    # (If your table schema matches AIR_COLS/OCEAN_COLS + time_utc/station_id/ingested_at, this Just Works™)
    _merge_upsert_df(client, air_table_id,   air_out)      # keys: station_id+time_utc
    _merge_upsert_df(client, water_table_id, ocean_out)    # keys: station_id+time_utc

    # 5) (Optional) Airports -> pwn_airport
    # If you already have a DataFrame `airport_df` with columns like:
    # time_utc, station_id (ICAO), temp_c, dewpoint_c, wind_mps, gust_mps, pressure_hpa, ...
    # just call:
    #   airport_table_id = _full_table_id(BQ_TABLE_AIRPORT)
    #   _merge_upsert_df(client, airport_table_id, airport_df)
    # I’m keeping this commented until your pwn_airport table exists with final schema.

if __name__ == "__main__":
    main()

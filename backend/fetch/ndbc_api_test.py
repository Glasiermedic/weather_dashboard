#!/usr/bin/env python3
from ndbc_api import NdbcApi
import pandas as pd
import math

# ---------- config ----------
STATIONS = ['46050', '46015', '46027', '46059', '46076', '51002', '44065', '41009', '46011', '46041']
AIR_COLS   = ['WDIR', 'WSPD', 'GST', 'PRES', 'ATMP', 'DEWP']
OCEAN_COLS = ['WVHT', 'DPD', 'APD', 'MWD', 'WTMP', 'VIS', 'PTDY', 'TIDE']
START = '2025-01-01'
END   = '2025-09-01'
POPULATED_THRESHOLD = 0.30   # 30% of columns must be non-null
TARGET_MINUTE = 10
MINUTE_TOLERANCE = "3min" # allows for buoy and other stations to post their data within a window and count towards the overall data
# ---------- helpers ----------
def filter_to_minute(df: pd.DataFrame, minute: int = 10, tolerance: str = "0min") -> pd.DataFrame:
    """
    Keep only rows where timestamp is at HH:{minute}, with optional ±tolerance.
    Works with MultiIndex [timestamp, station_id].
    """
    if df.empty:
        return df
    ts = pd.DatetimeIndex(df.index.get_level_values(0))
    target = ts.floor('H') + pd.to_timedelta(minute, unit='m')
    tol = pd.Timedelta(tolerance)
    mask = (ts >= target - tol) & (ts <= target + tol)
    return df[mask]


def count_populated_by_station(df: pd.DataFrame, threshold: float, station: list[str]) -> pd.Series:
    """
    Given a MultiIndex df indexed by [timestamp, station_id], return a Series
    with counts of rows per station where non-null ratio >= threshold.
    """
    if df.empty:
        # still return a series with 0 for any stations we expected
        return pd.Series(0, index=pd.Index(stations, name= "station_id"), name="populated_rows")
    out = {}
    for stn, g in df.groupby(level="station_id"):
        #keep only columns that have at least one non-null for that station
        valid_cols = [c for c in g.columns if g[c].notna().any()]
        if not valid_cols:
            out[stn] = 0
            continue
        needed = math.ceil(threshold * len(valid_cols))
        row_nonnull = g[valid_cols].notna().sum(axis=1)
        out[stn] = int((row_nonnull >= needed).sum())

    s = pd.Series(out, name="populated_rows").reindex(STATIONS, fill_value=0)
    return s

    # ratio of non-null values across columns for each row
    non_null = df.notna().sum(axis=1)
    needed = math.ceil(threshold * df.shape[1])  # minimum non-nulls to pass
    mask = non_null >= needed

    # group by station_id (level=1) and sum True values
    counts = mask.groupby(level="station_id").sum().astype(int)

    # ensure all requested stations appear (fill missing with 0)
    counts = counts.reindex(STATIONS, fill_value=0)
    counts.name = "populated_rows"
    return counts

# ---------- fetch ----------
ndbc_api = NdbcApi()

air_buoys_df = ndbc_api.get_data(
    station_ids=STATIONS,
    modes=['stdmet', 'cwind'],
    start_time=START,
    end_time=END,
    cols=AIR_COLS
)

ocean_buoys_df = ndbc_api.get_data(
    station_ids=STATIONS,
    modes=['stdmet', 'cwind'],
    start_time=START,
    end_time=END,
    cols=OCEAN_COLS
)

# ---------- processing ----------
# only HH:10 (optionally ± MINUTE_TOLERANCE)
ocean_10_df = filter_to_minute(ocean_buoys_df, minute=TARGET_MINUTE, tolerance=MINUTE_TOLERANCE)

# counts with "smart" denominator per station
air_counts   = count_populated_by_station(air_buoys_df, POPULATED_THRESHOLD, STATIONS)
ocean_counts = count_populated_by_station(ocean_10_df, POPULATED_THRESHOLD, STATIONS)

# combine for a tidy summary table
summary = pd.DataFrame({
    "air_populated": air_counts,
    f"ocean_{TARGET_MINUTE:02d}_populated": ocean_counts
}).astype(int)

# ---------- output ----------
th_label = int(POPULATED_THRESHOLD * 100)
print(f"Populated row counts by station (≥{th_label}% non-null):")
print(summary)

print("\nSample ocean rows at :10 past the hour:")
print(ocean_10_df.head(10))
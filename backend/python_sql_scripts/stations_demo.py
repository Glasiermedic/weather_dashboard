# wd_backend/scripts/stations_demo.py
from wd_backend.common.stations_store import upsert_station, resolve, build_reverse_index

# 1) upsert some stations
upsert_station(
    "ndbc", "46029",
    name_by_provider={"ndbc": "Columbia River Bar (example label)"},
    ids_by_provider={"ndbc": "46029", "twc": "46029"},
    lat=46.10, lon=-124.20,
    meta={"state": "WA", "country": "US"}
)

upsert_station(
    "icao", "KMMV",
    name_by_provider={"awc": "McMinnville Municipal Airport"},
    ids_by_provider={"awc": "KMMV", "twc": "KMMV"},
    meta={"state": "OR", "country": "US"}
)

upsert_station(
    "pws", "KORMCMIN127",
    name_by_provider={"twc": "McMinnville East (PWS)"},
    ids_by_provider={"twc": "KORMCMIN127"},
    meta={"state": "OR", "country": "US"}
)

print("✅ Upserts done.")

# 2) resolve by any provider+code
print("resolve('ndbc','46029') ->", resolve("ndbc", "46029"))
print("resolve('awc','KMMV')  ->", resolve("awc", "KMMV"))
print("resolve('twc','KORMCMIN127') ->", resolve("twc", "KORMCMIN127"))

# 3) build in-memory reverse index (optional cache)
cache = build_reverse_index()
print("cache['ndbc:46029'] =", cache.get("ndbc:46029"))
print("cache['awc:KMMV']   =", cache.get("awc:KMMV"))

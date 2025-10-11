#!/usr/bin/env python3
"""
Aggregate marine buoy + airport observations into a PWS-like schema.

Outputs (per station):
{
  'station_id': '46029',
  'source': 'BUOY',                      # or 'METAR'
  'period_hours': 6,
  'count': 7,                            # number of obs in window
  'time_start_utc': '2025-09-01T12:53:00Z',
  'time_end_utc':   '2025-09-01T18:53:00Z',

  # Temperature (air)
  'temp_avg': 68.3, 'temp_low': 63.9, 'temp_high': 71.1,            # °F (default units='us')
  # Dew point / RH (if available or derivable)
  'dew_point_avg': 54.0, 'humidity_avg': 63.2,                      # °F, %
  # Wind (sustained & gust)
  'wind_speed_avg': 7.8, 'wind_speed_low': 0.0, 'wind_speed_high': 14.2, # mph
  'wind_gust_max': 22.5,                                            # mph
  # Pressure
  'pressure_avg': 30.05,                                            # inHg
  # Sea surface temp (buoys only, if present)
  'sea_temp_avg': 60.4,                                             # °F
  # Raw units used
  'units': 'us'                                                     # 'us' or 'si'
}

Customize the station lists and `LOOKBACK_HOURS` in __main__.
"""

from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Optional, Tuple
import math

import requests
import pandas as pd
from ndbc_api import NdbcApi   # pip install ndbc-api

# --------------------------- Config ---------------------------

AWC_METAR = "https://aviationweather.gov/api/data/metar"  # airport METAR JSON
DEFAULT_UNITS = "us"  # 'us' (°F, mph, inHg) or 'si' (°C, m/s, hPa)

# --------------------------- Unit helpers ---------------------------

def c_to_f(c: Optional[float]) -> Optional[float]:
    return None if c is None or pd.isna(c) else (c * 9/5 + 32)

def f_to_c(f: Optional[float]) -> Optional[float]:
    return None if f is None or pd.isna(f) else ((f - 32) * 5/9)

def ms_to_mph(v: Optional[float]) -> Optional[float]:
    return None if v is None or pd.isna(v) else (v * 2.236936)

def kt_to_mps(v: Optional[float]) -> Optional[float]:
    return None if v is None or pd.isna(v) else (v * 0.514444)

def kt_to_mph(v: Optional[float]) -> Optional[float]:
    return None if v is None or pd.isna(v) else (v * 1.15078)

def hpa_to_inhg(v: Optional[float]) -> Optional[float]:
    return None if v is None or pd.isna(v) else (v / 33.8639)

def inhg_to_hpa(v: Optional[float]) -> Optional[float]:
    return None if v is None or pd.isna(v) else (v * 33.8639)

# --------------------------- Psychrometrics ---------------------------

def rh_from_t_and_td(temp_c: Optional[float], dewpoint_c: Optional[float]) -> Optional[float]:
    """Compute relative humidity (%) from T (°C) and Td (°C)."""
    if temp_c is None or dewpoint_c is None or pd.isna(temp_c) or pd.isna(dewpoint_c):
        return None
    # Magnus approximation
    a, b = 17.625, 243.04
    es = math.exp(a * temp_c / (b + temp_c))
    e  = math.exp(a * dewpoint_c / (b + dewpoint_c))
    rh = 100.0 * (e / es)
    return max(0.0, min(100.0, rh))

def dewpoint_from_t_and_rh(temp_c: Optional[float], rh_percent: Optional[float]) -> Optional[float]:
    """Compute dewpoint (°C) from T (°C) and RH (%)."""
    if temp_c is None or rh_percent is None or pd.isna(temp_c) or pd.isna(rh_percent) or rh_percent <= 0:
        return None
    a, b = 17.625, 243.04
    gamma = (a * temp_c / (b + temp_c)) + math.log(rh_percent / 100.0)
    td = (b * gamma) / (a - gamma)
    return td

# --------------------------- METAR (airports) ---------------------------

def human_obs_time(t: Optional[str]) -> Optional[pd.Timestamp]:
    """Return pd.Timestamp[UTC] from epoch seconds or ISO string."""
    if t is None:
        return None
    try:
        return pd.to_datetime(int(t), unit="s", utc=True)
    except Exception:
        return pd.to_datetime(t, utc=True, errors="coerce")

def fetch_metars_awc(icao_ids: List[str], hours: int = 6) -> Dict[str, pd.DataFrame]:
    """
    Fetch a window of METARs for ICAO stations; return dict of DataFrames per ICAO.
    Columns normalized (SI): time_utc, temp_c, dewpoint_c, wind_mps, gust_mps, pressure_hpa.
    """
    params = {"ids": ",".join(icao_ids), "format": "json", "hours": hours}
    r = requests.get(AWC_METAR, params=params, timeout=25)
    r.raise_for_status()
    data = r.json() if r.headers.get("content-type","").startswith("application/json") else []

    by_icao: Dict[str, list] = {icao: [] for icao in icao_ids}
    for rec in data:
        icao = (rec.get("icaoId") or rec.get("station") or rec.get("siteId") or "").upper()
        if not icao or icao not in by_icao:
            continue
        t = human_obs_time(rec.get("obsTime") or rec.get("dateTime") or rec.get("valid"))
        temp_c = rec.get("tempC")
        dew_c  = rec.get("dewpointC")
        wind_kt = rec.get("windSpeedKt") or rec.get("windSpeed")
        gust_kt = rec.get("windGustKt")  or rec.get("windGust")
        alt_inhg = rec.get("altimInHg") or rec.get("altimeter")

        by_icao[icao].append({
            "time_utc": t,
            "temp_c": float(temp_c) if temp_c is not None else None,
            "dewpoint_c": float(dew_c) if dew_c is not None else None,
            "wind_mps": kt_to_mps(wind_kt) if wind_kt is not None else None,
            "gust_mps": kt_to_mps(gust_kt) if gust_kt is not None else None,
            "pressure_hpa": inhg_to_hpa(alt_inhg) if alt_inhg is not None else None,
        })

    out: Dict[str, pd.DataFrame] = {}
    for icao, rows in by_icao.items():
        df = pd.DataFrame(rows)
        if not df.empty:
            df["time_utc"] = pd.to_datetime(df["time_utc"], utc=True, errors="coerce")
            df = df.dropna(subset=["time_utc"]).sort_values("time_utc")
        out[icao] = df
    return out

# --------------------------- Buoys (NDBC stdmet) ---------------------------

def _to_utc_series_any(ts: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(ts, errors="coerce", utc=False)
    try:
        if getattr(parsed.dt, "tz", None) is None:
            return parsed.dt.tz_localize("UTC")
        else:
            return parsed.dt.tz_convert("UTC")
    except Exception:
        return parsed

def _ensure_buoy_time(df: pd.DataFrame) -> pd.Series:
    # DatetimeIndex?
    if isinstance(df.index, pd.DatetimeIndex):
        idx = df.index
        try:
            return idx.tz_localize("UTC") if idx.tz is None else idx.tz_convert("UTC")
        except Exception:
            pass
    # Common columns
    for cand in ["datetime", "date_time", "time", "timestamp", "obs_time", "DATE_TIME"]:
        if cand in df.columns:
            return _to_utc_series_any(df[cand])
    # Build from parts
    cols = set(df.columns)
    def pick(*names):
        for n in names:
            if n in cols: return n
        return None
    y  = pick("YYYY", "YY", "Year")
    mo = pick("MM", "Month")
    d  = pick("DD", "Day")
    h  = pick("hh", "HH", "Hr", "HR")
    mi = pick("mm", "MIN", "Minute")

    if y and mo and d:
        def to_num(c): return pd.to_numeric(df[c], errors="coerce") if c else 0
        year  = to_num(y)
        # Fix two-digit years if present
        if (year <= 99).any():
            year = year.apply(lambda v: 2000+int(v) if pd.notna(v) and int(v) <= 69 else (1900+int(v) if pd.notna(v) else v))
        month = to_num(mo)
        day   = to_num(d)
        hour  = to_num(h) if h else 0
        minu  = to_num(mi) if mi else 0
        ts = pd.to_datetime(dict(year=year, month=month, day=day, hour=hour, minute=minu), errors="coerce")
        return _to_utc_series_any(ts)
    return pd.Series(pd.NaT, index=df.index)

def fetch_buoys_stdmet(buoy_ids: List[str], hours: int = 6) -> Dict[str, pd.DataFrame]:
    """
    Fetch standard meteorological data for buoys via ndbc-api, then filter to last `hours`.
    Normalize to (SI): time_utc, temp_c (ATMP), dewpoint_c (DEWP), wind_mps (WSPD),
    gust_mps (GST), pressure_hpa (PRES), sea_temp_c (WTMP).
    """
    api = NdbcApi()
    now_utc = datetime.now(timezone.utc)
    start_utc = now_utc - timedelta(hours=hours)
    start_date = start_utc.date().isoformat()
    end_date   = now_utc.date().isoformat()

    out: Dict[str, pd.DataFrame] = {}
    for stn in buoy_ids:
        try:
            raw = api.get_data(station_id=stn, mode="stdmet",
                               start_time=start_date, end_time=end_date, as_df=True)
        except Exception:
            out[stn] = pd.DataFrame()
            continue

        df = raw if isinstance(raw, pd.DataFrame) else pd.DataFrame()
        if df.empty:
            out[stn] = df
            continue

        # build/parse time column (may come back tz-naive)
        t = _ensure_buoy_time(df)
        df = df.assign(time_utc=t)

        def col(name): return name if name in df.columns else None
        mapped = pd.DataFrame({
            "time_utc": df["time_utc"],
            "temp_c":   df[col("ATMP")] if col("ATMP") else None,
            "dewpoint_c": df[col("DEWP")] if col("DEWP") else None,
            "wind_mps": df[col("WSPD")] if col("WSPD") else None,
            "gust_mps": df[col("GST")]  if col("GST")  else None,
            "pressure_hpa": df[col("PRES")] if col("PRES") else None,
            "sea_temp_c": df[col("WTMP")] if col("WTMP") else None,
        })

        # 🔧 force tz-aware UTC to avoid tz-naive vs tz-aware comparisons
        mapped["time_utc"] = pd.to_datetime(mapped["time_utc"], utc=True, errors="coerce")

        # numeric coercion
        for k in ["temp_c","dewpoint_c","wind_mps","gust_mps","pressure_hpa","sea_temp_c"]:
            if k in mapped.columns:
                mapped[k] = pd.to_numeric(mapped[k], errors="coerce")

        mapped = mapped.dropna(subset=["time_utc"])
        mapped = mapped[mapped["time_utc"] >= start_utc].sort_values("time_utc")
        out[stn] = mapped

    return out

# --------------------------- Aggregation ---------------------------

def _nanavg(series: pd.Series) -> Optional[float]:
    if series is None or series.empty:
        return None
    try:
        return float(series.dropna().mean()) if series.notna().any() else None
    except Exception:
        return None

def _nanmin(series: pd.Series) -> Optional[float]:
    if series is None or series.empty:
        return None
    s = series.dropna()
    return float(s.min()) if not s.empty else None

def _nanmax(series: pd.Series) -> Optional[float]:
    if series is None or series.empty:
        return None
    s = series.dropna()
    return float(s.max()) if not s.empty else None

def to_pws_metrics(df: pd.DataFrame, station_id: str, period_hours: int, source: str, units: str = DEFAULT_UNITS) -> Dict[str, Optional[float]]:
    """
    Aggregate a normalized SI dataframe into PWS-like metrics.
    Expects columns: time_utc, temp_c, dewpoint_c, wind_mps, gust_mps, pressure_hpa, sea_temp_c (optional).
    """
    rec = {
        "station_id": station_id,
        "source": source,
        "period_hours": period_hours,
        "count": 0,
        "time_start_utc": None,
        "time_end_utc": None,
        "temp_avg": None, "temp_low": None, "temp_high": None,
        "humidity_avg": None, "dew_point_avg": None,
        "wind_speed_avg": None, "wind_speed_low": None, "wind_speed_high": None,
        "wind_gust_max": None,
        "pressure_avg": None,
        "sea_temp_avg": None,
        "units": units,
    }
    if df is None or df.empty:
        return rec

    df = df.copy()
    df["time_utc"] = pd.to_datetime(df["time_utc"], utc=True, errors="coerce")
    df = df.dropna(subset=["time_utc"]).sort_values("time_utc")
    if df.empty:
        return rec

    rec["count"] = int(len(df))
    rec["time_start_utc"] = df["time_utc"].iloc[0].isoformat()
    rec["time_end_utc"]   = df["time_utc"].iloc[-1].isoformat()

    # Relative humidity if missing: compute from temp & dewpoint
    if "dewpoint_c" in df and "temp_c" in df:
        if "humidity" not in df.columns or df["humidity"].isna().all():
            df["humidity"] = [rh_from_t_and_td(t, d) for t, d in zip(df["temp_c"], df["dewpoint_c"])]

    # Unit conversion
    if units == "us":
        t_col = df["temp_c"].apply(c_to_f) if "temp_c" in df else pd.Series(dtype=float)
        td_col = df["dewpoint_c"].apply(c_to_f) if "dewpoint_c" in df else pd.Series(dtype=float)
        w_col = df["wind_mps"].apply(ms_to_mph) if "wind_mps" in df else pd.Series(dtype=float)
        g_col = df["gust_mps"].apply(ms_to_mph) if "gust_mps" in df else pd.Series(dtype=float)
        p_col = df["pressure_hpa"].apply(hpa_to_inhg) if "pressure_hpa" in df else pd.Series(dtype=float)
        st_col= df["sea_temp_c"].apply(c_to_f) if "sea_temp_c" in df else pd.Series(dtype=float)
    else:  # 'si'
        t_col  = df.get("temp_c", pd.Series(dtype=float))
        td_col = df.get("dewpoint_c", pd.Series(dtype=float))
        w_col  = df.get("wind_mps", pd.Series(dtype=float))
        g_col  = df.get("gust_mps", pd.Series(dtype=float))
        p_col  = df.get("pressure_hpa", pd.Series(dtype=float))
        st_col = df.get("sea_temp_c", pd.Series(dtype=float))

    # Aggregate
    rec["temp_avg"] = _nanavg(t_col)
    rec["temp_low"] = _nanmin(t_col)
    rec["temp_high"] = _nanmax(t_col)

    if "humidity" in df.columns:
        rec["humidity_avg"] = _nanavg(df["humidity"])

    rec["dew_point_avg"] = _nanavg(td_col)

    rec["wind_speed_avg"] = _nanavg(w_col)
    rec["wind_speed_low"] = _nanmin(w_col)
    rec["wind_speed_high"] = _nanmax(w_col)
    rec["wind_gust_max"] = _nanmax(g_col)

    rec["pressure_avg"] = _nanavg(p_col)

    if not st_col.empty:
        rec["sea_temp_avg"] = _nanavg(st_col)

    return rec

# --------------------------- End-to-end convenience ---------------------------

def fetch_and_aggregate(
    buoy_ids: List[str],
    airport_ids: List[str],
    hours: int = 6,
    units: str = DEFAULT_UNITS
) -> Dict[str, Dict]:
    """
    Return {"BUOY": {station: metrics}, "METAR": {station: metrics}}
    where metrics match the PWS-like schema you use (temp_* / wind_* / humidity_avg / etc.).
    """
    # Fetch
    buoy_df_map  = fetch_buoys_stdmet(buoy_ids, hours=hours)
    metar_df_map = fetch_metars_awc(airport_ids, hours=hours)

    # Aggregate
    result = {"BUOY": {}, "METAR": {}}
    for stn, df in buoy_df_map.items():
        result["BUOY"][stn] = to_pws_metrics(df, stn, hours, "BUOY", units=units)
    for icao, df in metar_df_map.items():
        # For METARs, add humidity from T & Td inside to_pws_metrics
        result["METAR"][icao] = to_pws_metrics(df, icao, hours, "METAR", units=units)
    return result

# --------------------------- Example run ---------------------------

if __name__ == "__main__":
    # Your stations:
    buoys    = ["46029", "46050"]        # ocean buoys near OR coast
    airports = ["KMMV", "KHIO", "KUAO"]  # near McMinnville

    LOOKBACK_HOURS = 6
    UNITS = "us"  # change to 'si' for °C, m/s, hPa

    data = fetch_and_aggregate(buoys, airports, hours=LOOKBACK_HOURS, units=UNITS)

    # Pretty print
    import json
    print(json.dumps(data, indent=2, sort_keys=True))

import os
from dotenv import load_dotenv
import psycopg2
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from process_weather_data import run_all
import requests
from urllib.parse import urlparse

# 🔍 Locate and load the .env from project root
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ENV_PATH = os.path.join(ROOT_DIR, ".env")

print("Looking for .env at:", ENV_PATH)  # 👈 For debugging
load_dotenv(dotenv_path=ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")
print("Loaded DATABASE_URL:", DATABASE_URL)  # 👈 Confirm it's working
app = Flask(__name__)
CORS(app)
def get_pg_connection():
    return psycopg2.connect(DATABASE_URL)

def column_exists(table, column):
    with get_pg_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = %s AND column_name = %s
                );
            """, (table, column))
            return cur.fetchone()[0]

@app.route("/api/summary_data")
def get_summary_data():
    station_id = request.args.get("station_id")
    period = request.args.get("period", "1d")

    with get_pg_connection() as conn:
        df = pd.read_sql_query(
            "SELECT * FROM weather_hourly WHERE station_id = %s",
            conn,
            params=(station_id,)
        )

    df["local_time"] = pd.to_datetime(df["local_time"])
    df = df.sort_values("local_time")

    now = pd.Timestamp.now()
    if period == "1d":
        df = df[df["local_time"] >= now - pd.Timedelta(days=1)]
    elif period == "7d":
        df = df[df["local_time"] >= now - pd.Timedelta(days=7)]
    elif period == "30d":
        df = df[df["local_time"] >= now - pd.Timedelta(days=30)]
    elif period == "ytd":
        df = df[df["local_time"].dt.year == now.year]

    summary = {
        "temp_avg": round(df["temp_avg"].mean(skipna=True), 2),
        "temp_low": round(df["temp_avg"].min(skipna=True), 2),
        "temp_high": round(df["temp_avg"].max(skipna=True), 2),
        "humidity_avg": round(df["humidity_avg"].mean(skipna=True), 2),
        "wind_speed_high": round(df["wind_speed_avg"].max(skipna=True), 2),
        "wind_speed_low": round(df["wind_speed_avg"].min(skipna=True), 2),
        "wind_speed_avg": round(df["wind_speed_avg"].mean(skipna=True), 2),
        "wind_gust_max": round(df["wind_gust_max"].max(skipna=True), 2),
        "dew_point_avg": round(df["dew_point_avg"].mean(skipna=True), 2),
        "windchillAvg": round(df["windchillAvg"].mean(skipna=True), 2),
        "heatindexAvg": round(df["heatindexAvg"].mean(skipna=True), 2),
        "pressureTrend": round(df["pressureTrend"].mean(skipna=True), 2),
        "solar_rad_max": round(df["solar_rad_max"].max(skipna=True), 2),
        "uv_max": round(df["uv_max"].max(skipna=True), 2),
        "precipRate": 0.0,
        "precip_total": round(df["precip_total"].sum(skipna=True), 2)
    }

    return jsonify(summary)

@app.route("/api/graph_data")
def get_graph_data():
    station_ids_param = request.args.get("station_id") or request.args.get("station_ids")
    period = request.args.get("period", "1d")
    column = request.args.get("column", "temp_avg")

    print(f"📊 Request received: station_ids={station_ids_param}, period={period}, column={column}")

    if not station_ids_param or not column:
        return jsonify({"error": "Missing required parameters"}), 400

    station_ids = station_ids_param.split(",")

    if period == "1d":
        table = "weather_hourly"
        timestamp_field = "local_time"
        days_back = 1
    elif period == "7d":
        table = "weather_hourly"
        timestamp_field = "local_time"
        days_back = 7
    elif period in ["30d", "ytd"]:
        table = "weather_daily"
        timestamp_field = "date"
        days_back = 30 if period == "30d" else 365
    else:
        return jsonify({"error": "Invalid period"}), 400

    if not column_exists(table, column):
        return jsonify({"error": f"Invalid column '{column}' for table '{table}'"}), 400

    try:
        with get_pg_connection() as conn:
            if len(station_ids) == 1:
                df = pd.read_sql_query(
                    f"""
                    SELECT {timestamp_field} AS ts, {column}
                    FROM {table}
                    WHERE station_id = %s AND {timestamp_field} >= NOW() - INTERVAL '{days_back} days'
                    ORDER BY {timestamp_field}
                    """,
                    conn,
                    params=(station_ids[0],)
                )
            else:
                station_placeholders = ",".join(["%s"] * len(station_ids))
                df = pd.read_sql_query(
                    f"""
                    SELECT {timestamp_field} AS ts, AVG({column}) AS {column}
                    FROM {table}
                    WHERE station_id IN ({station_placeholders})
                      AND {timestamp_field} >= NOW() - INTERVAL '{days_back} days'
                    GROUP BY {timestamp_field}
                    ORDER BY {timestamp_field}
                    """,
                    conn,
                    params=station_ids
                )

            if df.empty:
                return jsonify({"timestamps": [], "values": []})

            df["ts"] = pd.to_datetime(df["ts"])
            return jsonify({
                "timestamps": df["ts"].dt.strftime("%Y-%m-%d %H:%M").tolist(),
                "values": df[column].where(pd.notnull(df[column]), None).tolist()
            })

    except Exception as e:
        import traceback
        print(f"❌ Error loading graph data: {e}")
        traceback.print_exc()
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

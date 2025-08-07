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
from psycopg2 import pool

# 👇 Create a global connection pool object
db_pool = None

# 👇 At startup, initialize the connection pool
def init_db_pool():
    global db_pool
    if db_pool is None:
        db_pool = pool.SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=DATABASE_URL
        )
        if db_pool:
            print("✅ Database connection pool created")

# 👇 Function to get a connection from the pool
def get_pg_connection():
    if db_pool is None:
        init_db_pool()
    return db_pool.getconn()

# 👇 Function to return a connection back to the pool
def release_pg_connection(conn):
    if db_pool and conn:
        db_pool.putconn(conn)


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
        timestamp_field = "hour"  # 🔁 use 'hour' instead of 'local_time'
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
@app.route("/api/current_data_live")
def get_current_data_live():
    station_id = request.args.get("station_id")
    if not station_id:
        return jsonify({"error": "Missing station_id"}), 400

    try:
        with get_pg_connection() as conn:
            df = pd.read_sql_query(
                "SELECT * FROM weather_raw WHERE station_id = %s ORDER BY local_time DESC LIMIT 1",
                conn,
                params=(station_id,)
            )
            if not df.empty:
                row = df.iloc[0]
                return jsonify({
                    "temp": row.get("avg_temp"),
                    "humidity": row.get("avg_humidity"),
                    "wind_speed": row.get("avg_wnd_spd"),
                    "precip": row.get("precip_rate", 0.0),
                    "timestamp": row.get("local_time"),
                    "fallback": True
                })
    except Exception as e:
        print(f"❌ Fallback error: {e}")

    return jsonify({"error": "No data available"}), 500


@app.route("/api/table_data")
def get_table_data():
    station_ids_param = request.args.get("station_id") or request.args.get("station_ids")
    if not station_ids_param:
        return jsonify({"error": "Missing station_id(s)"}), 400

    station_ids = station_ids_param.split(",")

    try:
        with get_pg_connection() as conn:
            station_placeholders = ",".join(["%s"] * len(station_ids))
            df = pd.read_sql_query(
                f"""
                SELECT *
                FROM weather_hourly
                WHERE station_id IN ({station_placeholders})
                  AND local_time >= NOW() - INTERVAL '48 hours'
                ORDER BY local_time DESC
                """,
                conn,
                params=station_ids
            )
        return jsonify({
            "rows": df.to_dict(orient="records")
        })
    except Exception as e:
        print("❌ Error fetching table data:", e)
        return jsonify({"error": "Internal server error"}), 500


@app.route("/api/debug/weather_daily_columns")
def get_weather_daily_columns():
    try:
        with get_pg_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'weather_hourly';
                """)
                columns = [row[0] for row in cur.fetchall()]
        return jsonify({"columns": columns})
    except Exception as e:
        print(f"❌ Error in get_weather_daily_columns: {e}")
        return jsonify({"error": "Failed to fetch columns"}), 500
@app.route("/api/generate_summary")
def generate_summary():
    try:
        period = request.args.get("period", "7d")
        stations_param = request.args.get("station_ids")
        station_ids = stations_param.split(",") if stations_param else None

        result = run_all(station_ids=station_ids, period=period)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/api/test_db")
def test_db():
    try:
        conn = get_pg_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            return jsonify({"results": cur.fetchone()[0]})
    finally:
        release_pg_connection(conn)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True)
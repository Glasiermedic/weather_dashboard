import os
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from process_weather_data import main as run_all
app = Flask(__name__)
CORS(app)

# ✅ Correct relative path from backend/app.py to data_exports/weather.db
DB_PATH = os.path.join("..", "data_exports", "weather.db")

@app.route("/api/summary_data")
def get_summary_data():
    station_id = request.args.get("station_id")
    period = request.args.get("period", "1d")

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM weather_hourly WHERE station_id = ?", conn, params=(station_id,))
    conn.close()

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
    station_id = request.args.get("station_id")
    period = request.args.get("period", "1d")
    column = request.args.get("column", "temp_avg")

    if not station_id or not column:
        return jsonify({"error": "Missing required parameters"}), 400

    # Choose table and timestamp field based on time period
    if period == "1d":
        table = "weather_raw"
        timestamp_field = "local_time"
    elif period == "7d":
        table = "weather_hourly"
        timestamp_field = "local_time"
    elif period in ["30d", "ytd"]:
        table = "weather_daily"
        timestamp_field = "local_date"
    else:
        return jsonify({"error": "Invalid period"}), 400

    # Build SQL query
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        f"SELECT {timestamp_field} AS timestamp, {column} FROM {table} WHERE station_id = ?",
        conn,
        params=(station_id,)
    )
    conn.close()

    # Convert and filter by period
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    now = pd.Timestamp.now()

    if period == "1d":
        df = df[df["timestamp"] >= now - pd.Timedelta(days=1)]
        label_format = "%H:%M"
    elif period == "7d":
        df = df[df["timestamp"] >= now - pd.Timedelta(days=7)]
        label_format = "%m-%d %H:%M"
    elif period == "30d":
        df = df[df["timestamp"] >= now - pd.Timedelta(days=30)]
        label_format = "%m-%d"
    elif period == "ytd":
        df = df[df["timestamp"].dt.year == now.year]
        label_format = "%m-%d"

    df = df.sort_values("timestamp")

    return jsonify({
        "labels": df["timestamp"].dt.strftime(label_format).tolist(),
        "data": df[column].fillna(0).round(2).tolist()
    })

@app.route("/api/current_data_live")
def get_current_data_live():
    station_id = request.args.get("station_id")
    if not station_id:
        return jsonify({"error": "Missing station_id"}), 400

    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return jsonify({"error": "API key missing"}), 500

    url = (
        f"https://api.weather.com/v2/pws/observations/current?"
        f"stationId={station_id}&format=json&units=e&apiKey={api_key}"
    )

    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            obs = data.get("observations", [])
            if obs:
                latest = obs[0]
                return jsonify({
                    "temp": latest.get("imperial", {}).get("temp"),
                    "humidity": latest.get("humidity"),
                    "wind_speed": latest.get("imperial", {}).get("windSpeed"),
                    "precip": latest.get("imperial", {}).get("precipRate", 0.0),
                    "timestamp": latest.get("obsTimeLocal"),
                    "fallback": False
                })
        elif response.status_code == 204:
            print("⚠️ No current data from API (204 No Content)")
        else:
            print(f"⚠️ Error from Weather API: {response.status_code}")
    except Exception as e:
        print(f"❌ Live data error: {e}")

    # Fallback: get the most recent value from SQLite
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(
            "SELECT * FROM weather_raw WHERE station_id = ? ORDER BY local_time DESC LIMIT 1",
            conn, params=(station_id,)
        )
        conn.close()
        if not df.empty:
            row = df.iloc[0]
            return jsonify({
                "temp": row.get("temp"),
                "humidity": row.get("humidity"),
                "wind_speed": row.get("wind_speed"),
                "precip": row.get("precipRate", 0.0),
                "timestamp": row.get("local_time"),
                "fallback": True
            })
    except Exception as e:
        print(f"❌ Fallback error: {e}")

    return jsonify({"error": "No data available"}), 500

@app.route("/api/generate_summary")
def generate_summary():
    try:
        # Optional: use query params ?period=30d or ?station_ids=dustprop,propdada
        period = request.args.get("period", "7d")
        stations_param = request.args.get("station_ids")
        station_ids = stations_param.split(",") if stations_param else None

        result = run_all(station_ids=station_ids, period=period)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)

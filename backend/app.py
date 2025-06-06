from flask import Flask, request, jsonify
import sqlite3
import pandas as pd
import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
load_dotenv()

# === Configuration ===
DB_PATH = os.path.join(os.path.dirname(__file__), '../data_exports/weather.db')
API_KEY = os.getenv("WEATHER_API_KEY")

STATION_ID_MAP = {
    "propdada": "KORMCMIN133",
    "dustprop": "KORMCMIN127"
}

# === Helper Function ===
def filter_by_period(df, period):
    now = datetime.now()
    df["local_time"] = pd.to_datetime(df["local_time"])

    if period == "1d":
        return df[df["local_time"] >= now - timedelta(days=1)]
    elif period == "7d":
        return df[df["local_time"] >= now - timedelta(days=7)]
    elif period == "30d":
        return df[df["local_time"] >= now - timedelta(days=30)]
    elif period == "week":
        return df[df["local_time"] >= now - timedelta(days=now.weekday())]
    elif period == "month":
        return df[(df["local_time"].dt.month == now.month) & (df["local_time"].dt.year == now.year)]
    elif period == "ytd":
        return df[df["local_time"].dt.year == now.year]
    return df

# === Endpoints ===
@app.route("/api/summary_data")
def summary_data():
    station_id = request.args.get("station_id")
    period = request.args.get("period", "30d")

    if not station_id:
        return jsonify({"error": "Missing station_id"}), 400

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM weather WHERE station_id = ?", conn, params=(station_id,))
    conn.close()

    if df.empty:
        return jsonify({"error": "No data found"}), 404

    df = filter_by_period(df, period)

    summary = {
        "temp_avg": round(df['temp_avg'].mean(), 1) if 'temp_avg' in df else None,
        "humidity_avg": round(df['humidity_avg'].mean(), 1) if 'humidity_avg' in df else None,
        "wind_speed_avg": round(df['wind_speed_avg'].mean(), 1) if 'wind_speed_avg' in df else None,
        "precip_total": round(df['precip_total'].sum(), 2) if 'precip_total' in df else None,
    }
    return jsonify(summary)

@app.route("/api/graph_data")
def graph_data():
    station_id = request.args.get("station_id")
    period = request.args.get("period")
    column = request.args.get("column")

    if not station_id or not period or not column:
        return jsonify({"error": "Missing parameters"}), 400

    # Choose the correct table
    if period == "1d":
        table = "weather_raw"
        time_column = "local_time"
        time_cutoff = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    elif period == "7d":
        table = "weather_hourly"
        time_column = "local_hour"
        time_cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
    else:
        table = "weather_daily"
        time_column = "local_date"
        if period == "30d":
            time_cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        elif period == "ytd":
            time_cutoff = f"{datetime.now().year}-01-01"
        else:
            return jsonify({"error": "Invalid period"}), 400

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT {time_column}, {column}
            FROM {table}
            WHERE station_id = ?
            AND {time_column} >= ?
            ORDER BY {time_column}
        """, (station_id, time_cutoff))
        rows = cursor.fetchall()
        conn.close()

        labels = [r[0] for r in rows]
        data = [r[1] for r in rows]

        return jsonify({
            "labels": labels,
            "data": data
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/current_data")
def current_data():
    station_id = request.args.get("station_id")
    if not station_id:
        return jsonify({"error": "Missing station_id"}), 400

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM weather WHERE station_id = ? ORDER BY local_time DESC LIMIT 1", conn, params=(station_id,))
    conn.close()

    if df.empty:
        return jsonify({"error": "No data found"}), 404

    row = df.iloc[0]
    return jsonify({
        "timestamp": row["local_time"],
        "temp": row.get("temp_avg"),
        "humidity": row.get("humidity_avg"),
        "wind_speed": row.get("wind_speed_avg"),
        "precip": row.get("precip_total"),
        "fallback": True
    })

@app.route("/api/current_data_live")
def current_data_live():
    station_id = request.args.get("station_id")
    if not station_id:
        return jsonify({"error": "Missing station_id"}), 400

    real_station_id = STATION_ID_MAP.get(station_id, station_id)
    url = "https://api.weather.com/v2/pws/observations/current"
    params = {
        "stationId": real_station_id,
        "format": "json",
        "units": "e",
        "apiKey": API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        print(f"\n🔍 Raw API response:\n{response.text}\n")

        data = response.json()
        obs_list = data.get("observations")

        if obs_list and len(obs_list) > 0:
            obs = obs_list[0]
            current = {
                "timestamp": obs.get("obsTimeLocal"),
                "temp": obs.get("imperial", {}).get("temp"),
                "humidity": obs.get("humidity"),
                "wind_speed": obs.get("imperial", {}).get("windSpeed"),
                "precip": obs.get("imperial", {}).get("precipTotal"),
                "fallback": False
            }
            return jsonify(current)

        raise ValueError("No valid live observation found")

    except Exception as e:
        print(f"⚠️ Live API failed for {station_id}. Falling back to DB. Error: {e}")
        fallback = current_data().json
        fallback["fallback"] = True
        return jsonify(fallback)

if __name__ == "__main__":
    app.run(debug=True)

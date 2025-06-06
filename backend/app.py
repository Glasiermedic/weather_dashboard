import os
import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd

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

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT local_time, {column} FROM weather_hourly WHERE station_id = ?", conn, params=(station_id,))
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

    return jsonify({
        "labels": df["local_time"].dt.strftime("%m-%d %H:%M").tolist(),
        "data": df[column].fillna(0).round(2).tolist()
    })

if __name__ == "__main__":
    app.run(debug=True)

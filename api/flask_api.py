import os
from flask import Flask, jsonify
from flask_cors import CORS
from google.cloud import bigquery
from dotenv import load_dotenv
from datetime import datetime
import base64

# Decode and write the credentials file if in Render
if os.getenv("GOOGLE_CREDENTIALS_B64"):
    credentials_path = "/tmp/service-account.json"
    with open(credentials_path, "wb") as f:
        f.write(base64.b64decode(os.environ["GOOGLE_CREDENTIALS_B64"]))
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
# Load environment variables
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = os.getenv("BQ_DATASET")
TABLE_ID = "transformer_sales"
FULL_TABLE = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

client = bigquery.Client(project=PROJECT_ID)

app = Flask(__name__)
CORS(app)

@app.route("/api/sales_summary")
def sales_summary():
    query = f"""
        SELECT
            ROUND(SUM(total_sale), 2) AS total_revenue,
            ROUND(AVG(unit_price), 2) AS avg_unit_price,
            (SELECT product_type FROM `{FULL_TABLE}`
             GROUP BY product_type
             ORDER BY SUM(total_sale) DESC
             LIMIT 1) AS top_product
        FROM `{FULL_TABLE}`
    """
    result = client.query(query).result()
    row = list(result)[0]
    return jsonify(dict(row))

@app.route("/api/sales_by_region")
def sales_by_region():
    query = f"""
        SELECT region, ROUND(SUM(total_sale), 2) AS total_sales
        FROM `{FULL_TABLE}`
        GROUP BY region
        ORDER BY total_sales DESC
    """
    result = client.query(query).result()
    data = [{"region": row["region"], "total_sales": row["total_sales"]} for row in result]
    return jsonify(data)

@app.route("/api/top_reps")
def top_reps():
    start_of_year = datetime.utcnow().replace(month=1, day=1).date()

    query = f"""
        SELECT
            sales_rep,
            COUNT(*) AS num_sales,
            SUM(units_sold) AS total_units,
            ROUND(SUM(total_sale), 2) AS total_sales
        FROM `{FULL_TABLE}`
        WHERE DATE(sale_date) >= '{start_of_year}'
        GROUP BY sales_rep
        ORDER BY total_sales DESC
        LIMIT 5
    """

    result = client.query(query).result()
    data = [
        {
            "sales_rep": row["sales_rep"],
            "num_sales": row["num_sales"],
            "total_units": row["total_units"],
            "total_sales": row["total_sales"]
        }
        for row in result
    ]
    return jsonify(data)

@app.route("/api/sales_window_summary")
def sales_window_summary():
    today = datetime.utcnow().date()
    first_of_month = today.replace(day=1)

    query = f"""
        WITH today_sales AS (
            SELECT
                ROUND(SUM(total_sale), 2) AS total_revenue,
                ROUND(AVG(unit_price), 2) AS avg_unit_price,
                COUNT(*) AS transactions
            FROM `{FULL_TABLE}`
            WHERE DATE(sale_date) = '{today}'
        ),
        month_sales AS (
            SELECT
                ROUND(SUM(total_sale), 2) AS total_revenue,
                ROUND(AVG(unit_price), 2) AS avg_unit_price,
                COUNT(*) AS transactions
            FROM `{FULL_TABLE}`
            WHERE DATE(sale_date) >= '{first_of_month}'
        )
        SELECT * FROM today_sales, month_sales
    """

    result = client.query(query).result()
    row = list(result)[0]

    data = {
        "today": {
            "total_revenue": row["total_revenue"],
            "avg_unit_price": row["avg_unit_price"],
            "transactions": row["transactions"]
        },
        "month": {
            "total_revenue": row["total_revenue_1"],
            "avg_unit_price": row["avg_unit_price_1"],
            "transactions": row["transactions_1"]
        }
    }

    return jsonify(data)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

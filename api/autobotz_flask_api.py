# imports the needed libaries to utfrom flask import Flask, jsonify
import base64

from flask import Flask
# handles cross-origin resource sharing - allowing Vercel to make API requests to a separate wd_backend (render)
# and prevents browser from blocking requests due to origin mismatch
#lets our app talk to bigquery to run queries  and simulate the cloud environment locally
# loads .env file variables into os.environ for local deployment/testing
# handles date and time operations to get current date or the start of year or month
from flask_cors import CORS
from google.cloud import bigquery
from dotenv import load_dotenv
from datetime import datetime

# load the envronmental variables from .env file
load_dotenv()

# Checks whether the google credentials environmental variable is present
# defines a temporary file path where the decoded service account key will be saved to address the
# file writing limitations of Render
# Opens the file at /tmp/service_account.json in binary write mode "wb" and the with makes it close after writing
# Decodes the base64 credentials and writes the original json file
#Set the environment variable to point to the file we had just created, for google sdk and bigQuery utilization
if os.getenv("GOOGLE_CREDENTIALS_B64"):
    credentials_path = "/tmp/service-account.json"
    with open(credentials_path, "wb") as f:
        f.write(base64.b64decode(os.environ["GOOGLE_CREDENTIALS_B64"]))
    os.evniron["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

# Load environment variables from .env, identifying what project, dataset table and makes the full address
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = os.getenv("BQ_DATASET")
TABLE_ID = "transformer_sales"
FULL_TABLE = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

# Setup Flask api calls allow cross origin resource sharing and a google big query client
app = Flask(__name__)
CORS(app)
bq = bigquery.Client(project=PROJECT_ID)
# ------------------------------
# Endpoint: /api/sales_summary
# defines an api/url that when visited or fetched runs the function sales_summary on big query table(s)
# query fetches total revenue, average unit price and the top  product type with the highest total sales
# ------------------------------
@app.route("/api/sales_summary")
def sales_summary():
    query = f"""
        SELECT
            ROUND(SUM(total_sale), 2) AS total_revenue,
            ROUND(AVG(unit_price), 2) AS avg_unit_price,
            (SELECT product_type
             FROM `{FULL_TABLE}`
             GROUP BY product_type
             ORDER BY SUM(total_sale) DESC
             LIMIT 1) AS top_product
        FROM `{FULL_TABLE}`
    """
    row = list(bq.query(query).result())[0]
    return jsonify(dict(row)) # converts the data into json format for use by frontend


# ------------------------------
# Endpoint: /api/sales_by_region
# defines an api/url that when visited or fetched runs the function sales_by_region on big query table(s)
# query fetches sales data, groups the data by region, then calculates the total sales per region.
# ------------------------------
@app.route("/api/sales_by_region")
def sales_by_region():
    query = f"""
        SELECT region, ROUND(SUM(total_sale), 2) AS total_sales
        FROM `{FULL_TABLE}`
        GROUP BY region
        ORDER BY total_sales DESC
    """
    results = bq.query(query).result()
    data = [{"region": r["region"], "total_sales": r["total_sales"]} for r in results]
    return jsonify(data) # converts the data into json format for use by frontend


# ------------------------------
# Endpoint: /api/top_reps
# defines an api/url that when visited or fetched runs the function top_reps on BigQuery table(s)
# query fetches sales data, filters to sales from the current year,
# groups the data by sales_rep, then calculates:
#    - number of sales (num_sales)
#    - total units sold (total_units)
#    - total revenue (total_sales)
# orders by total revenue and returns the top 5 performing sales reps
# ------------------------------
@app.route("/api/top_reps")
def top_reps():
    start_of_year = datetime.utcnow().replace(month=1, day=1).date()
    query = f"""
        SELECT sales_rep,
               COUNT(*) AS num_sales,
               SUM(units_sold) AS total_units,
               ROUND(SUM(total_sale), 2) AS total_sales
        FROM `{FULL_TABLE}`
        WHERE DATE(sale_date) >= '{start_of_year}'
        GROUP BY sales_rep
        ORDER BY total_sales DESC
        LIMIT 5
    """
    results = bq.query(query).result()
    data = [{
        "sales_rep": r["sales_rep"],
        "num_sales": r["num_sales"],
        "total_units": r["total_units"],
        "total_sales": r["total_sales"]
    } for r in results]
    return jsonify(data)   # converts the data into json format for use by frontend


# ------------------------------
# Endpoint: /api/sales_window_summary
# defines an api/url that when visited or fetched runs the function sales_window_summary on BigQuery table(s)
# query pulls two windows of sales data:
#    - today's sales (total revenue, avg unit price, transactions)
#    - this month's sales (same metrics)
# returns both in a single response under "today" and "month" keys
# ------------------------------
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
    row = list(bq.query(query).result())[0]

    return jsonify({
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
    })


# ------------------------------
# Run app locally (Render uses gunicorn)
This block allows the Flask app to be started with:
#    python autobotz_flask_api.py
#
# - Render will ignore this block in production, as it uses gunicorn.
# - It binds the app to all IPs (0.0.0.0) on the specified port.
# - PORT can be set in .env or default to 5000.
# ------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



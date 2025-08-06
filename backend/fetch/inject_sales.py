import os
import random
from datetime import datetime
from google.cloud import bigquery
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set credentials path for local or server
credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if credentials_path:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

# Load BigQuery env vars
project_id = os.getenv("GCP_PROJECT_ID")
dataset = os.getenv("BQ_DATASET")

if not project_id or not dataset:
    raise EnvironmentError("Missing GCP_PROJECT_ID or BQ_DATASET in environment variables.")

TABLE_ID = f"{project_id}.{dataset}.transformer_sales"
client = bigquery.Client(project=project_id)

# Constants
SALES_REPS = ['Ava', 'Carlos', 'John', 'Lisa', 'Mary', 'Noah']
SALES_WEIGHTS = [0.25, 0.25, 0.25, 0.1, 0.1, 0.05]
REGIONS = ['US-East', 'US-North', 'US-South', 'US-West', 'CA', 'EUR', 'AFR-North', 'AFR-South',
           'AUS', 'PAC-Islands', 'RUS', 'CHIN', 'JPN', 'AMER-South', 'AMER-Central']
PRODUCT_TYPES = ['Cast Resin', 'Dry-Type', 'Oil-Insulated', 'Padmount', 'Substation', 'Switchgear', 'Three-Phase']
UNIT_OPTIONS = [1, 2, 3, 4, 5, 7]
UNIT_WEIGHTS = [0.24, 0.24, 0.10, 0.18, 0.14, 0.10]

def generate_transaction(order_id, timestamp):
    units_sold = random.choices(UNIT_OPTIONS, weights=UNIT_WEIGHTS, k=1)[0]
    unit_price = round(random.uniform(300, 1500), 2)
    total_sale = round(units_sold * unit_price, 2)
    return {
        'order_id': order_id,
        'sale_timestamp': timestamp.isoformat(),
        'sale_date': timestamp.date().isoformat(),
        'sales_rep': random.choices(SALES_REPS, weights=SALES_WEIGHTS, k=1)[0],
        'region': random.choice(REGIONS),
        'product_type': random.choice(PRODUCT_TYPES),
        'units_sold': units_sold,
        'unit_price': unit_price,
        'total_sale': total_sale
    }

def main():
    now = datetime.utcnow()
    if not (3 <= now.hour < 20):
        print("⏱️ Outside permitted window (3 AM–7 PM UTC). Exiting.")
        return

    # Get max order_id
    query = f"SELECT MAX(order_id) AS max_id FROM `{TABLE_ID}`"
    result = client.query(query).result()
    row = next(result)
    starting_id = (row.max_id or 0) + 1

    # Create records
    num_rows = random.randint(1, 4)
    entries = [
        generate_transaction(order_id=starting_id + i, timestamp=now.replace(minute=random.randint(0, 59), second=random.randint(0, 59)))
        for i in range(num_rows)
    ]

    # Insert into BigQuery
    client.insert_rows_json(TABLE_ID, entries)
    print(f"✅ Inserted {num_rows} record(s) to {TABLE_ID} starting at order_id {starting_id}")

if __name__ == "__main__":
    main()

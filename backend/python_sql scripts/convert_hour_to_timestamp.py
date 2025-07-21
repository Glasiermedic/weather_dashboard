import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ENV_PATH = os.path.join(ROOT_DIR, ".env")
load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def convert_hour_column():
    print("🔧 Converting weather_hourly.hour to TIMESTAMP...")
    sql = """
    ALTER TABLE weather_hourly
    ALTER COLUMN hour TYPE timestamp USING hour::timestamp;
    """
    try:
        with engine.begin() as conn:
            conn.execute(text(sql))
        print("✅ Conversion successful.")
    except Exception as e:
        print(f"❌ Failed to convert column: {e}")

if __name__ == "__main__":
    convert_hour_column()

import os
import psycopg2
from dotenv import load_dotenv

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_PATH = os.path.join(ROOT_DIR, ".env")
print("Loading .env from:", ENV_PATH)
load_dotenv(dotenv_path=ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")
print("Connecting to:", DATABASE_URL)

def fix_column_type():
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cur:
                print("🔧 Running column type correction...")

                cur.execute("""
                    ALTER TABLE weather_daily
                    ALTER COLUMN date TYPE date USING date::date;
                """)

                conn.commit()
                print("✅ 'date' column successfully converted to type DATE in 'weather_daily'.")

    except Exception as e:
        print("❌ Error updating column type:", e)

if __name__ == "__main__":
    fix_column_type()

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# ───────────────────────────────────────────────
# 🧩 1. PASTE YOUR SQL QUERY BELOW
# Leave it empty ("") to run the default query instead.
# ───────────────────────────────────────────────
CUSTOM_SQL = """
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'weather_hourly'
ORDER BY ordinal_position;
"""

# ───────────────────────────────────────────────
# 🔧 2. Load environment and connect
# ───────────────────────────────────────────────
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ENV_PATH = os.path.join(ROOT_DIR, ".env")
load_dotenv(ENV_PATH)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL not found in .env")

engine = create_engine(DATABASE_URL, future=True)


# ───────────────────────────────────────────────
# 🧮 3. Helper to execute and print results
# ───────────────────────────────────────────────
def run_query(sql, params=None):
    try:
        with engine.connect() as conn:
            result = conn.execute(text(sql), params or {})
            rows = result.mappings().all()
            if not rows:
                print("⚠️ No rows returned.")
            else:
                # pretty print
                headers = list(rows[0].keys())
                col_widths = {h: max(len(str(h)), *(len(str(r[h])) for r in rows)) for h in headers}
                header_line = " | ".join(h.ljust(col_widths[h]) for h in headers)
                sep_line = "-+-".join("-" * col_widths[h] for h in headers)
                print(header_line)
                print(sep_line)
                for r in rows:
                    print(" | ".join(str(r[h]).ljust(col_widths[h]) for h in headers))
    except Exception as e:
        print(f"❌ Query failed: {e}")


# ───────────────────────────────────────────────
# 🚀 4. Run your query (or default)
# ───────────────────────────────────────────────
def main():
    print(f"🔗 Connected to: {engine.url}\n")

    sql = CUSTOM_SQL.strip()
    if not sql:
        sql = """
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
        """

    run_query(sql)


if __name__ == "__main__":
    main()



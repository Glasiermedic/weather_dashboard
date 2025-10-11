def add_column_if_not_exists(table, column, dtype):
    sql = f"""
    DO $$
    BEGIN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name='{table}' AND column_name='{column}'
        ) THEN
            ALTER TABLE {table} ADD COLUMN {column} {dtype};
        END IF;
    END
    $$;
    """
    print(f"➕ Ensuring column: {table}.{column}")
    try:
        # Use raw psycopg2 connection to force immediate commit
        with engine.raw_connection() as raw_conn:
            with raw_conn.cursor() as cur:
                cur.execute(sql)
            raw_conn.commit()
        print(f"✅ Column {table}.{column} added or already exists.")
    except Exception as e:
        print(f"❌ Failed to add column {table}.{column}: {e}")
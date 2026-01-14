import psycopg2
import time

conn = psycopg2.connect("dbname=fudstop3 user=chuck password=fud")
cur = conn.cursor()

while True:
    print(f"\n-- Checking at {time.strftime('%Y-%m-%d %H:%M:%S')} --", flush=True)

    cur.execute("""
        SELECT table_name
        FROM information_schema.columns
        WHERE column_name = 'insertion_timestamp'
          AND table_schema = 'public'
    """)
    tables = cur.fetchall()

    for (table,) in tables:
        try:
            cur.execute(f"""
                SELECT 1
                FROM public.{table}
                WHERE insertion_timestamp > NOW() - INTERVAL '1 minute'
                ORDER BY insertion_timestamp DESC
                LIMIT 1
            """)
            row = cur.fetchone()
            if row:
                print(f"✅ Recent data in table: {table}", flush=True)
        except Exception as e:
            print(f"⚠️ Error in {table}: {e}", flush=True)

    time.sleep(1)
import asyncio
import sys
from pathlib import Path

# Add project root to path if needed
project_dir = str(Path.cwd().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)


from fudstop4.apis.polygonio.polygon_options import PolygonOptions

# Your full query_dict should already be defined/imported
from query_dict import query_dict  # <-- replace with actual path if separate

db = PolygonOptions()


async def verify_table_counts():
    await db.connect()
    for table in query_dict.keys():
        try:
            count_query = f"SELECT COUNT(*) AS count FROM {table}"
            result = await db.fetch(count_query)
            count = result[0]['count']
            print(f"{table:30s} → {count:>8} rows")
        except Exception as e:
            print(f"{table:30s} → ❌ Error: {e}")


# Run the verification
if __name__ == "__main__":
    asyncio.run(verify_table_counts())

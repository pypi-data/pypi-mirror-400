from pathlib import Path
import sys
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
import pandas as pd
import aiohttp
from datetime import datetime, timedelta
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
import asyncio
opts = PolygonOptions()
async def download_finra_data(date: str, session: aiohttp.ClientSession) -> str | None:
    """
    Download FINRA short volume data for a given date using the provided
    aiohttp session.  Returns the raw text on success or ``None`` if the
    request fails.

    Args:
        date: Date string in YYYYMMDD format.
        session: An aiohttp ClientSession for making HTTP requests.
    """
    url = f"https://cdn.finra.org/equity/regsho/daily/CNMSshvol{date}.txt"
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.text()
            else:
                print(f"Failed to download data for {date} (status {resp.status})")
                return None
    except Exception as e:
        print(f"Error downloading data for {date}: {e}")
        return None

def parse_finra_data(raw_data: str):
    """Parses raw FINRA data into a structured dataframe."""
    from io import StringIO
    df = pd.read_csv(StringIO(raw_data), sep='|')
    return df

async def fetch_finra_data(start_date: str, end_date: str, session: aiohttp.ClientSession) -> pd.DataFrame | None:
    """
    Fetch FINRA short volume data between two dates asynchronously using
    a shared HTTP session.  Results from each day are concatenated into a
    single DataFrame.  Returns ``None`` if no data could be fetched.

    Args:
        start_date: Start date in YYYYMMDD format.
        end_date: End date in YYYYMMDD format or a datetime object.
        session: An aiohttp ClientSession for making HTTP requests.
    """
    current_date = datetime.strptime(start_date, "%Y%m%d")
    if isinstance(end_date, str):
        end_date_dt = datetime.strptime(end_date, "%Y%m%d")
    else:
        end_date_dt = end_date
    # Collect date strings
    date_strings = []
    while current_date <= end_date_dt:
        date_strings.append(current_date.strftime("%Y%m%d"))
        current_date += timedelta(days=1)
    # Download all files concurrently
    tasks = [download_finra_data(d, session) for d in date_strings]
    raw_results = await asyncio.gather(*tasks)
    dataframes = []
    for raw_data in raw_results:
        if raw_data:
            df = parse_finra_data(raw_data)
            dataframes.append(df)
    if dataframes:
        return pd.concat(dataframes, ignore_index=True)
    else:
        print("No data fetched for the given date range.")
        return None
import asyncio
async def main() -> None:
    """
    Periodically fetch FINRA short volume data for the past month, upsert
    it into the ``finra_shorts`` table, and sleep for a configured interval.
    Uses a single database connection and a single HTTP session for
    efficiency.
    """
    await opts.connect()
    try:
        async with aiohttp.ClientSession() as session:
            while True:
                today = datetime.today().strftime("%Y%m%d")
                prior_date = (datetime.today() - timedelta(days=30)).strftime("%Y%m%d")
                final_df = await fetch_finra_data(prior_date, today, session)
                if final_df is not None:
                    # Rename columns to match database schema
                    final_df = final_df.rename(
                        columns={
                            "Date": "date",
                            "Symbol": "ticker",
                            "ShortVolume": "short_volume",
                            "TotalVolume": "total_volume",
                            "Market": "market",
                            "ShortExemptVolume": "short_exempt_volume",
                        }
                    )
                    await opts.batch_upsert_dataframe(
                        final_df,
                        table_name='finra_shorts',
                        unique_columns=['ticker', 'date'],
                    )
                    print(
                        f"[✓] Upserted {len(final_df)} FINRA short volume records "
                        f"for {prior_date}–{today}"
                    )
                await asyncio.sleep(600)  # Wait 10 minutes between fetches
    finally:
        await opts.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
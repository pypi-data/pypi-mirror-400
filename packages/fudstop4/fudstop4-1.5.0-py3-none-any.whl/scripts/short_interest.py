from pathlib import Path
import sys
import asyncio

# Set up project directory for imports
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from imports import *
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers
from fudstop4.apis.ultimate.ultimate_sdk import UltimateSDK
ultimate = UltimateSDK()
BATCH_SIZE = 10
SLEEP_SECONDS = 86400  # 24 hours

async def main():
    await db.connect()

    while True:
        try:
            short_interest_data = await ultimate.short_interest_for_tickers(most_active_tickers)

            for ticker, short_interest_obj in short_interest_data.items():
                if not short_interest_obj or short_interest_obj.df.empty:
                    continue

                # Get outstanding shares from multi_quote
                query = f"SELECT outstanding_shares FROM multi_quote WHERE ticker = '{ticker.upper()}'"
                result = await db.fetch(query)

                if not result:
                    continue

                try:
                    outstanding_shares = float(result[0]['outstanding_shares'])
                    if outstanding_shares <= 0:
                        continue
                except (ValueError, KeyError):
                    continue

                df = short_interest_obj.df.copy()

                # Ensure required columns exist
                required = ['settlement_date', 'short_interest']
                if not all(col in df.columns for col in required):
                    continue

                # Coerce date format to match PostgreSQL DATE column
                df['settlement_date'] = pd.to_datetime(df['settlement_date'], errors='coerce').dt.date

                # Drop rows where date is still null
                df = df.dropna(subset=['settlement_date'])

                # Coerce numerics and calculate float shorted
                df['short_interest'] = pd.to_numeric(df['short_interest'], errors='coerce')
                df['average_volume'] = pd.to_numeric(df.get('average_volume'), errors='coerce')
                df['days_to_cover'] = pd.to_numeric(df.get('days_to_cover'), errors='coerce')

                # Add metadata
                df['ticker'] = ticker
                df['outstanding_shares'] = outstanding_shares
                df['pct_float_shorted'] = (df['short_interest'] / outstanding_shares) * 100

                # Final cleanup: drop incomplete rows
                df = df.dropna(subset=['short_interest', 'pct_float_shorted'])

                # Upsert to DB
                await db.batch_upsert_dataframe(
                    df,
                    table_name='short_interest',
                    unique_columns=['ticker', 'settlement_date']
                )

            print(f"[✓] Short interest updated. Sleeping for 12 hours...")
            await asyncio.sleep(43200)  # 12 hours

        except Exception as e:
            print(f"[!] Error in main loop: {e}")

asyncio.run(main())

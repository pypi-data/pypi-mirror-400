import asyncio
import sys
from pathlib import Path
from datetime import datetime

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers
from imports import *
from _yfinance.models.news import YFNews
from typing import Tuple, List, Any
import yfinance as yf


async def fetch_and_store_news():
    await db.connect()
    tickers_obj = yf.Tickers(most_active_tickers)
    news_data = tickers_obj.news()  # Dict keyed by ticker

    for symbol, articles in news_data.items():
        print(f"\n=== {symbol} === {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        id = [i.get('id') for i in articles]
        content = [i.get('content') for i in articles]

        news = YFNews(content, symbol)
        df = news.as_dataframe
        df['id'] = id

        await db.batch_upsert_dataframe(df, table_name='yf_news', unique_columns=['id'])
        print(f"[+] Upserted {len(df)} news articles for {symbol}")

async def main_loop():
    while True:
        try:
            await fetch_and_store_news()
        except Exception as e:
            print(f"[!] Error during news fetch: {e}")
        print("[*] Waiting 5 minutes before next news scan...\n")
        await asyncio.sleep(300)  # 5 minutes

if __name__ == "__main__":
    asyncio.run(main_loop())

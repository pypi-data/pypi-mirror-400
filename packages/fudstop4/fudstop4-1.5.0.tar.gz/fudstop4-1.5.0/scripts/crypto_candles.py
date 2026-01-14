import aiohttp
import asyncio
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv
load_dotenv()

import time
from datetime import datetime, timedelta

from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from fudstop4.apis.webull.webull_crypto import WebullCrypto
trading = WebullCrypto()

db = PolygonOptions()


import pandas as pd
from fudstop4.apis.helpers import generate_webull_headers

headers = generate_webull_headers(access_token=os.environ.get('ACCESS_TOKEN'))



CANDLE_COLUMNS = ["ts", "open", "close", "high", "low", "avg", "volume", "amount"]

async def normalize_webull_crypto_chart(payload, tz="America/New_York") -> pd.DataFrame:
    if not payload:
        return pd.DataFrame(columns=CANDLE_COLUMNS)

    obj = payload[0]
    rows = obj.get("data", [])
    if not rows:
        return pd.DataFrame(columns=CANDLE_COLUMNS)

    df = pd.DataFrame([r.split(",") for r in rows], columns=CANDLE_COLUMNS)

    # numeric conversion
    df["ts"] = pd.to_numeric(df["ts"], errors="coerce")
    for c in CANDLE_COLUMNS[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # overwrite ts with Eastern-time datetime (naive)
    df["ts"] = (
        pd.to_datetime(df["ts"], unit="s", utc=True)
        .dt.tz_convert(tz)
        .dt.tz_localize(None)
    )

    df = df.sort_values("ts").reset_index(drop=True)
    return df

# --- single request using a shared session (important for scale) ---
async def fetch_multi_candle_df(
    session: aiohttp.ClientSession,
    ticker: str,
    timespan: str,
    num_candles: int,
) -> Tuple[str, pd.DataFrame]:
    ticker_id = trading.coin_to_id_map.get(ticker)
    if not ticker_id:
        # Empty DF for unknown tickers, keeps pipeline consistent
        return ticker, pd.DataFrame(columns=["ts"] + CANDLE_COLUMNS)

    url = (
        "https://quotes-gw.webullfintech.com/api/crypto/charts/query"
        f"?type={timespan}&count={num_candles}&restorationType=0&tickerIds={ticker_id}"
    )

    async with session.get(url, headers=headers) as resp:
        payload = await resp.json()

    df = await normalize_webull_crypto_chart(payload)
    return ticker, df

def _extract_tickers_from_csv(csv_path: str) -> List[str]:
    df = pd.read_csv(csv_path)

    # common column names
    for col in ["ticker", "symbol", "coin", "base", "asset"]:
        if col in df.columns:
            s = df[col].astype(str)
            break
    else:
        # fallback: first column
        s = df.iloc[:, 0].astype(str)

    tickers = (
        s.str.strip()
         .str.upper()
         .replace({"": None})
         .dropna()
         .unique()
         .tolist()
    )
    return tickers

# --- batching runner ---
async def run_tickers_in_batches(
    csv_path: str,
    timespan: str = "m1",
    num_candles: int = 5,
    batch_size: int = 20,
    out_dir: Optional[str] = None,   # e.g. r"C:\temp\candles"
) -> Dict[str, pd.DataFrame]:
    tickers = _extract_tickers_from_csv(csv_path)

    results: Dict[str, pd.DataFrame] = {}

    timeout = aiohttp.ClientTimeout(total=20)
    connector = aiohttp.TCPConnector(limit=200, ssl=False)  # plenty of headroom

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i + batch_size]

            tasks = [
                fetch_multi_candle_df(session, t, timespan, num_candles)
                for t in batch
            ]

            batch_out = await asyncio.gather(*tasks, return_exceptions=True)

            for item in batch_out:
                if isinstance(item, Exception):
                    # skip hard failures, keep going
                    continue
                ticker, df = item
                results[ticker] = df
                df['ticker'] = ticker
                df['timespan'] = timespan
                await db.batch_upsert_dataframe(df, table_name='crypto_candles', unique_columns=['ticker', 'timespan', 'ts'])
                if out_dir:
                    Path(out_dir).mkdir(parents=True, exist_ok=True)
                    # Parquet is better, but CSV is universal. Pick your poison.
                    df.to_csv(Path(out_dir) / f"{ticker}_{timespan}_{num_candles}.csv", index=False)

    return results

TIMESPAN_LABELS = {
    "m1": "1min",
    "m5": "5min",
    "m15": "15min",
    "m30": "30min",
    "m60": "1hr",
    "m120": "2hr",
    "m240": "4hr",
    "d1": "day",
    "w1": "week",
}

async def run_crypto_once():
    csv_path = r"C:\Users\chuck\OneDrive\Desktop\FUDSTOP\fudstop\files\crypto_tickers.csv"
    timespans = ["m1", "m5", "m15", "m30", "m60", "m120", "m240", "d1", "w1"]

    tasks = [
        run_tickers_in_batches(
            csv_path=csv_path,
            timespan=ts,
            num_candles=50,
            batch_size=20,
            out_dir=None,
        )
        for ts in timespans
    ]

    await asyncio.gather(*tasks, return_exceptions=True)

    print(f"run complete @ {datetime.now().strftime('%H:%M:%S')}")


async def run_crypto_scheduler():
    await db.connect()

    while True:
        start = time.time()

        try:
            await run_crypto_once()

            print(f"Run done..")
        except Exception as e:
            # don’t let one bad run kill the daemon
            print(f"run failed: {e}")

        # sleep until next minute boundary
        elapsed = time.time() - start
        sleep_for = max(0, 60 - elapsed)

        await asyncio.sleep(sleep_for)


if __name__ == "__main__":
    asyncio.run(run_crypto_scheduler())
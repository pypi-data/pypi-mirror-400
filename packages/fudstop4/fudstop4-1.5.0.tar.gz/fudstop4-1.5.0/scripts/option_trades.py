import asyncio
import sys
from pathlib import Path
from datetime import datetime, time
import pytz
import aiohttp
import pandas as pd
from more_itertools import chunked  # pip install more-itertools
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
import aiohttp
import asyncio
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers
import os
from dotenv import load_dotenv
load_dotenv()
import pandas as pd
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from fudstop4.apis.helpers import generate_webull_headers
from fudstop4.apis.webull.webull_trading import WebullTrading
from fudstop4.apis.webull.webull_options.webull_options import WebullOptions
from aiohttp import ClientResponseError, ClientConnectorError
db = PolygonOptions()
opts = WebullOptions()
trading = WebullTrading()
from UTILS.confluence import score_volume_breakdown
# Tunables
# ===== Tunables =====
MAX_CONCURRENCY = 10         # per-ticker (for option_id fan-out)
REQUEST_TIMEOUT = 20
MAX_RETRIES = 3
RETRY_BACKOFF = 1.5
BATCH_SIZE = 5

BASE_URL = "https://quotes-gw.webullfintech.com/api/statistic/option/queryDeals"




async def fetch_option_deals(session: aiohttp.ClientSession, option_id: str, sem: asyncio.Semaphore):
    url = f"{BASE_URL}?count=800&tickerId={option_id}"
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with sem:
                async with session.get(url, timeout=REQUEST_TIMEOUT, headers=generate_webull_headers(access_token=os.environ.get('ACCESS_TOKEN'))) as resp:
                    resp.raise_for_status()
                    return option_id, (await resp.json()), None
        except (ClientResponseError, ClientConnectorError, asyncio.TimeoutError) as e:
            if attempt >= MAX_RETRIES:
                return option_id, None, e
            await asyncio.sleep(RETRY_BACKOFF ** (attempt - 1))
        except Exception as e:
            return option_id, None, e


def payload_to_df(option_id: str, payload: dict, fallback_ticker: str, meta: dict) -> pd.DataFrame:
    """
    Convert one payload (one option) into a per-trade DataFrame and
    append meta: ticker, strike, call_put, expiry (from atm_options).
    """
    datas = payload.get("datas", []) or []
    if not datas:
        return pd.DataFrame()

    trade_time = [d.get("tradeTime") for d in datas]
    deal = [d.get("deal") for d in datas]
    volume = [d.get("volume") for d in datas]
    trade_bs_flag = [d.get("tradeBsFlag") for d in datas]
    print(trade_bs_flag)
    trade_ticker_id = [d.get("tickerId") for d in datas]
    exchange = [d.get("trdEx") for d in datas]

    # Metadata from payload (scalar)
    ticker_id = payload.get("tickerId")
    belong_ticker_id = payload.get("belongTickerId")
    last_timestamp = payload.get("lastTimestamp")
    time_zone = payload.get("timeZone")

    # Metadata from atm_options row for this option_id
    m = meta.get(option_id, {})
    meta_ticker = m.get("ticker", fallback_ticker)
    strike = m.get("strike")
    call_put = m.get("call_put")
    expiry = m.get("expiry")

    n = len(datas)
    df = pd.DataFrame({
        "ticker": [meta_ticker] * n,
        "option_id": [option_id] * n,
        "strike": [strike] * n,
        "call_put": [call_put] * n,
        "expiry": [expiry] * n,
        "trade_time": trade_time,
        "deal": deal,
        "volume": volume,
        "flag": trade_bs_flag,
        "trade_ticker_id": trade_ticker_id,
        "exchange": exchange,
        "belong_ticker_id": [belong_ticker_id] * n,
        "last_timestamp": [last_timestamp] * n,
        "time_zone": [time_zone] * n,
    })

    return df


async def main(ticker: str) -> pd.DataFrame:
    """
    Returns a single DataFrame for this ticker:
    one row per trade across all its current (ATM) option IDs.

    Columns include:
      ticker, option_id, strike, call_put, expiry,
      trade_time, deal, volume, flag, trade_ticker_id,
      exchange, belong_ticker_id, last_timestamp, time_zone
    """
    query = f"""
        SELECT option_id, ticker, strike, call_put, expiry
        FROM atm_options
        WHERE ticker = '{ticker}' AND expiry >= '{db.today}'
        ORDER BY insertion_timestamp DESC
    """
    rows = await db.fetch(query)
    if not rows:
        pass

    # Build per-option metadata map
    option_meta = {
        r["option_id"]: {
            "ticker": r.get("ticker"),
            "strike": r.get("strike"),
            "call_put": r.get("call_put"),
            "expiry": r.get("expiry"),
        }
        for r in rows
    }
    ids = list(option_meta.keys())

    sem = asyncio.Semaphore(MAX_CONCURRENCY)
    async with aiohttp.ClientSession(headers=generate_webull_headers(access_token=os.environ.get('ACCESS_TOKEN'))) as session:
        fetched = await asyncio.gather(
            *[fetch_option_deals(session, option_id, sem) for option_id in ids],
            return_exceptions=False
        )

    dfs = []
    for option_id, payload, err in fetched:
        if err is not None or not payload:
            continue
        df = payload_to_df(option_id, payload, fallback_ticker=ticker, meta=option_meta)
        df["flag"] = (
        df["flag"]
        .astype("string")   # keeps NaN as <NA>
        .str.lower()
    )
        # Persist (optional): note that unique_columns=['option_id'] will overwrite;
        # for per-trade uniqueness consider a compound key (option_id, trade_time, deal, volume).
        await db.batch_upsert_dataframe(
            df,
            table_name="option_trades",
            unique_columns=["ticker", "strike", "call_put", "expiry"]
        )

        if not df.empty:
            dfs.append(df)

    if not dfs:
        return pd.DataFrame()

    out = pd.concat(dfs, ignore_index=True)

    # Normalize a couple types
    for c in ("deal", "volume"):
        out[c] = pd.to_numeric(out[c], errors="coerce")

    if out.empty:
        return out

    volume_totals = out.groupby('flag')['volume'].sum(min_count=1)
    total_volume = out['volume'].sum(skipna=True)
    buy_volume = volume_totals.get('buy', 0.0)
    sell_volume = volume_totals.get('sell', 0.0)
    neutral_volume = volume_totals.get('neutral', 0.0)
    if total_volume <= 0:
        buy_pct = sell_pct = neutral_pct = 0.0
    else:
        buy_pct = (buy_volume / total_volume) * 100.0
        sell_pct = (sell_volume / total_volume) * 100.0
        neutral_pct = max(0.0, 100.0 - buy_pct - sell_pct)

    flow_score = score_volume_breakdown(buy_pct, sell_pct, neutral_pct)
    for col, value in flow_score.to_columns("trade_flow").items():
        out[col] = value
    out["trade_flow_total_volume"] = total_volume
    out["trade_flow_buy_volume"] = buy_volume
    out["trade_flow_sell_volume"] = sell_volume
    out["trade_flow_neutral_volume"] = neutral_volume
    out["trade_flow_buy_pct"] = buy_pct
    out["trade_flow_sell_pct"] = sell_pct
    out["trade_flow_neutral_pct"] = neutral_pct
    print(f"Good")
    return out


async def run_main() -> dict[str, pd.DataFrame]:
    """
    Process most_active_tickers with a hard concurrency cap.
    Returns: {ticker: DataFrame}
    """
    await db.connect()

    sem = asyncio.Semaphore(MAX_CONCURRENCY)

    async def limited_main(ticker: str) -> pd.DataFrame:
        async with sem:
            return await main(ticker)

    while True:
        results: dict[str, pd.DataFrame] = {}

        for i in range(0, len(most_active_tickers), BATCH_SIZE):
            batch = most_active_tickers[i:i + BATCH_SIZE]

            batch_results = await asyncio.gather(
                *(limited_main(t) for t in batch),
                return_exceptions=True
            )

            for tkr, res in zip(batch, batch_results):
                if isinstance(res, Exception):
                    results[tkr] = pd.DataFrame()
                else:
                    results[tkr] = res

        # do something with results here (write to DB, emit signals, etc.)
        # then sleep or break
        # await asyncio.sleep(1)

# Example:
asyncio.run(run_main())
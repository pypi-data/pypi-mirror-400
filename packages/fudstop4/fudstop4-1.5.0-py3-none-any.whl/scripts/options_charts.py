from pathlib import Path
import sys
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
import aiohttp
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers
from fudstop4.apis.helpers import generate_webull_headers
import asyncio
import numpy as np
from script_helpers import compute_wilders_rsi, add_bollinger_bands,  add_sdc_indicator, add_td9_counts, macd_from_close

db = PolygonOptions()
def infer_ohlc_from_rows(rows: list[dict]) -> pd.DataFrame:
    records = []
    prev_close = None

    for r in rows:
        ts = r.get("ts")
        prices_raw = r.get("prices", [])

        # require valid ts and 4 valid price numbers
        if ts is None or pd.isna(ts):
            continue
        prices = [p for p in prices_raw if p is not None and not pd.isna(p)]
        if len(prices) != 4:
            continue

        # high/low are deterministic
        hi = max(prices)
        lo = min(prices)

        # open/close are the remaining two numbers
        mid = sorted(prices)[1:3]  # two middle values
        a, b = mid[0], mid[1]

        if prev_close is None or pd.isna(prev_close):
            open_, close_ = a, b
        else:
            # choose CLOSE as the one closest to previous close
            if abs(a - prev_close) <= abs(b - prev_close):
                close_, open_ = a, b
            else:
                close_, open_ = b, a

        prev_close = close_

        records.append(
            {"ts": int(ts), "o": float(open_), "h": float(hi), "l": float(lo), "c": float(close_)}
        )

    return pd.DataFrame.from_records(records)


def parse_kline_lines(lines: list[str], *, debug_bad: int = 0) -> pd.DataFrame:
    raw = []
    bad = []

    for line in lines:
        if line is None:
            continue
        s = str(line).strip()
        if not s:
            continue

        parts = [p.strip() for p in s.split(",")]

        # We expect at least: ts + 4 prices + volume + ... => but we only NEED first 5 fields
        if len(parts) < 5:
            if debug_bad:
                bad.append(("too_few_fields", s))
            continue

        ts = pd.to_numeric(parts[0], errors="coerce")
        p1 = pd.to_numeric(parts[1], errors="coerce")
        p2 = pd.to_numeric(parts[2], errors="coerce")
        p3 = pd.to_numeric(parts[3], errors="coerce")
        p4 = pd.to_numeric(parts[4], errors="coerce")

        if pd.isna(ts) or any(pd.isna(x) for x in (p1, p2, p3, p4)):
            if debug_bad:
                bad.append(("non_numeric", s))
            continue

        raw.append({"ts": ts, "prices": [p1, p2, p3, p4]})

    df = infer_ohlc_from_rows(raw)

    # If nothing parsed, return empty df (no KeyError)
    if df.empty:
        if debug_bad and bad:
            print("BAD LINES (sample):")
            for reason, sample in bad[:debug_bad]:
                print(reason, sample)
        return df

    df["dt_utc"] = pd.to_datetime(df["ts"], unit="s", utc=True, errors="coerce")
    df["dt_et"] = df["dt_utc"].dt.tz_convert("America/New_York")

    df = df.dropna(subset=["dt_et"]).sort_values("dt_et").set_index("dt_et")

    # remove tz suffix like -05:00 / +00:00
    df.index = df.index.tz_localize(None)

    return df.drop(columns=["dt_utc"])
async def scan_contract_charts(timespan, num_candles:str='800'):
    await db.connect()

    last_seen_id = None

    while True:
        query = """
        SELECT option_id, ticker, strike, call_put, expiry
        FROM atm_options
        ORDER BY insertion_timestamp DESC
        LIMIT 1
        """

        result = await db.fetch(query)
        if not result:
            await asyncio.sleep(1)
            continue

        latest_id = [i.get('option_id') for i in result][0]
        ticker = [i.get('ticker') for i in result][0]
        strike = [i.get('strike') for i in result][0]
        call_put  = [i.get('call_put') for i in result][0]
        expiry = [i.get('expiry') for i in result][0]
        if latest_id != last_seen_id:
            print(latest_id)
            last_seen_id = latest_id

        await asyncio.sleep(0.01)  # prevent CPU from screaming



        chart_data_url = (
            "https://quotes-gw.webullfintech.com/api/quote/option/chart/kdata"
            f"?derivativeId={latest_id}&type={timespan}&count={num_candles}"
        )

        async with aiohttp.ClientSession(
            headers=generate_webull_headers(access_token=os.environ.get("ACCESS_TOKEN"))
        ) as session:
            async with session.get(chart_data_url) as resp:
                resp.raise_for_status()
                payload = await resp.json()

        # Your current logic: data = [i.get('data') for i in data]; for i in data[0]: print(i)
        # So payload is a list, each item has "data": [ "csvline", "csvline", ... ]
        lines = []
        for item in payload:
            if item and item.get("data"):
                lines.extend(item["data"])

        df = parse_kline_lines(lines)
        df = df.iloc[::-1].reset_index(drop=True)

        # Technical indicators
        df = compute_wilders_rsi(df, window=14)
        df = add_bollinger_bands(df, window=20, num_std=2.0)
        df = add_td9_counts(df)
        df = add_sdc_indicator(df)
        if df is not None and not df.empty:
            df["ts"] = ( pd.to_datetime( pd.to_numeric(df["ts"], errors="coerce"), unit="s", utc=True, errors="coerce" ) .dt.tz_convert("America/New_York").dt.tz_localize(None))
            df['timespan'] = timespan
            df['option_id'] = latest_id
            df['ticker'] = ticker
            df['expiry'] = expiry
            df['call_put'] = call_put
            df['strike'] = strike


 


            await db.batch_upsert_dataframe(df, table_name='option_candles', unique_columns=['option_id', 'ts'])

asyncio.run(scan_contract_charts(num_candles='100', timespan='1m'))
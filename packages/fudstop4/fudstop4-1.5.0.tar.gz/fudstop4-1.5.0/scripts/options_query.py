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
import os
from dotenv import load_dotenv
load_dotenv()
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers
from fudstop4.apis.webull.webull_options.webull_options import WebullOptions
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from fudstop4.apis.webull.webull_trading import WebullTrading
from fudstop4.apis.helpers import generate_webull_headers
wbt = WebullTrading()
wb_opts = WebullOptions()
db = PolygonOptions()
from UTILS.db_tables import OptionsQuery

def clean_filters(**kwargs):
    """Return a dict of non-None arg names and their values."""
    return {k: v for k, v in kwargs.items() if v is not None}
id_to_ticker_map = {v: k for k, v in wb_opts.ticker_to_id_map.items()}

async def options_query(
    
    tickers_list,
    delta_gte=None, delta_lte=None,
    dte_gte=None, dte_lte=None,
    oi_gte=None, oi_lte=None,
    volume_gte=None, volume_lte=None,
    tickeriv_gte=None, tickeriv_lte=None,
    ivPercent_gte=None, ivPercent_lte=None,
    hvol_gte=None, hvol_lte=None,
    ask_gte=None, ask_lte=None,
    close_gte=None, close_lte=None,
    bid_gte=None, bid_lte=None,
    change_pct_gte=None, change_pct_lte=None,
    iv_gte=None, iv_lte=None,
    theta_gte=None, theta_lte=None,
    gamma_gte=None, gamma_lte=None,
    rho_gte=None, rho_lte=None,
    vega_gte=None, vega_lte=None,
    prob_itm_gte=None, prob_itm_lte=None,
    leverage_ratio_gte=None, leverage_ratio_lte=None,
    pulse_gte=None, pulse_lte=None,
    avg_30d_vol_gte=None, avg_30d_vol_lte=None,
    total_oi_gte=None, total_oi_lte=None,
    total_volume_gte=None, total_volume_lte=None,
    avg_30d_oi_gte=None, avg_30d_oi_lte=None,
    fetch_size=200
):
    # Step 1: Build the normalized query dict for the result dataframe
    arg_filters = clean_filters(
        delta_gte=delta_gte, delta_lte=delta_lte,
        dte_gte=dte_gte, dte_lte=dte_lte,
        oi_gte=oi_gte, oi_lte=oi_lte,
        volume_gte=volume_gte, volume_lte=volume_lte,
        tickeriv_gte=tickeriv_gte, tickeriv_lte=tickeriv_lte,
        ivPercent_gte=ivPercent_gte, ivPercent_lte=ivPercent_lte,
        hvol_gte=hvol_gte, hvol_lte=hvol_lte,
        ask_gte=ask_gte, ask_lte=ask_lte,
        close_gte=close_gte, close_lte=close_lte,
        bid_gte=bid_gte, bid_lte=bid_lte,
        change_pct_gte=change_pct_gte, change_pct_lte=change_pct_lte,
        iv_gte=iv_gte, iv_lte=iv_lte,
        theta_gte=theta_gte, theta_lte=theta_lte,
        gamma_gte=gamma_gte, gamma_lte=gamma_lte,
        rho_gte=rho_gte, rho_lte=rho_lte,
        vega_gte=vega_gte, vega_lte=vega_lte,
        prob_itm_gte=prob_itm_gte, prob_itm_lte=prob_itm_lte,
        leverage_ratio_gte=leverage_ratio_gte, leverage_ratio_lte=leverage_ratio_lte,
        pulse_gte=pulse_gte, pulse_lte=pulse_lte,
        avg_30d_vol_gte=avg_30d_vol_gte, avg_30d_vol_lte=avg_30d_vol_lte,
        total_oi_gte=total_oi_gte, total_oi_lte=total_oi_lte,
        total_volume_gte=total_volume_gte, total_volume_lte=total_volume_lte,
        avg_30d_oi_gte=avg_30d_oi_gte, avg_30d_oi_lte=avg_30d_oi_lte
    )

    url = "https://quotes-gw.webullfintech.com/api/wlas/option/screener/query"

    # Step 2: Dynamically get source IDs for most_active_tickers
    # If no wb_opts is provided, you need a fallback or raise error

    ticker_ids = [wbt.ticker_to_id_map.get(ticker) for ticker in tickers_list]
    print(ticker_ids)
    # Step 3: Build the mapping for the API
    mapping = {
        "delta": ("options.screener.rule.delta", delta_gte, delta_lte),
        "expireDate": ("options.screener.rule.expireDate", dte_gte, dte_lte),
        "openInterest": ("options.screener.rule.openInterest", oi_gte, oi_lte),
        "volume": ("options.screener.rule.volume", volume_gte, volume_lte),
        "tickerImplVol": ("options.screener.rule.tickerImplVol", tickeriv_gte, tickeriv_lte),
        "ivPercent": ("options.screener.rule.ivPercent", ivPercent_gte, ivPercent_lte),
        "hisVolatility": ("options.screener.rule.hisVolatility", hvol_gte, hvol_lte),
        "ask": ("options.screener.rule.ask", ask_gte, ask_lte),
        "close": ("options.screener.rule.close", close_gte, close_lte),
        "bid": ("options.screener.rule.bid", bid_gte, bid_lte),
        "changeRatio": ("options.screener.rule.changeRatio", change_pct_gte, change_pct_lte),
        "implVol": ("options.screener.rule.implVol", iv_gte, iv_lte),
        "theta": ("options.screener.rule.theta", theta_gte, theta_lte),
        "gamma": ("options.screener.rule.gamma", gamma_gte, gamma_lte),
        "rho": ("options.screener.rule.rho", rho_gte, rho_lte),
        "vega": ("options.screener.rule.vega", vega_gte, vega_lte),
        "probITM": ("options.screener.rule.probITM", prob_itm_gte, prob_itm_lte),
        "leverageRatio": ("options.screener.rule.leverageRatio", leverage_ratio_gte, leverage_ratio_lte),
        "pulseIndex": ("options.screener.rule.pulseIndex", pulse_gte, pulse_lte),
        "avg30Volume": ("options.screener.rule.avg30Volume", avg_30d_vol_gte, avg_30d_vol_lte),
        "totalOpenInterest": ("options.screener.rule.totalOpenInterest", total_oi_gte, total_oi_lte),
        "totalVolume": ("options.screener.rule.totalVolume", total_volume_gte, total_volume_lte),
        "avg30OpenInterest": ("options.screener.rule.avg30OpenInterest", avg_30d_oi_gte, avg_30d_oi_lte),
    }

    filter_dict = {}

    # Always inject the source filter
    filter_dict["options.screener.rule.source"] = ticker_ids

    # Add all dynamic filters as usual
    for key, (screener_key, gte, lte) in mapping.items():
        if gte is not None or lte is not None:
            clause = []
            if gte is not None:
                clause.append(f"gte={gte}")
            if lte is not None:
                clause.append(f"lte={lte}")
            filter_dict[screener_key] = "&".join(clause)

    payload = {"filter": filter_dict, "page": {"fetchSize": fetch_size}}

    async with aiohttp.ClientSession(headers=generate_webull_headers(access_token=os.environ.get('ACCESS_TOKEN'))) as session:
        async with session.post(url, json=payload) as resp:
            data = await resp.json()
            # Return data AND normalized filters
            return data, arg_filters


async def process_bid_ask_range(bid_gte, bid_lte, ask_gte, ask_lte):
    x, used_filters = await options_query(
        dte_gte=0, dte_lte=30,
        total_oi_gte=10000, total_oi_lte=100000,
        bid_gte=bid_gte, bid_lte=bid_lte,
        ask_gte=ask_gte, ask_lte=ask_lte,
        tickers_list=most_active_tickers
    )

    datas = x['datas']
    derivative = [i.get('derivative') for i in datas]
    data = OptionsQuery(derivative, used_filters)
    df = data.as_dataframe

    print(df)
    await db.batch_upsert_dataframe(df, table_name='options_query', unique_columns=['ticker', 'strike', 'call_put', 'query'])


async def run_all_queries():
    await db.connect()
    while True:
        # Define your bid/ask buckets
        bid_ask_ranges = [
            (0.10, 0.15, 0.10, 0.15),
            (0.16, 0.25, 0.16, 0.25),
            (0.06, 0.09, 0.06, 0.09),
            (0.26, 0.30, 0.26, 0.30),
            (0.31, 0.35, 0.31, 0.35),
            (0.36, 0.40, 0.36, 0.40),
            (0.41, 0.45, 0.41, 0.45),
            (0.46, 0.50, 0.46, 0.50)
            # Add more as needed
        ]

        # Create tasks
        tasks = [
            process_bid_ask_range(bid_gte, bid_lte, ask_gte, ask_lte)
            for bid_gte, bid_lte, ask_gte, ask_lte in bid_ask_ranges
        ]

        # Run them concurrently
        await asyncio.gather(*tasks)
        print(f"Done..sleeping 10 seconds.")
        await asyncio.sleep(10)

asyncio.run(run_all_queries())
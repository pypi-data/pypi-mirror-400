import asyncio
import sys
from pathlib import Path
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from imports import *
from UTILS.db_tables import CompanyBoard, CompanyExecutives
from fudstop4._markets.list_sets.ticker_lists import most_active_nonetf

async def executives(ticker: str, session: aiohttp.ClientSession) -> None:
    """
    Fetch board and executive information for a given ticker and upsert
    the results into the ``company_board`` and ``company_executives`` tables.

    Args:
        ticker: The stock ticker symbol.
        session: A pre-existing aiohttp ClientSession for making HTTP requests.
    """
    ticker_id = wbt.ticker_to_id_map.get(ticker)
    if not ticker_id:
        print(f"[ERROR] Unknown ticker id for {ticker}")
        return
    url = (
        "https://quotes-gw.webullfintech.com/api/information/company/"
        f"queryKeyExecutivesList?tickerId={ticker_id}"
    )
    try:
        async with session.get(url) as resp:
            data = await resp.json()
        board = data.get('board', [])
        execs = data.get('executives', [])
        # Convert raw data to dataframes using the helper classes
        board_model = CompanyBoard(board)
        exec_model = CompanyExecutives(execs)
        b_df = board_model.as_dataframe
        b_df['ticker'] = ticker
        e_df = exec_model.as_dataframe
        e_df['ticker'] = ticker
        await db.batch_upsert_dataframe(
            b_df,
            table_name='company_board',
            unique_columns=['ticker', 'company_id'],
        )
        await db.batch_upsert_dataframe(
            e_df,
            table_name='company_executives',
            unique_columns=['ticker', 'company_id'],
        )
    except Exception as e:
        print(f"[ERROR] {e} - {ticker}")

async def run_execs() -> None:
    """
    Fetch and store executive information for all non-ETF tickers.  A
    single database connection and HTTP session are reused for all requests.
    """
    await db.connect()
    try:
        async with aiohttp.ClientSession() as session:
            tasks = [executives(tkr, session) for tkr in most_active_nonetf]
            await asyncio.gather(*tasks)
    finally:
        await db.disconnect()
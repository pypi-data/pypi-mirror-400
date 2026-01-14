import sys
import asyncio
from pathlib import Path
import pandas as pd
from typing import Any, Dict, List

# Ensure project directory in sys.path
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from imports import generate_webull_headers  # type: ignore
import aiohttp
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
db = PolygonOptions()
SLEEP_SECONDS = 60  # Sleep between cycles to avoid hammering the API

async def volume_analysis(
    session: aiohttp.ClientSession, option_id: str, headers: Dict[str, str]
) -> Dict[str, Any]:
    """
    Fetch volume analysis for a single option ID using a shared HTTP session.
    """
    url = (
        "https://quotes-gw.webullfintech.com/api/statistic/option/queryVolumeAnalysis"
        f"?count=800&tickerId={option_id}"
    )
    async with session.get(url, headers=headers) as resp:
        data = await resp.json()
        return data


async def atm_vol_anal() -> None:
    """
    Continuously perform volume analysis for the most recent ATM options.
    Uses a shared aiohttp session and sleeps between cycles to respect API limits.
    """
    await db.connect()
    try:
        headers = generate_webull_headers()
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    query = (
                        "SELECT * FROM atm_options "
                        f"WHERE expiry >= '{db.today}' "
                        "ORDER BY insertion_timestamp DESC "
                        "LIMIT 10"
                    )
                    results = await db.fetch(query)
                    if not results:
                        print("No ATM options found.")
                        await asyncio.sleep(SLEEP_SECONDS)
                        continue
                    option_ids: List[str] = [i["option_id"] for i in results]
                    tickers: List[str] = [i["ticker"] for i in results]
                    strikes: List[float] = [i["strike"] for i in results]
                    call_puts: List[str] = [i["call_put"] for i in results]
                    expiries: List[str] = [i["expiry"] for i in results]

                    # Fetch volume analysis concurrently using shared session
                    tasks = [
                        volume_analysis(session, option_id, headers)
                        for option_id in option_ids
                    ]
                    vol_results = await asyncio.gather(*tasks)
                    # Assemble rows for upsert
                    rows: List[Dict[str, Any]] = []
                    for idx, option_id in enumerate(option_ids):
                        vol_data = vol_results[idx]
                        rows.append(
                            {
                                "option_id": option_id,
                                "ticker": tickers[idx],
                                "strike": strikes[idx],
                                "call_put": call_puts[idx],
                                "expiry": expiries[idx],
                                "total_trades": vol_data.get("totalNum"),
                                "total_vol": vol_data.get("totalVolume"),
                                "avg_price": vol_data.get("avgPrice"),
                                "buy_vol": vol_data.get("buyVolume"),
                                "sell_vol": vol_data.get("sellVolume"),
                                "neut_vol": vol_data.get("neutralVolume"),
                                "ticker_id": vol_data.get("tickerId"),
                            }
                        )
                    df = pd.DataFrame(rows)
                    await db.batch_upsert_dataframe(
                        df,
                        table_name="atm_vol_anal",
                        unique_columns=["ticker", "strike", "call_put", "expiry"],
                    )
                    # Sleep after successful update
                    await asyncio.sleep(SLEEP_SECONDS)
                except Exception as inner:
                    print(f"[!] Error in atm_vol_anal: {inner}")
                    await asyncio.sleep(SLEEP_SECONDS)
    finally:
        await db.disconnect()


if __name__ == "__main__":
    asyncio.run(atm_vol_anal())
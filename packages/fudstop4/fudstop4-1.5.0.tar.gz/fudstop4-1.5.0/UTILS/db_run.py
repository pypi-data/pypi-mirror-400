from imports import *
from _yfinance.models.price_target import yfPriceTarget
from _webull.models.etf_holdings import ETFHoldings
from more_itertools import chunked  # or use manual chunking if you prefer
from typing import Tuple, List, Any
from trade.paper import place_trade, get_positions
from datetime import datetime, time as dtime
from datetime import datetime
from fudstop4._markets.list_sets.ticker_lists import most_active_nonetf
import yfinance as yf
from fudstop4._markets.list_sets.dicts import hex_color_dict
from UTILS.db_tables import InfoTable, MostActive, AnalystsTable, VolAnalTable, BuySurgeTable, VolumeSurgeTable, YfEarningsEstimateTable,YfInsiderRosterHoldingsTable,YfNewsTable,YfPtTable, ShortInterestTable,WbOptsTable,CostDistributionTable,RiseFallTables, PlaysTable, HighDividendsTable, MultiQuoteTable, OvernightTable, YfInsidersTable


data_map = { 
    'active_rvol10d': MostActive,
    'active_range': MostActive,
    'active_turnoverratio': MostActive,
    'active_volume': MostActive,
    'wb_opts': WbOptsTable,
    'plays': PlaysTable,
    'buy_surge': BuySurgeTable,
    'fall_1d': RiseFallTables,
    'rise_5min': RiseFallTables,
    'rise_5d': RiseFallTables,
    'rise_52w': RiseFallTables,\
    'rise_3m': RiseFallTables,
    'rise_1m': RiseFallTables,
    'rise_premarket': RiseFallTables,
    'rise_aftermarket': RiseFallTables,
    'fall_1d': RiseFallTables,
    'fall_5min': RiseFallTables,
    'fall_premarket': RiseFallTables,
    'fall_aftermarket': RiseFallTables,
    'fall_52w': RiseFallTables,
    'fall_5d': RiseFallTables,
    'fall_3m': RiseFallTables,
    'fall_1m': RiseFallTables,
    'feed_costdist': CostDistributionTable,
    'high_dividends': HighDividendsTable,
    'short_interest': ShortInterestTable,
    'vol_anal': VolAnalTable,
    'volume_surge': VolumeSurgeTable,
    'buy_surge': BuySurgeTable,
    'yf_news': YfNewsTable,
    'yf_pt': YfPtTable,
    'yf_earnings_estimate': YfEarningsEstimateTable,
    'yf_insider_roster_holdings': YfInsiderRosterHoldingsTable,
    'info': InfoTable,
    'multi_quote': MultiQuoteTable,
    'analysts': AnalystsTable,
    'overnight': OvernightTable,
    'yf_insiders': YfInsidersTable,

    


}

processed = set()

import asyncio
from datetime import datetime
from imports import *

# Define all active script-related tables
scripts = [
    'wb_opts', 'analysts', 'feed_costdist', 'high_dividends', 'info',
    'ipos_filing', 'ipos_upcoming', 'multi_quote', 'buy_contracts', 'sell_contracts', 'overnight', 'plays',
    'fall_1d', 'fall_5d', 'fall_5min', 'fall_premarket', 'fall_aftermarket', 'fall_52w', 'fall_3m', 'fall_1m', 'rise_1d', 'rise_5d', 'rise_5min', 'rise_premarket', 'rise_aftermarket', 'rise_52w', 'rise_3m', 'rise_1m', 'top_followed', 'yf_earnings_estimate', 'yf_insiders',
    'yf_mfholders', 'yf_news', 'yf_pt', 'technical_events', 'balance_sheet',
    'cash_flow', 'income_statement', 'stock_monitor', 'ticker_bonds',
    'iv_skew', 'historic_ivx', 'etf_holdings', 'factors',
]

async def fetch_latest_rows():
    await db.connect()

    results = []
    for table in scripts:
        try:
            query = f"""
                SELECT *
                FROM {table}
                ORDER BY insertion_timestamp DESC NULLS LAST
                LIMIT 1
            """
            row = await db.fetch(query)
            if row:
                ts = row[0].get('insertion_timestamp') or 'N/A'
                results.append(f"{table:<25} | ⏱️ {ts}")
            else:
                results.append(f"{table:<25} | ⚠️ No data")
        except Exception as e:
            results.append(f"{table:<25} | ❌ Error: {str(e).splitlines()[0]}")

    print("\n📊 Latest Insertion Timestamps\n" + "-"*50)
    for line in sorted(results):
        print(line)

if __name__ == "__main__":
    asyncio.run(fetch_latest_rows())

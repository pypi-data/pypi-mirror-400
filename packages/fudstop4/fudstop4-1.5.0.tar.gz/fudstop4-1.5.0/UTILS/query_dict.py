import asyncio
import sys
from pathlib import Path
from datetime import datetime

project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)


query_dict = { 


    """td9_rsi_volatility""": """SELECT p.ticker, p.timespan FROM plays p JOIN info i ON p.ticker = i.ticker JOIN multi_quote m ON p.ticker = m.ticker WHERE p.rsi <= 26 AND p.td_buy_count >= 8 AND p.c < p.vwap AND i.sentiment ILIKE '%bull%' AND i.volatile_rank ILIKE '%volatile%' AND m.forward_pe < m.pe AND m.next_earning_day != 'today' ;""",

    """oversold_rsi""": """SELECT ticker, timespan, rsi from plays where rsi <= 30 order by rsi asc limit 50""",

    """overbought_rsi""": """SELECT ticker, timespan, rsi from plays where rsi >= 70 order by rsi desc limit 50""",

    """bullish_td9""": """SELECT ticker, timespan, td_buy_count from plays where td_buy_count >= 9 limit 50""",

    """bearish_td9""": """SELECT ticker, timespan, td_sell_count from plays where td_sell_count >= 9 limit 50""",

    "extreme_oversold_rsi": """SELECT ticker, timespan, rsi from plays where rsi <= 24 order by rsi asc limit 25""",

    "extreme_overbought_rsi": """SELECT ticker, timespan, rsi from plays where rsi >= 76 order by rsi desc limit 25""",

    "bullish_td9_rsi": """SELECT ticker, timespan, rsi, td_buy_count from plays where rsi <= 28 and td_buy_count >= 8 order by rsi asc limit 25""",

    "bearish_td9_rsi": """SELECT ticker, timespan, rsi, td_sell_count from plays where rsi >= 72 and td_sell_count >= 8 order by rsi desc limit 25""",

    "bullish_pe": """SELECT ticker, forward_pe, pe from multi_quote where pe > forward_pe""",

    "bearish_pe": """SELECT ticker, forward_pe, pe from multi_quote where pe < forward_pe""",

    "signal": """SELECT ticker, signal, score, time_horizon FROM technical_events WHERE  insertion_timestamp >= NOW() - INTERVAL '2 minutes';""",

    "unusual_options": """SELECT ticker, strike, call_put, expiry, volume FROM wb_opts WHERE volume > 5000 AND volume > (oi * 50) AND expiry::date >= CURRENT_DATE; """,

    "highest_volume": """SELECT sub.ticker, sub.strike, sub.call_put, sub.expiry, sub.volume, m.close, CASE WHEN sub.strike > m.close THEN 'Above' WHEN sub.strike < m.close THEN 'Below' ELSE 'At' END AS strike_vs_price FROM ( SELECT *, ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY volume DESC) AS rn FROM wb_opts ) sub JOIN multi_quote m ON sub.ticker = m.ticker WHERE sub.rn = 1""",

    "highest_oi_strike": """WITH nearest_expiry AS ( SELECT ticker, MIN(expiry::date) AS min_expiry FROM wb_opts GROUP BY ticker ), filtered_opts AS ( SELECT w.* FROM wb_opts w JOIN nearest_expiry n ON w.ticker = n.ticker AND w.expiry::date = n.min_expiry ) SELECT sub.ticker, sub.strike, sub.call_put, m.close, sub.strike AS oi_strike, CASE WHEN sub.strike > m.close THEN 'A' WHEN sub.strike < m.close THEN 'B' ELSE 'At' END AS diff FROM ( SELECT *, ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY oi DESC) AS rn FROM filtered_opts ) sub JOIN multi_quote m ON sub.ticker = m.ticker WHERE sub.rn = 1""",
    "theta_exposure": "WITH nearest_expiry AS ( SELECT ticker, MIN(expiry::date) AS min_expiry FROM wb_opts WHERE expiry::date > CURRENT_DATE GROUP BY ticker ) SELECT w.ticker, w.expiry, SUM(w.theta) AS total_theta_exposure FROM wb_opts w JOIN nearest_expiry n ON w.ticker = n.ticker AND w.expiry::date = n.min_expiry GROUP BY w.ticker, w.expiry ORDER BY w.ticker;",

    
    "highest_td_buys":"""SELECT ticker, timespan, td_buy_count from plays order by td_buy_count desc limit 25""",
    "highest_td_sells": """SELECT ticker, timespan, td_sell_count from plays order by td_sell_count desc limit 25""",
    "earnings_not_today": """SELECT ticker FROM multi_quote WHERE TO_DATE(next_earning_day, 'YYYY-MM-DD') != CURRENT_DATE;""",
    "earnings_today": """SELECT ticker FROM multi_quote WHERE TO_DATE(next_earning_day, 'YYYY-MM-DD') = CURRENT_DATE;""",
    "bullish_sentiment": """SELECT ticker, sentiment from info where sentiment ILIKE '%bull%' limit 20""",
    "bearish_sentiment": """SELECT ticker, sentiment from info where sentiment ILIKE '%bear%' limit 20""",
    "volatile": "SELECT ticker, volatile_rank from info where volatile_rank ilike '%volatile%' limit 20",
    "highest_shorted": "SELECT ticker, pct_float_shorted from short_interest order by pct_float_shorted desc limit 20",
    """high_ownership""":"""SELECT ticker, ROUND((holding_ratio * 100)::numeric, 2) || '%' AS holding_ratio_pct FROM institutions ORDER BY holding_ratio DESC;""",
    """top_gainers""": """( SELECT 'rise_1d' AS category, ticker, change_pct FROM rise_1d WHERE change_pct > 0 ORDER BY change_pct DESC LIMIT 1 ) UNION ALL ( SELECT 'rise_1m' AS category, ticker, change_pct FROM rise_1m WHERE change_pct > 0 ORDER BY change_pct DESC LIMIT 1 ) UNION ALL ( SELECT 'rise_3m' AS category, ticker, change_pct FROM rise_3m WHERE change_pct > 0 ORDER BY change_pct DESC LIMIT 1 ) UNION ALL ( SELECT 'rise_52w' AS category, ticker, change_pct FROM rise_52w WHERE change_pct > 0 ORDER BY change_pct DESC LIMIT 1 ) UNION ALL ( SELECT 'rise_5d' AS category, ticker, change_pct FROM rise_5d WHERE change_pct > 0 ORDER BY change_pct DESC LIMIT 1 ) UNION ALL ( SELECT 'rise_5min' AS category, ticker, change_pct FROM rise_5min WHERE change_pct > 0 ORDER BY change_pct DESC LIMIT 1 ) UNION ALL ( SELECT 'rise_aftermarket' AS category, ticker, change_pct FROM rise_aftermarket WHERE change_pct > 0 ORDER BY change_pct DESC LIMIT 1 ) UNION ALL ( SELECT 'rise_premarket' AS category, ticker, change_pct FROM rise_premarket WHERE change_pct > 0 ORDER BY change_pct DESC LIMIT 1 ); """, 
    "top_losers": """( SELECT 'fall_1d' AS category, ticker, change_pct FROM fall_1d WHERE change_pct < 0 ORDER BY change_pct ASC LIMIT 1 ) UNION ALL ( SELECT 'fall_1m' AS category, ticker, change_pct FROM fall_1m WHERE change_pct < 0 ORDER BY change_pct ASC LIMIT 1 ) UNION ALL ( SELECT 'fall_3m' AS category, ticker, change_pct FROM fall_3m WHERE change_pct < 0 ORDER BY change_pct ASC LIMIT 1 ) UNION ALL ( SELECT 'fall_52w' AS category, ticker, change_pct FROM fall_52w WHERE change_pct < 0 ORDER BY change_pct ASC LIMIT 1 ) UNION ALL ( SELECT 'fall_5d' AS category, ticker, change_pct FROM fall_5d WHERE change_pct < 0 ORDER BY change_pct ASC LIMIT 1 ) UNION ALL ( SELECT 'fall_5min' AS category, ticker, change_pct FROM fall_5min WHERE change_pct < 0 ORDER BY change_pct ASC LIMIT 1 ) UNION ALL ( SELECT 'fall_aftermarket' AS category, ticker, change_pct FROM fall_aftermarket WHERE change_pct < 0 ORDER BY change_pct ASC LIMIT 1 ) UNION ALL ( SELECT 'fall_premarket' AS category, ticker, change_pct FROM fall_premarket WHERE change_pct < 0 ORDER BY change_pct ASC LIMIT 1 ); """,
    """top_oi_strikes""": """SELECT DISTINCT ON (ticker, expiry) ticker, strike, call_put, expiry, oi FROM wb_opts WHERE oi IS NOT NULL ORDER BY ticker, expiry, oi DESC; """, 
    """oi_deviation""": """SELECT ticker, oi, avg_oi, pct_deviation FROM oi_outliers ORDER BY pct_deviation DESC LIMIT 10; """,
    """ssr""": """SELECT ticker from multi_quote where change_ratio <= -0.10""",
    "volume_analysis_buys":"SELECT ticker, buy_pct FROM volume_analysis ORDER BY buy_pct DESC LIMIT 10;",
    "volume_analysis_sells":"SELECT ticker, sell_pct FROM volume_analysis ORDER BY sell_pct DESC LIMIT 10;",
    """call_scalps""": """SELECT ticker, timespan, rsi from plays where candle_completely_below_lower = 't'""",
    """put_scalps""": """SELECT ticker, timespan, rsi from plays where candle_completely_above_upper = 't'""",
    "earnings_score": """/*--------------------------------------------------------------------
   FINANCIAL‑SCORE  +  RECENCY‑WEIGHTED RSI   (returns 3 columns)
--------------------------------------------------------------------*/
WITH q AS (           -- last 8 quarterly earnings
    SELECT
        ticker,
        end_date::date,
        net_income,
        ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY end_date::date DESC) AS rn
    FROM income_statement
    WHERE fiscal_period IN (1,2,3,4)
),
w AS (
    SELECT
        ticker,
        net_income,
        POWER(0.5, rn - 1) AS wt
    FROM q
    WHERE rn <= 8
),
ni AS (               -- weighted net‑income
    SELECT
        ticker,
        SUM(net_income * wt) / NULLIF(SUM(wt),0) AS weighted_net_income
    FROM w
    GROUP BY ticker
),
bs AS (               -- latest balance‑sheet snapshot
    SELECT DISTINCT ON (ticker)
        ticker,
        total_assets
    FROM balance_sheet
    ORDER BY ticker, end_date::date DESC
),
fin AS (              -- size‑adjusted profitability score
    SELECT
        ticker,
        (weighted_net_income / NULLIF(total_assets,0)) AS financial_score
    FROM ni
    JOIN bs USING (ticker)
),
rsi_raw AS (          -- grab daily, weekly, monthly RSI
    SELECT
        ticker,
        MAX(CASE WHEN timespan = 'd1' THEN rsi END) AS rsi_d1,
        MAX(CASE WHEN timespan = 'w'  THEN rsi END) AS rsi_w,
        MAX(CASE WHEN timespan = 'm'  THEN rsi END) AS rsi_m
    FROM plays
    WHERE timespan IN ('d1','w','m')
    GROUP BY ticker
),
rsi AS (              -- recency‑weighted RSI (d1 50 %, w 30 %, m 20 %)
    SELECT
        ticker,
        ( 0.5*COALESCE(rsi_d1,0)
        + 0.3*COALESCE(rsi_w ,0)
        + 0.2*COALESCE(rsi_m ,0) ) / 1.0            AS weighted_rsi
    FROM rsi_raw
)

/*--------------------------------------------------------------------
   FINAL OUTPUT  – 3 columns
--------------------------------------------------------------------*/
SELECT
    f.ticker,
    ROUND(f.financial_score::numeric, 6) AS financial_score,
    ROUND(r.weighted_rsi::numeric, 2)    AS weighted_rsi
FROM fin f
JOIN rsi r USING (ticker)
ORDER BY financial_score DESC
LIMIT 100;

""",
"call_walls": """SELECT g.ticker,
       (g.max_pos_gamma_strike - g.spot_price) AS gamma_strike_delta
FROM gex g
JOIN plays p ON g.ticker = p.ticker
WHERE g.max_pos_gamma_strike IS NOT NULL
  AND g.spot_price IS NOT NULL
  AND p.rsi_14 <= 30
  AND p.td_buy_count >= 9
ORDER BY gamma_strike_delta DESC
LIMIT 1;""",
"put_walls": """SELECT g.ticker,
       (g.spot_price - g.max_neg_gamma_strike) AS put_strike_delta
FROM gex g
JOIN plays p ON g.ticker = p.ticker
WHERE g.max_neg_gamma_strike IS NOT NULL
  AND g.spot_price IS NOT NULL
  AND p.rsi_14 >= 70
  AND p.td_sell_count >= 9
ORDER BY put_strike_delta DESC
LIMIT 1;""",

"short_interest_momentum": """WITH ranked AS (
    SELECT
        settlement_date,
        ticker,
        short_interest,
        pct_float_shorted,
        ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY settlement_date DESC) AS rn
    FROM short_interest
)
SELECT settlement_date,
       ticker,
       short_interest,
       pct_float_shorted
FROM   ranked
WHERE  rn <= 3
ORDER  BY settlement_date DESC, ticker;
""",
"upcoming_7day_earnings": """SELECT
    ticker,
    name,
    price,
    volume,
    change_ratio,
    CAST(start_time AS timestamp)::date AS report_date,
    eps_estimate,
    revenue_estimate
FROM   earnings_soon
WHERE  CAST(start_time AS timestamp)::date 
       BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
ORDER  BY report_date, price DESC;
""",
"iv_expansion": """SELECT
    ticker,
    price,
    iv_rank AS ivr30,
    volatile_rank
FROM   info
WHERE  ivr30 >= 80
  AND  volatile_rank = 'Extremely volatile'
  AND  price      IS NOT NULL   -- avoid null / nanB
ORDER  BY ivr30 DESC;
""",
"oi_spike": """SELECT
    ticker,
    oi,
    avg_oi,
    pct_deviation,
    insertion_timestamp
FROM   oi_outliers
WHERE  pct_deviation >= 40            -- ≥ +40 % vs. average 
ORDER  BY pct_deviation DESC;""",
"consensus_buys": """
SELECT
    ticker,
    strong_buy,
    buy,
    hold,
    underperform,
    sell,

FROM   analysts
WHERE  strong_buy > 0
  AND  strong_buy >= (buy + hold + underperform + sell)  -- majority strong‑buy
ORDER  BY strong_buy DESC;""",
"""pt_upside""": """SELECT
    y.ticker,
    i.price,
    y.average AS pt_avg,
    ROUND(((y.average - i.price) / i.price * 100)::numeric, 2) AS upside_pct
FROM   yf_pt  y
JOIN   info   i USING (ticker)
WHERE  i.price IS NOT NULL
  AND  y.average > i.price * 1.20
ORDER  BY upside_pct DESC;
""",
"extreme_put_skews":"""SELECT
    ticker,
    expiry::date AS expiry,
    strike,
    iv,
    skew_diff
FROM   iv_skew
WHERE  skew_type = 'put_skew'
  AND  skew_diff >= 1.00
ORDER  BY skew_diff DESC;
""",
"large_buy_orders": """SELECT
    ticker,
    alert,
    volume,
 
FROM   volume_alerts
WHERE  alert_type = 'Large Order (Buy)'
ORDER  BY insertion_timestamp DESC;""",
"short_ratio_monitor": """SELECT
    date,
    ticker,
    short_volume,
    total_volume,
    ROUND((short_volume::numeric / total_volume * 100)::numeric, 2) AS short_ratio_pct
FROM   finra_shorts
WHERE  date >= CAST(TO_CHAR(CURRENT_DATE - INTERVAL '10 days', 'YYYYMMDD') AS integer)
ORDER  BY short_ratio_pct DESC;
""",
"deepvalue_dividends": """SELECT
    ticker,
    close, 
    yield,
    forward_pe
FROM   multi_quote
WHERE  yield IS NOT NULL
  AND  forward_pe IS NOT NULL
  AND  yield     >= 0.04
  AND  forward_pe <= 12
ORDER  BY yield DESC;""",
"bond_yield_divergence": """SELECT
    m.ticker,
    m.close, 
    tb.bond_yield,
    (tb.bond_yield - (m.dividend * 4) / NULLIF(m.close, 0)) AS spread_vs_dividend_yld 
FROM   multi_quote   m
JOIN   ticker_bonds  tb USING (ticker)
WHERE  tb.bond_yield IS NOT NULL
  AND  m.dividend    IS NOT NULL
ORDER  BY spread_vs_dividend_yld DESC;""",
"long_yield_strips": """SELECT
    symbol,
    term,
    bond_yield,
    yield_ytw,
    close
FROM treasury_strips
WHERE REGEXP_REPLACE(term, '[^0-9.]', '', 'g')::numeric >= 10
ORDER BY bond_yield DESC;
""",
"daily_td9s": """SELECT
    ticker,
    ts::date AS ts,
    td_buy_count,
    td_sell_count,
    ROUND(rsi, 2) AS rsi
FROM plays
WHERE timespan = 'day'
  AND td_sell_count >= 9
ORDER BY ts DESC;
""",
"""breakout_candles""": """SELECT
    c.ticker,
    c.ts,
    c.c          AS close_price,
    i.high_price_52wk
FROM   candles c
JOIN   info    i USING (ticker)
WHERE  c.timespan = 'd1'
  AND  c.c > i.high_price_52wk
ORDER  BY c.ts DESC;""",
"ivhv_gap": """SELECT
    h.ticker,
    h.date,
    h.ivx30,
    h.hv20,
    (h.ivx30 - h.hv20) AS iv_hv_spread
FROM   historic_ivx h
WHERE  (h.ivx30 - h.hv20) >= 1.0
ORDER  BY iv_hv_spread DESC;""",
"""callable_bonds""":"""SELECT
    bond_ticker,
    ticker,
    coupon,
    next_call_date,
    next_call_price,
    bid_yield
FROM   ticker_bonds
WHERE  is_callable = '1'
  AND  next_call_date IS NOT NULL
  AND  CAST(next_call_date AS DATE) BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '6 months'
ORDER  BY next_call_date, bid_yield DESC;
""",
"liquidity_risks": """SELECT
    ticker,
    call_ivbid,
    call_ivask,
    (call_ivask - call_ivbid) AS iv_spread
FROM   options_monitor
WHERE  (call_ivask - call_ivbid) >= 0.25       -- ≥25 vol‑points wide
ORDER  BY iv_spread DESC;
"""



}


# Re-create the columns_mapping after code execution state reset
columns_mapping = {
    "td9_rsi_volatility": ['ticker', 'timespan'],
    "oversold_rsi": ['ticker', 'timespan', 'rsi'],
    "overbought_rsi": ['ticker', 'timespan', 'rsi'],
    "bullish_td9": ['ticker', 'timespan', 'td_buy_count'],
    "bearish_td9": ['ticker', 'timespan', 'td_sell_count'],
    "extreme_oversold_rsi": ['ticker', 'timespan', 'rsi'],
    "extreme_overbought_rsi": ['ticker', 'timespan', 'rsi'],
    "bullish_td9_rsi": ['ticker', 'timespan', 'rsi', 'td_buy_count'],
    "bearish_td9_rsi": ['ticker', 'timespan', 'rsi', 'td_sell_count'],
    "bullish_pe": ['ticker', 'forward_pe', 'pe'],
    "bearish_pe": ['ticker', 'forward_pe', 'pe'],
    "signal": ["ticker", "signal", "score", "time_horizon"],
    "unusual_options": ["ticker", "strike", "call_put", "expiry", "oi"],
    "highest_volume": ["ticker", "strike", "call_put", "expiry", "volume", "close", "strike_vs_price"],
    "highest_oi_strike": ["ticker", "strike", "call_put", "close", "oi_strike", "diff"],
    "theta_exposure": ['ticker', 'expiry', 'thex'],
    "highest_td_buys": ['ticker', 'timespan', 'td_buy_count'],
    "highest_td_sells": ['ticker', 'timespan', 'td_sell_count'],
    "earnings_not_today": ['ticker'],
    "earnings_today": ['ticker'],
    "bullish_sentiment": ['ticker', 'sentiment'],
    "bearish_sentiment": ['ticker', 'sentiment'],
    "volatile": ['ticker', 'volatile_rank'],
    "highest_shorted": ['ticker', 'pct_float_shorted'],
    "high_ownership": ['ticker', 'holding_ratio_pct'],
    "top_gainers": ['category', 'ticker', 'change_pct'],
    "top_losers": ['category', 'ticker', 'change_pct'],
    "top_oi_strikes": ['ticker', 'strike', 'call_put', 'expiry', 'oi'],
    "oi_deviation": ['ticker', 'oi', 'avg_oi', 'pct_deviation'],
    "ssr": ['ticker'],
    "volume_analysis_buys": ['ticker', 'buy_pct'],
    "volume_analysis_sells": ['ticker', 'sell_pct'],
    "call_scalps": ['ticker', 'timespan', 'rsi'],
    "put_scalps": ['ticker', 'timespan', 'rsi'],
    "earnings_score": ['ticker', 'financial_score', 'weighted_rsi']

}


# Define all the keys in query_dict
query_dict_keys = [
    "td9_rsi_volatility", "oversold_rsi", "overbought_rsi", "bullish_td9", "bearish_td9",
    "extreme_oversold_rsi", "extreme_overbought_rsi", "bullish_td9_rsi", "bearish_td9_rsi",
    "bullish_pe", "bearish_pe", "signal", "unusual_options", "highest_volume",
    "highest_oi_strike", "theta_exposure", "highest_td_buys", "highest_td_sells",
    "earnings_not_today", "earnings_today", "bullish_sentiment", "bearish_sentiment",
    "volatile", "highest_shorted", "high_ownership", "top_gainers", "top_losers",
    "top_oi_strikes", "oi_deviation", "ssr", "volume_analysis_buys", "volume_analysis_sells",
    "call_scalps", "put_scalps", "top_call_skews", "top_put_skews", "top_earnings_yield",
    "gap_support_nearby", "gap_resistance_nearby"
]







from imports import *
from fudstop4.apis.polygonio.polygon_options import PolygonOptions

db = PolygonOptions()

import asyncio
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Append the project root directory to sys.path
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

# Import database connection class
from imports import *
from fudstop4.apis.polygonio.polygon_options import PolygonOptions

# Instantiate the DB class
db = PolygonOptions()





async def master_query():
    await db.connect()
    for name, query in query_dict.items():
        try:
            results = await db.fetch(query)
            if not results:
                continue

            # Use predefined columns or fallback to result keys
            columns = columns_mapping.get(name, list(results[0].keys()) if results else [])
            df = pd.DataFrame(results, columns=columns)
            df['name'] = name  # Optional: add source label
            
            # Determine unique keys (fallback to 'ticker' if unknown)
            unique_keys = ['ticker'] if 'ticker' in df.columns else columns[:1]

            await db.batch_upsert_dataframe(df, table_name=name, unique_columns=unique_keys)
        
        except Exception as e:
            # Log error and optionally drop the table to recover
            print(f"Error processing {name}: {e}")
            try:
                await db.fetch(f"""DROP TABLE IF EXISTS {name}""")
            except Exception as drop_err:
                print(f"Failed to drop table {name}: {drop_err}")

# # Run the query execution
# asyncio.run(master_query())
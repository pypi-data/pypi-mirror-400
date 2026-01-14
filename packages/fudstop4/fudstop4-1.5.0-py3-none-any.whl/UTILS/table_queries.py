table_feeds = {
    'multi_quote': {
        "top_gainers_1d": """
            SELECT ticker, name, close, change_ratio
            FROM multi_quote
            WHERE change_ratio > 0
            ORDER BY change_ratio DESC
            LIMIT 25;
        """,
        "top_losers_1d": """
            SELECT ticker, name, close, change_ratio
            FROM multi_quote
            WHERE change_ratio < 0
            ORDER BY change_ratio
            LIMIT 25;
        """,
        "volume_spike_vs_3m": """
            SELECT ticker, name, volume, avg_vol_3m,
                   ROUND(volume / NULLIF(avg_vol_3m, 0), 2) AS vol_multiple
            FROM multi_quote
            WHERE volume / NULLIF(avg_vol_3m, 0) >= 1
            ORDER BY vol_multiple DESC;
        """,
        "ten_day_accelerating_volume": """
            SELECT ticker, name, avg_vol_10d, avg_vol_3m,
                   ROUND(avg_vol_10d / NULLIF(avg_vol_3m, 0), 2) AS accel_multiple
            FROM multi_quote
            WHERE avg_vol_10d / NULLIF(avg_vol_3m, 0) >= 2
            ORDER BY accel_multiple DESC;
        """,
        "turnover_surge": """
            SELECT ticker, name, turnover_rate
            FROM multi_quote
            WHERE turnover_rate >= 0.10
            ORDER BY turnover_rate DESC;
        """,
        "near_52_high": """
            SELECT ticker, name, close, fifty_high,
                   ROUND((close / fifty_high - 1)::numeric, 4) AS pct_from_high
            FROM multi_quote
            WHERE fifty_high > 0
              AND close >= fifty_high * 0.98
            ORDER BY pct_from_high DESC;
        """,
        "near_52_low": """
            SELECT ticker, name, close, fifty_low,
                   ROUND((close / fifty_low - 1)::numeric, 4) AS pct_from_low
            FROM multi_quote
            WHERE fifty_low > 0
              AND close <= fifty_low * 1.02
            ORDER BY pct_from_low ASC;
        """,
        "low_forward_pe": """
            SELECT ticker, name, close, forward_pe, pb
            FROM multi_quote
            WHERE forward_pe > 0
              AND forward_pe <= 15
              AND pb <= 1.5
            ORDER BY forward_pe, pb;
        """,
        "growth_high_multiple": """
            SELECT ticker, name, close, forward_pe, ps
            FROM multi_quote
            WHERE forward_pe >= 50
              AND ps >= 10
            ORDER BY forward_pe DESC;
        """,
        "deep_value_ps": """
            SELECT ticker, name, close, ps
            FROM multi_quote
            WHERE ps > 0
              AND ps <= 1
            ORDER BY ps;
        """,
        "big_cap_liquidity": """
            SELECT ticker, name, close, market_value AS mkt_cap_usd
            FROM multi_quote
            WHERE market_value >= 1.0e11
            ORDER BY market_value DESC;
        """,
        "small_cap_screen": """
            SELECT ticker, name, close, market_value
            FROM multi_quote
            WHERE market_value BETWEEN 3.0e8 AND 3.0e9
            ORDER BY market_value;
        """,
        "recent_earnings_gap": """
            SELECT ticker, name, close, latest_earnings_date
            FROM multi_quote
            WHERE latest_earnings_date >= CURRENT_DATE - INTERVAL '2 days'
            ORDER BY latest_earnings_date DESC;
        """,
        "dividend_next_7days": """
            SELECT ticker, name, close, latest_dividend_date
            FROM multi_quote
            WHERE latest_dividend_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '7 days'
            ORDER BY latest_dividend_date;
        """,
        "pe_turnaround": """
            SELECT ticker, name, close, pe, volume, avg_vol_3m
            FROM multi_quote
            WHERE pe < 0
              AND volume >= avg_vol_3m
            ORDER BY volume DESC;
        """,
        "sector_rotation_strength": """
            SELECT sector, ticker, name, change_ratio
            FROM multi_quote
            WHERE sector IS NOT NULL
              AND change_ratio >= 0.02
            ORDER BY sector, change_ratio DESC;
        """,
        "low_float_high_turnover": """
            SELECT ticker, name, outstanding_shares, turnover_rate
            FROM multi_quote
            WHERE outstanding_shares <= 50e6
              AND turnover_rate >= 0.20
            ORDER BY turnover_rate DESC;
        """,
        "pb_discount": """
            SELECT ticker, name, close, pb
            FROM multi_quote
            WHERE pb > 0
              AND pb <= 0.8
            ORDER BY pb;
        """
    },

    'info': {
        'upcoming_dividends': """SELECT
    ticker,
    dividend_date,
    dividend_amount,
    yield
FROM info
WHERE dividend_date IS NOT NULL
  AND dividend_date BETWEEN CURRENT_DATE AND CURRENT_DATE + INTERVAL '14 days'
  AND dividend_amount IS NOT NULL
  AND dividend_amount > 0
ORDER BY dividend_date ASC;
""",
"high_yields": """SELECT
    ticker,
    yield,
    dividend_amount,
    dividend_frequency
FROM info
WHERE yield IS NOT NULL
  AND yield >= 0.008      -- 2 × 0.004 (avg_yield)
ORDER BY yield DESC;
""",
"""ivx30_jump""": """SELECT
    ticker,
    ivx30,
    ivx30_chg,
    ivx30_chg_percent
FROM info
WHERE ivx30 IS NOT NULL
  AND ivx30_chg IS NOT NULL
  AND ivx30_chg > 0
ORDER BY ivx30_chg DESC
LIMIT 50;
""",
"top_iv_rank": """SELECT
    ticker,
    iv_rank
FROM info
WHERE iv_rank IS NOT NULL
  AND iv_rank >= 0.80
ORDER BY iv_rank DESC;
""",
"deep_volatility_crush": """SELECT
    ticker,
    ivx30,
    ivx30_chg_percent
FROM info
WHERE ivx30_chg_percent IS NOT NULL
  AND ivx30_chg_percent <= -10
ORDER BY ivx30_chg_percent ASC;
""",
"extremely_volatile": """SELECT
    ticker,
    volatile_rank,
    price,
    iv_rank,
    hv30
FROM info
WHERE volatile_rank = 'Extremely volatile';
""",
"strong_bullish_sentiment": """SELECT
    ticker,
    sentiment,
    price,
    change_percent
FROM info
WHERE sentiment = 'Strong bullish';
""",
"""high_beta""": """SELECT
    ticker,
    beta90d
FROM info
WHERE beta90d IS NOT NULL
  AND beta90d >= 1.3
ORDER BY beta90d DESC;
""",
"highest_volatility_per_share": """SELECT
    ticker,
    volatility_per_share
FROM info
WHERE volatility_per_share IS NOT NULL
ORDER BY volatility_per_share DESC
LIMIT 50;
""",
"high_iv_percentile": """SELECT
    ticker,
    ivp90
FROM info
WHERE ivp90 IS NOT NULL
  AND ivp90 >= 90
ORDER BY ivp90 DESC;
""",
"rich_iv_vs_hv": """SELECT
    ticker,
    iv_ratio,
    ivx30,
    hv30
FROM info
WHERE iv_ratio IS NOT NULL
  AND iv_ratio >= 1.5
ORDER BY iv_ratio DESC;
""",
"call_heavy_flow": """SELECT
    ticker,
    call_vol,
    put_vol,
    ROUND((call_vol / NULLIF(put_vol, 0))::numeric, 2) AS call_put_ratio
FROM info
WHERE call_vol IS NOT NULL
  AND put_vol IS NOT NULL
  AND put_vol > 0
  AND call_vol / put_vol >= 2
ORDER BY call_put_ratio DESC;
""",
"put_heavy_flow": """SELECT
    ticker,
    put_vol,
    call_vol,
    ROUND((put_vol / NULLIF(call_vol, 0))::numeric, 2) AS put_call_ratio
FROM info
WHERE put_vol IS NOT NULL
  AND call_vol IS NOT NULL
  AND call_vol > 0
  AND put_vol / call_vol >= 2
ORDER BY put_call_ratio DESC;
""",



    }
}
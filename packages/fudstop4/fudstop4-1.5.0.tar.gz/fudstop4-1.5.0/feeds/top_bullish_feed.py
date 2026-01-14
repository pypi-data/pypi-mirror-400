import asyncio
import os
from datetime import timedelta

import pandas as pd
from dotenv import load_dotenv

try:
    from asyncdiscordwebhook import AsyncDiscordWebhook, DiscordEmbed
except Exception:
    from discord_webhook import AsyncDiscordWebhook, DiscordEmbed

from fudstop4.apis.polygonio.polygon_options import PolygonOptions

load_dotenv()

db = PolygonOptions()

# ---- Feed config ----
HOOK_URL = os.getenv("TOP_BULLISH_FEED_WEBHOOK", os.getenv("RSI_TD9_BBANDS_WEBHOOK", ""))
TIMESPAN = os.getenv("TOP_BULLISH_TIMESPAN", "m1")
LOOKBACK_MINUTES = int(os.getenv("TOP_BULLISH_LOOKBACK_MINUTES", "3"))
COOLDOWN_MINUTES = int(os.getenv("TOP_BULLISH_COOLDOWN_MINUTES", "5"))
POLL_SECONDS = float(os.getenv("TOP_BULLISH_POLL_SECONDS", "1"))

# ---- Top bullish rule (from latest findings with decent support) ----
# Base:
#   rsi <= 30 AND td_buy_count >= 10 AND candle_completely_below_lower = true
# Add-ons:
#   bb_width >= 0.03 AND rvol >= 1.5 AND stoch_rsi_k <= 10
HOLD_MIN = 1
HOLD_MAX = 15
PROB_20BP = 0.96
AVG_MOVE = 0.01189388283803471
P15_MOVE = 0.004558227105448542


async def main() -> None:
    await db.connect()
    last_sent = {}

    while True:
        query = f"""
            SELECT
                ticker,
                timespan,
                rsi,
                td_buy_count,
                candle_completely_below_lower,
                ts_utc,
                c,
                rvol,
                bb_width,
                stoch_rsi_k
            FROM candle_analysis_live
            WHERE
                timespan = '{TIMESPAN}'
                AND ts_utc::timestamptz >= now() - interval '{LOOKBACK_MINUTES} minutes'
                AND rsi <= 30
                AND td_buy_count >= 10
                AND candle_completely_below_lower = true
                AND bb_width >= 0.03
                AND rvol >= 1.5
                AND stoch_rsi_k <= 10
            ORDER BY ts_utc::timestamptz DESC;
        """

        results = await db.fetch(query)
        if not results:
            await asyncio.sleep(POLL_SECONDS)
            continue

        rows = sorted(results, key=lambda r: r["ts_utc"])
        for r in rows:
            ts_utc = pd.Timestamp(r["ts_utc"])
            if ts_utc.tzinfo is None:
                ts_utc = ts_utc.tz_localize("UTC")
            ts_et = ts_utc.tz_convert("America/New_York")

            key = (r["ticker"], "bullish")
            last_ts = last_sent.get(key)
            if last_ts and ts_utc <= last_ts + timedelta(minutes=COOLDOWN_MINUTES):
                continue
            last_sent[key] = ts_utc

            embed = DiscordEmbed(
                title="Top Bullish Reversal",
                description=f"{r['ticker']} @ {ts_et.strftime('%Y-%m-%d %H:%M ET')}",
                color="2ecc71",
            )
            embed.add_embed_field(
                name="Setup",
                value=(
                    "RSI ≤ 30, TD Buy ≥ 10, Candle Completely Below Lower Band\n"
                    "BBW ≥ 0.03, RVOL ≥ 1.5, StochRSI K ≤ 10"
                ),
                inline=False,
            )
            embed.add_embed_field(
                name="Stats (historical)",
                value=(
                    f"Probability (≥20bp): **{PROB_20BP:.1%}**\n"
                    f"Expected Hold: **{HOLD_MIN}-{HOLD_MAX} min**\n"
                    f"Expected Move (avg / p15): **{AVG_MOVE:.2%} / {P15_MOVE:.2%}**"
                ),
                inline=False,
            )
            embed.set_footer(text="Top bullish feed (strict confluence)")
            embed.set_timestamp()

            webhook = AsyncDiscordWebhook(url=HOOK_URL)
            webhook.add_embed(embed)
            await webhook.execute()

        await asyncio.sleep(POLL_SECONDS)


asyncio.run(main())

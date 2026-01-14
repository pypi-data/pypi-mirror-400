import asyncio
import os
from datetime import timedelta

import pandas as pd
from dotenv import load_dotenv

try:
    from discord_webhook import AsyncDiscordWebhook, DiscordEmbed
except Exception:
    from discord_webhook import AsyncDiscordWebhook, DiscordEmbed

from fudstop4.apis.polygonio.polygon_options import PolygonOptions

load_dotenv()

db = PolygonOptions()

# ---- Feed config ----
HOOK_URL = os.getenv("https://discord.com/api/webhooks/1458720348391604427/Ow69LwrgKhC_EyRs1RwQumWvtaCoypd-r91BpoAkHxjn7pxAcH7OewbwlZOGZ0Epsil2", os.getenv("RSI_TD9_BBANDS_WEBHOOK", ""))
TIMESPAN = os.getenv("TOP_BEARISH_TIMESPAN", "m1")
LOOKBACK_MINUTES = int(os.getenv("TOP_BEARISH_LOOKBACK_MINUTES", "3"))
COOLDOWN_MINUTES = int(os.getenv("TOP_BEARISH_COOLDOWN_MINUTES", "5"))
POLL_SECONDS = float(os.getenv("TOP_BEARISH_POLL_SECONDS", "1"))

# ---- Top bearish rule (from latest findings with decent support) ----
# Base:
#   rsi >= 70 AND td_sell_count >= 10 AND candle_completely_above_upper = true
# Add-ons:
#   bb_width >= 0.06 AND adx_strong = true
HOLD_MIN = 1
HOLD_MAX = 20
PROB_20BP = 0.9038461538461539
AVG_MOVE = 0.01567800079143449
P15_MOVE = 0.0032319357852195417


async def main() -> None:
    await db.connect()
    last_sent = {}

    while True:
        query = f"""
            SELECT
                ticker,
                timespan,
                rsi,
                td_sell_count,
                candle_completely_above_upper,
                ts_utc,
                c,
                bb_width,
                adx_strong
            FROM candle_analysis_live
            WHERE
                timespan = '{TIMESPAN}'
                AND ts_utc::timestamptz >= now() - interval '{LOOKBACK_MINUTES} minutes'
                AND rsi >= 70
                AND td_sell_count >= 10
                AND candle_completely_above_upper = true
                AND bb_width >= 0.06
                AND adx_strong = true
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

            key = (r["ticker"], "bearish")
            last_ts = last_sent.get(key)
            if last_ts and ts_utc <= last_ts + timedelta(minutes=COOLDOWN_MINUTES):
                continue
            last_sent[key] = ts_utc

            embed = DiscordEmbed(
                title="Top Bearish Reversal",
                description=f"{r['ticker']} @ {ts_et.strftime('%Y-%m-%d %H:%M ET')}",
                color="e74c3c",
            )
            embed.add_embed_field(
                name="Setup",
                value=(
                    "RSI ≥ 70, TD Sell ≥ 10, Candle Completely Above Upper Band\n"
                    "BBW ≥ 0.06, ADX Strong"
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
            embed.set_footer(text="Top bearish feed (strict confluence)")
            embed.set_timestamp()

            webhook = AsyncDiscordWebhook(url=HOOK_URL)
            webhook.add_embed(embed)
            await webhook.execute()

        await asyncio.sleep(POLL_SECONDS)


asyncio.run(main())

import asyncio
import os
import time
import uuid
from datetime import timedelta
import hashlib
import random
import string

import pandas as pd
from dotenv import load_dotenv
from discord_webhook import AsyncDiscordWebhook, DiscordEmbed
import requests

from fudstop4.apis.polygonio.polygon_options import PolygonOptions

load_dotenv()

ACCESS_TOKEN_BLOCK = os.environ.get("ACCESS_TOKEN_BLOCK")

PAPER_ID = 56840164
PAPER_ID_BLOCK = 56851633

db = PolygonOptions()


def generate_webull_headers_BLOCK(access_token_BLOCK=None):
    offset_hours = 6
    offset_millis = offset_hours * 3600 * 1000

    current_millis = int(time.time() * 1000)
    t_time_value = current_millis - offset_millis

    random_str = "".join(random.choices(string.ascii_lowercase + string.digits, k=12))
    x_s_value = hashlib.sha256(f"{random_str}{t_time_value}".encode()).hexdigest()

    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9",
        "access_token": os.environ.get("ACCESS_TOKEN_BLOCK"),
        "app": "global",
        "app-group": "broker",
        "appid": "wb_web_app",
        "cache-control": "no-cache",
        "content-type": "application/json",
        "device-type": "Web",
        "did": "y4qye7g0lrk5c5swu8qx678lhlnjfdc2",
        "dnt": "1",
        "hl": "en",
        "lzone": "dc_core_r001",
        "origin": "https://app.webull.com",
        "os": "web",
        "osv": "i9zh",
        "platform": "web",
        "pragma": "no-cache",
        "priority": "u=1, i",
        "referer": "https://app.webull.com/",
        "reqid": "oskf6g03ybscp94g4glus7r1pdecd_00",
        "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": '"Android"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "t_time": str(t_time_value),
        "tz": "America/New_York",
        "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36",
        "ver": "6.2.0",
        "x-s": x_s_value,
        "x-sv": "xodp2vg9",
    }
    return headers


HOOK_URL = os.getenv(
    "RSI_TD9_BBANDS_RVOL_BEAR_WEBHOOK",
    os.getenv(
        "RSI_TD9_BBANDS_WEBHOOK",
        "https://discord.com/api/webhooks/1458720501341097994/gHRG0iNdojS2kRpviFJZTpM3c-FMalujWyaaQL4YSz6fozH_P4cgeJ7CcMd9e9zl0vD4",
    ),
)
TIMESPAN = os.getenv("RSI_TD9_TIMESPAN", "m1")
LOOKBACK_MINUTES = int(os.getenv("RSI_TD9_LOOKBACK_MINUTES", "3"))
COOLDOWN_MINUTES = int(os.getenv("RSI_TD9_COOLDOWN_MINUTES", "5"))
POLL_SECONDS = float(os.getenv("RSI_TD9_POLL_SECONDS", "1"))

MIN_RVOL = float(os.getenv("RSI_TD9_MIN_RVOL", "1.5"))
MIN_BB_WIDTH = float(os.getenv("RSI_TD9_MIN_BB_WIDTH", "0.03"))


async def main():
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
                rvol,
                bb_width
            FROM candle_analysis_live
            WHERE
                timespan = '{TIMESPAN}'
                AND ts_utc::timestamptz >= now() - interval '{LOOKBACK_MINUTES} minutes'
                AND rsi >= 70
                AND td_sell_count >= 10
                AND candle_completely_above_upper = true
                AND rvol >= {MIN_RVOL}
                AND bb_width >= {MIN_BB_WIDTH}
            ORDER BY ts_utc::timestamptz DESC;
        """

        results = await db.fetch(query)
        if not results:
            await asyncio.sleep(POLL_SECONDS)
            continue

        rows = sorted(results, key=lambda r: r["ts_utc"])
        for r in rows:
            close = float(r["c"])
            ticker = r["ticker"]

            ts_utc = pd.Timestamp(r["ts_utc"])
            if ts_utc.tzinfo is None:
                ts_utc = ts_utc.tz_localize("UTC")
            ts_et = ts_utc.tz_convert("America/New_York")

            if not (
                r["rsi"] >= 70
                and r["td_sell_count"] >= 10
                and r["candle_completely_above_upper"]
                and float(r["rvol"]) >= MIN_RVOL
                and float(r["bb_width"]) >= MIN_BB_WIDTH
            ):
                continue

            side = "bearish"
            label = "Downside Sell Pressure (Above Upper Band)"

            key = (ticker, side)
            last_ts = last_sent.get(key)
            if last_ts and ts_utc <= last_ts + timedelta(minutes=COOLDOWN_MINUTES):
                continue
            last_sent[key] = ts_utc

            embed = DiscordEmbed(
                title="TD9 + RSI + RVOL + BBW Signal",
                description=f"{ticker} @ {ts_et.strftime('%Y-%m-%d %H:%M ET')}",
                color="e74c3c",
            )

            embed.add_embed_field(
                name=label,
                value=(
                    f"RSI **{r['rsi']:.2f}**, "
                    f"TD Sell **{r['td_sell_count']}**, "
                    f"RVOL **{float(r['rvol']):.2f}**, "
                    f"BBW **{float(r['bb_width']):.4f}**, "
                    "Band: **Above Upper**"
                ),
                inline=False,
            )
            embed.set_footer(text="TD9 + RSI + RVOL + BB Width + Bollinger Confluence")
            embed.set_timestamp()

            webhook = AsyncDiscordWebhook(url=HOOK_URL)
            webhook.add_embed(embed)
            await webhook.execute()

            PAPER_QUERY = f"""
                SELECT option_id, expiry, strike
                FROM atm_options
                WHERE ticker = '{ticker}'
                AND call_put = 'put'
                AND expiry >= CURRENT_DATE
                AND strike < {close}
                ORDER BY
                expiry ASC,
                ({close} - strike) ASC
                LIMIT 1;
            """
            PAPER_RESULTS = await db.fetch(PAPER_QUERY)
            try:
                option_id = PAPER_RESULTS[0]["option_id"]
                strike = PAPER_RESULTS[0]["strike"]
                expiry = PAPER_RESULTS[0]["expiry"]
                call_put = "put"

                print(option_id, ticker, strike, call_put, expiry)

                TRADE_URL = "https://act.webullfintech.com/webull-paper-center/api/paper/v1/order/optionPlace"
                TRADE_PAYLOAD = {
                    "tickerId": option_id,
                    "action": "BUY",
                    "orderType": "MKT",
                    "quantity": 1,
                    "timeInForce": "DAY",
                    "orders": [{"action": "BUY", "quantity": 1, "tickerId": option_id, "tickerType": "OPTION"}],
                    "tickerType": "OPTION",
                    "paperId": 1,
                    "accountId": PAPER_ID_BLOCK,
                    "optionStrategy": "Single",
                    "serialId": str(uuid.uuid4()),
                    "checkOrPlace": "PLACE",
                }

                resp = requests.post(
                    TRADE_URL,
                    headers=generate_webull_headers_BLOCK(access_token_BLOCK=ACCESS_TOKEN_BLOCK),
                    json=TRADE_PAYLOAD,
                    timeout=10,
                )
                print(resp.status_code, resp.text[:500])
            except Exception as e:
                print(f"Paper trade skipped for {ticker}: {e}")

        await asyncio.sleep(POLL_SECONDS)


asyncio.run(main())

#!/usr/bin/env python3
"""
FUDSTOP · async Webull/Polygon pipeline
Version: 2025‑08‑01b  –  bug‑fix release
"""

import sys, time, logging, asyncio
from asyncio import Semaphore, Lock
from pathlib import Path
from typing import Dict, Tuple, Optional

import aiohttp, asyncpg, pandas as pd, numpy as np
from numba import njit

# ─── project imports (adjust to your tree) ──────────────────────────────────
ROOT = Path(__file__).resolve().parents[2]
sys.path.append(str(ROOT))

from script_helpers import (add_td9_counts, add_bollinger_bands,
                            compute_wilders_rsi, macd_curvature_label,
                            add_parabolic_sar_signals, generate_webull_headers)

from fudstop4.apis.webull.webull_ta import WebullTA
from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers

# ─── viz imports ───────────────────────────────────────────────────────────
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from mplfinance.original_flavor import candlestick_ohlc
from matplotlib.ticker import AutoMinorLocator
from io import BytesIO

# ─── logging ───────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    level=logging.INFO,
    datefmt="%H:%M:%S",
)

# ─── globals ───────────────────────────────────────────────────────────────
SEM = Semaphore(75)
ticker_id_cache: Dict[str, int] = {}
ticker_cache_lock = Lock()

db = PolygonOptions()
ta = WebullTA()

# ─── helpers ────────────────────────────────────────────────────────────────
def add_macd(df: pd.DataFrame) -> pd.DataFrame:
    ema12 = df["c"].ewm(span=12, adjust=False).mean()
    ema26 = df["c"].ewm(span=26, adjust=False).mean()
    df["macd"] = ema12 - ema26
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"] = df["macd"] - df["macd_signal"]
    return df

def add_emas(df: pd.DataFrame) -> pd.DataFrame:
    df["ema20"] = df["c"].ewm(span=20, adjust=False).mean()
    df["ema50"] = df["c"].ewm(span=50, adjust=False).mean()
    return df

# ─── DB pool ───────────────────────────────────────────────────────────────
async def init_db_pool() -> asyncpg.Pool:
    return await asyncpg.create_pool(
        user="chuck", password="fud", database="fudstop3",
        host="localhost", port=5432,
        min_size=1, max_size=10, command_timeout=60
    )

async def store_chart_image(pool: asyncpg.Pool, ticker: str, span: str, img: bytes):
    async with pool.acquire() as con:
        await con.execute("""
            INSERT INTO ticker_charts (ticker,timespan,image_data)
            VALUES ($1,$2,$3)
            ON CONFLICT (ticker,timespan)
            DO UPDATE SET image_data=EXCLUDED.image_data,created_at=now()
        """, ticker, span, img)

# ─── chart generation ───────────────────────────────────────────────────────
def _stylize_axes(ax):
    ax.set_facecolor("#111")
    ax.grid(ls="--", lw=0.4, alpha=.25, color="#444")
    ax.xaxis.set_minor_locator(AutoMinorLocator())
    ax.tick_params(axis="x", colors="#bbb", labelsize=8)
    ax.tick_params(axis="y", colors="#bbb", labelsize=8)

def _price_label(ax, x, y, txt, fc):
    ax.text(x, y, f"{txt:,.2f}", va="center", ha="right",
            fontsize=7.5, color="#fff",
            bbox=dict(boxstyle="round,pad=0.17", fc=fc, ec="none", alpha=.95))

async def generate_chart_image(df: pd.DataFrame, ticker: str, span: str) -> bytes:
    plot = df.copy()
    plot["num"] = mdates.date2num(plot["ts"])
    ohlc = plot[["num","o","h","l","c"]].values

    # handle the >1‑row requirement gracefully
    if len(ohlc) < 2:  # not enough to chart
        return b""

    fig, (ax_p, ax_m, ax_r) = plt.subplots(
        3,1, figsize=(12,7.5), sharex=True,
        gridspec_kw={"height_ratios":[3.8,1.8,1.5]}
    )
    plt.rcParams["savefig.facecolor"] = "#111"

    # ── price panel ───────────────────────────────────────────────────────
    candlestick_ohlc(
        ax_p, ohlc,
        width=0.6*(ohlc[1,0]-ohlc[0,0]),
        colorup="#9aff30", colordown="#ff2b98", alpha=0.9
    )
    ax_p.plot(plot["num"], plot["ema20"], lw=.9, label="EMA 20", color="#299fff")
    ax_p.plot(plot["num"], plot["ema50"], lw=.9, label="EMA 50", color="#f4a400")

    x_last = plot["num"].iat[-1]
    ax_p.axvline(x_last, ls="--", lw=.7, color="#999", alpha=.6)
    ax_p.scatter(x_last, plot["c"].iat[-1], s=30, color="#ff9500", zorder=5)

    _price_label(ax_p, x_last+2, plot["c"].iat[-1], plot["c"].iat[-1], "#2d7df6")
    _price_label(ax_p, x_last+2, plot["ema20"].iat[-1], plot["ema20"].iat[-1], "#299fff")
    _price_label(ax_p, x_last+2, plot["ema50"].iat[-1], plot["ema50"].iat[-1], "#f4a400")
    _price_label(ax_p, x_last+2, plot["h"].iat[-1], plot["h"].iat[-1], "#00b59c")
    _price_label(ax_p, x_last+2, plot["l"].iat[-1], plot["l"].iat[-1], "#ff1744")

    ax_p.set_title(f"{ticker.upper()} Chart", loc="left", color="#fff", fontsize=12)
    ax_p.legend(frameon=False, fontsize=8, loc="upper left")
    _stylize_axes(ax_p)

    # ── MACD panel ─────────────────────────────────────────────────────────
    ax_m.bar(plot["num"], plot["macd_hist"],
             width=0.6, color=np.where(plot["macd_hist"]>=0,"#9aff30","#ff2b98"), alpha=.65)
    ax_m.plot(plot["num"], plot["macd"], lw=.8, color="#d9d9d9", label="MACD")
    ax_m.plot(plot["num"], plot["macd_signal"], lw=.8, color="#6c6cff", label="Signal")
    ax_m.axhline(0, lw=.5, color="#777")
    ax_m.legend(frameon=False, fontsize=7, loc="upper left")
    _stylize_axes(ax_m)

    # ── RSI panel ──────────────────────────────────────────────────────────
    ax_r.plot(plot["num"], plot["rsi"], lw=.8, color="#d9d9d9")
    ax_r.axhline(70, ls="--", lw=.5, color="#ff2b98")
    ax_r.axhline(30, ls="--", lw=.5, color="#9aff30")
    ax_r.set_ylim(0,100)
    _stylize_axes(ax_r)

    fig.tight_layout()
    buf = BytesIO()
    fig.savefig(buf, dpi=110, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return buf.read()

# ─── fetch JSON with retry ──────────────────────────────────────────────────
async def fetch_json(session,aurl,headers,retries=3,delay=1):
    for i in range(retries):
        try:
            async with session.get(aurl,headers=headers,timeout=aiohttp.ClientTimeout(total=10)) as r:
                r.raise_for_status()
                return await r.json()
        except Exception as e:
            if i<retries-1:
                await asyncio.sleep(delay)
            else:
                raise e

# ─── core fetch for each ticker/span ─────────────────────────────────────────
async def grab_span(session,ticker,span,chart,db_pool):
    try:
        async with SEM:
            async with ticker_cache_lock:
                tid = ticker_id_cache.get(ticker) or await ta.get_webull_id(ticker)
                ticker_id_cache[ticker]=tid

            url = ( "https://quotes-gw.webullfintech.com/api/quote/charts/query-mini"
                    f"?type={span}&count=90&restorationType=1&loadFactor=1&extendTrading=0&tickerId={tid}" )
            raw = await fetch_json(session,url,generate_webull_headers())
        if not raw or not raw[0].get("data"):
            return None
        rows = [r.split(",") for r in raw[0]["data"]]
        df = pd.DataFrame(rows,columns=["ts","o","c","h","l","a","v","vwap"])

        df["ts"] = pd.to_datetime(pd.to_numeric(df["ts"]), unit="s", utc=True)

        numeric_cols = ["o","c","h","l","v","vwap","a"]
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # first reverse so oldest at index 0, then fill NaNs
        df = df.iloc[::-1].reset_index(drop=True)
        df[numeric_cols] = df[numeric_cols].fillna(method="ffill").fillna(method="bfill")
        df = df.drop(columns="a")

        # indicators
        df = (compute_wilders_rsi(df)
              .pipe(add_bollinger_bands)
              .pipe(add_macd)
              .pipe(add_emas)
        )
        df["ticker"], df["timespan"] = ticker, span

        if chart:
            img = await generate_chart_image(df,ticker,span)
            if img:
                await store_chart_image(db_pool,ticker,span,img)
        return df
    except Exception as e:
        logging.error("%s %s error: %s", ticker, span, e)
        return None

# ─── concurrent driver ──────────────────────────────────────────────────────
async def run_cycle(tickers,spans,db_pool):
    connlim = aiohttp.TCPConnector(limit=105)
    async with aiohttp.ClientSession(connector=connlim) as sess:
        tasks = [grab_span(sess,t,s,True,db_pool) for t in tickers for s in spans]
        await asyncio.gather(*tasks)

# ─── main loop ──────────────────────────────────────────────────────────────
async def main():
    db_pool = await init_db_pool()
    await db.connect()

    spans = ["m30","m60","d1"]
    cycle=0
    try:
        while True:
            cycle+=1
            t0=time.time()
            logging.info("Cycle %d",cycle)
            await run_cycle(most_active_tickers[:2],spans,db_pool)
            logging.info("Done in %.1fs",time.time()-t0)
            await asyncio.sleep(6)
    finally:
        await db.disconnect()
        await db_pool.close()

# ─── quick viewer ───────────────────────────────────────────────────────────
async def view():
    pool = await init_db_pool()
    async with pool.acquire() as con:
        row = await con.fetchrow("SELECT image_data FROM ticker_charts ORDER BY created_at DESC LIMIT 1")
    if row:
        import matplotlib.pyplot as plt, io
        plt.imshow(plt.imread(io.BytesIO(row["image_data"]),format="png"))
        plt.axis("off"); plt.show()

        plt.savefig("latest_chart.png", bbox_inches="tight", pad_inches=0)
    await pool.close()

# ─── CLI ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(view())


#!/usr/bin/env python3
"""
OI Summary maintenance service (production-ready).

For a list of tickers (most_active_tickers), this service:
- Calls https://www.fudstop.io/api/oi_summary?ticker={ticker}
- Normalizes the JSON into a DataFrame
- Upserts into `oi_summary` table (unique: ticker, expiry)

Features:
- Anchored scheduler (exact interval between *starts*)
- DB transaction scoped around write phase
- Advisory lock around the write phase (no overlapping writers)
- Per-run statement_timeout & lock_timeout (SET LOCAL)
- Exponential retries with jitter on transient DB errors
- Prometheus metrics on /metrics, liveness /healthz, readiness /ready
- Env/CLI configuration, clean shutdown

ENV (overridable by CLI):
  RUN_INTERVAL_SECONDS=43200      # 12 hours
  LOCK_KEY=981277
  STATEMENT_TIMEOUT_MS=300000     # 5 minutes
  LOCK_TIMEOUT_MS=5000
  DB_SEARCH_PATH=None             # e.g. "public,app"

  BATCH_SIZE=7
  FUDSTOP_API_KEY=fudstop4
  OI_SUMMARY_API_BASE=https://www.fudstop.io
  OI_SUMMARY_PATH=/api/oi_summary

  HTTP_HOST=0.0.0.0
  HTTP_PORT=9112
  READINESS_TTL_SECONDS=600

  RETRY_MAX_ATTEMPTS=5
  RETRY_BASE_DELAY_SECONDS=0.2
  RETRY_MAX_DELAY_SECONDS=5.0

  LOG_LEVEL=INFO
"""

import os
import sys
import asyncio
import signal
import logging
import time
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, List

import aiohttp
import pandas as pd
from aiohttp import web
from prometheus_client import (
    Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
)
from dotenv import load_dotenv

# Make project root importable (same pattern as your original script)
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from fudstop4.apis.helpers import format_large_numbers_in_dataframe2
from fudstop4._markets.list_sets.ticker_lists import most_active_tickers

load_dotenv()

# -----------------------
# Config & Logging
# -----------------------

@dataclass
class Config:
    # Scheduling / locking
    interval_seconds: float = float(os.getenv("RUN_INTERVAL_SECONDS", "43200"))
    lock_key: int = int(os.getenv("LOCK_KEY", "981277"))
    statement_timeout_ms: int = int(os.getenv("STATEMENT_TIMEOUT_MS", "300000"))
    lock_timeout_ms: int = int(os.getenv("LOCK_TIMEOUT_MS", "5000"))
    search_path: Optional[str] = os.getenv("DB_SEARCH_PATH")

    # Batching / API
    batch_size: int = int(os.getenv("BATCH_SIZE", "7"))
    api_key: str = os.getenv("FUDSTOP_API_KEY", "fudstop4")
    api_base: str = os.getenv("OI_SUMMARY_API_BASE", "https://www.fudstop.io")
    api_path: str = os.getenv("OI_SUMMARY_PATH", "/api/oi_summary")

    # HTTP server for metrics
    http_host: str = os.getenv("HTTP_HOST", "0.0.0.0")
    http_port: int = int(os.getenv("HTTP_PORT", "9112"))
    readiness_ttl_seconds: float = float(os.getenv("READINESS_TTL_SECONDS", "600"))

    # Retries
    retry_max_attempts: int = int(os.getenv("RETRY_MAX_ATTEMPTS", "5"))
    retry_base_delay: float = float(os.getenv("RETRY_BASE_DELAY_SECONDS", "0.2"))
    retry_max_delay: float = float(os.getenv("RETRY_MAX_DELAY_SECONDS", "5.0"))

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        stream=sys.stdout,
    )


logger = logging.getLogger("oi_summary_service")

# -----------------------
# Metrics
# -----------------------

NS = "oi_summary_job"

RUNS_TOTAL = Counter(f"{NS}_runs_total", "Total runs executed.", ["result", "phase"])
LOCK_SKIPS_TOTAL = Counter(f"{NS}_lock_skips_total", "Runs skipped due to advisory lock.")
ERRORS_TOTAL = Counter(f"{NS}_errors_total", "Errors by type.", ["type"])
RUN_DURATION = Histogram(
    f"{NS}_run_duration_seconds",
    "Run duration seconds.",
    buckets=(0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 30, 60, 120, 300, 600),
)
LAST_RUN_START_TS = Gauge(f"{NS}_last_run_start_timestamp", "Last run start ts.")
LAST_RUN_END_TS = Gauge(f"{NS}_last_run_end_timestamp", "Last run end ts.")
LAST_SUCCESS_TS = Gauge(f"{NS}_last_success_timestamp", "Last successful run ts.")
ROWS_UPSERTED = Gauge(f"{NS}_rows_upserted", "Number of rows upserted in latest run.")
TICKERS_PROCESSED = Gauge(f"{NS}_tickers_processed", "Number of tickers processed in latest run.")
SERVICE_UP = Gauge(f"{NS}_up", "1 if service loop running, else 0.")

# -----------------------
# DB helpers
# -----------------------

db = PolygonOptions()


async def ensure_connected() -> None:
    await db.connect()


async def fetchval(sql: str, *args) -> Any:
    return await db.fetchval(sql, *args)


async def execute(sql: str, *args) -> None:
    await db.execute(sql, *args)


# -----------------------
# Error classification & retries (DB-focused)
# -----------------------

TRANSIENT_STATES = {
    "40001",  # serialization_failure
    "40P01",  # deadlock_detected
    "55P03",  # lock_not_available
    "57014",  # query_canceled (statement_timeout)
    "53300",  # too_many_connections
    "57P01",  # admin_shutdown
    "57P02",  # crash_shutdown
    "57P03",  # cannot_connect_now
}


def _get_sqlstate(exc: Exception) -> Optional[str]:
    state = getattr(exc, "sqlstate", None)
    if state:
        return str(state)
    msg = str(exc) or ""
    for code in TRANSIENT_STATES:
        if code in msg:
            return code
    return None


def is_transient_db_error(exc: Exception) -> bool:
    state = _get_sqlstate(exc)
    if state and state in TRANSIENT_STATES:
        return True
    msg = str(exc).lower()
    hints = (
        "deadlock detected",
        "serialization failure",
        "could not serialize",
        "lock timeout",
        "canceling statement due to statement timeout",
        "too many connections",
        "cannot connect now",
        "connection reset",
    )
    return any(h in msg for h in hints)


def backoff_delay(base: float, attempt: int, cap: float) -> float:
    exp = min(cap, base * (2 ** attempt))
    return random.uniform(0, exp)


# -----------------------
# HTTP fetch phase
# -----------------------

async def fetch_oi_summary_for_ticker(
    session: aiohttp.ClientSession, cfg: Config, ticker: str
) -> pd.DataFrame:
    """
    Fetch OI summary for a single ticker from the external API and
    return a DataFrame. Returns empty DataFrame on error.
    """
    url = f"{cfg.api_base.rstrip('/')}{cfg.api_path}?ticker={ticker}"
    try:
        async with session.get(url) as resp:
            if resp.status != 200:
                text = await resp.text()
                logger.warning(
                    "Non-200 response for %s: %s - %s",
                    ticker,
                    resp.status,
                    text,
                )
                return pd.DataFrame()
            data = await resp.json()

            # Normalize into DataFrame
            df = pd.DataFrame(data)
            if df.empty:
                return df
            if "ticker" not in df.columns:
                df["ticker"] = ticker
            return df
    except Exception as e:
        logger.warning("Error fetching OI summary for %s: %s", ticker, e)
        return pd.DataFrame()


async def fetch_all_oi_summaries(cfg: Config) -> pd.DataFrame:
    """
    Fetch OI summaries for all tickers in most_active_tickers in batches.
    Returns a single concatenated DataFrame (may be empty).
    """
    headers = {"X-API-KEY": cfg.api_key}
    all_frames: List[pd.DataFrame] = []

    async with aiohttp.ClientSession(headers=headers) as session:
        tickers = list(most_active_tickers)
        for i in range(0, len(tickers), cfg.batch_size):
            batch = tickers[i : i + cfg.batch_size]
            logger.info("Fetching batch: %s", batch)
            dfs = await asyncio.gather(
                *[fetch_oi_summary_for_ticker(session, cfg, t) for t in batch]
            )
            batch_frames = [df for df in dfs if not df.empty]
            if batch_frames:
                all_frames.append(pd.concat(batch_frames, ignore_index=True))

    if not all_frames:
        return pd.DataFrame()

    df_all = pd.concat(all_frames, ignore_index=True)
    return df_all


# -----------------------
# Core job (write phase under advisory lock)
# -----------------------

async def oi_summary_once(cfg: Config) -> Dict[str, Any]:
    """
    One full run:
    - Fetch OI summaries for all tickers (HTTP, no DB transaction or lock)
    - If we got data, start a transaction, grab advisory lock, upsert, commit.
    """
    metrics: Dict[str, Any] = {"phase": "default"}

    # 1) Fetch data via HTTP
    df = await fetch_all_oi_summaries(cfg)
    tickers_processed = len(most_active_tickers)
    TICKERS_PROCESSED.set(tickers_processed)
    metrics["tickers_processed"] = tickers_processed

    if df.empty:
        logger.info("No OI data fetched; skipping DB write.")
        metrics["rows_upserted"] = 0
        metrics["skipped_db"] = True
        return metrics

    # Optional formatting for logging / consistency (doesn't affect DB)
    df_for_db = df.copy()
    df_for_log = format_large_numbers_in_dataframe2(df.copy())
    logger.info("Fetched %d rows of OI summary data.", len(df_for_db))

    # 2) DB write under transaction + advisory lock
    await execute("BEGIN;")

    if cfg.search_path:
        await execute(f"SET LOCAL search_path = {cfg.search_path};")

    await execute(f"SET LOCAL statement_timeout = {cfg.statement_timeout_ms};")
    await execute(f"SET LOCAL lock_timeout = {cfg.lock_timeout_ms};")

    got_lock = await fetchval(
        "SELECT pg_try_advisory_xact_lock($1);", cfg.lock_key
    )
    if not got_lock:
        await execute("ROLLBACK;")
        metrics["skipped_lock"] = True
        logger.info("DB phase skipped: advisory lock held by another worker.")
        return metrics

    try:
        await db.batch_upsert_dataframe(
            df_for_db,
            table_name="oi_summary",
            unique_columns=["ticker", "expiry"],
        )
    except Exception as e:
        logger.exception("Error during batch_upsert_dataframe: %s", e)
        # Let higher layer handle rollback
        raise

    await execute("COMMIT;")

    metrics["rows_upserted"] = len(df_for_db)
    ROWS_UPSERTED.set(len(df_for_db))

    # Log a small sample for inspection
    try:
        sample = df_for_log.head(10)
        logger.info("Sample of upserted data (first 10 rows):\n%s", sample.to_string())
    except Exception:
        pass

    return metrics


async def oi_summary_with_retries(cfg: Config) -> Dict[str, Any]:
    attempt = 0
    while True:
        try:
            LAST_RUN_START_TS.set_to_current_time()
            t0 = time.perf_counter()
            metrics = await oi_summary_once(cfg)
            duration = time.perf_counter() - t0
            LAST_RUN_END_TS.set_to_current_time()

            if metrics.get("skipped_lock"):
                LOCK_SKIPS_TOTAL.inc()
                RUNS_TOTAL.labels(result="skipped", phase=metrics.get("phase", "default")).inc()
                return metrics

            RUN_DURATION.observe(duration)
            RUNS_TOTAL.labels(result="ok", phase=metrics.get("phase", "default")).inc()
            LAST_SUCCESS_TS.set_to_current_time()

            logger.info(
                "Run ok | duration=%.3fs | rows_upserted=%s tickers=%s",
                duration,
                metrics.get("rows_upserted", 0),
                metrics.get("tickers_processed", 0),
            )
            return metrics

        except Exception as e:
            LAST_RUN_END_TS.set_to_current_time()
            transient = is_transient_db_error(e)
            ERRORS_TOTAL.labels(type="transient" if transient else "permanent").inc()
            RUNS_TOTAL.labels(result="error", phase="default").inc()

            attempt += 1
            if transient and attempt < cfg.retry_max_attempts:
                delay = backoff_delay(
                    cfg.retry_base_delay,
                    attempt,
                    cfg.retry_max_delay,
                )
                logger.warning(
                    "Run failed (attempt %d/%d, transient). Retrying in %.2fs. Error: %s",
                    attempt,
                    cfg.retry_max_attempts,
                    delay,
                    e,
                )
                try:
                    await execute("ROLLBACK;")
                except Exception:
                    pass
                await asyncio.sleep(delay)
                continue

            logger.exception(
                "Run failed (attempt %d). No more retries. Error: %s",
                attempt,
                e,
            )
            try:
                await execute("ROLLBACK;")
            except Exception:
                pass
            raise


# -----------------------
# HTTP: /healthz /ready /metrics
# -----------------------

class HealthServer:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._app = web.Application()
        self._runner: Optional[web.AppRunner] = None
        self._site: Optional[web.TCPSite] = None
        self._routes()

    def _routes(self) -> None:
        self._app.router.add_get("/healthz", self.healthz)
        self._app.router.add_get("/ready", self.ready)
        self._app.router.add_get("/metrics", self.metrics)

    async def start(self) -> None:
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        self._site = web.TCPSite(self._runner, self.cfg.http_host, self.cfg.http_port)
        await self._site.start()
        logger.info(
            "HTTP server listening on http://%s:%d",
            self.cfg.http_host,
            self.cfg.http_port,
        )

    async def stop(self) -> None:
        if self._runner:
            await self._runner.cleanup()

    async def healthz(self, request: web.Request) -> web.Response:
        status = "ok" if SERVICE_UP._value.get() == 1.0 else "stopped"
        payload = {
            "status": status,
            "last_success_ts": LAST_SUCCESS_TS._value.get(),
            "last_run_start_ts": LAST_RUN_START_TS._value.get(),
            "last_run_end_ts": LAST_RUN_END_TS._value.get(),
        }
        return web.json_response(payload, status=200 if status == "ok" else 503)

    async def ready(self, request: web.Request) -> web.Response:
        now = time.time()
        last_ok = LAST_SUCCESS_TS._value.get() or 0
        age = now - last_ok if last_ok else float("inf")
        ready = age <= self.cfg.readiness_ttl_seconds
        payload = {
            "ready": ready,
            "age_since_last_success_sec": None if age == float("inf") else age,
            "threshold_sec": self.cfg.readiness_ttl_seconds,
        }
        return web.json_response(payload, status=200 if ready else 503)

    async def metrics(self, request: web.Request) -> web.Response:
        data = generate_latest()
        return web.Response(body=data, content_type=CONTENT_TYPE_LATEST)


# -----------------------
# Runner (anchored scheduler)
# -----------------------

class Runner:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._stop = asyncio.Event()
        self._http = HealthServer(cfg)

    def _install_signal_handlers(self) -> None:
        loop = asyncio.get_event_loop()
        for sig in (getattr(signal, "SIGINT", None), getattr(signal, "SIGTERM", None)):
            if sig is None:
                continue
            try:
                loop.add_signal_handler(sig, self._stop.set)
            except NotImplementedError:
                # Not supported on some platforms (e.g., Windows)
                pass

    async def run(self) -> None:
        self._install_signal_handlers()
        SERVICE_UP.set(1)
        await ensure_connected()
        await self._http.start()

        interval = self.cfg.interval_seconds
        target_next = time.perf_counter()  # start immediately

        try:
            while not self._stop.is_set():
                now = time.perf_counter()
                if now < target_next:
                    timeout = target_next - now
                    try:
                        await asyncio.wait_for(self._stop.wait(), timeout=timeout)
                        break
                    except asyncio.TimeoutError:
                        pass

                try:
                    await oi_summary_with_retries(self.cfg)
                except Exception as e:
                    logger.error("Unrecoverable run failure: %s", e)

                # Anchor next start
                target_next += interval
                now = time.perf_counter()
                while target_next <= now:
                    target_next += interval
        finally:
            SERVICE_UP.set(0)
            await self._http.stop()
            logger.info("Runner stopped.")


# -----------------------
# CLI / Entrypoint
# -----------------------

def parse_args(argv: Optional[list] = None) -> Config:
    import argparse

    p = argparse.ArgumentParser(description="OI Summary service")
    p.add_argument(
        "-i",
        "--interval-seconds",
        type=float,
        default=float(os.getenv("RUN_INTERVAL_SECONDS", "43200")),
    )
    p.add_argument(
        "--lock-key",
        type=int,
        default=int(os.getenv("LOCK_KEY", "981277")),
    )
    p.add_argument(
        "--statement-timeout-ms",
        type=int,
        default=int(os.getenv("STATEMENT_TIMEOUT_MS", "300000")),
    )
    p.add_argument(
        "--lock-timeout-ms",
        type=int,
        default=int(os.getenv("LOCK_TIMEOUT_MS", "5000")),
    )
    p.add_argument(
        "--search-path",
        type=str,
        default=os.getenv("DB_SEARCH_PATH"),
    )

    p.add_argument(
        "--batch-size",
        type=int,
        default=int(os.getenv("BATCH_SIZE", "7")),
    )
    p.add_argument(
        "--api-key",
        type=str,
        default=os.getenv("FUDSTOP_API_KEY", "fudstop4"),
    )
    p.add_argument(
        "--api-base",
        type=str,
        default=os.getenv("OI_SUMMARY_API_BASE", "https://www.fudstop.io"),
    )
    p.add_argument(
        "--api-path",
        type=str,
        default=os.getenv("OI_SUMMARY_PATH", "/api/oi_summary"),
    )

    p.add_argument(
        "--http-host",
        type=str,
        default=os.getenv("HTTP_HOST", "0.0.0.0"),
    )
    p.add_argument(
        "--http-port",
        type=int,
        default=int(os.getenv("HTTP_PORT", "9112")),
    )
    p.add_argument(
        "--readiness-ttl-seconds",
        type=float,
        default=float(os.getenv("READINESS_TTL_SECONDS", "600")),
    )

    p.add_argument(
        "--retry-max-attempts",
        type=int,
        default=int(os.getenv("RETRY_MAX_ATTEMPTS", "5")),
    )
    p.add_argument(
        "--retry-base-delay",
        type=float,
        default=float(os.getenv("RETRY_BASE_DELAY_SECONDS", "0.2")),
    )
    p.add_argument(
        "--retry-max-delay",
        type=float,
        default=float(os.getenv("RETRY_MAX_DELAY_SECONDS", "5.0")),
    )

    p.add_argument(
        "--log-level",
        type=str,
        default=os.getenv("LOG_LEVEL", "INFO"),
    )

    a = p.parse_args(argv)
    return Config(
        interval_seconds=a.interval_seconds,
        lock_key=a.lock_key,
        statement_timeout_ms=a.statement_timeout_ms,
        lock_timeout_ms=a.lock_timeout_ms,
        search_path=a.search_path,
        batch_size=a.batch_size,
        api_key=a.api_key,
        api_base=a.api_base,
        api_path=a.api_path,
        http_host=a.http_host,
        http_port=a.http_port,
        readiness_ttl_seconds=a.readiness_ttl_seconds,
        retry_max_attempts=a.retry_max_attempts,
        retry_base_delay=a.retry_base_delay,
        retry_max_delay=a.retry_max_delay,
        log_level=a.log_level,
    )


async def _amain(cfg: Config) -> None:
    setup_logging(cfg.log_level)
    logger.info(
        "Starting OI Summary service | interval=%.3fs lock_key=%s search_path=%s "
        "http=%s:%d readiness_ttl=%.1fs batch_size=%d",
        cfg.interval_seconds,
        cfg.lock_key,
        cfg.search_path,
        cfg.http_host,
        cfg.http_port,
        cfg.readiness_ttl_seconds,
        cfg.batch_size,
    )
    runner = Runner(cfg)
    await runner.run()


def main() -> None:
    cfg = parse_args()
    asyncio.run(_amain(cfg))


if __name__ == "__main__":
    main()

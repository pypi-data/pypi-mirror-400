#!/usr/bin/env python3
"""
OI Outliers maintenance & notification service (production-ready).

Scans `info` for large deviations of `open_interest` vs `avg_opt_oi_1mo`,
writes outliers to `oi_outliers` table, and posts a Discord embed.

Features:
- Transaction-scoped advisory lock (no overlapping DB work)
- Anchored scheduler (exact interval between *starts*)
- Per-run statement_timeout & lock_timeout (SET LOCAL)
- Exponential retries with jitter on transient DB errors
- Prometheus metrics on /metrics, liveness /healthz, readiness /ready
- Env/CLI configuration, clean shutdown
- Optional search_path for DB
- Optional Discord webhook (skips send if not configured)

ENV (overridable by CLI):
  RUN_INTERVAL_SECONDS=600
  LOCK_KEY=981276
  STATEMENT_TIMEOUT_MS=10000
  LOCK_TIMEOUT_MS=2000
  DB_SEARCH_PATH=None   # e.g., "public,app"

  OI_DEVIATION_THRESHOLD=0.2  # 20% deviation
  OI_OUTLIERS_WEBHOOK_URL=... # falls back to env "oi_outliers" if unset

  HTTP_HOST=0.0.0.0
  HTTP_PORT=9110
  READINESS_TTL_SECONDS=300

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

import pandas as pd
from aiohttp import web
from prometheus_client import (
    Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
)
from discord_webhook import AsyncDiscordWebhook, DiscordEmbed
from dotenv import load_dotenv

# Ensure project root in sys.path (like your original script)
project_dir = str(Path(__file__).resolve().parents[1])
if project_dir not in sys.path:
    sys.path.append(project_dir)

from fudstop4.apis.polygonio.polygon_options import PolygonOptions
from fudstop4.apis.helpers import format_large_numbers_in_dataframe2

load_dotenv()

# -----------------------
# Config & Logging
# -----------------------

@dataclass
class Config:
    # Core scheduling/locking
    interval_seconds: float = float(os.getenv("RUN_INTERVAL_SECONDS", "600"))
    lock_key: int = int(os.getenv("LOCK_KEY", "981276"))
    statement_timeout_ms: int = int(os.getenv("STATEMENT_TIMEOUT_MS", "10000"))
    lock_timeout_ms: int = int(os.getenv("LOCK_TIMEOUT_MS", "2000"))
    search_path: Optional[str] = os.getenv("DB_SEARCH_PATH")

    # OI deviation logic
    oi_deviation_threshold: float = float(os.getenv("OI_DEVIATION_THRESHOLD", "0.2"))

    # Discord
    webhook_url: Optional[str] = (
        os.getenv("OI_OUTLIERS_WEBHOOK_URL") or os.getenv("oi_outliers")
    )

    # HTTP
    http_host: str = os.getenv("HTTP_HOST", "0.0.0.0")
    http_port: int = int(os.getenv("HTTP_PORT", "9110"))
    readiness_ttl_seconds: float = float(os.getenv("READINESS_TTL_SECONDS", "300"))

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


logger = logging.getLogger("oi_outliers_service")


# -----------------------
# Metrics
# -----------------------

NS = "oi_outliers_job"

RUNS_TOTAL = Counter(f"{NS}_runs_total", "Total runs executed.", ["result", "path"])
LOCK_SKIPS_TOTAL = Counter(f"{NS}_lock_skips_total", "Runs skipped due to advisory lock.")
ERRORS_TOTAL = Counter(f"{NS}_errors_total", "Errors by type.", ["type"])
RUN_DURATION = Histogram(
    f"{NS}_run_duration_seconds",
    "Run duration seconds.",
    buckets=(0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 30, 60, 120, 300),
)
LAST_RUN_START_TS = Gauge(f"{NS}_last_run_start_timestamp", "Last run start ts.")
LAST_RUN_END_TS = Gauge(f"{NS}_last_run_end_timestamp", "Last run end ts.")
LAST_SUCCESS_TS = Gauge(f"{NS}_last_success_timestamp", "Last successful run ts.")
OUTLIER_ROWS = Gauge(f"{NS}_outlier_rows", "Number of OI outliers in latest run.")
DISCORD_MESSAGES_TOTAL = Counter(
    f"{NS}_discord_messages_total", "Total Discord messages sent."
)
SERVICE_UP = Gauge(f"{NS}_up", "1 if service loop running, else 0.")


# -----------------------
# DB helpers
# -----------------------

db = PolygonOptions()


async def ensure_connected() -> None:
    await db.connect()


async def fetch(sql: str) -> List[Any]:
    return await db.fetch(sql)


async def fetchval(sql: str, *args) -> Any:
    return await db.fetchval(sql, *args)


async def execute(sql: str, *args) -> None:
    await db.execute(sql, *args)


# -----------------------
# Error classification & retries
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
# Core job
# -----------------------

# Template with a placeholder for the deviation threshold
OI_QUERY_TEMPLATE = """
SELECT
    ticker,
    open_interest,
    avg_opt_oi_1mo,
    CASE
        WHEN avg_opt_oi_1mo = 0 THEN NULL
        ELSE ROUND((100.0 * (open_interest - avg_opt_oi_1mo) / avg_opt_oi_1mo)::numeric, 2)
    END AS oi_percent_deviation
FROM info
WHERE
    avg_opt_oi_1mo > 0
    AND (
        open_interest > avg_opt_oi_1mo * (1.0 + {th})  -- above avg by threshold
        OR
        open_interest < avg_opt_oi_1mo * (1.0 - {th})  -- below avg by threshold
    )
ORDER BY ABS(open_interest - avg_opt_oi_1mo) DESC;
"""


async def oi_outliers_once(cfg: Config) -> Dict[str, Any]:
    """
    One transactional refresh guarded by a tx-scoped advisory lock.
    Returns metrics dict.
    """
    metrics: Dict[str, Any] = {"path": "default"}

    await execute("BEGIN;")

    if cfg.search_path:
        await execute(f"SET LOCAL search_path = {cfg.search_path};")

    await execute(f"SET LOCAL statement_timeout = {cfg.statement_timeout_ms};")
    await execute(f"SET LOCAL lock_timeout = {cfg.lock_timeout_ms};")

    # tx-scoped lock (auto-released on COMMIT/ROLLBACK)
    got = await fetchval("SELECT pg_try_advisory_xact_lock($1);", cfg.lock_key)
    if not got:
        await execute("ROLLBACK;")
        metrics["skipped"] = True
        return metrics

    # Build SQL with inlined threshold (no params, so we don't break PolygonOptions.fetch_all)
    th_str = f"{cfg.oi_deviation_threshold:.6f}"
    query = OI_QUERY_TEMPLATE.replace("{th}", th_str)

    # Fetch outliers
    rows = await fetch(query)

    if rows:
        df = pd.DataFrame(
            rows,
            columns=["ticker", "oi", "avg_oi", "pct_deviation"],
        )
        metrics["outlier_rows"] = len(df)

        # Persist outliers (upsert) if there is data
        try:
            await db.batch_upsert_dataframe(
                df,
                table_name="oi_outliers",
                unique_columns=["ticker", "oi"],
            )
        except Exception as e:
            # Let this bubble up for retry; it's part of the DB job
            logger.exception("Error during batch_upsert_dataframe: %s", e)
            raise
    else:
        df = pd.DataFrame(columns=["ticker", "oi", "avg_oi", "pct_deviation"])
        metrics["outlier_rows"] = 0

    await execute("COMMIT;")

    # Discord notification (outside DB transaction)
    if df.empty:
        metrics["discord_sent"] = False
        return metrics

    webhook_url = cfg.webhook_url
    if not webhook_url:
        logger.warning(
            "No Discord webhook URL configured (OI_OUTLIERS_WEBHOOK_URL/oi_outliers). "
            "Skipping Discord notification."
        )
        metrics["discord_sent"] = False
        return metrics

    df_fmt = format_large_numbers_in_dataframe2(df)
    from tabulate import tabulate  # local import to match your original

    table = tabulate(
        df_fmt.values.tolist(),
        headers=list(df_fmt.columns),
        tablefmt="heavy_rounded",
        showindex=False,
    )

    embed = DiscordEmbed(
        title="OI Outliers",
        description=f"```py\n{table}```",
    )
    embed.add_embed_field(name="Info:", value="> Viewing OI Outliers.")
    embed.set_footer(text="OI Outliers")
    embed.set_timestamp()

    hook = AsyncDiscordWebhook(webhook_url)
    hook.add_embed(embed)
    await hook.execute()

    DISCORD_MESSAGES_TOTAL.inc()
    metrics["discord_sent"] = True

    return metrics


async def oi_outliers_with_retries(cfg: Config) -> Dict[str, Any]:
    attempt = 0
    while True:
        try:
            LAST_RUN_START_TS.set_to_current_time()
            t0 = time.perf_counter()
            metrics = await oi_outliers_once(cfg)
            duration = time.perf_counter() - t0
            LAST_RUN_END_TS.set_to_current_time()

            if metrics.get("skipped"):
                LOCK_SKIPS_TOTAL.inc()
                RUNS_TOTAL.labels(result="skipped", path=metrics.get("path", "default")).inc()
                logger.info("Run skipped: lock held by another worker.")
                return metrics

            RUN_DURATION.observe(duration)
            RUNS_TOTAL.labels(result="ok", path=metrics.get("path", "default")).inc()
            LAST_SUCCESS_TS.set_to_current_time()
            OUTLIER_ROWS.set(metrics.get("outlier_rows", 0))

            logger.info(
                "Run ok | duration=%.3fs | outlier_rows=%s discord_sent=%s",
                duration,
                metrics.get("outlier_rows", 0),
                metrics.get("discord_sent", False),
            )
            return metrics

        except Exception as e:
            LAST_RUN_END_TS.set_to_current_time()
            transient = is_transient_db_error(e)
            ERRORS_TOTAL.labels(type="transient" if transient else "permanent").inc()
            RUNS_TOTAL.labels(result="error", path="default").inc()

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
# Runner (anchored)
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
                    await oi_outliers_with_retries(self.cfg)
                except Exception as e:
                    logger.error("Unrecoverable run failure: %s", e)

                # anchor next start
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

    p = argparse.ArgumentParser(description="OI Outliers service")
    p.add_argument(
        "-i",
        "--interval-seconds",
        type=float,
        default=float(os.getenv("RUN_INTERVAL_SECONDS", "600")),
    )
    p.add_argument(
        "--lock-key",
        type=int,
        default=int(os.getenv("LOCK_KEY", "981276")),
    )
    p.add_argument(
        "--statement-timeout-ms",
        type=int,
        default=int(os.getenv("STATEMENT_TIMEOUT_MS", "10000")),
    )
    p.add_argument(
        "--lock-timeout-ms",
        type=int,
        default=int(os.getenv("LOCK_TIMEOUT_MS", "2000")),
    )
    p.add_argument(
        "--search-path",
        type=str,
        default=os.getenv("DB_SEARCH_PATH"),
    )

    p.add_argument(
        "--oi-deviation-threshold",
        type=float,
        default=float(os.getenv("OI_DEVIATION_THRESHOLD", "0.2")),
        help="Fractional deviation threshold (e.g., 0.2 = 20%%).",
    )
    p.add_argument(
        "--webhook-url",
        type=str,
        default=os.getenv("OI_OUTLIERS_WEBHOOK_URL") or os.getenv("oi_outliers"),
        help="Discord webhook URL for OI outliers.",
    )

    p.add_argument(
        "--http-host",
        type=str,
        default=os.getenv("HTTP_HOST", "0.0.0.0"),
    )
    p.add_argument(
        "--http-port",
        type=int,
        default=int(os.getenv("HTTP_PORT", "9110")),
    )
    p.add_argument(
        "--readiness-ttl-seconds",
        type=float,
        default=float(os.getenv("READINESS_TTL_SECONDS", "300")),
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
        oi_deviation_threshold=a.oi_deviation_threshold,
        webhook_url=a.webhook_url,
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
        "Starting OI Outliers service | interval=%.3fs lock_key=%s "
        "search_path=%s http=%s:%d readiness_ttl=%.1fs oi_deviation_threshold=%.3f",
        cfg.interval_seconds,
        cfg.lock_key,
        cfg.search_path,
        cfg.http_host,
        cfg.http_port,
        cfg.readiness_ttl_seconds,
        cfg.oi_deviation_threshold,
    )
    runner = Runner(cfg)
    await runner.run()


def main() -> None:
    cfg = parse_args()
    asyncio.run(_amain(cfg))


if __name__ == "__main__":
    main()
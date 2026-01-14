#!/usr/bin/env python3
"""
MACD consensus maintenance service (production-ready).

Maintains table `macd_consensus` with exactly one row per ticker **only if**
MACD sentiment is uniformly equal to `consensus_value` (default: 'bullish')
across the required timespans (default: 5min,15min,30min,1hr,2hr,4hr,day).

Features:
- Transaction-scoped advisory lock (no overlap, no stale locks)
- Anchored scheduler (exact interval between *starts*)
- Postgres 15+ MERGE or portable fallback (temp table + UPDATE/INSERT/DELETE)
- Per-run statement_timeout & lock_timeout (SET LOCAL)
- Exponential retries with jitter on transient DB errors
- Prometheus metrics on /metrics, liveness /healthz, readiness /ready
- Env/CLI configuration, clean shutdown

ENV (overridable by CLI):
  RUN_INTERVAL_SECONDS=60
  LOCK_KEY=981275
  STATEMENT_TIMEOUT_MS=10000
  LOCK_TIMEOUT_MS=2000
  USE_MERGE_IF_AVAILABLE=1
  DB_SEARCH_PATH=None   # e.g., "public,app"

  MACD_TIMESPANS="5min,15min,30min,1hr,2hr,4hr,day"
  MACD_CONSENSUS_VALUE="bullish"

  HTTP_HOST=0.0.0.0
  HTTP_PORT=9109
  READINESS_TTL_SECONDS=180

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
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

from aiohttp import web
from prometheus_client import (
    Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
)

# Your DB wrapper
from fudstop4.apis.polygonio.polygon_options import PolygonOptions


# -----------------------
# Config & Logging
# -----------------------

def _parse_timespans(s: str) -> List[str]:
    return [t.strip() for t in s.split(",") if t.strip()]

@dataclass
class Config:
    # Core scheduling/locking
    interval_seconds: float = float(os.getenv("RUN_INTERVAL_SECONDS", "60"))
    lock_key: int = int(os.getenv("LOCK_KEY", "981275"))
    statement_timeout_ms: int = int(os.getenv("STATEMENT_TIMEOUT_MS", "10000"))
    lock_timeout_ms: int = int(os.getenv("LOCK_TIMEOUT_MS", "2000"))
    use_merge_if_available: bool = os.getenv("USE_MERGE_IF_AVAILABLE", "1") != "0"
    search_path: Optional[str] = os.getenv("DB_SEARCH_PATH")

    # MACD logic
    macd_timespans: List[str] = field(
        default_factory=lambda: _parse_timespans(
            os.getenv("MACD_TIMESPANS", "5min,15min,30min,1hr,2hr,4hr,day")
        )
    )
    macd_consensus_value: str = os.getenv("MACD_CONSENSUS_VALUE", "bullish")

    # HTTP
    http_host: str = os.getenv("HTTP_HOST", "0.0.0.0")
    http_port: int = int(os.getenv("HTTP_PORT", "9109"))
    readiness_ttl_seconds: float = float(os.getenv("READINESS_TTL_SECONDS", "180"))

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

logger = logging.getLogger("macd_consensus_service")


# -----------------------
# Metrics
# -----------------------

NS = "macd_job"

RUNS_TOTAL = Counter(f"{NS}_runs_total", "Total runs executed.", ["result", "path"])
LOCK_SKIPS_TOTAL = Counter(f"{NS}_lock_skips_total", "Runs skipped due to advisory lock.")
ERRORS_TOTAL = Counter(f"{NS}_errors_total", "Errors by type.", ["type"])
RUN_DURATION = Histogram(f"{NS}_run_duration_seconds", "Run duration seconds.",
                         buckets=(0.05,0.1,0.2,0.5,1,2,5,10,30,60,120,300))
LAST_RUN_START_TS = Gauge(f"{NS}_last_run_start_timestamp", "Last run start ts.")
LAST_RUN_END_TS   = Gauge(f"{NS}_last_run_end_timestamp", "Last run end ts.")
LAST_SUCCESS_TS   = Gauge(f"{NS}_last_success_timestamp", "Last successful run ts.")
SOURCE_ROWS       = Gauge(f"{NS}_source_rows", "Consensus rows in source (tickers).")
ROWS_UPDATED      = Counter(f"{NS}_rows_updated_total", "Rows updated (fallback).")
ROWS_INSERTED     = Counter(f"{NS}_rows_inserted_total", "Rows inserted (fallback).")
ROWS_DELETED      = Counter(f"{NS}_rows_deleted_total", "Rows deleted (fallback).")
SERVICE_UP        = Gauge(f"{NS}_up", "1 if service loop running, else 0.")


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
# SQL builders (parameterized)
# -----------------------

def cte_consensus_sql() -> str:
    """
    Parameterized CTE for consensus:
      $1 -> text[] of timespans
      $2 -> consensus value (e.g., 'bullish')
    Produces CTEs: req, filtered, consensus
    """
    return """
WITH req(ts) AS (
  SELECT unnest($1::text[])
),
filtered AS (
  SELECT p.ticker, p.timespan, p.macd_sentiment
  FROM plays p
  JOIN req r ON p.timespan = r.ts
),
consensus AS (
  SELECT
    f.ticker,
    MIN(f.macd_sentiment) AS macd_sentiment
  FROM filtered f
  GROUP BY f.ticker
  HAVING
    COUNT(DISTINCT f.timespan) = (SELECT COUNT(*) FROM req)
    AND COUNT(DISTINCT f.macd_sentiment) = 1
    AND MIN(f.macd_sentiment) = $2
)
"""

def merge_sql() -> str:
    # WITH ... MERGE is valid in Postgres 15+
    return cte_consensus_sql() + """
MERGE INTO macd_consensus AS t
USING consensus AS s
  ON (t.ticker = s.ticker)
WHEN MATCHED THEN
  UPDATE SET macd_sentiment = s.macd_sentiment, updated_at = now()
WHEN NOT MATCHED THEN
  INSERT (ticker, macd_sentiment, updated_at)
  VALUES (s.ticker, s.macd_sentiment, now())
WHEN NOT MATCHED BY SOURCE THEN
  DELETE;
"""

def fallback_make_temp_source_sql() -> str:
    # IMPORTANT: WITH must appear after AS in CREATE TABLE ... AS
    return """
CREATE TEMP TABLE tmp_consensus
ON COMMIT DROP
AS
""" + cte_consensus_sql() + """
SELECT ticker, macd_sentiment
FROM consensus;
"""

def fallback_counts_sql() -> Dict[str, str]:
    return {
        "count_src": "SELECT COUNT(*) FROM tmp_consensus;",
        "update": """
WITH upd AS (
  UPDATE macd_consensus AS t
     SET macd_sentiment = s.macd_sentiment, updated_at = now()
    FROM tmp_consensus AS s
   WHERE t.ticker = s.ticker
     AND t.macd_sentiment IS DISTINCT FROM s.macd_sentiment
   RETURNING 1
)
SELECT COUNT(*) FROM upd;
""",
        "insert": """
WITH ins AS (
  INSERT INTO macd_consensus (ticker, macd_sentiment, updated_at)
  SELECT s.ticker, s.macd_sentiment, now()
    FROM tmp_consensus s
    LEFT JOIN macd_consensus t ON t.ticker = s.ticker
   WHERE t.ticker IS NULL
  RETURNING 1
)
SELECT COUNT(*) FROM ins;
""",
        "delete": """
WITH del AS (
  DELETE FROM macd_consensus t
   WHERE NOT EXISTS (
     SELECT 1 FROM tmp_consensus s WHERE s.ticker = t.ticker
   )
   RETURNING 1
)
SELECT COUNT(*) FROM del;
""",
    }


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
    hints = ("deadlock detected", "serialization failure", "could not serialize",
             "lock timeout", "canceling statement due to statement timeout",
             "too many connections", "cannot connect now", "connection reset")
    return any(h in msg for h in hints)

def backoff_delay(base: float, attempt: int, cap: float) -> float:
    exp = min(cap, base * (2 ** attempt))
    return random.uniform(0, exp)


# -----------------------
# Core transactional job
# -----------------------

async def server_version_num() -> Optional[int]:
    try:
        v = await fetchval("SHOW server_version_num;")
        return int(v) if v is not None else None
    except Exception:
        logger.warning("Could not determine server_version_num; defaulting to fallback.")
        return None

async def macd_consensus_once(cfg: Config) -> Dict[str, Any]:
    """
    One transactional refresh guarded by a tx-scoped advisory lock.
    Returns metrics dict.
    """
    metrics: Dict[str, Any] = {}

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

    # choose path (MERGE on PG15+)
    use_merge = False
    if cfg.use_merge_if_available:
        ver = await server_version_num()
        metrics["server_version_num"] = ver
        use_merge = ver is not None and ver >= 150000

    params = (cfg.macd_timespans, cfg.macd_consensus_value)

    if use_merge:
        await execute(merge_sql(), *params)
        metrics["path"] = "merge"
        src_count = await fetchval(cte_consensus_sql() + "SELECT COUNT(*) FROM consensus;", *params)
        metrics["source_rows"] = int(src_count or 0)
    else:
        # portable fallback with counts
        await execute(fallback_make_temp_source_sql(), *params)
        counts = fallback_counts_sql()
        src_count = await fetchval(counts["count_src"])
        upd_count = await fetchval(counts["update"])
        ins_count = await fetchval(counts["insert"])
        del_count = await fetchval(counts["delete"])
        metrics.update({
            "path": "fallback",
            "source_rows": int(src_count or 0),
            "updated": int(upd_count or 0),
            "inserted": int(ins_count or 0),
            "deleted": int(del_count or 0),
        })

    await execute("COMMIT;")
    return metrics

async def macd_consensus_with_retries(cfg: Config) -> Dict[str, Any]:
    attempt = 0
    while True:
        try:
            LAST_RUN_START_TS.set_to_current_time()
            t0 = time.perf_counter()
            metrics = await macd_consensus_once(cfg)
            duration = time.perf_counter() - t0
            LAST_RUN_END_TS.set_to_current_time()

            if metrics.get("skipped"):
                LOCK_SKIPS_TOTAL.inc()
                RUNS_TOTAL.labels(result="skipped", path=metrics.get("path","unknown")).inc()
                logger.info("Run skipped: lock held by another worker.")
                return metrics

            RUN_DURATION.observe(duration)
            RUNS_TOTAL.labels(result="ok", path=metrics.get("path","unknown")).inc()
            LAST_SUCCESS_TS.set_to_current_time()
            SOURCE_ROWS.set(metrics.get("source_rows", 0))

            if metrics.get("path") == "fallback":
                ROWS_UPDATED.inc(metrics.get("updated", 0))
                ROWS_INSERTED.inc(metrics.get("inserted", 0))
                ROWS_DELETED.inc(metrics.get("deleted", 0))

            logger.info("Run ok | duration=%.3fs | %s",
                        duration, ", ".join(f"{k}={v}" for k, v in metrics.items()))
            return metrics

        except Exception as e:
            LAST_RUN_END_TS.set_to_current_time()
            transient = is_transient_db_error(e)
            ERRORS_TOTAL.labels(type="transient" if transient else "permanent").inc()
            RUNS_TOTAL.labels(result="error", path="unknown").inc()

            attempt += 1
            if transient and attempt < cfg.retry_max_attempts:
                delay = backoff_delay(cfg.retry_base_delay, attempt, cfg.retry_max_delay)
                logger.warning("Run failed (attempt %d/%d, transient). Retrying in %.2fs. Error: %s",
                               attempt, cfg.retry_max_attempts, delay, e)
                try:
                    await execute("ROLLBACK;")
                except Exception:
                    pass
                await asyncio.sleep(delay)
                continue

            logger.exception("Run failed (attempt %d). No more retries. Error: %s", attempt, e)
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
        logger.info("HTTP server listening on http://%s:%d", self.cfg.http_host, self.cfg.http_port)

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
                    await macd_consensus_with_retries(self.cfg)
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
    p = argparse.ArgumentParser(description="MACD consensus service")
    p.add_argument("-i", "--interval-seconds", type=float, default=float(os.getenv("RUN_INTERVAL_SECONDS", "60")))
    p.add_argument("--lock-key", type=int, default=int(os.getenv("LOCK_KEY", "981275")))
    p.add_argument("--statement-timeout-ms", type=int, default=int(os.getenv("STATEMENT_TIMEOUT_MS", "10000")))
    p.add_argument("--lock-timeout-ms", type=int, default=int(os.getenv("LOCK_TIMEOUT_MS", "2000")))
    p.add_argument("--no-merge", action="store_true", help="Force fallback even on Postgres 15+.")
    p.add_argument("--search-path", type=str, default=os.getenv("DB_SEARCH_PATH"))

    p.add_argument("--timespans", type=str,
                   default=os.getenv("MACD_TIMESPANS", "5min,15min,30min,1hr,2hr,4hr,day"),
                   help="Comma-separated list of required timespans.")
    p.add_argument("--consensus-value", type=str,
                   default=os.getenv("MACD_CONSENSUS_VALUE", "bullish"),
                   help="The MACD sentiment that must be uniform across all timespans.")

    p.add_argument("--http-host", type=str, default=os.getenv("HTTP_HOST", "0.0.0.0"))
    p.add_argument("--http-port", type=int, default=int(os.getenv("HTTP_PORT", "9109")))
    p.add_argument("--readiness-ttl-seconds", type=float, default=float(os.getenv("READINESS_TTL_SECONDS", "180")))

    p.add_argument("--retry-max-attempts", type=int, default=int(os.getenv("RETRY_MAX_ATTEMPTS", "5")))
    p.add_argument("--retry-base-delay", type=float, default=float(os.getenv("RETRY_BASE_DELAY_SECONDS", "0.2")))
    p.add_argument("--retry-max-delay", type=float, default=float(os.getenv("RETRY_MAX_DELAY_SECONDS", "5.0")))

    p.add_argument("--log-level", type=str, default=os.getenv("LOG_LEVEL", "INFO"))

    a = p.parse_args(argv)
    return Config(
        interval_seconds=a.interval_seconds,
        lock_key=a.lock_key,
        statement_timeout_ms=a.statement_timeout_ms,
        lock_timeout_ms=a.lock_timeout_ms,
        use_merge_if_available=(not a.no_merge),
        search_path=a.search_path,
        macd_timespans=_parse_timespans(a.timespans),
        macd_consensus_value=a.consensus_value,
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
        "Starting MACD service | interval=%.3fs lock_key=%s merge=%s search_path=%s "
        "http=%s:%d readiness_ttl=%.1fs timespans=%s consensus=%s",
        cfg.interval_seconds, cfg.lock_key, cfg.use_merge_if_available, cfg.search_path,
        cfg.http_host, cfg.http_port, cfg.readiness_ttl_seconds,
        ",".join(cfg.macd_timespans), cfg.macd_consensus_value
    )
    runner = Runner(cfg)
    await runner.run()

def main() -> None:
    cfg = parse_args()
    asyncio.run(_amain(cfg))

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
RSI extremes maintenance service (10/10 productionized).

- Computes {lowest, highest} RSI per `timespan` from `plays`.
- Syncs into `rsi_conditions` (upsert + "delete rows not in source").
- Uses tx-scoped advisory locks to prevent overlap.
- Anchored schedule: exact interval between *starts* (no drift).
- Postgres 15+ `MERGE` or portable fallback (temp table + UPDATE/INSERT/DELETE).
- Per-run statement/lock timeouts.
- Exponential retry with jitter on transient DB errors.
- Prometheus metrics + health and readiness endpoints.

Environment variables (overridable by CLI):
  RUN_INTERVAL_SECONDS        float  default=60
  LOCK_KEY                    int    default=981274
  STATEMENT_TIMEOUT_MS        int    default=10000
  LOCK_TIMEOUT_MS             int    default=2000
  USE_MERGE_IF_AVAILABLE      0/1    default=1
  DB_SEARCH_PATH              str    default=None  (e.g., "public,app")

  # HTTP server (metrics/health)
  HTTP_HOST                   str    default="0.0.0.0"
  HTTP_PORT                   int    default=9108
  READINESS_TTL_SECONDS       float  default=180   (must have a success in this window)

  # Retries
  RETRY_MAX_ATTEMPTS          int    default=5
  RETRY_BASE_DELAY_SECONDS    float  default=0.2   (exponential backoff base)
  RETRY_MAX_DELAY_SECONDS     float  default=5.0

  LOG_LEVEL                   str    default="INFO"

Indexes you should create once (recommended):
  CREATE INDEX IF NOT EXISTS plays_timespan_rsi_ticker_idx ON plays (timespan, rsi, ticker);
  CREATE UNIQUE INDEX IF NOT EXISTS rsi_conditions_timespan_kind_udx ON rsi_conditions (timespan, kind);
"""

import os
import sys
import asyncio
import signal
import logging
import time
import random
from dataclasses import dataclass
from typing import Optional, Dict, Any

from aiohttp import web
from prometheus_client import (
    Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
)

# Your project DB wrapper
from fudstop4.apis.polygonio.polygon_options import PolygonOptions

# -----------------------
# Configuration & Logging
# -----------------------

@dataclass
class Config:
    # Core
    interval_seconds: float = float(os.getenv("RUN_INTERVAL_SECONDS", "60"))
    lock_key: int = int(os.getenv("LOCK_KEY", "981274"))
    statement_timeout_ms: int = int(os.getenv("STATEMENT_TIMEOUT_MS", "10000"))
    lock_timeout_ms: int = int(os.getenv("LOCK_TIMEOUT_MS", "2000"))
    use_merge_if_available: bool = os.getenv("USE_MERGE_IF_AVAILABLE", "1") != "0"
    search_path: Optional[str] = os.getenv("DB_SEARCH_PATH")

    # HTTP server for metrics/health
    http_host: str = os.getenv("HTTP_HOST", "0.0.0.0")
    http_port: int = int(os.getenv("HTTP_PORT", "9108"))
    readiness_ttl_seconds: float = float(os.getenv("READINESS_TTL_SECONDS", "180"))

    # Retry policy
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

logger = logging.getLogger("rsi_conditions_service")

# -----------------------
# Prometheus Metrics
# -----------------------

METRIC_NAMESPACE = "rsi_job"

RUNS_TOTAL = Counter(
    f"{METRIC_NAMESPACE}_runs_total",
    "Total runs executed (including retries).",
    ["result", "path"],  # result=ok|skipped|error, path=merge|fallback|unknown
)

LOCK_SKIPS_TOTAL = Counter(
    f"{METRIC_NAMESPACE}_lock_skips_total",
    "Total runs skipped because another worker held the tx advisory lock."
)

ERRORS_TOTAL = Counter(
    f"{METRIC_NAMESPACE}_errors_total",
    "Total errors by type.",
    ["type"],  # type=transient|permanent|unknown
)

RUN_DURATION = Histogram(
    f"{METRIC_NAMESPACE}_run_duration_seconds",
    "Duration of a single successful run in seconds.",
    buckets=(0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10, 30, 60, 120, 300),
)

LAST_RUN_START_TS = Gauge(
    f"{METRIC_NAMESPACE}_last_run_start_timestamp",
    "Unix timestamp of last run start."
)
LAST_RUN_END_TS = Gauge(
    f"{METRIC_NAMESPACE}_last_run_end_timestamp",
    "Unix timestamp of last run end."
)
LAST_SUCCESS_TS = Gauge(
    f"{METRIC_NAMESPACE}_last_success_timestamp",
    "Unix timestamp of last successful run."
)
SOURCE_ROWS = Gauge(
    f"{METRIC_NAMESPACE}_source_rows",
    "Rows produced by the extremes source on last run."
)
ROWS_UPDATED = Counter(
    f"{METRIC_NAMESPACE}_rows_updated_total",
    "Total rows updated in fallback path."
)
ROWS_INSERTED = Counter(
    f"{METRIC_NAMESPACE}_rows_inserted_total",
    "Total rows inserted in fallback path."
)
ROWS_DELETED = Counter(
    f"{METRIC_NAMESPACE}_rows_deleted_total",
    "Total rows deleted in fallback path."
)
SERVICE_UP = Gauge(
    f"{METRIC_NAMESPACE}_up",
    "1 if the service loop is running; 0 otherwise."
)


# -----------------------
# SQL builders
# -----------------------

def _extremes_cte() -> str:
    return """
WITH extremes AS (
  -- lowest per timespan
  SELECT timespan, 'lowest'::text AS kind, ticker, rsi
  FROM (
    SELECT
      timespan, ticker, rsi,
      ROW_NUMBER() OVER (PARTITION BY timespan ORDER BY rsi ASC, ticker ASC) rn
    FROM plays
  ) x
  WHERE rn = 1
  UNION ALL
  -- highest per timespan
  SELECT timespan, 'highest'::text AS kind, ticker, rsi
  FROM (
    SELECT
      timespan, ticker, rsi,
      ROW_NUMBER() OVER (PARTITION BY timespan ORDER BY rsi DESC, ticker ASC) rn
    FROM plays
  ) y
  WHERE rn = 1
)
"""

def merge_sql() -> str:
    return _extremes_cte() + """
MERGE INTO rsi_conditions AS t
USING extremes AS s
  ON (t.timespan = s.timespan AND t.kind = s.kind)
WHEN MATCHED THEN
  UPDATE SET ticker = s.ticker, rsi = s.rsi, updated_at = now()
WHEN NOT MATCHED THEN
  INSERT (timespan, kind, ticker, rsi, updated_at)
  VALUES (s.timespan, s.kind, s.ticker, s.rsi, now())
WHEN NOT MATCHED BY SOURCE THEN
  DELETE;
"""

def fallback_make_temp_source_sql() -> str:
    return """
CREATE TEMP TABLE tmp_extremes
ON COMMIT DROP
AS
""" + _extremes_cte() + """
SELECT timespan, kind, ticker, rsi
FROM extremes;
"""

def fallback_counts_sql() -> Dict[str, str]:
    return {
        "count_src": "SELECT COUNT(*) FROM tmp_extremes;",
        "update": """
WITH upd AS (
  UPDATE rsi_conditions AS t
     SET ticker = s.ticker, rsi = s.rsi, updated_at = now()
    FROM tmp_extremes AS s
   WHERE t.timespan = s.timespan
     AND t.kind     = s.kind
     AND (t.ticker IS DISTINCT FROM s.ticker OR t.rsi IS DISTINCT FROM s.rsi)
   RETURNING 1
)
SELECT COUNT(*) FROM upd;
""",
        "insert": """
WITH ins AS (
  INSERT INTO rsi_conditions (timespan, kind, ticker, rsi, updated_at)
  SELECT s.timespan, s.kind, s.ticker, s.rsi, now()
    FROM tmp_extremes s
    LEFT JOIN rsi_conditions t
      ON t.timespan = s.timespan AND t.kind = s.kind
   WHERE t.timespan IS NULL
  RETURNING 1
)
SELECT COUNT(*) FROM ins;
""",
        "delete": """
WITH del AS (
  DELETE FROM rsi_conditions t
   WHERE NOT EXISTS (
     SELECT 1 FROM tmp_extremes s
      WHERE s.timespan = t.timespan
        AND s.kind     = t.kind
   )
   RETURNING 1
)
SELECT COUNT(*) FROM del;
""",
    }

# -----------------------
# DB wrapper passthrough
# -----------------------

db = PolygonOptions()

async def ensure_connected() -> None:
    await db.connect()

async def fetchval(sql: str, *args) -> Any:
    return await db.fetchval(sql, *args)

async def execute(sql: str) -> None:
    await db.execute(sql)

# -----------------------
# Transient error classification & retry helpers
# -----------------------

# Common transient SQLSTATE codes
TRANSIENT_STATES = {
    "40001",  # serialization_failure
    "40P01",  # deadlock_detected
    "55P03",  # lock_not_available
    "57014",  # query_canceled (e.g., statement_timeout)
    "53300",  # too_many_connections
    "57P01",  # admin_shutdown
    "57P02",  # crash_shutdown
    "57P03",  # cannot_connect_now
}

def _get_sqlstate(exc: Exception) -> Optional[str]:
    # asyncpg exceptions usually expose .sqlstate; generic exceptions may not.
    state = getattr(exc, "sqlstate", None)
    if state:
        return str(state)
    # Some wrappers include code in args or message; very conservative heuristics:
    msg = str(exc) or ""
    for code in TRANSIENT_STATES:
        if code in msg:
            return code
    return None

def is_transient_db_error(exc: Exception) -> bool:
    state = _get_sqlstate(exc)
    if state and state in TRANSIENT_STATES:
        return True
    # Message-based fallback (last resort)
    msg = str(exc).lower()
    hints = ("deadlock detected", "serialization failure", "could not serialize",
             "lock timeout", "canceling statement due to statement timeout",
             "too many connections", "cannot connect now", "connection reset")
    return any(h in msg for h in hints)

def backoff_delay(base: float, attempt: int, cap: float) -> float:
    # Exponential backoff with jitter (Full Jitter)
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
        logger.warning("Could not determine server_version_num; defaulting to fallback path.")
        return None

async def rsi_conditions_once(cfg: Config) -> Dict[str, Any]:
    """
    One transactional run guarded by pg_try_advisory_xact_lock.
    Returns metrics dict.
    """
    metrics: Dict[str, Any] = {}

    await execute("BEGIN;")

    if cfg.search_path:
        await execute(f"SET LOCAL search_path = {cfg.search_path};")

    await execute(f"SET LOCAL statement_timeout = {cfg.statement_timeout_ms};")
    await execute(f"SET LOCAL lock_timeout = {cfg.lock_timeout_ms};")

    got = await fetchval("SELECT pg_try_advisory_xact_lock($1);", cfg.lock_key)
    if not got:
        await execute("ROLLBACK;")
        metrics["skipped"] = True
        return metrics

    use_merge = False
    if cfg.use_merge_if_available:
        ver = await server_version_num()
        metrics["server_version_num"] = ver
        use_merge = ver is not None and ver >= 150000

    if use_merge:
        await execute(merge_sql())
        metrics["path"] = "merge"
        src_count = await fetchval(_extremes_cte() + "SELECT COUNT(*) FROM extremes;")
        metrics["source_rows"] = int(src_count or 0)
    else:
        await execute(fallback_make_temp_source_sql())
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

async def rsi_conditions_with_retries(cfg: Config) -> Dict[str, Any]:
    """
    Runs rsi_conditions_once with exponential backoff on transient errors.
    Returns metrics for the final outcome (or raises after exhausting retries).
    """
    attempt = 0
    while True:
        try:
            LAST_RUN_START_TS.set_to_current_time()
            t0 = time.perf_counter()
            metrics = await rsi_conditions_once(cfg)
            duration = time.perf_counter() - t0
            LAST_RUN_END_TS.set_to_current_time()

            if metrics.get("skipped"):
                LOCK_SKIPS_TOTAL.inc()
                RUNS_TOTAL.labels(result="skipped", path=metrics.get("path", "unknown")).inc()
                logger.info("Run skipped: lock held by another worker.")
                return metrics

            # Success
            RUN_DURATION.observe(duration)
            RUNS_TOTAL.labels(result="ok", path=metrics.get("path", "unknown")).inc()
            LAST_SUCCESS_TS.set_to_current_time()
            SOURCE_ROWS.set(metrics.get("source_rows", 0))

            # Row counters for fallback path
            if metrics.get("path") == "fallback":
                ROWS_UPDATED.inc(metrics.get("updated", 0))
                ROWS_INSERTED.inc(metrics.get("inserted", 0))
                ROWS_DELETED.inc(metrics.get("deleted", 0))

            logger.info(
                "Run ok | duration=%.3fs | %s",
                duration,
                ", ".join(f"{k}={v}" for k, v in metrics.items())
            )
            return metrics

        except Exception as e:
            LAST_RUN_END_TS.set_to_current_time()
            transient = is_transient_db_error(e)
            err_type = "transient" if transient else "permanent"
            ERRORS_TOTAL.labels(type=err_type).inc()
            RUNS_TOTAL.labels(result="error", path="unknown").inc()

            attempt += 1
            if transient and attempt < cfg.retry_max_attempts:
                delay = backoff_delay(cfg.retry_base_delay, attempt, cfg.retry_max_delay)
                logger.warning(
                    "Run failed (attempt %d/%d, transient). Retrying in %.2fs. Error: %s",
                    attempt, cfg.retry_max_attempts, delay, e
                )
                # Defensive rollback in case the TX is still open:
                try:
                    await execute("ROLLBACK;")
                except Exception:
                    pass
                await asyncio.sleep(delay)
                continue

            # permanent or exhausted
            logger.exception("Run failed (attempt %d). No more retries. Error: %s", attempt, e)
            # Defensive rollback:
            try:
                await execute("ROLLBACK;")
            except Exception:
                pass
            raise

# -----------------------
# HTTP: /healthz, /ready, /metrics
# -----------------------

class HealthServer:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self._app = web.Application()
        self._runner: Optional[web.AppRunner] = None
        self._site: Optional[web.TCPSite] = None
        self._setup_routes()

    def _setup_routes(self) -> None:
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
        # Basic liveness: service loop running if SERVICE_UP == 1
        status = "ok" if SERVICE_UP._value.get() == 1.0 else "stopped"
        payload = {
            "status": status,
            "last_success_ts": LAST_SUCCESS_TS._value.get(),
            "last_run_start_ts": LAST_RUN_START_TS._value.get(),
            "last_run_end_ts": LAST_RUN_END_TS._value.get(),
        }
        return web.json_response(payload, status=200 if status == "ok" else 503)

    async def ready(self, request: web.Request) -> web.Response:
        # Readiness: success within ttl window
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
    def __init__(self, cfg: Config) -> None:
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
                    await rsi_conditions_with_retries(self.cfg)
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
    p = argparse.ArgumentParser(description="RSI extremes synchronizer (10/10)")
    p.add_argument("-i", "--interval-seconds", type=float, default=float(os.getenv("RUN_INTERVAL_SECONDS", "60")))
    p.add_argument("--lock-key", type=int, default=int(os.getenv("LOCK_KEY", "981274")))
    p.add_argument("--statement-timeout-ms", type=int, default=int(os.getenv("STATEMENT_TIMEOUT_MS", "10000")))
    p.add_argument("--lock-timeout-ms", type=int, default=int(os.getenv("LOCK_TIMEOUT_MS", "2000")))
    p.add_argument("--no-merge", action="store_true", help="Force fallback path even on Postgres 15+.")
    p.add_argument("--search-path", type=str, default=os.getenv("DB_SEARCH_PATH"))

    p.add_argument("--http-host", type=str, default=os.getenv("HTTP_HOST", "0.0.0.0"))
    p.add_argument("--http-port", type=int, default=int(os.getenv("HTTP_PORT", "9108")))
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
        "Starting service | interval=%.3fs lock_key=%s merge=%s search_path=%s http=%s:%d readiness_ttl=%.1fs",
        cfg.interval_seconds, cfg.lock_key, cfg.use_merge_if_available,
        cfg.search_path, cfg.http_host, cfg.http_port, cfg.readiness_ttl_seconds
    )
    runner = Runner(cfg)
    await runner.run()

def main() -> None:
    cfg = parse_args()
    asyncio.run(_amain(cfg))

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
IV Skew maintenance service (production-ready).

Calculates robust skew metrics per (ticker, expiry) for the next N expiries:
- slope        : regr_slope(iv, ln(strike/close))  [skew proxy]
- iv_atm       : IV at strike closest to spot
- iv_lo/iv_hi  : avg IV in moneyness buckets (<= 1 - band, >= 1 + band)
- rr_approx    : iv_hi - iv_lo  [rough risk reversal]
- skew_type    : put_skew / call_skew / flat (by slope sign)
- counts       : n_total, n_lo, n_hi
Then MERGE (PG15+) or fallback (temp table + UPDATE/INSERT/DELETE) into iv_skew.

Service features:
- Tx-scoped advisory lock (pg_try_advisory_xact_lock) to prevent overlap
- Anchored scheduler (exact interval between *starts*)
- Per-run statement_timeout & lock_timeout (SET LOCAL)
- Exponential retries with jitter on transient DB errors
- Prometheus endpoints: /metrics, /healthz, /ready
- Env/CLI config; optional history capture

ENV (CLI can override):
  TABLE_NAME=iv_skew
  RUN_INTERVAL_SECONDS=60
  LOCK_KEY=981276
  STATEMENT_TIMEOUT_MS=10000
  LOCK_TIMEOUT_MS=2000
  USE_MERGE_IF_AVAILABLE=1
  DB_SEARCH_PATH=<optional schemas>

  IVSKEW_NEXT_EXPIRIES=2
  IVSKEW_BAND_PCT=0.10
  IVSKEW_MIN_POINTS=6
  HISTORY_ENABLED=0
  HISTORY_TABLE=iv_skew_history

  HTTP_HOST=0.0.0.0
  HTTP_PORT=9111
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
from dataclasses import dataclass
from typing import Optional, Dict, Any

from aiohttp import web
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST

from fudstop4.apis.polygonio.polygon_options import PolygonOptions

# -----------------------
# Config & logging
# -----------------------

@dataclass
class Config:
    table_name: str = os.getenv("TABLE_NAME", "iv_skew")

    interval_seconds: float = float(os.getenv("RUN_INTERVAL_SECONDS", "60"))
    lock_key: int = int(os.getenv("LOCK_KEY", "981276"))
    statement_timeout_ms: int = int(os.getenv("STATEMENT_TIMEOUT_MS", "10000"))
    lock_timeout_ms: int = int(os.getenv("LOCK_TIMEOUT_MS", "2000"))
    use_merge_if_available: bool = os.getenv("USE_MERGE_IF_AVAILABLE", "1") != "0"
    search_path: Optional[str] = os.getenv("DB_SEARCH_PATH")

    next_expiries: int = int(os.getenv("IVSKEW_NEXT_EXPIRIES", "2"))
    band_pct: float = float(os.getenv("IVSKEW_BAND_PCT", "0.10"))
    min_points: int = int(os.getenv("IVSKEW_MIN_POINTS", "6"))

    history_enabled: bool = os.getenv("HISTORY_ENABLED", "0") == "1"
    history_table: str = os.getenv("HISTORY_TABLE", "iv_skew_history")

    http_host: str = os.getenv("HTTP_HOST", "0.0.0.0")
    http_port: int = int(os.getenv("HTTP_PORT", "9111"))
    readiness_ttl_seconds: float = float(os.getenv("READINESS_TTL_SECONDS", "180"))

    retry_max_attempts: int = int(os.getenv("RETRY_MAX_ATTEMPTS", "5"))
    retry_base_delay: float = float(os.getenv("RETRY_BASE_DELAY_SECONDS", "0.2"))
    retry_max_delay: float = float(os.getenv("RETRY_MAX_DELAY_SECONDS", "5.0"))

    log_level: str = os.getenv("LOG_LEVEL", "INFO")


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        stream=sys.stdout,
    )

logger = logging.getLogger("iv_skew_service")

# -----------------------
# Metrics
# -----------------------

NS = "ivskew_job"

RUNS_TOTAL = Counter(f"{NS}_runs_total", "Total runs executed.", ["result", "path"])
LOCK_SKIPS_TOTAL = Counter(f"{NS}_lock_skips_total", "Runs skipped due to advisory lock.")
ERRORS_TOTAL = Counter(f"{NS}_errors_total", "Errors by type.", ["type"])
RUN_DURATION = Histogram(
    f"{NS}_run_duration_seconds", "Duration of successful runs (seconds).",
    buckets=(0.05,0.1,0.2,0.5,1,2,5,10,30,60,120,300)
)
LAST_RUN_START_TS = Gauge(f"{NS}_last_run_start_timestamp", "Last run start ts.")
LAST_RUN_END_TS   = Gauge(f"{NS}_last_run_end_timestamp", "Last run end ts.")
LAST_SUCCESS_TS   = Gauge(f"{NS}_last_success_timestamp", "Last successful run ts.")
SOURCE_ROWS       = Gauge(f"{NS}_source_rows", "Rows in source (tickers×expiries).")
ROWS_UPDATED      = Counter(f"{NS}_rows_updated_total", "Rows updated (fallback).")
ROWS_INSERTED     = Counter(f"{NS}_rows_inserted_total", "Rows inserted (fallback).")
ROWS_DELETED      = Counter(f"{NS}_rows_deleted_total", "Rows deleted (fallback).")
SERVICE_UP        = Gauge(f"{NS}_up", "1 if the service loop is running; 0 otherwise.")

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
# SQL builders
# -----------------------

def _source_select_sql(table_name: str) -> str:
    """
    Returns a SELECT ... that produces the rows to sync into {table_name}.
    Parameters (bind order): $1 = next_expiries (int), $2 = band_pct (float), $3 = min_points (int)
    """
    return f"""
WITH base AS (
  SELECT w.ticker, w.expiry, w.strike, w.iv, mq.close
  FROM wb_opts w
  JOIN (
    SELECT DISTINCT ON (ticker) ticker, close
    FROM multi_quote
    ORDER BY ticker, insertion_timestamp DESC
  ) mq ON mq.ticker = w.ticker
  WHERE w.expiry >= CURRENT_DATE
    AND w.iv IS NOT NULL
),
nextn AS (
  SELECT ticker, expiry,
         ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY expiry) AS rn_exp
  FROM (SELECT DISTINCT ticker, expiry FROM base) d
),
filtered AS (
  SELECT b.*,
         (b.strike / b.close) AS m,
         LN(b.strike / b.close) AS lm
  FROM base b
  JOIN nextn n
    ON n.ticker = b.ticker AND n.expiry = b.expiry
  WHERE n.rn_exp <= $1
),
atm_pick AS (
  SELECT *, ROW_NUMBER() OVER (
           PARTITION BY ticker, expiry
           ORDER BY ABS(m - 1.0), ABS(strike - close)
         ) AS rn
  FROM filtered
),
iv_atm AS (
  SELECT ticker, expiry, iv AS iv_atm
  FROM atm_pick
  WHERE rn = 1
),
lo AS (
  SELECT ticker, expiry, AVG(iv) AS iv_lo, COUNT(*) AS n_lo
  FROM filtered
  WHERE m <= (1.0 - $2)
  GROUP BY ticker, expiry
),
hi AS (
  SELECT ticker, expiry, AVG(iv) AS iv_hi, COUNT(*) AS n_hi
  FROM filtered
  WHERE m >= (1.0 + $2)
  GROUP BY ticker, expiry
),
slope AS (
  SELECT ticker, expiry, REGR_SLOPE(iv, lm) AS slope, COUNT(*) AS n_total
  FROM filtered
  GROUP BY ticker, expiry
),
joined AS (
  SELECT
    s.ticker,
    s.expiry,
    MAX(f.close) AS close,
    s.slope,
    s.n_total,
    a.iv_atm,
    l.iv_lo, l.n_lo,
    h.iv_hi, h.n_hi,
    (h.iv_hi - l.iv_lo) AS rr_approx
  FROM slope s
  JOIN (SELECT DISTINCT ticker, expiry, close FROM filtered) f
    ON f.ticker = s.ticker AND f.expiry = s.expiry
  LEFT JOIN iv_atm a ON a.ticker = s.ticker AND a.expiry = s.expiry
  LEFT JOIN lo l     ON l.ticker = s.ticker AND l.expiry = s.expiry
  LEFT JOIN hi h     ON h.ticker = s.ticker AND h.expiry = s.expiry
  GROUP BY s.ticker, s.expiry, s.slope, s.n_total, a.iv_atm, l.iv_lo, l.n_lo, h.iv_hi, h.n_hi
)
SELECT
  j.ticker,
  j.expiry,
  j.close,
  j.iv_atm,
  j.iv_lo,
  j.iv_hi,
  j.rr_approx,
  j.slope,
  CASE
    WHEN j.slope IS NULL THEN 'flat'
    WHEN j.slope < 0 THEN 'put_skew'
    WHEN j.slope > 0 THEN 'call_skew'
    ELSE 'flat'
  END AS skew_type,
  j.n_total,
  j.n_lo,
  j.n_hi,
  $2::double precision AS band,
  $1::integer AS expiries_considered,
  now() AS updated_at
FROM joined j
WHERE j.n_total >= $3
ORDER BY j.ticker, j.expiry
"""

def merge_sql(table_name: str) -> str:
    return f"""
WITH src AS (
{_source_select_sql(table_name)}
)
MERGE INTO {table_name} AS t
USING src AS s
  ON (t.ticker = s.ticker AND t.expiry = s.expiry)
WHEN MATCHED THEN UPDATE SET
  close = s.close,
  iv_atm = s.iv_atm,
  iv_lo = s.iv_lo,
  iv_hi = s.iv_hi,
  rr_approx = s.rr_approx,
  slope = s.slope,
  skew_type = s.skew_type,
  n_total = s.n_total,
  n_lo = s.n_lo,
  n_hi = s.n_hi,
  band = s.band,
  expiries_considered = s.expiries_considered,
  updated_at = s.updated_at
WHEN NOT MATCHED THEN
  INSERT (ticker, expiry, close, iv_atm, iv_lo, iv_hi, rr_approx, slope, skew_type,
          n_total, n_lo, n_hi, band, expiries_considered, updated_at)
  VALUES (s.ticker, s.expiry, s.close, s.iv_atm, s.iv_lo, s.iv_hi, s.rr_approx, s.slope, s.skew_type,
          s.n_total, s.n_lo, s.n_hi, s.band, s.expiries_considered, s.updated_at)
WHEN NOT MATCHED BY SOURCE THEN
  DELETE;
"""

def fallback_make_temp_source_sql(table_name: str) -> str:
    return f"""
CREATE TEMP TABLE tmp_ivskew_src
ON COMMIT DROP
AS
{_source_select_sql(table_name)}
"""

def fallback_counts_sql(table_name: str) -> Dict[str, str]:
    return {
        "count_src": "SELECT COUNT(*) FROM tmp_ivskew_src;",
        "update": f"""
WITH upd AS (
  UPDATE {table_name} AS t
     SET close = s.close,
         iv_atm = s.iv_atm,
         iv_lo = s.iv_lo,
         iv_hi = s.iv_hi,
         rr_approx = s.rr_approx,
         slope = s.slope,
         skew_type = s.skew_type,
         n_total = s.n_total,
         n_lo = s.n_lo,
         n_hi = s.n_hi,
         band = s.band,
         expiries_considered = s.expiries_considered,
         updated_at = s.updated_at
    FROM tmp_ivskew_src AS s
   WHERE t.ticker = s.ticker
     AND t.expiry = s.expiry
     AND (
           t.close IS DISTINCT FROM s.close OR
           t.iv_atm IS DISTINCT FROM s.iv_atm OR
           t.iv_lo IS DISTINCT FROM s.iv_lo OR
           t.iv_hi IS DISTINCT FROM s.iv_hi OR
           t.rr_approx IS DISTINCT FROM s.rr_approx OR
           t.slope IS DISTINCT FROM s.slope OR
           t.skew_type IS DISTINCT FROM s.skew_type OR
           t.n_total IS DISTINCT FROM s.n_total OR
           t.n_lo IS DISTINCT FROM s.n_lo OR
           t.n_hi IS DISTINCT FROM s.n_hi OR
           t.band IS DISTINCT FROM s.band OR
           t.expiries_considered IS DISTINCT FROM s.expiries_considered
         )
   RETURNING 1
)
SELECT COUNT(*) FROM upd;
""",
        "insert": f"""
WITH ins AS (
  INSERT INTO {table_name} (
    ticker, expiry, close, iv_atm, iv_lo, iv_hi, rr_approx, slope, skew_type,
    n_total, n_lo, n_hi, band, expiries_considered, updated_at
  )
  SELECT s.ticker, s.expiry, s.close, s.iv_atm, s.iv_lo, s.iv_hi, s.rr_approx, s.slope, s.skew_type,
         s.n_total, s.n_lo, s.n_hi, s.band, s.expiries_considered, s.updated_at
  FROM tmp_ivskew_src s
  LEFT JOIN {table_name} t ON t.ticker = s.ticker AND t.expiry = s.expiry
  WHERE t.ticker IS NULL
  RETURNING 1
)
SELECT COUNT(*) FROM ins;
""",
        "delete": f"""
WITH del AS (
  DELETE FROM {table_name} t
  WHERE NOT EXISTS (
    SELECT 1 FROM tmp_ivskew_src s
    WHERE s.ticker = t.ticker AND s.expiry = t.expiry
  )
  RETURNING 1
)
SELECT COUNT(*) FROM del;
""",
    }

def history_insert_sql(history_table: str, table_name: str) -> str:
    # Rebuild src, then append to history. Safe to run in same TX.
    return f"""
WITH src AS (
{_source_select_sql(table_name)}
)
INSERT INTO {history_table} (
  observed_at, ticker, expiry, close, iv_atm, iv_lo, iv_hi, rr_approx, slope,
  skew_type, n_total, n_lo, n_hi, band, expiries_considered
)
SELECT now(), ticker, expiry, close, iv_atm, iv_lo, iv_hi, rr_approx, slope,
       skew_type, n_total, n_lo, n_hi, band, expiries_considered
FROM src;
"""

# -----------------------
# Retry helpers
# -----------------------

TRANSIENT_STATES = {"40001","40P01","55P03","57014","53300","57P01","57P02","57P03"}

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
    m = (str(exc) or "").lower()
    hints = ("deadlock detected","serialization failure","could not serialize",
             "lock timeout","canceling statement due to statement timeout",
             "too many connections","cannot connect now","connection reset")
    return any(h in m for h in hints)

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

async def iv_skew_once(cfg: Config) -> Dict[str, Any]:
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

    ver = await server_version_num() if cfg.use_merge_if_available else None
    use_merge = ver is not None and ver >= 150000

    params = (cfg.next_expiries, cfg.band_pct, cfg.min_points)

    if use_merge:
        await execute(merge_sql(cfg.table_name), *params)
        metrics["path"] = "merge"
        src_count = await fetchval(f"WITH src AS ({_source_select_sql(cfg.table_name)}) SELECT COUNT(*) FROM src;", *params)
        metrics["source_rows"] = int(src_count or 0)

        if cfg.history_enabled:
            await execute(history_insert_sql(cfg.history_table, cfg.table_name), *params)
    else:
        await execute(fallback_make_temp_source_sql(cfg.table_name), *params)
        c = fallback_counts_sql(cfg.table_name)
        src_count = await fetchval(c["count_src"])
        upd_count = await fetchval(c["update"])
        ins_count = await fetchval(c["insert"])
        del_count = await fetchval(c["delete"])
        metrics.update({
            "path": "fallback",
            "source_rows": int(src_count or 0),
            "updated": int(upd_count or 0),
            "inserted": int(ins_count or 0),
            "deleted": int(del_count or 0),
        })

        if cfg.history_enabled:
            await execute(f"""
                INSERT INTO {cfg.history_table} (
                  observed_at, ticker, expiry, close, iv_atm, iv_lo, iv_hi,
                  rr_approx, slope, skew_type, n_total, n_lo, n_hi, band, expiries_considered
                )
                SELECT now(), ticker, expiry, close, iv_atm, iv_lo, iv_hi,
                       rr_approx, slope, skew_type, n_total, n_lo, n_hi, band, expiries_considered
                FROM tmp_ivskew_src;
            """)

    await execute("COMMIT;")
    return metrics

async def iv_skew_with_retries(cfg: Config) -> Dict[str, Any]:
    attempt = 0
    while True:
        try:
            LAST_RUN_START_TS.set_to_current_time()
            t0 = time.perf_counter()
            metrics = await iv_skew_once(cfg)
            duration = time.perf_counter() - t0
            LAST_RUN_END_TS.set_to_current_time()

            if metrics.get("skipped"):
                LOCK_SKIPS_TOTAL.inc()
                RUNS_TOTAL.labels(result="skipped", path=metrics.get("path","unknown")).inc()
                logger.info("Run skipped: lock held elsewhere.")
                return metrics

            RUN_DURATION.observe(duration)
            RUNS_TOTAL.labels(result="ok", path=metrics.get("path","unknown")).inc()
            LAST_SUCCESS_TS.set_to_current_time()
            SOURCE_ROWS.set(metrics.get("source_rows", 0))

            if metrics.get("path") == "fallback":
                ROWS_UPDATED.inc(metrics.get("updated", 0))
                ROWS_INSERTED.inc(metrics.get("inserted", 0))
                ROWS_DELETED.inc(metrics.get("deleted", 0))

            logger.info("Run ok | duration=%.3fs | %s", duration, ", ".join(f"{k}={v}" for k, v in metrics.items()))
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
        target_next = time.perf_counter()

        try:
            while not self._stop.is_set():
                now = time.perf_counter()
                if now < target_next:
                    try:
                        await asyncio.wait_for(self._stop.wait(), timeout=target_next - now)
                        break
                    except asyncio.TimeoutError:
                        pass

                try:
                    await iv_skew_with_retries(self.cfg)
                except Exception as e:
                    logger.error("Unrecoverable run failure: %s", e)

                target_next += interval
                now = time.perf_counter()
                while target_next <= now:
                    target_next += interval
        finally:
            SERVICE_UP.set(0)
            await self._http.stop()
            logger.info("Runner stopped.")

# -----------------------
# CLI / entrypoint
# -----------------------

def parse_args(argv: Optional[list] = None) -> Config:
    import argparse
    p = argparse.ArgumentParser(description="IV Skew service (production-ready)")
    p.add_argument("--table-name", type=str, default=os.getenv("TABLE_NAME", "iv_skew"))
    p.add_argument("-i", "--interval-seconds", type=float, default=float(os.getenv("RUN_INTERVAL_SECONDS", "60")))
    p.add_argument("--lock-key", type=int, default=int(os.getenv("LOCK_KEY", "981276")))
    p.add_argument("--statement-timeout-ms", type=int, default=int(os.getenv("STATEMENT_TIMEOUT_MS", "10000")))
    p.add_argument("--lock-timeout-ms", type=int, default=int(os.getenv("LOCK_TIMEOUT_MS", "2000")))
    p.add_argument("--no-merge", action="store_true")
    p.add_argument("--search-path", type=str, default=os.getenv("DB_SEARCH_PATH"))

    p.add_argument("--next-expiries", type=int, default=int(os.getenv("IVSKEW_NEXT_EXPIRIES", "2")))
    p.add_argument("--band-pct", type=float, default=float(os.getenv("IVSKEW_BAND_PCT", "0.10")))
    p.add_argument("--min-points", type=int, default=int(os.getenv("IVSKEW_MIN_POINTS", "6")))
    p.add_argument("--history-enabled", action="store_true" if os.getenv("HISTORY_ENABLED","0")=="1" else "store_false")
    p.add_argument("--history-table", type=str, default=os.getenv("HISTORY_TABLE", "iv_skew_history"))

    p.add_argument("--http-host", type=str, default=os.getenv("HTTP_HOST", "0.0.0.0"))
    p.add_argument("--http-port", type=int, default=int(os.getenv("HTTP_PORT", "9111")))
    p.add_argument("--readiness-ttl-seconds", type=float, default=float(os.getenv("READINESS_TTL_SECONDS", "180")))

    p.add_argument("--retry-max-attempts", type=int, default=int(os.getenv("RETRY_MAX_ATTEMPTS", "5")))
    p.add_argument("--retry-base-delay", type=float, default=float(os.getenv("RETRY_BASE_DELAY_SECONDS", "0.2")))
    p.add_argument("--retry-max-delay", type=float, default=float(os.getenv("RETRY_MAX_DELAY_SECONDS", "5.0")))

    p.add_argument("--log-level", type=str, default=os.getenv("LOG_LEVEL", "INFO"))

    a = p.parse_args(argv)
    return Config(
        table_name=a.table_name,
        interval_seconds=a.interval_seconds,
        lock_key=a.lock_key,
        statement_timeout_ms=a.statement_timeout_ms,
        lock_timeout_ms=a.lock_timeout_ms,
        use_merge_if_available=(not a.no_merge),
        search_path=a.search_path,
        next_expiries=a.next_expiries,
        band_pct=a.band_pct,
        min_points=a.min_points,
        history_enabled=a.history_enabled,
        history_table=a.history_table,
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
        "Starting IV Skew service | table=%s interval=%.3fs expiries=%d band=%.3f min_pts=%d "
        "lock_key=%s merge=%s http=%s:%d readiness_ttl=%.1fs",
        cfg.table_name, cfg.interval_seconds, cfg.next_expiries, cfg.band_pct, cfg.min_points,
        cfg.lock_key, cfg.use_merge_if_available, cfg.http_host, cfg.http_port, cfg.readiness_ttl_seconds
    )
    runner = Runner(cfg)
    await runner.run()

def main() -> None:
    cfg = parse_args()
    asyncio.run(_amain(cfg))

if __name__ == "__main__":
    main()

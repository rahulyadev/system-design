#!/usr/bin/env python3
"""Deterministic reference benchmark for SD-BEG-110-T01.

This is a learning measurement, not a production capacity benchmark. It uses
persistent sequential clients, checks exact payload correctness, and reports
distributions without asserting that one product must always be faster.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import math
import os
import statistics
import time
from collections.abc import Callable
from typing import Any

import psycopg
import redis


TASK_ID = "SD-BEG-110-T01"
KEY_PREFIX = "sd-beg-110:t01:"
KEY = f"{KEY_PREFIX}profile:42"
TABLE = "public.cache_benchmark"
PAYLOAD = json.dumps(
    {
        "id": 42,
        "name": "synthetic-profile",
        "region": "local-lab",
        "roles": ["reader", "learner"],
        "bio": "x" * 160,
    },
    separators=(",", ":"),
    sort_keys=True,
)


def require_local_scope() -> dict[str, object]:
    settings: dict[str, object] = {
        "redis_host": os.environ.get("REDIS_HOST", "127.0.0.1"),
        "redis_port": int(os.environ.get("REDIS_PORT", "55110")),
        "postgres_host": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "postgres_port": int(os.environ.get("POSTGRES_PORT", "55111")),
        "postgres_db": os.environ.get("POSTGRES_DB", "sd_beg_110_t01"),
        "postgres_user": os.environ.get("POSTGRES_USER", "benchmark"),
        "postgres_password": os.environ.get(
            "POSTGRES_PASSWORD", "sd_beg_110_t01_postgres_local"
        ),
    }
    if settings["redis_host"] not in {"127.0.0.1", "localhost"}:
        raise RuntimeError(f"refusing non-loopback Redis host: {settings['redis_host']}")
    if settings["postgres_host"] not in {"127.0.0.1", "localhost"}:
        raise RuntimeError(
            f"refusing non-loopback PostgreSQL host: {settings['postgres_host']}"
        )
    if settings["redis_port"] != 55110 or settings["postgres_port"] != 55111:
        raise RuntimeError(f"refusing unexpected task ports: {settings}")
    if settings["postgres_db"] != "sd_beg_110_t01":
        raise RuntimeError(f"refusing unexpected database: {settings['postgres_db']}")
    if settings["postgres_user"] != "benchmark":
        raise RuntimeError(f"refusing unexpected PostgreSQL user: {settings['postgres_user']}")
    return settings


def percentile(ordered: list[float], fraction: float) -> float:
    index = max(0, min(len(ordered) - 1, math.ceil(len(ordered) * fraction) - 1))
    return ordered[index]


def summarize(samples_us: list[float]) -> dict[str, float | int]:
    if not samples_us:
        raise ValueError("latency sample list is empty")
    ordered = sorted(samples_us)
    return {
        "count": len(ordered),
        "min_us": round(ordered[0], 3),
        "mean_us": round(statistics.fmean(ordered), 3),
        "p50_us": round(percentile(ordered, 0.50), 3),
        "p95_us": round(percentile(ordered, 0.95), 3),
        "max_us": round(ordered[-1], 3),
    }


def measure(operation: Callable[[], Any], iterations: int) -> list[float]:
    samples: list[float] = []
    for _ in range(iterations):
        started = time.perf_counter_ns()
        operation()
        elapsed = time.perf_counter_ns() - started
        if elapsed <= 0:
            raise AssertionError(f"non-positive latency sample: {elapsed}")
        samples.append(elapsed / 1_000)
    return samples


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=250)
    parser.add_argument("--warmup", type=int, default=40)
    args = parser.parse_args()
    if args.iterations < 50 or args.warmup < 10:
        raise SystemExit("use at least 50 measured iterations and 10 warm-up iterations")

    settings = require_local_scope()
    redis_client = redis.Redis(
        host=str(settings["redis_host"]),
        port=int(settings["redis_port"]),
        db=0,
        decode_responses=True,
        socket_timeout=3,
    )
    postgres = psycopg.connect(
        host=str(settings["postgres_host"]),
        port=int(settings["postgres_port"]),
        dbname=str(settings["postgres_db"]),
        user=str(settings["postgres_user"]),
        password=str(settings["postgres_password"]),
        autocommit=True,
        connect_timeout=3,
    )

    try:
        cursor = postgres.cursor()
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {TABLE} (
                item_key text PRIMARY KEY,
                payload text NOT NULL,
                updated_at timestamptz NOT NULL DEFAULT clock_timestamp()
            )
            """
        )
        cursor.execute(f"DELETE FROM {TABLE}")
        redis_client.unlink(KEY)

        def redis_set() -> bool:
            result = redis_client.set(KEY, PAYLOAD)
            if result is not True:
                raise AssertionError(f"Redis SET failed: {result!r}")
            return result

        def redis_get() -> str:
            value = redis_client.get(KEY)
            if value != PAYLOAD:
                raise AssertionError(f"Redis payload mismatch: {value!r}")
            return value

        def postgres_upsert() -> None:
            cursor.execute(
                f"""
                INSERT INTO {TABLE}(item_key, payload)
                VALUES (%s, %s)
                ON CONFLICT (item_key) DO UPDATE
                SET payload = EXCLUDED.payload, updated_at = clock_timestamp()
                """,
                (KEY, PAYLOAD),
            )

        def postgres_select() -> str:
            cursor.execute(f"SELECT payload FROM {TABLE} WHERE item_key = %s", (KEY,))
            row = cursor.fetchone()
            if row is None or row[0] != PAYLOAD:
                raise AssertionError(f"PostgreSQL payload mismatch: {row!r}")
            return str(row[0])

        def postgres_expensive_select() -> str:
            cursor.execute(
                f"SELECT payload, pg_sleep(0.004) FROM {TABLE} WHERE item_key = %s",
                (KEY,),
            )
            row = cursor.fetchone()
            if row is None or row[0] != PAYLOAD:
                raise AssertionError(f"delayed PostgreSQL payload mismatch: {row!r}")
            return str(row[0])

        redis_set()
        postgres_upsert()
        for _ in range(args.warmup):
            redis_set()
            redis_get()
            postgres_upsert()
            postgres_select()

        baseline = {
            "redis_set": summarize(measure(redis_set, args.iterations)),
            "redis_get": summarize(measure(redis_get, args.iterations)),
            "postgres_upsert_autocommit": summarize(
                measure(postgres_upsert, args.iterations)
            ),
            "postgres_primary_key_select": summarize(
                measure(postgres_select, args.iterations)
            ),
        }
        variation_iterations = max(50, args.iterations // 2)
        variation = {
            "redis_cached_get": summarize(
                measure(redis_get, variation_iterations)
            ),
            "postgres_select_plus_4ms_work": summarize(
                measure(postgres_expensive_select, variation_iterations)
            ),
        }

        redis_value = redis_get()
        postgres_value = postgres_select()
        cursor.execute(f"SELECT count(*) FROM {TABLE} WHERE item_key = %s", (KEY,))
        row_count = int(cursor.fetchone()[0])
        if redis_value != postgres_value or row_count != 1:
            raise AssertionError(
                f"final correctness mismatch: redis={redis_value!r} "
                f"postgres={postgres_value!r} rows={row_count}"
            )
        delayed_p50 = float(variation["postgres_select_plus_4ms_work"]["p50_us"])
        if delayed_p50 < 3_500:
            raise AssertionError(
                f"controlled 4 ms variation was not visible: p50_us={delayed_p50}"
            )

        redis_read_p50 = float(baseline["redis_get"]["p50_us"])
        postgres_read_p50 = float(baseline["postgres_primary_key_select"]["p50_us"])
        ordering = (
            "redis-lower"
            if redis_read_p50 < postgres_read_p50
            else "postgres-lower-or-equal"
        )
        result = {
            "task_id": TASK_ID,
            "method": {
                "clients": "persistent",
                "concurrency": 1,
                "iterations": args.iterations,
                "warmup": args.warmup,
                "payload_bytes": len(PAYLOAD.encode("utf-8")),
                "clock": "time.perf_counter_ns",
                "redis_persistence": "disabled by task Compose configuration",
                "postgres_writes": "one autocommit transaction per upsert",
            },
            "versions": {
                "redis_py": importlib.metadata.version("redis"),
                "psycopg": importlib.metadata.version("psycopg"),
            },
            "correctness": {
                "key": KEY,
                "redis_exact_payload": True,
                "postgres_exact_payload": True,
                "postgres_rows": row_count,
            },
            "baseline": baseline,
            "baseline_read_ordering_observed": ordering,
            "variation": variation,
        }

        print(
            "CORRECTNESS "
            f"redis=exact postgres=exact rows={row_count} "
            f"payload_bytes={result['method']['payload_bytes']}"
        )
        for name, summary in baseline.items():
            print(
                "BASELINE "
                f"operation={name} count={summary['count']} "
                f"p50_us={summary['p50_us']} p95_us={summary['p95_us']} "
                f"mean_us={summary['mean_us']}"
            )
        print(
            "VARIATION "
            f"redis_get_p50_us={variation['redis_cached_get']['p50_us']} "
            "postgres_plus_4ms_p50_us="
            f"{variation['postgres_select_plus_4ms_work']['p50_us']}"
        )
        print(
            "SEMANTICS redis_persistence=disabled "
            "postgres_upsert=autocommit comparison=not-equivalent-durability"
        )
        print("BENCHMARK_JSON " + json.dumps(result, sort_keys=True))
    finally:
        postgres.close()
        redis_client.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

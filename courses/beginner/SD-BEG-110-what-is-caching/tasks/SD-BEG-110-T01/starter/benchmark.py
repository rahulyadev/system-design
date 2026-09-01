#!/usr/bin/env python3
"""Learner starter for SD-BEG-110-T01.

Complete the marked sections after writing a prediction in ATTEMPT.md. This
starter intentionally contains no finished Redis/PostgreSQL comparison.
"""

from __future__ import annotations

import os
import statistics
import time
from collections.abc import Callable

import psycopg
import redis


KEY = "sd-beg-110:t01:profile:42"
PAYLOAD = '{"id":42,"name":"synthetic-profile"}'
ITERATIONS = 250


def measure(operation: Callable[[], object], iterations: int) -> list[float]:
    """Return one latency sample per operation in microseconds."""

    samples: list[float] = []
    for _ in range(iterations):
        started = time.perf_counter_ns()
        operation()
        samples.append((time.perf_counter_ns() - started) / 1_000)
    return samples


def describe(samples: list[float]) -> str:
    ordered = sorted(samples)
    p95_index = min(len(ordered) - 1, max(0, int(len(ordered) * 0.95) - 1))
    return (
        f"count={len(samples)} mean_us={statistics.fmean(samples):.3f} "
        f"p50_us={statistics.median(samples):.3f} "
        f"p95_us={ordered[p95_index]:.3f}"
    )


def main() -> int:
    redis_client = redis.Redis(
        host=os.environ.get("REDIS_HOST", "127.0.0.1"),
        port=int(os.environ.get("REDIS_PORT", "55110")),
        decode_responses=True,
    )
    postgres = psycopg.connect(
        host=os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        port=int(os.environ.get("POSTGRES_PORT", "55111")),
        dbname=os.environ.get("POSTGRES_DB", "sd_beg_110_t01"),
        user=os.environ.get("POSTGRES_USER", "benchmark"),
        password=os.environ.get(
            "POSTGRES_PASSWORD", "sd_beg_110_t01_postgres_local"
        ),
        autocommit=True,
    )

    # TODO 1: create one task-owned PostgreSQL table and reset only its rows.
    # TODO 2: implement Redis SET/GET and PostgreSQL upsert/primary-key SELECT.
    # TODO 3: assert that every read returns PAYLOAD before trusting timings.
    # TODO 4: warm each path, then call measure() with persistent clients.
    # TODO 5: print units, sample count, mean, p50, and p95 for all four paths.
    # TODO 6: change one condition and predict the effect before measuring again.

    postgres.close()
    redis_client.close()
    raise SystemExit(
        "Starter incomplete: finish the TODOs after recording your prediction."
    )


if __name__ == "__main__":
    raise SystemExit(main())

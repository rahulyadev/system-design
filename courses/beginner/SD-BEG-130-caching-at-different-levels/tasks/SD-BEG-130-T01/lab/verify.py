#!/usr/bin/env python3
"""Verify the reference cache model without contacting a network or provider."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys


TASK_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = TASK_ROOT / "reference" / "cdn_cache_model.py"
IMAGE_PATH = "/assets/sd-beg-130-image.png"
TTL_SECONDS = 300


def load_model():
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location("sd_beg_130_cdn_model", MODEL_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load reference model: {MODEL_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def line(label: str, response, *, authoritative: str | None = None) -> str:
    fields = [
        label,
        f"status={response.cache_status}",
        f"served={response.served_version}",
    ]
    if authoritative is not None:
        fields.append(f"authoritative={authoritative}")
    fields.extend(
        [
            f"age={response.age_seconds}",
            f"origin_reads={response.origin_reads}",
            f"sha256={response.body_sha256[:12]}",
        ]
    )
    return " ".join(fields)


def main() -> int:
    model = load_model()
    origin = model.Origin()
    edge = model.EdgeCache(now_seconds=0)

    origin.put(IMAGE_PATH, b"synthetic-image-version-1", "v1")

    first = edge.request(IMAGE_PATH, origin, TTL_SECONDS)
    assert (first.cache_status, first.served_version, first.age_seconds) == (
        "MISS",
        "v1",
        0,
    )
    assert first.origin_reads == 1

    edge.advance(10)
    second = edge.request(IMAGE_PATH, origin, TTL_SECONDS)
    assert (second.cache_status, second.served_version, second.age_seconds) == (
        "HIT",
        "v1",
        10,
    )
    assert second.origin_reads == 1
    assert second.body_sha256 == first.body_sha256

    origin.put(IMAGE_PATH, b"synthetic-image-version-2", "v2")
    edge.advance(10)
    before_purge = edge.request(IMAGE_PATH, origin, TTL_SECONDS)
    assert before_purge.cache_status == "HIT"
    assert before_purge.served_version == "v1"
    assert origin.version(IMAGE_PATH) == "v2"
    assert before_purge.origin_reads == 1

    assert edge.purge_exact(IMAGE_PATH) is True
    after_purge = edge.request(IMAGE_PATH, origin, TTL_SECONDS)
    assert (after_purge.cache_status, after_purge.served_version) == ("MISS", "v2")
    assert after_purge.origin_reads == 2
    assert after_purge.body_sha256 != first.body_sha256

    edge.advance(TTL_SECONDS)
    at_expiry = edge.request(IMAGE_PATH, origin, TTL_SECONDS)
    assert (at_expiry.cache_status, at_expiry.served_version) == ("EXPIRED", "v2")
    assert at_expiry.origin_reads == 3

    print("preflight mode=deterministic-simulation network=none persistent_state=none")
    print(line("request=1", first))
    print(line("request=2", second))
    print(
        line(
            "origin_changed_same_url",
            before_purge,
            authoritative=origin.version(IMAGE_PATH),
        )
    )
    print(line("after_exact_url_purge", after_purge))
    print(line("at_ttl_boundary", at_expiry))
    print("SD-BEG-130-T01_LOCAL_MODEL_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

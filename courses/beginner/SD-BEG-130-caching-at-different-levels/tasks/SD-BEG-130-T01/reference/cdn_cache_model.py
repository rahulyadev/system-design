#!/usr/bin/env python3
"""Deterministic one-origin, one-edge cache model for reference verification.

This is intentionally not a CDN implementation. It models only cache-key
identity, freshness, pull-on-miss population, exact-key purge, and origin read
count so the lecture's state transitions can be asserted without cloud state.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True)
class OriginObject:
    body: bytes
    version: str


@dataclass(frozen=True)
class StoredObject:
    body: bytes
    version: str
    stored_at_seconds: int
    ttl_seconds: int


@dataclass(frozen=True)
class CacheResponse:
    cache_status: str
    served_version: str
    age_seconds: int
    body_sha256: str
    origin_reads: int


class Origin:
    def __init__(self) -> None:
        self._objects: dict[str, OriginObject] = {}
        self.read_count = 0

    def put(self, path: str, body: bytes, version: str) -> None:
        self._objects[path] = OriginObject(body=body, version=version)

    def fetch(self, path: str) -> OriginObject:
        self.read_count += 1
        return self._objects[path]

    def version(self, path: str) -> str:
        return self._objects[path].version


class EdgeCache:
    def __init__(self, now_seconds: int = 0) -> None:
        self.now_seconds = now_seconds
        self._objects: dict[str, StoredObject] = {}

    def advance(self, seconds: int) -> None:
        if seconds < 0:
            raise ValueError("clock cannot move backwards")
        self.now_seconds += seconds

    def purge_exact(self, path: str) -> bool:
        return self._objects.pop(path, None) is not None

    def request(self, path: str, origin: Origin, ttl_seconds: int) -> CacheResponse:
        if ttl_seconds < 0:
            raise ValueError("ttl must be non-negative")

        stored = self._objects.get(path)
        status = "MISS"
        if stored is not None:
            age = self.now_seconds - stored.stored_at_seconds
            if age < stored.ttl_seconds:
                return CacheResponse(
                    cache_status="HIT",
                    served_version=stored.version,
                    age_seconds=age,
                    body_sha256=sha256(stored.body).hexdigest(),
                    origin_reads=origin.read_count,
                )
            status = "EXPIRED"

        fetched = origin.fetch(path)
        self._objects[path] = StoredObject(
            body=fetched.body,
            version=fetched.version,
            stored_at_seconds=self.now_seconds,
            ttl_seconds=ttl_seconds,
        )
        return CacheResponse(
            cache_status=status,
            served_version=fetched.version,
            age_seconds=0,
            body_sha256=sha256(fetched.body).hexdigest(),
            origin_reads=origin.read_count,
        )

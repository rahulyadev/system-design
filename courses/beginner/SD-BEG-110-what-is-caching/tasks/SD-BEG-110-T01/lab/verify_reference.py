#!/usr/bin/env python3
"""Run and verify the isolated SD-BEG-110-T01 reference experiment."""

from __future__ import annotations

import importlib.metadata
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
TASK = HERE.parent
REFERENCE = TASK / "reference"
PROJECT = "sd-beg-110-t01"
TASK_ID = "SD-BEG-110-T01"
KEY = "sd-beg-110:t01:profile:42"
DB_NAME = "sd_beg_110_t01"
DB_USER = "benchmark"
POSTGRES_VOLUME = "sd-beg-110-t01-postgres-18"
SERVICES = {
    "redis": {"image": "redis:8.10.1", "host_port": "55110", "target_port": "6379"},
    "postgres": {"image": "postgres:18.6", "host_port": "55111", "target_port": "5432"},
}
COMPOSE = [
    "docker",
    "compose",
    "-f",
    str(HERE / "compose.yaml"),
    "--project-name",
    PROJECT,
    "--profile",
    "lab",
]


def run(
    command: list[str],
    *,
    check: bool = True,
    timeout: int = 120,
    echo: bool = True,
) -> subprocess.CompletedProcess[str]:
    if echo:
        print("$ " + " ".join(command))
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
    )
    if check and completed.returncode != 0:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"stdout={completed.stdout.strip()}\nstderr={completed.stderr.strip()}"
        )
    return completed


def compose(*arguments: str) -> list[str]:
    return COMPOSE + list(arguments)


def require_dependencies() -> None:
    expected = {"redis": "8.1.0", "psycopg": "3.3.4", "psycopg-binary": "3.3.4"}
    observed: dict[str, str] = {}
    for package, version in expected.items():
        try:
            observed[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError as exc:
            raise RuntimeError(
                "reference dependencies missing; install reference/requirements.txt "
                "inside the task-local virtual environment"
            ) from exc
        if observed[package] != version:
            raise RuntimeError(
                f"dependency version mismatch for {package}: "
                f"expected {version}, observed {observed[package]}"
            )
    print(
        "CLIENT_VERSIONS "
        + " ".join(f"{name}={version}" for name, version in observed.items())
        + f" python={sys.version.split()[0]}"
    )


def wait_healthy(service: str, timeout: int = 90) -> str:
    deadline = time.monotonic() + timeout
    last = "container not created"
    while time.monotonic() < deadline:
        container_id = run(compose("ps", "-q", service), echo=False).stdout.strip()
        if container_id:
            inspected = json.loads(
                run(["docker", "inspect", container_id], echo=False).stdout
            )[0]
            state = inspected.get("State", {})
            last = str((state.get("Health") or {}).get("Status", state.get("Status")))
            if last == "healthy":
                print(f"HEALTH service={service} status=healthy container={container_id[:12]}")
                return container_id
            if last in {"exited", "dead"}:
                raise RuntimeError(f"{service} exited before becoming healthy")
        time.sleep(1)
    raise RuntimeError(f"{service} health timeout; last_state={last}")


def verify_container(service: str, container_id: str) -> str:
    details = json.loads(run(["docker", "inspect", container_id], echo=False).stdout)[0]
    expected = SERVICES[service]
    labels = details.get("Config", {}).get("Labels", {}) or {}
    if details.get("Config", {}).get("Image") != expected["image"]:
        raise RuntimeError(f"{service} image identity mismatch")
    if labels.get("com.rahulyadav.learning-task") != TASK_ID:
        raise RuntimeError(f"{service} task label mismatch")
    if labels.get("com.docker.compose.project") != PROJECT:
        raise RuntimeError(f"{service} Compose project mismatch")
    bindings = details.get("NetworkSettings", {}).get("Ports", {}) or {}
    expected_binding = bindings.get(f"{expected['target_port']}/tcp") or []
    if not any(
        item.get("HostIp") == "127.0.0.1"
        and item.get("HostPort") == expected["host_port"]
        for item in expected_binding
    ):
        raise RuntimeError(f"{service} runtime port mismatch: {expected_binding}")
    if service == "postgres":
        mounts = details.get("Mounts", []) or []
        if not any(
            item.get("Type") == "volume"
            and item.get("Name") == POSTGRES_VOLUME
            and item.get("Destination") == "/var/lib/postgresql"
            for item in mounts
        ):
            raise RuntimeError(f"PostgreSQL volume identity mismatch: {mounts}")
    image_details = json.loads(
        run(["docker", "image", "inspect", expected["image"]], echo=False).stdout
    )[0]
    digest = (image_details.get("RepoDigests") or ["unavailable"])[0]
    print(
        f"RUNTIME_IDENTITY service={service} image={expected['image']} "
        f"port=127.0.0.1:{expected['host_port']} digest={digest}"
    )
    return digest


def redis_command(*arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(compose("exec", "-T", "redis", "redis-cli", *arguments), check=check)


def postgres_query(sql: str, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run(
        compose(
            "exec",
            "-T",
            "postgres",
            "psql",
            "-v",
            "ON_ERROR_STOP=1",
            "-U",
            DB_USER,
            "-d",
            DB_NAME,
            "-Atc",
            sql,
        ),
        check=check,
    )


def redis_config_value(name: str) -> str:
    output = redis_command("--json", "CONFIG", "GET", name).stdout.strip()
    parsed: Any = json.loads(output)
    if isinstance(parsed, dict):
        return str(parsed.get(name, ""))
    if isinstance(parsed, list) and len(parsed) >= 2:
        return str(parsed[1])
    raise RuntimeError(f"unexpected Redis CONFIG GET output for {name}: {output}")


def run_benchmark() -> dict[str, object]:
    completed = run(
        [sys.executable, str(REFERENCE / "benchmark.py"), "--iterations", "250", "--warmup", "40"],
        timeout=180,
    )
    print(completed.stdout.strip())
    marker = "BENCHMARK_JSON "
    lines = [line for line in completed.stdout.splitlines() if line.startswith(marker)]
    if len(lines) != 1:
        raise RuntimeError("benchmark did not emit exactly one BENCHMARK_JSON record")
    result = json.loads(lines[0][len(marker) :])
    if result.get("task_id") != TASK_ID:
        raise RuntimeError(f"benchmark task identity mismatch: {result.get('task_id')}")
    correctness = result.get("correctness", {})
    if correctness != {
        "key": KEY,
        "postgres_exact_payload": True,
        "postgres_rows": 1,
        "redis_exact_payload": True,
    }:
        raise RuntimeError(f"benchmark correctness mismatch: {correctness}")
    baseline = result.get("baseline", {})
    for operation in (
        "redis_set",
        "redis_get",
        "postgres_upsert_autocommit",
        "postgres_primary_key_select",
    ):
        summary = baseline.get(operation, {})
        if summary.get("count") != 250 or float(summary.get("p50_us", 0)) <= 0:
            raise RuntimeError(f"invalid latency summary for {operation}: {summary}")
    delayed = (
        result.get("variation", {})
        .get("postgres_select_plus_4ms_work", {})
        .get("p50_us", 0)
    )
    if float(delayed) < 3_500:
        raise RuntimeError(f"controlled delay missing from variation: {delayed}")
    return result


def reset_and_stop(started: bool) -> None:
    if not started:
        return
    reset_error: Exception | None = None
    try:
        redis_command("UNLINK", KEY)
        table_name = postgres_query(
            "SELECT COALESCE(to_regclass('public.cache_benchmark')::text, '')"
        ).stdout.strip()
        if table_name:
            postgres_query("DELETE FROM public.cache_benchmark")
        redis_exists = redis_command("--raw", "EXISTS", KEY).stdout.strip()
        remaining_rows = (
            postgres_query("SELECT count(*) FROM public.cache_benchmark").stdout.strip()
            if table_name
            else "0"
        )
        if redis_exists != "0" or remaining_rows != "0":
            raise RuntimeError(
                f"scoped reset failed: redis_exists={redis_exists} "
                f"postgres_rows={remaining_rows}"
            )
        print(
            "RESET redis_key=absent postgres_rows=0 "
            "targets=exact-task-key-and-table"
        )
    except Exception as exc:
        reset_error = exc
    finally:
        run(compose("stop", "redis", "postgres"), timeout=90)

    states: list[str] = []
    for service in SERVICES:
        container_id = run(compose("ps", "-a", "-q", service), echo=False).stdout.strip()
        if not container_id:
            raise RuntimeError(f"cleanup lost expected {service} container")
        state = run(
            ["docker", "inspect", "--format", "{{.State.Status}}", container_id],
            echo=False,
        ).stdout.strip()
        if state != "exited":
            raise RuntimeError(f"cleanup did not stop {service}: {state}")
        states.append(f"{service}=exited")
    volume = json.loads(
        run(["docker", "volume", "inspect", POSTGRES_VOLUME], echo=False).stdout
    )[0]
    labels = volume.get("Labels", {}) or {}
    if labels.get("com.rahulyadav.learning-task") != TASK_ID:
        raise RuntimeError("retained PostgreSQL volume label mismatch")
    print(
        "CLEANUP "
        + " ".join(states)
        + " postgres_volume=retained-and-labeled recoverable=true "
        + "redis_persistence=disabled"
    )
    if reset_error is not None:
        raise reset_error


def execute_reference(state: dict[str, bool]) -> dict[str, object]:
    run([sys.executable, str(HERE / "preflight.py")])
    require_dependencies()
    print(
        "PREDICTION correctness=both-exact likely_ordering=redis-lower "
        "asserted_ordering=none reason=different-semantics-and-host-noise"
    )
    run(compose("up", "-d", "redis", "postgres"), timeout=240)
    state["started"] = True
    containers = {service: wait_healthy(service) for service in SERVICES}
    digests = {
        service: verify_container(service, container_id)
        for service, container_id in containers.items()
    }

    redis_info = redis_command("--raw", "INFO", "server").stdout
    redis_version = next(
        (line.split(":", 1)[1].strip() for line in redis_info.splitlines() if line.startswith("redis_version:")),
        "",
    )
    postgres_version_full = postgres_query("SHOW server_version").stdout.strip()
    postgres_version = postgres_version_full.split()[0] if postgres_version_full else ""
    if redis_version != "8.10.1" or postgres_version != "18.6":
        raise RuntimeError(
            "runtime version mismatch: "
            f"redis={redis_version} postgres={postgres_version_full}"
        )
    save_value = redis_config_value("save")
    appendonly_value = redis_config_value("appendonly")
    if save_value != "" or appendonly_value != "no":
        raise RuntimeError(
            f"Redis persistence mismatch: save={save_value!r} "
            f"appendonly={appendonly_value!r}"
        )
    print(
        "SERVER_VERSIONS "
        f"redis={redis_version} postgres={postgres_version} "
        f"postgres_build={json.dumps(postgres_version_full)} "
        "redis_save=empty redis_appendonly=no"
    )

    result = run_benchmark()
    result["image_digests"] = digests
    return result


def main() -> int:
    state = {"started": False}
    failure: Exception | None = None
    result: dict[str, object] | None = None
    try:
        result = execute_reference(state)
    except Exception as exc:
        failure = exc

    cleanup_failure: Exception | None = None
    try:
        reset_and_stop(state["started"])
    except Exception as exc:
        cleanup_failure = exc

    if failure is not None:
        print(f"REFERENCE_FAILED {failure}", file=sys.stderr)
        if cleanup_failure is not None:
            print(f"CLEANUP_ALSO_FAILED {cleanup_failure}", file=sys.stderr)
        return 1
    if cleanup_failure is not None:
        print(f"CLEANUP_FAILED {cleanup_failure}", file=sys.stderr)
        return 1
    if result is None:
        print("REFERENCE_FAILED missing result", file=sys.stderr)
        return 1
    print(
        "RESULT_BOUNDARY ordering="
        f"{result['baseline_read_ordering_observed']} "
        "claim=local-sequential-measurement-not-production-capacity"
    )
    print("SD-BEG-110-T01_REFERENCE_VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

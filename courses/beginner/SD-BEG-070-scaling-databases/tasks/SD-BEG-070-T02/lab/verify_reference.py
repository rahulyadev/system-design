#!/usr/bin/env python3
"""Execute and assert the isolated SD-BEG-070-T02 reference path."""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


HERE = Path(__file__).resolve().parent
REFERENCE = HERE.parent / "reference"
PROJECT = "sd-beg-070-t02"
TASK_ID = "SD-BEG-070-T02"
SERVICES = {"shard_am": "55711", "shard_nz": "55712"}
SERVER_IDS = {"shard_am": 711, "shard_nz": 712}
VOLUMES = {
    "shard_am": "sd-beg-070-t02-am-mysql-8-4",
    "shard_nz": "sd-beg-070-t02-nz-mysql-8-4",
}
IMAGE = "mysql:8.4.11"
DB_NAME = "sd_beg_070_t02"
ROOT_PASSWORD = "sd_beg_070_t02_root_local"
APP_PASSWORD = "sd_beg_070_t02_app_local"
API_PORT = 58072
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


def shown(command: list[str]) -> str:
    return " ".join(command)


def run(
    command: list[str],
    *,
    input_text: str | None = None,
    check: bool = True,
    echo: bool = True,
    timeout: int = 120,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    if echo:
        print(f"$ {shown(command)}", flush=True)
    completed = subprocess.run(
        command,
        input=input_text,
        capture_output=True,
        text=True,
        check=False,
        timeout=timeout,
        cwd=cwd,
        env=env,
    )
    if echo and completed.stdout.strip():
        print(completed.stdout.strip(), flush=True)
    if echo and completed.stderr.strip():
        print(completed.stderr.strip(), file=sys.stderr, flush=True)
    if check and completed.returncode != 0:
        raise RuntimeError(f"command failed ({completed.returncode}): {shown(command)}")
    return completed


def compose(*arguments: str) -> list[str]:
    return COMPOSE + list(arguments)


def mysql_process(
    service: str,
    sql: str,
    *,
    user: str = "root",
    password: str = ROOT_PASSWORD,
    database: str | None = None,
    check: bool = True,
    echo: bool = False,
    input_mode: bool = False,
) -> subprocess.CompletedProcess[str]:
    command = compose(
        "exec",
        "-T",
        "-e",
        f"MYSQL_PWD={password}",
        service,
        "mysql",
        "--protocol=TCP",
        "-h",
        "127.0.0.1",
        "-u",
        user,
        "-N",
        "-B",
    )
    if database:
        command.extend(["-D", database])
    if not input_mode:
        command.extend(["-e", sql])
    return run(
        command,
        input_text=sql if input_mode else None,
        check=check,
        echo=echo,
        timeout=90,
    )


def mysql(service: str, sql: str, **kwargs: object) -> str:
    return mysql_process(service, sql, **kwargs).stdout.strip()


def wait_until_healthy(service: str) -> str:
    deadline = time.monotonic() + 120
    last = "container-not-created"
    while time.monotonic() < deadline:
        probe = run(compose("ps", "-q", service), check=False, echo=False)
        container_id = probe.stdout.strip()
        if container_id:
            health = run(
                ["docker", "inspect", "--format", "{{.State.Health.Status}}", container_id],
                check=False,
                echo=False,
            )
            last = health.stdout.strip() or health.stderr.strip()
            if health.returncode == 0 and last == "healthy":
                print(f"HEALTH service={service} status=healthy container={container_id[:12]}")
                return container_id
        time.sleep(1)
    raise RuntimeError(f"{service} did not become healthy: {last}")


def verify_runtime_identity(service: str, container_id: str) -> None:
    details = json.loads(run(["docker", "inspect", container_id], echo=False).stdout)[0]
    labels = details.get("Config", {}).get("Labels", {}) or {}
    if labels.get("com.docker.compose.project") != PROJECT:
        raise RuntimeError(f"{service} project label mismatch")
    if labels.get("com.docker.compose.service") != service:
        raise RuntimeError(f"{service} service label mismatch")
    if labels.get("com.rahulyadav.learning-task") != TASK_ID:
        raise RuntimeError(f"{service} task label mismatch")
    if details.get("Config", {}).get("Image") != IMAGE:
        raise RuntimeError(f"{service} image mismatch")

    bindings = details.get("HostConfig", {}).get("PortBindings", {}).get("3306/tcp") or []
    expected_port = SERVICES[service]
    if len(bindings) != 1 or bindings[0].get("HostIp") != "127.0.0.1" or bindings[0].get(
        "HostPort"
    ) != expected_port:
        raise RuntimeError(f"{service} loopback binding mismatch: {bindings}")

    volume_name = VOLUMES[service]
    mounts = details.get("Mounts", [])
    if not any(item.get("Type") == "volume" and item.get("Name") == volume_name for item in mounts):
        raise RuntimeError(f"{service} exact task volume not mounted")
    volume = json.loads(run(["docker", "volume", "inspect", volume_name], echo=False).stdout)[0]
    volume_labels = volume.get("Labels", {}) or {}
    if volume_labels.get("com.rahulyadav.learning-task") != TASK_ID:
        raise RuntimeError(f"{service} volume task label mismatch")

    print(
        "RUNTIME_IDENTITY "
        f"project={PROJECT} service={service} port=127.0.0.1:{expected_port} "
        f"database={DB_NAME} volume={volume_name} labels=verified"
    )


def http_json(method: str, path: str, payload: dict[str, object] | None = None) -> tuple[int, dict[str, object]]:
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        f"http://127.0.0.1:{API_PORT}{path}",
        data=data,
        method=method,
        headers={"content-type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode())


def wait_for_api(process: subprocess.Popen[str]) -> dict[str, object]:
    deadline = time.monotonic() + 30
    last_error = "not attempted"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            output = process.stdout.read().strip() if process.stdout else ""
            raise RuntimeError(f"reference API exited early ({process.returncode}): {output}")
        try:
            status, body = http_json("GET", "/health")
            if status == 200:
                return body
            last_error = f"HTTP {status}: {body}"
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            last_error = str(exc)
        time.sleep(0.25)
    raise RuntimeError(f"reference API did not become ready: {last_error}")


def count_key(service: str, key: str) -> int:
    escaped = key.replace("'", "''")
    return int(
        mysql(
            service,
            f"SELECT COUNT(*) FROM records WHERE key_name='{escaped}'",
            user="app",
            password=APP_PASSWORD,
            database=DB_NAME,
        )
    )


def total_count(service: str) -> int:
    return int(
        mysql(
            service,
            "SELECT COUNT(*) FROM records",
            user="app",
            password=APP_PASSWORD,
            database=DB_NAME,
        )
    )


def prefix_count(service: str, prefix: str) -> int:
    escaped = prefix.replace("'", "''")
    return int(
        mysql(
            service,
            f"SELECT COUNT(*) FROM records WHERE key_name LIKE '{escaped}%'",
            user="app",
            password=APP_PASSWORD,
            database=DB_NAME,
        )
    )


def stop_api(process: subprocess.Popen[str] | None) -> None:
    if process is None:
        return
    if process.poll() is None:
        process.send_signal(signal.SIGTERM)
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)
    output = process.stdout.read().strip() if process.stdout else ""
    if output:
        print("REFERENCE_API_LOG")
        print(output)


def stop_and_verify_cleanup(started: bool) -> None:
    if not started:
        return
    run(compose("stop", "shard_am", "shard_nz"), timeout=90)
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
    for volume_name in VOLUMES.values():
        volume = json.loads(run(["docker", "volume", "inspect", volume_name], echo=False).stdout)[0]
        labels = volume.get("Labels", {}) or {}
        if labels.get("com.rahulyadav.learning-task") != TASK_ID:
            raise RuntimeError(f"cleanup volume label mismatch: {volume_name}")
    print(
        "CLEANUP "
        + " ".join(states)
        + " volumes=retained-and-labeled recoverable=true"
    )


def execute_reference(state: dict[str, object]) -> None:
    dependency = REFERENCE / "node_modules" / "mysql2" / "package.json"
    if not dependency.is_file():
        raise RuntimeError(
            "reference dependency missing; run npm ci --prefix reference --ignore-scripts"
        )

    run([sys.executable, str(HERE / "preflight.py")])
    print("PREDICTION boundary=a-m@711,n-z@712 invalid=422 skew=20:2")
    run(compose("up", "-d", "shard_am", "shard_nz"), timeout=240)
    state["started"] = True
    containers = {service: wait_until_healthy(service) for service in SERVICES}
    for service, container_id in containers.items():
        verify_runtime_identity(service, container_id)

    versions = {
        service: mysql(service, "SELECT VERSION(), @@server_id").split("\t")
        for service in SERVICES
    }
    for service, expected_id in SERVER_IDS.items():
        if versions[service][1] != str(expected_id) or not versions[service][0].startswith("8.4.11"):
            raise RuntimeError(f"unexpected MySQL version/server ID for {service}: {versions[service]}")
    image_inspect = json.loads(run(["docker", "image", "inspect", IMAGE], echo=False).stdout)[0]
    digest = (image_inspect.get("RepoDigests") or ["unavailable"])[0]
    node_version = run(["node", "--version"], echo=False).stdout.strip()
    print(
        "VERSIONS "
        f"shard_am={versions['shard_am'][0]}@711 shard_nz={versions['shard_nz'][0]}@712 "
        f"node={node_version} mysql2=3.24.2 image_digest={digest}"
    )

    schema = (REFERENCE / "schema.sql").read_text(encoding="utf-8")
    for service in SERVICES:
        mysql_process(service, schema, database=DB_NAME, input_mode=True, echo=True)
        table_count = mysql(
            service,
            "SELECT COUNT(*) FROM information_schema.tables "
            f"WHERE table_schema='{DB_NAME}' AND table_name='records'",
        )
        if table_count != "1":
            raise RuntimeError(f"schema missing on {service}: {table_count}")
    print("SCHEMA_CHECK records_table=present shards=2 independent=true")

    env = os.environ.copy()
    env.update(
        {
            "API_PORT": str(API_PORT),
            "SHARD_AM_PORT": SERVICES["shard_am"],
            "SHARD_NZ_PORT": SERVICES["shard_nz"],
            "DB_NAME": DB_NAME,
            "DB_USER": "app",
            "DB_PASSWORD": APP_PASSWORD,
        }
    )
    api = subprocess.Popen(
        ["node", "server.mjs"],
        cwd=REFERENCE,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    state["api"] = api
    health = wait_for_api(api)
    if health.get("shard_am_server_id") != 711 or health.get("shard_nz_server_id") != 712:
        raise RuntimeError(f"API health identity mismatch: {health}")
    print("API_HEALTH shard_am_server_id=711 shard_nz_server_id=712")

    baseline = {
        "apple": ("am", 711, "shard_am", "shard_nz"),
        "mango": ("am", 711, "shard_am", "shard_nz"),
        "nectar": ("nz", 712, "shard_nz", "shard_am"),
        "zebra": ("nz", 712, "shard_nz", "shard_am"),
    }
    for key, (expected_shard, expected_id, owner, other) in baseline.items():
        status, posted = http_json("POST", "/records", {"key": key, "value": f"value-{key}"})
        if status != 201 or posted.get("shard") != expected_shard or posted.get(
            "server_id"
        ) != expected_id:
            raise RuntimeError(f"POST routing failed for {key}: {status} {posted}")
        status, read = http_json("GET", f"/records/{key}")
        if status != 200 or read.get("shard") != expected_shard or read.get(
            "server_id"
        ) != expected_id:
            raise RuntimeError(f"GET routing failed for {key}: {status} {read}")
        if count_key(owner, key) != 1 or count_key(other, key) != 0:
            raise RuntimeError(f"physical ownership failed for {key}")
        print(
            f"BOUNDARY key={key} shard={expected_shard} server={expected_id} "
            "owner_count=1 wrong_shard_count=0"
        )

    status, uppercase = http_json("POST", "/records", {"key": "ZULU", "value": "normalized"})
    if status != 201 or uppercase.get("key") != "zulu" or uppercase.get("server_id") != 712:
        raise RuntimeError(f"uppercase normalization failed: {status} {uppercase}")
    if count_key("shard_nz", "zulu") != 1 or count_key("shard_am", "zulu") != 0:
        raise RuntimeError("normalized physical ownership failed")
    print("NORMALIZATION input=ZULU stored=zulu shard=nz server=712")

    before = {service: total_count(service) for service in SERVICES}
    status, invalid = http_json("POST", "/records", {"key": "9-invalid", "value": "reject"})
    after = {service: total_count(service) for service in SERVICES}
    if status != 422 or before != after:
        raise RuntimeError(f"invalid key did not fail safely: {status} {invalid} {before}/{after}")
    print(f"INVALID_KEY status=422 rows_unchanged={before}")

    for index in range(20):
        key = f"a-hot-{index:02d}"
        status, body = http_json("POST", "/records", {"key": key, "value": "hot-range"})
        if status != 201 or body.get("server_id") != 711:
            raise RuntimeError(f"hot-range route failed for {key}: {status} {body}")
    for index in range(2):
        key = f"z-cold-{index:02d}"
        status, body = http_json("POST", "/records", {"key": key, "value": "cold-range"})
        if status != 201 or body.get("server_id") != 712:
            raise RuntimeError(f"cold-range route failed for {key}: {status} {body}")

    counts = {
        "am_hot": prefix_count("shard_am", "a-hot-"),
        "am_cold": prefix_count("shard_am", "z-cold-"),
        "nz_hot": prefix_count("shard_nz", "a-hot-"),
        "nz_cold": prefix_count("shard_nz", "z-cold-"),
    }
    if counts != {"am_hot": 20, "am_cold": 0, "nz_hot": 0, "nz_cold": 2}:
        raise RuntimeError(f"skew physical counts mismatch: {counts}")
    print("SKEW_VARIATION a_hot@711=20 z_cold@712=2 ratio=10:1 wrong_shard_counts=0/0")


def main() -> int:
    state: dict[str, object] = {"api": None, "started": False}
    failure: Exception | None = None
    try:
        execute_reference(state)
    except Exception as exc:
        failure = exc
    cleanup_failure: Exception | None = None
    try:
        api = state["api"] if isinstance(state["api"], subprocess.Popen) else None
        stop_api(api)
        stop_and_verify_cleanup(bool(state["started"]))
    except Exception as exc:
        cleanup_failure = exc

    if failure is not None:
        print(f"REFERENCE_FAILED {failure}", file=sys.stderr)
        return 1
    if cleanup_failure is not None:
        print(f"CLEANUP_FAILED {cleanup_failure}", file=sys.stderr)
        return 1
    print("SD-BEG-070-T02_REFERENCE_VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Execute and assert the isolated SD-BEG-070-T01 reference path."""

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
PROJECT = "sd-beg-070-t01"
TASK_ID = "SD-BEG-070-T01"
SERVICES = {"source": "55701", "replica": "55702"}
VOLUMES = {
    "source": "sd-beg-070-t01-source-mysql-8-4",
    "replica": "sd-beg-070-t01-replica-mysql-8-4",
}
IMAGE = "mysql:8.4.11"
DB_NAME = "sd_beg_070_t01"
ROOT_PASSWORD = "sd_beg_070_t01_root_local"
APP_PASSWORD = "sd_beg_070_t01_app_local"
API_PORT = 58071
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
    batch: bool = True,
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
    )
    if database:
        command.extend(["-D", database])
    if batch:
        command.extend(["-N", "-B"])
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

    mounts = details.get("Mounts", [])
    volume_name = VOLUMES[service]
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


def source_position() -> tuple[str, int]:
    output = mysql("source", "SHOW BINARY LOG STATUS")
    fields = output.split("\t")
    if len(fields) < 2:
        raise RuntimeError(f"could not parse source binary log status: {output!r}")
    return fields[0], int(fields[1])


def replica_status() -> dict[str, str]:
    output = mysql("replica", "SHOW REPLICA STATUS\\G", batch=False)
    status: dict[str, str] = {}
    for raw_line in output.splitlines():
        if ":" not in raw_line:
            continue
        key, value = raw_line.strip().split(":", 1)
        status[key.strip()] = value.strip()
    return status


def wait_replica_state(expected_io: str, expected_sql: str, timeout: int = 30) -> dict[str, str]:
    deadline = time.monotonic() + timeout
    last: dict[str, str] = {}
    while time.monotonic() < deadline:
        last = replica_status()
        if last.get("Replica_IO_Running") == expected_io and last.get(
            "Replica_SQL_Running"
        ) == expected_sql:
            print(
                "REPLICA_STATE "
                f"io={expected_io} sql={expected_sql} "
                f"source={last.get('Source_Host')} "
                f"read_file={last.get('Source_Log_File')} "
                f"exec_pos={last.get('Exec_Source_Log_Pos')}"
            )
            return last
        time.sleep(0.5)
    raise RuntimeError(
        "replica state timeout: "
        f"io={last.get('Replica_IO_Running')} sql={last.get('Replica_SQL_Running')} "
        f"io_error={last.get('Last_IO_Error')} sql_error={last.get('Last_SQL_Error')}"
    )


def configure_replication() -> None:
    status = replica_status()
    if not status:
        log_file, log_position = source_position()
        mysql(
            "replica",
            "CHANGE REPLICATION SOURCE TO "
            "SOURCE_HOST='source', "
            "SOURCE_USER='replicator', "
            "SOURCE_PASSWORD='sd_beg_070_t01_repl_local', "
            f"SOURCE_LOG_FILE='{log_file}', "
            f"SOURCE_LOG_POS={log_position}, "
            "GET_SOURCE_PUBLIC_KEY=1, SOURCE_CONNECT_RETRY=1; "
            "START REPLICA;",
        )
        print(f"REPLICATION_CONFIGURED file={log_file} position={log_position}")
    else:
        if status.get("Source_Host") != "source":
            raise RuntimeError(f"refusing unexpected existing source host: {status.get('Source_Host')}")
        if status.get("Replica_IO_Running") != "Yes" or status.get("Replica_SQL_Running") != "Yes":
            mysql("replica", "START REPLICA;")
        print("REPLICATION_CONFIGURED existing_channel=verified-and-resumed")

    mysql("replica", "SET GLOBAL read_only=ON; SET GLOBAL super_read_only=ON;")
    status = wait_replica_state("Yes", "Yes")
    if status.get("Last_IO_Error") or status.get("Last_SQL_Error"):
        raise RuntimeError("replica reports an error despite running state")
    guards = mysql("replica", "SELECT @@read_only, @@super_read_only")
    if guards != "1\t1":
        raise RuntimeError(f"replica read-only guards are not enabled: {guards}")
    print("REPLICA_GUARDS read_only=1 super_read_only=1")


def wait_for_position(log_file: str, log_position: int, timeout: int = 30) -> None:
    result = mysql(
        "replica",
        f"SELECT SOURCE_POS_WAIT('{log_file}', {log_position}, {timeout})",
    )
    if result in {"NULL", "-1", ""}:
        raise RuntimeError(
            f"replica did not reach {log_file}:{log_position}; SOURCE_POS_WAIT={result!r}"
        )
    status = replica_status()
    print(
        "REPLICA_CAUGHT_UP "
        f"file={log_file} position={log_position} wait_result={result} "
        f"exec_pos={status.get('Exec_Source_Log_Pos')}"
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


def direct_count(service: str, item_id: int) -> int:
    return int(
        mysql(
            service,
            f"SELECT COUNT(*) FROM items WHERE id={item_id}",
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
    status = replica_status()
    if status and status.get("Replica_SQL_Running") != "Yes":
        mysql("replica", "START REPLICA;", check=False)
    run(compose("stop", "source", "replica"), timeout=90)
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
    print("PREDICTION baseline=replicated paused_applier=strong:present,eventual:missing")
    run(compose("up", "-d", "source", "replica"), timeout=240)
    state["started"] = True
    containers = {service: wait_until_healthy(service) for service in SERVICES}
    for service, container_id in containers.items():
        verify_runtime_identity(service, container_id)

    versions = {
        service: mysql(service, "SELECT VERSION(), @@server_id").split("\t")
        for service in SERVICES
    }
    if versions["source"][1] != "701" or versions["replica"][1] != "702":
        raise RuntimeError(f"unexpected MySQL server IDs: {versions}")
    if not all(values[0].startswith("8.4.11") for values in versions.values()):
        raise RuntimeError(f"unexpected MySQL versions: {versions}")
    image_inspect = json.loads(run(["docker", "image", "inspect", IMAGE], echo=False).stdout)[0]
    digest = (image_inspect.get("RepoDigests") or ["unavailable"])[0]
    node_version = run(["node", "--version"], echo=False).stdout.strip()
    print(
        "VERSIONS "
        f"source={versions['source'][0]} replica={versions['replica'][0]} "
        f"node={node_version} mysql2=3.24.2 image_digest={digest}"
    )

    configure_replication()
    schema = (REFERENCE / "schema.sql").read_text(encoding="utf-8")
    mysql_process("source", schema, database=DB_NAME, input_mode=True, echo=True)
    log_file, log_position = source_position()
    wait_for_position(log_file, log_position)
    table_count = mysql(
        "replica",
        "SELECT COUNT(*) FROM information_schema.tables "
        f"WHERE table_schema='{DB_NAME}' AND table_name='items'",
    )
    if table_count != "1":
        raise RuntimeError(f"replicated table missing: {table_count}")
    print("SCHEMA_REPLICATION table=items source=present replica=present")

    env = os.environ.copy()
    env.update(
        {
            "API_PORT": str(API_PORT),
            "SOURCE_PORT": SERVICES["source"],
            "REPLICA_PORT": SERVICES["replica"],
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
    if health.get("primary_server_id") != 701 or health.get("replica_server_id") != 702:
        raise RuntimeError(f"API health identity mismatch: {health}")
    print("API_HEALTH primary_server_id=701 replica_server_id=702")

    status, posted = http_json("POST", "/items", {"id": 101, "name": "baseline"})
    if status != 201 or posted.get("server_id") != 701 or posted.get("served_by") != "primary":
        raise RuntimeError(f"baseline POST routing failed: {status} {posted}")
    log_file, log_position = source_position()
    wait_for_position(log_file, log_position)
    status, read = http_json("GET", "/items/101?consistency=eventual")
    if status != 200 or read.get("server_id") != 702 or read.get("served_by") != "replica":
        raise RuntimeError(f"baseline replica GET failed: {status} {read}")
    if direct_count("source", 101) != 1 or direct_count("replica", 101) != 1:
        raise RuntimeError("baseline physical row evidence mismatch")
    print("BASELINE_ROUTING post_server=701 eventual_get_server=702 rows=source:1,replica:1")

    rejected = mysql_process(
        "replica",
        "INSERT INTO items(id,name) VALUES (999,'must-fail')",
        user="app",
        password=APP_PASSWORD,
        database=DB_NAME,
        check=False,
    )
    if rejected.returncode == 0:
        raise RuntimeError("application write unexpectedly succeeded on replica")
    replica_error = " ".join(rejected.stderr.strip().split())[-220:]
    print(f"REPLICA_WRITE_REJECTED returncode={rejected.returncode} error={replica_error}")

    mysql("replica", "STOP REPLICA SQL_THREAD;")
    wait_replica_state("Yes", "No")
    status, posted = http_json("POST", "/items", {"id": 202, "name": "paused-applier"})
    if status != 201 or posted.get("server_id") != 701:
        raise RuntimeError(f"variation POST failed: {status} {posted}")
    paused_file, paused_position = source_position()
    strong_status, strong = http_json("GET", "/items/202?consistency=strong")
    eventual_status, eventual = http_json("GET", "/items/202?consistency=eventual")
    source_count = direct_count("source", 202)
    replica_count = direct_count("replica", 202)
    if strong_status != 200 or strong.get("server_id") != 701:
        raise RuntimeError(f"strong read did not see primary row: {strong_status} {strong}")
    if eventual_status != 404 or eventual.get("server_id") != 702:
        raise RuntimeError(f"eventual read was not stale as predicted: {eventual_status} {eventual}")
    if (source_count, replica_count) != (1, 0):
        raise RuntimeError(f"paused-applier physical counts mismatch: {source_count}/{replica_count}")
    print(
        "STALE_READ applier=paused strong=200@701 eventual=404@702 "
        "rows=source:1,replica:0"
    )

    mysql("replica", "START REPLICA SQL_THREAD;")
    wait_replica_state("Yes", "Yes")
    wait_for_position(paused_file, paused_position)
    eventual_status, eventual = http_json("GET", "/items/202?consistency=eventual")
    source_count = direct_count("source", 202)
    replica_count = direct_count("replica", 202)
    if eventual_status != 200 or eventual.get("server_id") != 702:
        raise RuntimeError(f"eventual read did not recover: {eventual_status} {eventual}")
    if (source_count, replica_count) != (1, 1):
        raise RuntimeError(f"catch-up physical counts mismatch: {source_count}/{replica_count}")
    print("CATCH_UP applier=resumed eventual=200@702 rows=source:1,replica:1")


def main() -> int:
    state: dict[str, object] = {"api": None, "started": False}
    failure: Exception | None = None
    try:
        execute_reference(state)
    except Exception as exc:  # cleanup still must run on a failed assertion
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
    print("SD-BEG-070-T01_REFERENCE_VERIFIED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

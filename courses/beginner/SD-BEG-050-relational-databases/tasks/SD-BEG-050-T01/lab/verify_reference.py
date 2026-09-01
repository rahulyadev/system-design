#!/usr/bin/env python3
"""Execute and assert the isolated reference crash-recovery path."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
REFERENCE = HERE.parent / "reference"
PROJECT = "sd-beg-050-t01"
SERVICE = "postgres"
TASK_ID = "SD-BEG-050-T01"
DB_USER = "sd_beg_050_t01"
DB_NAME = "sd_beg_050_t01"
SCHEMA = "sd_beg_050_t01"
VOLUME = "sd-beg-050-t01-postgres-18"
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
    timeout: int = 90,
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
    )
    if echo and completed.stdout.strip():
        print(completed.stdout.strip(), flush=True)
    if echo and completed.stderr.strip():
        print(completed.stderr.strip(), file=sys.stderr, flush=True)
    if check and completed.returncode != 0:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {shown(command)}"
        )
    return completed


def compose(*arguments: str) -> list[str]:
    return COMPOSE + list(arguments)


def psql(sql: str, *, tuples: bool = False, echo: bool = True) -> str:
    command = compose(
        "exec",
        "-T",
        SERVICE,
        "psql",
        "-X",
        "-v",
        "ON_ERROR_STOP=1",
        "-U",
        DB_USER,
        "-d",
        DB_NAME,
    )
    if tuples:
        command.append("-At")
    return run(command, input_text=sql, echo=echo).stdout.strip()


def wait_until_healthy() -> str:
    deadline = time.monotonic() + 75
    last = "container-not-created"
    while time.monotonic() < deadline:
        probe = run(compose("ps", "-q", SERVICE), echo=False, check=False)
        container_id = probe.stdout.strip()
        if container_id:
            health = run(
                ["docker", "inspect", "--format", "{{.State.Health.Status}}", container_id],
                echo=False,
                check=False,
            )
            last = health.stdout.strip() or health.stderr.strip()
            if health.returncode == 0 and last == "healthy":
                print(f"HEALTH service={SERVICE} status=healthy container={container_id[:12]}")
                return container_id
        time.sleep(1)
    raise RuntimeError(f"PostgreSQL did not become healthy: {last}")


def verify_runtime_identity(container_id: str) -> None:
    details = json.loads(run(["docker", "inspect", container_id], echo=False).stdout)[0]
    labels = details.get("Config", {}).get("Labels", {}) or {}
    if labels.get("com.docker.compose.project") != PROJECT:
        raise RuntimeError("container project label mismatch")
    if labels.get("com.docker.compose.service") != SERVICE:
        raise RuntimeError("container service label mismatch")
    if labels.get("com.rahulyadav.learning-task") != TASK_ID:
        raise RuntimeError("container task label mismatch")

    bindings = details.get("NetworkSettings", {}).get("Ports", {}).get("5432/tcp") or []
    if len(bindings) != 1 or bindings[0].get("HostIp") != "127.0.0.1" or bindings[0].get("HostPort") != "55450":
        raise RuntimeError(f"loopback port mismatch: {bindings}")

    mounts = details.get("Mounts", [])
    if not any(item.get("Type") == "volume" and item.get("Name") == VOLUME for item in mounts):
        raise RuntimeError(f"task volume not mounted: {mounts}")
    volume = json.loads(run(["docker", "volume", "inspect", VOLUME], echo=False).stdout)[0]
    volume_labels = volume.get("Labels", {}) or {}
    if volume_labels.get("com.rahulyadav.learning-task") != TASK_ID:
        raise RuntimeError("volume task label mismatch")

    print(
        "RUNTIME_IDENTITY "
        f"project={PROJECT} service={SERVICE} port=127.0.0.1:55450 "
        f"database={DB_NAME} schema={SCHEMA} volume={VOLUME} labels=verified"
    )


def load_reference_schema() -> None:
    schema_sql = (REFERENCE / "00_schema.sql").read_text(encoding="utf-8")
    psql(schema_sql)
    objects = psql(
        """
        SELECT count(*)
        FROM information_schema.tables
        WHERE table_schema = 'sd_beg_050_t01'
          AND table_type = 'BASE TABLE';
        """,
        tuples=True,
    )
    if objects != "5":
        raise RuntimeError(f"expected five reference tables, found {objects}")
    print("SCHEMA_CHECK tables=5 status=passed")


def open_transaction_then_crash() -> None:
    open_sql = """
    BEGIN;
    SET search_path TO sd_beg_050_t01, pg_catalog;
    INSERT INTO app_user(id, email) VALUES (1001, 'open-transaction@example.test');
    SELECT pg_backend_pid() AS crash_backend_pid;
    SELECT pg_sleep(300);
    INSERT INTO profile(user_id, display_name) VALUES (1001, 'Should Not Commit');
    COMMIT;
    """
    command = compose(
        "exec",
        "-T",
        "-e",
        "PGAPPNAME=sd_beg_050_open_transaction",
        SERVICE,
        "psql",
        "-X",
        "-v",
        "ON_ERROR_STOP=1",
        "-U",
        DB_USER,
        "-d",
        DB_NAME,
    )
    print(f"$ {shown(command)}  # open transaction and wait", flush=True)
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    assert process.stdin is not None
    process.stdin.write(open_sql)
    process.stdin.close()

    deadline = time.monotonic() + 30
    confirmed = False
    while time.monotonic() < deadline:
        active = psql(
            """
            SELECT count(*)
            FROM pg_stat_activity
            WHERE application_name = 'sd_beg_050_open_transaction'
              AND xact_start IS NOT NULL
              AND state = 'active';
            """,
            tuples=True,
            echo=False,
        )
        if active == "1":
            confirmed = True
            break
        time.sleep(0.5)
    if not confirmed:
        process.terminate()
        raise RuntimeError("open transaction was not observable before failure injection")
    print("OPEN_TRANSACTION_CONFIRMED active=1 commit_not_sent=true")

    run(compose("kill", "--signal", "SIGKILL", SERVICE))
    process.wait(timeout=30)
    stdout = process.stdout.read().strip() if process.stdout else ""
    stderr = process.stderr.read().strip() if process.stderr else ""
    relevant = [line for line in (stdout + "\n" + stderr).splitlines() if line.strip()]
    print("INTERRUPTED_SESSION_EVIDENCE")
    for line in relevant[-8:]:
        print(line)

    run(compose("up", "-d", SERVICE), timeout=180)
    wait_until_healthy()
    counts = psql(
        """
        SET search_path TO sd_beg_050_t01, pg_catalog;
        SELECT (SELECT count(*) FROM app_user), (SELECT count(*) FROM profile);
        """,
        tuples=True,
    ).splitlines()[-1]
    if counts != "0|0":
        raise RuntimeError(f"atomicity check failed after crash: {counts}")
    print("OPEN_TRANSACTION_RECOVERY users=0 profiles=0 status=passed")


def commit_then_crash() -> None:
    psql(
        """
        BEGIN;
        SET search_path TO sd_beg_050_t01, pg_catalog;
        INSERT INTO app_user(id, email) VALUES (2002, 'committed@example.test');
        INSERT INTO profile(user_id, display_name) VALUES (2002, 'Committed Pair');
        COMMIT;
        """
    )
    before = psql(
        """
        SET search_path TO sd_beg_050_t01, pg_catalog;
        SELECT (SELECT count(*) FROM app_user), (SELECT count(*) FROM profile);
        """,
        tuples=True,
    ).splitlines()[-1]
    if before != "1|1":
        raise RuntimeError(f"committed baseline was not 1|1: {before}")
    print("COMMITTED_BASELINE users=1 profiles=1")

    run(compose("kill", "--signal", "SIGKILL", SERVICE))
    run(compose("up", "-d", SERVICE), timeout=180)
    wait_until_healthy()
    after = psql(
        """
        SET search_path TO sd_beg_050_t01, pg_catalog;
        SELECT (SELECT count(*) FROM app_user), (SELECT count(*) FROM profile);
        """,
        tuples=True,
    ).splitlines()[-1]
    if after != "1|1":
        raise RuntimeError(f"durability check failed after crash: {after}")
    print("COMMITTED_RECOVERY users=1 profiles=1 status=passed")


def verify_constraints() -> None:
    marker = psql(
        """
        SET search_path TO sd_beg_050_t01, pg_catalog;
        DO $block$
        BEGIN
          BEGIN
            INSERT INTO profile(user_id, display_name)
            VALUES (999999, 'Missing Parent');
            RAISE EXCEPTION 'foreign key unexpectedly accepted missing parent';
          EXCEPTION WHEN foreign_key_violation THEN
            RAISE NOTICE 'EXPECTED_FOREIGN_KEY_VIOLATION';
          END;

          INSERT INTO app_user(id, email) VALUES (3003, 'cascade@example.test');
          INSERT INTO profile(user_id, display_name) VALUES (3003, 'Cascade Pair');
          DELETE FROM app_user WHERE id = 3003;
          IF EXISTS (SELECT 1 FROM profile WHERE user_id = 3003) THEN
            RAISE EXCEPTION 'profile did not cascade with owned user';
          END IF;
        END
        $block$;
        SELECT 'CONSTRAINTS_AND_CASCADE_OK';
        """,
        tuples=True,
    )
    if "CONSTRAINTS_AND_CASCADE_OK" not in marker:
        raise RuntimeError("constraint marker missing")
    print("CONSTRAINT_CHECK foreign_key=passed cascade=passed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--confirm-task-local-crash",
        action="store_true",
        help="required acknowledgement that this kills only the verified task-local PostgreSQL service",
    )
    args = parser.parse_args()
    if not args.confirm_task_local_crash:
        raise SystemExit(
            "Refusing failure injection without --confirm-task-local-crash"
        )

    print("PREDICTION open_transaction_crash=users:0,profiles:0")
    print("VARIATION_PREDICTION committed_then_crash=users:1,profiles:1")
    run([sys.executable, str(HERE / "preflight.py")])
    run(compose("up", "-d", SERVICE), timeout=180)
    container_id = wait_until_healthy()
    verify_runtime_identity(container_id)

    server = psql(
        """
        SELECT current_database(), current_user, current_setting('server_version');
        SHOW fsync;
        SHOW synchronous_commit;
        """,
        tuples=True,
    )
    print("SERVER_AND_DURABILITY_SETTINGS")
    print(server)

    load_reference_schema()
    verify_constraints()
    open_transaction_then_crash()
    commit_then_crash()
    print("SD-BEG-050-T01_REFERENCE_VERIFIED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"REFERENCE_VERIFICATION_FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)

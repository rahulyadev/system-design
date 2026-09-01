#!/usr/bin/env python3
"""Execute and assert the SD-BEG-060 PostgreSQL isolation reference path."""

from __future__ import annotations

import json
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
REFERENCE = HERE.parent / "reference"
ROOT = HERE.parents[5]
PROJECT = "system-design-learning"
SERVICE = "postgres"
TASK_ID = "SD-BEG-060-T01"
DB_USER = "sd_learner"
DB_NAME = "sd_learning"
SCHEMA = "sd_beg_060_t01"
PORT = "55434"
VOLUME = "system-design-learning-postgres-18"
COMPOSE = [
    "docker",
    "compose",
    "-f",
    str(ROOT / "compose.yaml"),
    "--project-name",
    PROJECT,
    "--profile",
    "postgres",
]
ACTIVE_SESSIONS: list["PsqlSession"] = []


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


def psql(sql: str, *, echo: bool = False, timeout: int = 30) -> list[str]:
    command = compose(
        "exec",
        "-T",
        SERVICE,
        "psql",
        "-X",
        "-qAt",
        "-v",
        "ON_ERROR_STOP=1",
        "-U",
        DB_USER,
        "-d",
        DB_NAME,
    )
    output = run(
        command,
        input_text=sql,
        echo=echo,
        timeout=timeout,
    ).stdout
    return [line.strip() for line in output.splitlines() if line.strip()]


class PsqlSession:
    """A persistent psql backend with marker-based command coordination."""

    def __init__(self, application_name: str) -> None:
        self.application_name = application_name
        self.counter = 0
        self.command = compose(
            "exec",
            "-T",
            "-e",
            f"PGAPPNAME={application_name}",
            SERVICE,
            "psql",
            "-X",
            "-qAt",
            "-v",
            "ON_ERROR_STOP=1",
            "-U",
            DB_USER,
            "-d",
            DB_NAME,
        )
        self.process = subprocess.Popen(
            self.command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )
        if self.process.stdin is None or self.process.stdout is None:
            raise RuntimeError(f"failed to open psql pipes for {application_name}")
        self.stdout_queue: queue.Queue[str | None] = queue.Queue()

        def pump_stdout() -> None:
            assert self.process.stdout is not None
            for line in self.process.stdout:
                self.stdout_queue.put(line.rstrip("\n"))
            self.stdout_queue.put(None)

        self.stdout_thread = threading.Thread(
            target=pump_stdout,
            name=f"{application_name}-stdout",
            daemon=True,
        )
        self.stdout_thread.start()
        self.process.stdin.write("\\set VERBOSITY verbose\n")
        self.process.stdin.flush()
        ACTIVE_SESSIONS.append(self)
        pid_lines = self.execute("SELECT pg_backend_pid();", timeout=10)
        if len(pid_lines) != 1 or not pid_lines[0].isdigit():
            raise RuntimeError(
                f"could not identify backend for {application_name}: {pid_lines}"
            )
        self.backend_pid = int(pid_lines[0])

    def send(self, sql: str) -> str:
        if self.process.poll() is not None:
            raise RuntimeError(f"session {self.application_name} already exited")
        assert self.process.stdin is not None
        self.counter += 1
        marker = f"__{self.application_name}_{self.counter}_DONE__"
        self.process.stdin.write(sql.rstrip() + "\n")
        self.process.stdin.write(f"SELECT '{marker}';\n")
        self.process.stdin.flush()
        return marker

    def read_until(self, marker: str, *, timeout: float = 12) -> list[str]:
        lines: list[str] = []
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            remaining = max(0.0, deadline - time.monotonic())
            try:
                line = self.stdout_queue.get(timeout=remaining)
            except queue.Empty:
                break
            if line is None:
                break
            stripped = line.strip()
            if stripped == marker:
                return lines
            if stripped:
                lines.append(stripped)
        stderr = self._stderr_if_exited()
        raise RuntimeError(
            f"session {self.application_name} did not reach marker {marker}; "
            f"output={lines}, stderr={stderr or 'none'}, returncode={self.process.poll()}"
        )

    def execute(self, sql: str, *, timeout: float = 12) -> list[str]:
        return self.read_until(self.send(sql), timeout=timeout)

    def expect_failure_after_send(
        self,
        marker: str,
        *,
        sqlstate: str,
        timeout: float = 12,
    ) -> str:
        assert self.process.stderr is not None
        try:
            self.process.wait(timeout=timeout)
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"session {self.application_name} did not fail as expected"
            ) from exc
        stdout_lines: list[str] = []
        drain_deadline = time.monotonic() + 2
        while time.monotonic() < drain_deadline:
            try:
                line = self.stdout_queue.get(timeout=0.1)
            except queue.Empty:
                if not self.stdout_thread.is_alive():
                    break
                continue
            if line is None:
                break
            stdout_lines.append(line)
        stdout = "\n".join(stdout_lines)
        stderr = self.process.stderr.read()
        combined = stdout + "\n" + stderr
        if marker in stdout:
            raise RuntimeError(
                f"session {self.application_name} unexpectedly reached success marker"
            )
        if self.process.returncode == 0 or sqlstate not in combined:
            raise RuntimeError(
                f"session {self.application_name} expected SQLSTATE {sqlstate}; "
                f"returncode={self.process.returncode}, output={combined.strip()}"
            )
        return combined.strip()

    def expect_failure(
        self,
        sql: str,
        *,
        sqlstate: str,
        timeout: float = 12,
    ) -> str:
        marker = self.send(sql)
        return self.expect_failure_after_send(
            marker,
            sqlstate=sqlstate,
            timeout=timeout,
        )

    def _stderr_if_exited(self) -> str:
        if self.process.poll() is None or self.process.stderr is None:
            return ""
        return self.process.stderr.read().strip()

    def close(self) -> None:
        if self.process.poll() is None:
            try:
                assert self.process.stdin is not None
                self.process.stdin.write("ROLLBACK;\n\\q\n")
                self.process.stdin.flush()
                self.process.stdin.close()
                self.process.wait(timeout=3)
            except (BrokenPipeError, subprocess.TimeoutExpired):
                self.process.terminate()
                try:
                    self.process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.process.kill()
                    self.process.wait(timeout=3)
        if self in ACTIVE_SESSIONS:
            ACTIVE_SESSIONS.remove(self)


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
                print(
                    f"HEALTH service={SERVICE} status=healthy "
                    f"container={container_id[:12]}"
                )
                return container_id
        time.sleep(1)
    raise RuntimeError(f"PostgreSQL did not become healthy: {last}")


def verify_runtime_identity(container_id: str) -> None:
    context_name = run(["docker", "context", "show"], echo=False).stdout.strip()
    contexts = json.loads(
        run(["docker", "context", "inspect", context_name], echo=False).stdout
    )
    endpoint = contexts[0].get("Endpoints", {}).get("docker", {}).get("Host", "")
    if not isinstance(endpoint, str) or not endpoint.startswith("unix://"):
        raise RuntimeError(
            f"refusing non-local Docker endpoint: context={context_name} endpoint={endpoint}"
        )

    details = json.loads(run(["docker", "inspect", container_id], echo=False).stdout)[0]
    config = details.get("Config", {}) or {}
    labels = config.get("Labels", {}) or {}
    if labels.get("com.docker.compose.project") != PROJECT:
        raise RuntimeError("container project label mismatch")
    if labels.get("com.docker.compose.service") != SERVICE:
        raise RuntimeError("container service label mismatch")
    if labels.get("com.rahulyadav.learning-system") != "system-design":
        raise RuntimeError("container learning-system label mismatch")
    if labels.get("com.rahulyadav.disposable") != "true":
        raise RuntimeError("container disposable label mismatch")
    if config.get("Image") != "postgres:18.6":
        raise RuntimeError(f"container image mismatch: {config.get('Image')}")

    environment = {}
    for item in config.get("Env", []) or []:
        if "=" in item:
            key, value = item.split("=", 1)
            environment[key] = value
    if environment.get("POSTGRES_USER") != DB_USER:
        raise RuntimeError("synthetic PostgreSQL user mismatch")
    if environment.get("POSTGRES_DB") != DB_NAME:
        raise RuntimeError("synthetic PostgreSQL database mismatch")
    if environment.get("PGDATA") != "/var/lib/postgresql/18/docker":
        raise RuntimeError("PostgreSQL 18 PGDATA mismatch")

    bindings = details.get("NetworkSettings", {}).get("Ports", {}).get("5432/tcp") or []
    if (
        len(bindings) != 1
        or bindings[0].get("HostIp") != "127.0.0.1"
        or bindings[0].get("HostPort") != PORT
    ):
        raise RuntimeError(f"loopback port mismatch: {bindings}")

    mounts = details.get("Mounts", []) or []
    if not any(
        item.get("Type") == "volume" and item.get("Name") == VOLUME
        for item in mounts
    ):
        raise RuntimeError(f"shared learning volume not mounted: {mounts}")
    volume = json.loads(
        run(["docker", "volume", "inspect", VOLUME], echo=False).stdout
    )[0]
    volume_labels = volume.get("Labels", {}) or {}
    if volume_labels.get("com.rahulyadav.learning-system") != "system-design":
        raise RuntimeError("volume learning-system label mismatch")
    if volume_labels.get("com.rahulyadav.disposable") != "true":
        raise RuntimeError("volume disposable label mismatch")

    print(
        "RUNTIME_IDENTITY "
        f"context={context_name} endpoint=local-unix project={PROJECT} "
        f"service={SERVICE} image=postgres:18.6 port=127.0.0.1:{PORT} "
        f"database={DB_NAME} user={DB_USER} schema={SCHEMA} "
        f"volume={VOLUME} labels=verified"
    )


def load_reference_schema() -> None:
    sql = (REFERENCE / "00_schema.sql").read_text(encoding="utf-8")
    output = psql(sql)
    if output[-1:] != ["1|A"]:
        raise RuntimeError(f"reference schema did not produce one A row: {output}")
    print("SCHEMA_CHECK schema=sd_beg_060_t01 rows=1 initial=A status=passed")


def reset_row() -> None:
    output = psql(
        """
        TRUNCATE sd_beg_060_t01.users;
        INSERT INTO sd_beg_060_t01.users(id, name) VALUES (1, 'A');
        SELECT count(*), min(name) FROM sd_beg_060_t01.users;
        """
    )
    if output[-1:] != ["1|A"]:
        raise RuntimeError(f"row reset failed: {output}")


def committed_update(value: str, *, isolation: str = "READ COMMITTED") -> None:
    output = psql(
        f"""
        BEGIN ISOLATION LEVEL {isolation};
        UPDATE sd_beg_060_t01.users SET name = '{value}' WHERE id = 1;
        COMMIT;
        SELECT name FROM sd_beg_060_t01.users WHERE id = 1;
        """
    )
    if output[-1:] != [value]:
        raise RuntimeError(f"committed update to {value} failed: {output}")


def verify_read_committed() -> None:
    reset_row()
    reader = PsqlSession("sd_beg_060_t01_rc_reader")
    try:
        first = reader.execute(
            """
            BEGIN ISOLATION LEVEL READ COMMITTED;
            SHOW transaction_isolation;
            SELECT name FROM sd_beg_060_t01.users WHERE id = 1;
            """
        )
        if first != ["read committed", "A"]:
            raise RuntimeError(f"Read Committed first observation mismatch: {first}")
        committed_update("B_RC")
        second = reader.execute(
            "SELECT name FROM sd_beg_060_t01.users WHERE id = 1;"
        )
        if second != ["B_RC"]:
            raise RuntimeError(f"Read Committed second observation mismatch: {second}")
        reader.execute("COMMIT;")
    finally:
        reader.close()
    print(
        "READ_COMMITTED isolation=read_committed first=A "
        "writer=commit:B_RC second=B_RC status=passed"
    )


def verify_repeatable_read() -> None:
    reset_row()
    reader = PsqlSession("sd_beg_060_t01_rr_reader")
    try:
        first = reader.execute(
            """
            BEGIN ISOLATION LEVEL REPEATABLE READ;
            SHOW transaction_isolation;
            SELECT name FROM sd_beg_060_t01.users WHERE id = 1;
            """
        )
        if first != ["repeatable read", "A"]:
            raise RuntimeError(f"Repeatable Read first observation mismatch: {first}")
        committed_update("B_RR")
        second = reader.execute(
            "SELECT name FROM sd_beg_060_t01.users WHERE id = 1;"
        )
        if second != ["A"]:
            raise RuntimeError(f"Repeatable Read second observation mismatch: {second}")
        reader.execute("COMMIT;")
    finally:
        reader.close()
    fresh = psql(
        "SELECT name FROM sd_beg_060_t01.users WHERE id = 1;"
    )
    if fresh != ["B_RR"]:
        raise RuntimeError(f"Repeatable Read fresh observation mismatch: {fresh}")
    print(
        "REPEATABLE_READ isolation=repeatable_read first=A "
        "writer=commit:B_RR second=A fresh_transaction=B_RR status=passed"
    )


def verify_read_uncommitted_mapping() -> None:
    reset_row()
    writer = PsqlSession("sd_beg_060_t01_ru_writer")
    reader = PsqlSession("sd_beg_060_t01_ru_reader")
    try:
        writer_view = writer.execute(
            """
            BEGIN ISOLATION LEVEL READ COMMITTED;
            UPDATE sd_beg_060_t01.users SET name = 'B_DIRTY' WHERE id = 1;
            SELECT name FROM sd_beg_060_t01.users WHERE id = 1;
            """
        )
        if writer_view != ["B_DIRTY"]:
            raise RuntimeError(f"writer did not see own uncommitted value: {writer_view}")
        observed = reader.execute(
            """
            BEGIN ISOLATION LEVEL READ UNCOMMITTED;
            SHOW transaction_isolation;
            SELECT name FROM sd_beg_060_t01.users WHERE id = 1;
            """
        )
        if observed != ["read uncommitted", "A"]:
            raise RuntimeError(f"PostgreSQL RU mapping mismatch: {observed}")
        writer.execute("ROLLBACK;")
        after_rollback = reader.execute(
            "SELECT name FROM sd_beg_060_t01.users WHERE id = 1;"
        )
        if after_rollback != ["A"]:
            raise RuntimeError(f"RU reader after rollback mismatch: {after_rollback}")
        reader.execute("COMMIT;")
    finally:
        reader.close()
        writer.close()
    print(
        "READ_UNCOMMITTED_REQUEST reported=read_uncommitted "
        "writer_uncommitted=B_DIRTY reader=A writer=rollback "
        "reader_after_rollback=A mapping=read_committed status=passed"
    )


def verify_serializable_conflict_and_retry() -> None:
    reset_row()
    stale = PsqlSession("sd_beg_060_t01_ser_stale")
    try:
        first = stale.execute(
            """
            BEGIN ISOLATION LEVEL SERIALIZABLE;
            SHOW transaction_isolation;
            SELECT name FROM sd_beg_060_t01.users WHERE id = 1;
            """
        )
        if first != ["serializable", "A"]:
            raise RuntimeError(f"Serializable first observation mismatch: {first}")
        committed_update("B_SER", isolation="SERIALIZABLE")
        failure = stale.expect_failure(
            """
            UPDATE sd_beg_060_t01.users SET name = 'STALE_WRITE' WHERE id = 1;
            COMMIT;
            """,
            sqlstate="40001",
        )
        if "could not serialize access due to concurrent update" not in failure:
            raise RuntimeError(f"unexpected Serializable failure: {failure}")
    finally:
        stale.close()

    current = psql("SELECT name FROM sd_beg_060_t01.users WHERE id = 1;")
    if current != ["B_SER"]:
        raise RuntimeError(f"failed stale attempt changed committed state: {current}")
    retry = psql(
        """
        BEGIN ISOLATION LEVEL SERIALIZABLE;
        SELECT name FROM sd_beg_060_t01.users WHERE id = 1;
        UPDATE sd_beg_060_t01.users SET name = 'T1_RETRY' WHERE id = 1
        RETURNING name;
        COMMIT;
        SELECT name FROM sd_beg_060_t01.users WHERE id = 1;
        """
    )
    if retry != ["B_SER", "T1_RETRY", "T1_RETRY"]:
        raise RuntimeError(f"whole-transaction retry mismatch: {retry}")
    print(
        "SERIALIZABLE_CONFLICT first=A concurrent_commit=B_SER "
        "stale_attempt_sqlstate=40001 stale_write_committed=false "
        "retry_read=B_SER retry_commit=T1_RETRY status=passed"
    )


def wait_for_lock(blocked_pid: int, blocker_pid: int) -> tuple[str, str, str]:
    deadline = time.monotonic() + 12
    last: list[str] = []
    while time.monotonic() < deadline:
        last = psql(
            f"""
            SELECT coalesce(wait_event_type, ''),
                   coalesce(wait_event, ''),
                   array_to_string(pg_blocking_pids(pid), ',')
            FROM pg_stat_activity
            WHERE pid = {blocked_pid};
            """
        )
        if last:
            fields = last[-1].split("|")
            if (
                len(fields) == 3
                and fields[0] == "Lock"
                and str(blocker_pid) in fields[2].split(",")
            ):
                return fields[0], fields[1], fields[2]
        time.sleep(0.25)
    raise RuntimeError(
        f"locking reader {blocked_pid} did not expose blocker {blocker_pid}: {last}"
    )


def verify_plain_vs_locking_read() -> None:
    reset_row()
    writer = PsqlSession("sd_beg_060_t01_lock_writer")
    plain = PsqlSession("sd_beg_060_t01_plain_reader")
    locker = PsqlSession("sd_beg_060_t01_locking_reader")
    try:
        writer_own = writer.execute(
            """
            BEGIN ISOLATION LEVEL SERIALIZABLE;
            UPDATE sd_beg_060_t01.users SET name = 'B_PENDING' WHERE id = 1;
            SELECT name FROM sd_beg_060_t01.users WHERE id = 1;
            """
        )
        if writer_own != ["B_PENDING"]:
            raise RuntimeError(f"locking writer setup mismatch: {writer_own}")

        started = time.monotonic()
        plain_first = plain.execute(
            """
            BEGIN ISOLATION LEVEL SERIALIZABLE;
            SELECT name FROM sd_beg_060_t01.users WHERE id = 1;
            """,
            timeout=5,
        )
        plain_seconds = time.monotonic() - started
        if plain_first != ["A"] or plain_seconds >= 5:
            raise RuntimeError(
                f"plain Serializable read mismatch: {plain_first}, {plain_seconds:.3f}s"
            )

        marker = locker.send(
            """
            BEGIN ISOLATION LEVEL SERIALIZABLE;
            SELECT name FROM sd_beg_060_t01.users WHERE id = 1 FOR UPDATE;
            """
        )
        wait_type, wait_event, blockers = wait_for_lock(
            locker.backend_pid,
            writer.backend_pid,
        )
        print(
            "LOCK_WAIT "
            f"blocked_pid={locker.backend_pid} blocker_pid={writer.backend_pid} "
            f"wait_event_type={wait_type} wait_event={wait_event} "
            f"pg_blocking_pids={blockers} status=observed"
        )

        writer.execute("COMMIT;")
        locking_failure = locker.expect_failure_after_send(
            marker,
            sqlstate="40001",
            timeout=12,
        )
        if "could not serialize access due to concurrent update" not in locking_failure:
            raise RuntimeError(
                f"locking reader had unexpected post-wait failure: {locking_failure}"
            )

        plain_second = plain.execute(
            "SELECT name FROM sd_beg_060_t01.users WHERE id = 1;"
        )
        if plain_second != ["A"]:
            raise RuntimeError(f"plain Serializable snapshot changed: {plain_second}")
        plain.execute("COMMIT;")
    finally:
        locker.close()
        plain.close()
        writer.close()

    fresh = psql("SELECT name FROM sd_beg_060_t01.users WHERE id = 1;")
    if fresh != ["B_PENDING"]:
        raise RuntimeError(f"fresh value after locking variation mismatch: {fresh}")
    print(
        "PLAIN_VS_LOCKING_READ plain_first=A plain_wait=false "
        f"plain_elapsed_ms={plain_seconds * 1000:.1f} "
        "locking_read_wait=true locking_read_sqlstate=40001 "
        "plain_second=A fresh_transaction=B_PENDING status=passed"
    )


def cleanup_schema(*, echo: bool = True) -> None:
    reset_sql = (HERE / "05_reset.sql").read_text(encoding="utf-8")
    output = psql(reset_sql, echo=echo)
    if output[-1:] != ["t"]:
        raise RuntimeError(f"scoped schema cleanup did not verify removal: {output}")
    print(
        "CLEANUP database=sd_learning user=sd_learner "
        "schema=sd_beg_060_t01 removed=true shared_volume=retained status=passed"
    )


def close_all_sessions() -> None:
    for session in list(reversed(ACTIVE_SESSIONS)):
        session.close()


def main() -> int:
    print("PREDICTION read_committed=A_to_B")
    print("PREDICTION repeatable_read=A_to_A_then_fresh_B")
    print("PREDICTION postgres_read_uncommitted=no_dirty_read")
    print("PREDICTION serializable_stale_update=sqlstate_40001_then_full_retry")
    print(
        "VARIATION_PREDICTION plain_serializable_read=no_wait; "
        "select_for_update=lock_wait_then_40001"
    )

    run(
        [
            sys.executable,
            str(ROOT / "scripts" / "lab_preflight.py"),
            "--compose-file",
            str(ROOT / "compose.yaml"),
            "--project",
            PROJECT,
            "--service",
            SERVICE,
        ]
    )
    run(compose("up", "-d", SERVICE), timeout=180)
    container_id = wait_until_healthy()
    verify_runtime_identity(container_id)

    safe_to_reset = True
    completed_cleanup = False
    try:
        server = psql(
            """
            SELECT current_database(), current_user, current_setting('server_version');
            SHOW default_transaction_isolation;
            """
        )
        server_identity = server[0].split("|") if server else []
        if (
            len(server) != 2
            or len(server_identity) != 3
            or server_identity[0] != DB_NAME
            or server_identity[1] != DB_USER
            or not server_identity[2].startswith("18.6")
            or server[1] != "read committed"
        ):
            raise RuntimeError(f"server/default isolation mismatch: {server}")
        print(
            f"SERVER version={server_identity[2]} database=sd_learning user=sd_learner "
            "default_isolation=read_committed"
        )

        load_reference_schema()
        verify_read_committed()
        verify_repeatable_read()
        verify_read_uncommitted_mapping()
        verify_serializable_conflict_and_retry()
        verify_plain_vs_locking_read()
        close_all_sessions()
        cleanup_schema()
        completed_cleanup = True
        print("SD-BEG-060-T01_REFERENCE_VERIFIED")
        return 0
    finally:
        close_all_sessions()
        if safe_to_reset and not completed_cleanup:
            try:
                cleanup_schema(echo=False)
            except Exception as cleanup_error:  # noqa: BLE001 - preserve primary failure
                print(
                    f"SCOPED_CLEANUP_FAILED: {cleanup_error}",
                    file=sys.stderr,
                )


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, subprocess.TimeoutExpired, json.JSONDecodeError) as exc:
        print(f"REFERENCE_VERIFICATION_FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)

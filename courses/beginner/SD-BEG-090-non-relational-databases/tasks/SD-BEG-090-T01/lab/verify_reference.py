#!/usr/bin/env python3
"""Execute and assert the isolated SD-BEG-090-T01 reference exploration."""

from __future__ import annotations

import json
import platform
import re
import subprocess
import sys
import time
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROJECT = "sd-beg-090-t01"
TASK_ID = "SD-BEG-090-T01"
MONGO_USER = "sd_beg_090_t01_root"
MONGO_PASSWORD = "sd_beg_090_t01_mongo_local"
REDIS_PASSWORD = "sd_beg_090_t01_redis_local"
NEO4J_PASSWORD = "sd_beg_090_t01_neo4j_local"
SERVICES = {
    "mongo": {
        "image": "mongo:8.0.29-noble",
        "ports": {"27017/tcp": ("127.0.0.1", "55901")},
        "volume": "sd-beg-090-t01-mongo-8-0-data",
    },
    "redis": {
        "image": "redis:8.10.1-alpine3.23",
        "ports": {"6379/tcp": ("127.0.0.1", "55902")},
        "volume": "sd-beg-090-t01-redis-8-10-data",
    },
    "neo4j": {
        "image": "neo4j:2026.07.1",
        "ports": {
            "7687/tcp": ("127.0.0.1", "55903"),
            "7474/tcp": ("127.0.0.1", "55904"),
        },
        "volume": "sd-beg-090-t01-neo4j-2026-07-data",
    },
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


def shown(command: list[str]) -> str:
    return " ".join(command)


def run(
    command: list[str],
    *,
    check: bool = True,
    echo: bool = True,
    timeout: int = 300,
) -> subprocess.CompletedProcess[str]:
    if echo:
        print(f"$ {shown(command)}", flush=True)
    completed = subprocess.run(
        command,
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


def wait_until_healthy(service: str) -> str:
    deadline = time.monotonic() + 180
    last = "container-not-created"
    while time.monotonic() < deadline:
        probe = run(compose("ps", "-q", service), echo=False, check=False)
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
                    f"HEALTH service={service} status=healthy container={container_id[:12]}"
                )
                return container_id
        time.sleep(1)
    raise RuntimeError(f"{service} did not become healthy: {last}")


def verify_runtime_identity(service: str, container_id: str) -> None:
    expected = SERVICES[service]
    details = json.loads(run(["docker", "inspect", container_id], echo=False).stdout)[0]
    labels = details.get("Config", {}).get("Labels", {}) or {}
    if labels.get("com.docker.compose.project") != PROJECT:
        raise RuntimeError(f"{service} container project label mismatch")
    if labels.get("com.docker.compose.service") != service:
        raise RuntimeError(f"{service} container service label mismatch")
    if labels.get("com.rahulyadav.learning-task") != TASK_ID:
        raise RuntimeError(f"{service} container task label mismatch")
    if details.get("Config", {}).get("Image") != expected["image"]:
        raise RuntimeError(f"{service} image mismatch")

    actual_ports = details.get("NetworkSettings", {}).get("Ports", {}) or {}
    for container_port, (host_ip, host_port) in expected["ports"].items():
        bindings = actual_ports.get(container_port) or []
        if (
            len(bindings) != 1
            or bindings[0].get("HostIp") != host_ip
            or bindings[0].get("HostPort") != host_port
        ):
            raise RuntimeError(
                f"{service} loopback port mismatch for {container_port}: {bindings}"
            )

    mounts = details.get("Mounts", [])
    if not any(
        item.get("Type") == "volume" and item.get("Name") == expected["volume"]
        for item in mounts
    ):
        raise RuntimeError(f"{service} task volume not mounted: {mounts}")
    volume = json.loads(
        run(["docker", "volume", "inspect", expected["volume"]], echo=False).stdout
    )[0]
    volume_labels = volume.get("Labels", {}) or {}
    if volume_labels.get("com.rahulyadav.learning-task") != TASK_ID:
        raise RuntimeError(f"{service} volume task label mismatch")

    ports = ",".join(
        f"{host_ip}:{host_port}->{container_port}"
        for container_port, (host_ip, host_port) in expected["ports"].items()
    )
    print(
        "RUNTIME_IDENTITY "
        f"project={PROJECT} service={service} image={expected['image']} "
        f"ports={ports} volume={expected['volume']} labels=verified"
    )


def start_service(service: str) -> str:
    run(compose("up", "-d", service), timeout=600)
    container_id = wait_until_healthy(service)
    verify_runtime_identity(service, container_id)
    return container_id


def stop_service(service: str, *, check: bool = True) -> None:
    run(compose("stop", "--timeout", "60", service), check=check, timeout=180)
    state = run(
        compose("ps", "-a", "--format", "json", service),
        check=False,
        echo=False,
    ).stdout.strip()
    print(f"CLEANUP service={service} action=stopped volume=retained state={state or 'not-listed'}")


def parse_json_line(output: str) -> dict[str, object]:
    for line in reversed(output.splitlines()):
        candidate = line.strip()
        if candidate.startswith("{") and candidate.endswith("}"):
            value = json.loads(candidate)
            if isinstance(value, dict):
                return value
    raise RuntimeError(f"JSON result not found in output: {output}")


def mongo_eval(script: str) -> str:
    return run(
        compose(
            "exec",
            "-T",
            "mongo",
            "mongosh",
            "--quiet",
            "--username",
            MONGO_USER,
            "--password",
            MONGO_PASSWORD,
            "--authenticationDatabase",
            "admin",
            "--eval",
            script,
        )
    ).stdout.strip()


def verify_mongo() -> None:
    result = parse_json_line(
        mongo_eval(
            """
const d = db.getSiblingDB('sd_beg_090_t01');
d.products.deleteMany({lab_id: 'SD-BEG-090-T01'});
d.products.insertMany([
  {_id: 'book-1', lab_id: 'SD-BEG-090-T01', title: 'Distributed Systems', category: 'book', stock: 2, author: 'Example Author'},
  {_id: 'shirt-1', lab_id: 'SD-BEG-090-T01', title: 'Learning Lab Shirt', category: 'apparel', stock: 5, size: 'M'}
]);
const before = d.products.findOne({_id: 'book-1'}).stock;
const updated = d.products.updateOne(
  {_id: 'book-1', lab_id: 'SD-BEG-090-T01'},
  {$inc: {stock: 1}}
);
const book = d.products.findOne({_id: 'book-1'});
const groups = d.products.aggregate([
  {$match: {lab_id: 'SD-BEG-090-T01'}},
  {$group: {_id: '$category', products: {$sum: 1}}},
  {$sort: {_id: 1}}
]).toArray();
print(JSON.stringify({
  server_version: d.version(),
  document_count: d.products.countDocuments({lab_id: 'SD-BEG-090-T01'}),
  size_m_count: d.products.countDocuments({lab_id: 'SD-BEG-090-T01', size: 'M'}),
  book_has_size: Object.prototype.hasOwnProperty.call(book, 'size'),
  stock_before: before,
  stock_after: book.stock,
  matched_count: updated.matchedCount,
  modified_count: updated.modifiedCount,
  groups: groups
}));
"""
        )
    )
    if not str(result.get("server_version", "")).startswith("8.0.29"):
        raise RuntimeError(f"unexpected MongoDB version: {result}")
    expected = {
        "document_count": 2,
        "size_m_count": 1,
        "book_has_size": False,
        "stock_before": 2,
        "stock_after": 3,
        "matched_count": 1,
        "modified_count": 1,
    }
    for key, value in expected.items():
        if result.get(key) != value:
            raise RuntimeError(f"MongoDB assertion failed for {key}: {result}")
    groups = result.get("groups")
    if groups != [
        {"_id": "apparel", "products": 1},
        {"_id": "book", "products": 1},
    ]:
        raise RuntimeError(f"MongoDB aggregation mismatch: {groups}")
    print(
        "MONGODB_OBSERVED "
        + json.dumps(result, sort_keys=True, separators=(",", ":"))
    )
    print("MONGODB_REFERENCE_CHECK status=passed")


def mongo_kernel_skip_reason() -> str | None:
    release = platform.release()
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", release)
    if match is None:
        return None
    version = tuple(int(item) for item in match.groups())
    if (6, 19, 0) <= version <= (7, 0, 13):
        return (
            f"host kernel {release} is in MongoDB's documented incompatible "
            "range 6.19 through 7.0.13"
        )
    return None


def redis_raw(*arguments: str) -> str:
    return run(
        compose(
            "exec",
            "-T",
            "-e",
            f"REDISCLI_AUTH={REDIS_PASSWORD}",
            "redis",
            "redis-cli",
            "--no-auth-warning",
            "--raw",
            *arguments,
        )
    ).stdout.strip()


def verify_redis() -> None:
    version_info = redis_raw("INFO", "server")
    match = re.search(r"(?m)^redis_version:([^\r\n]+)", version_info)
    version = match.group(1) if match else ""
    if version != "8.10.1":
        raise RuntimeError(f"unexpected Redis version: {version!r}")

    keys = (
        "sd:beg:090:t01:profile:42",
        "sd:beg:090:t01:counter",
        "sd:beg:090:t01:temporary",
    )
    redis_raw("DEL", *keys)
    if redis_raw("SET", keys[0], '{"user_id":42,"plan":"pro"}') != "OK":
        raise RuntimeError("Redis SET failed")
    profile = redis_raw("GET", keys[0])
    if profile != '{"user_id":42,"plan":"pro"}':
        raise RuntimeError(f"Redis GET mismatch: {profile!r}")

    if redis_raw("SET", keys[1], "270") != "OK":
        raise RuntimeError("Redis counter SET failed")
    incremented = redis_raw("INCR", keys[1])
    if incremented != "271" or redis_raw("GET", keys[1]) != "271":
        raise RuntimeError(f"Redis INCR mismatch: {incremented!r}")

    if redis_raw("SET", keys[2], "delete-me") != "OK":
        raise RuntimeError("Redis temporary SET failed")
    deleted = redis_raw("DEL", keys[2])
    exists = redis_raw("EXISTS", keys[2])
    if deleted != "1" or exists != "0":
        raise RuntimeError(f"Redis DELETE mismatch: deleted={deleted} exists={exists}")

    result = {
        "server_version": version,
        "profile": profile,
        "counter_after_incr": int(incremented),
        "deleted_count": int(deleted),
        "exists_after_delete": int(exists),
    }
    print(
        "REDIS_OBSERVED "
        + json.dumps(result, sort_keys=True, separators=(",", ":"))
    )
    print("REDIS_REFERENCE_CHECK status=passed")


def cypher(query: str) -> str:
    return run(
        compose(
            "exec",
            "-T",
            "neo4j",
            "cypher-shell",
            "-a",
            "bolt://127.0.0.1:7687",
            "-u",
            "neo4j",
            "-p",
            NEO4J_PASSWORD,
            "--format",
            "plain",
            query,
        )
    ).stdout.strip()


def last_integer(output: str) -> int:
    for line in reversed(output.splitlines()):
        candidate = line.strip()
        if re.fullmatch(r"-?\d+", candidate):
            return int(candidate)
    raise RuntimeError(f"integer result not found in Cypher output: {output}")


def verify_neo4j() -> None:
    version_output = cypher(
        "CALL dbms.components() YIELD name, versions "
        "RETURN name, versions[0] AS version;"
    )
    if "2026.07.1" not in version_output:
        raise RuntimeError(f"unexpected Neo4j version output: {version_output}")

    cypher(
        "MATCH (n:LabPerson {lab_id: 'SD-BEG-090-T01'}) DETACH DELETE n;"
    )
    cypher(
        """
CREATE (a:LabPerson {lab_id: 'SD-BEG-090-T01', name: 'Asha'}),
       (b:LabPerson {lab_id: 'SD-BEG-090-T01', name: 'Ben'}),
       (c:LabPerson {lab_id: 'SD-BEG-090-T01', name: 'Chen'}),
       (a)-[:FOLLOWS {lab_id: 'SD-BEG-090-T01'}]->(b),
       (b)-[:FOLLOWS {lab_id: 'SD-BEG-090-T01'}]->(c);
"""
    )
    node_count = last_integer(
        cypher(
            "MATCH (n:LabPerson {lab_id: 'SD-BEG-090-T01'}) "
            "RETURN count(n) AS node_count;"
        )
    )
    relationship_count = last_integer(
        cypher(
            "MATCH (:LabPerson {lab_id: 'SD-BEG-090-T01'})"
            "-[r:FOLLOWS {lab_id: 'SD-BEG-090-T01'}]->"
            "(:LabPerson {lab_id: 'SD-BEG-090-T01'}) "
            "RETURN count(r) AS relationship_count;"
        )
    )
    baseline_hops = last_integer(
        cypher(
            "MATCH (a:LabPerson {lab_id: 'SD-BEG-090-T01', name: 'Asha'}), "
            "(c:LabPerson {lab_id: 'SD-BEG-090-T01', name: 'Chen'}) "
            "MATCH p=shortestPath((a)-[:FOLLOWS*1..4]->(c)) "
            "RETURN length(p) AS hops;"
        )
    )
    if (node_count, relationship_count, baseline_hops) != (3, 2, 2):
        raise RuntimeError(
            "Neo4j baseline mismatch: "
            f"nodes={node_count} relationships={relationship_count} hops={baseline_hops}"
        )
    print(
        "NEO4J_BASELINE "
        f"nodes={node_count} relationships={relationship_count} shortest_hops={baseline_hops}"
    )

    print("VARIATION_PREDICTION add_direct_edge=shortest_hops:1")
    cypher(
        "MATCH (a:LabPerson {lab_id: 'SD-BEG-090-T01', name: 'Asha'}), "
        "(c:LabPerson {lab_id: 'SD-BEG-090-T01', name: 'Chen'}) "
        "MERGE (a)-[:FOLLOWS {lab_id: 'SD-BEG-090-T01'}]->(c);"
    )
    changed_relationship_count = last_integer(
        cypher(
            "MATCH (:LabPerson {lab_id: 'SD-BEG-090-T01'})"
            "-[r:FOLLOWS {lab_id: 'SD-BEG-090-T01'}]->"
            "(:LabPerson {lab_id: 'SD-BEG-090-T01'}) "
            "RETURN count(r) AS relationship_count;"
        )
    )
    changed_hops = last_integer(
        cypher(
            "MATCH (a:LabPerson {lab_id: 'SD-BEG-090-T01', name: 'Asha'}), "
            "(c:LabPerson {lab_id: 'SD-BEG-090-T01', name: 'Chen'}) "
            "MATCH p=shortestPath((a)-[:FOLLOWS*1..4]->(c)) "
            "RETURN length(p) AS hops;"
        )
    )
    if (changed_relationship_count, changed_hops) != (3, 1):
        raise RuntimeError(
            "Neo4j variation mismatch: "
            f"relationships={changed_relationship_count} hops={changed_hops}"
        )
    print(
        "NEO4J_VARIATION_OBSERVED "
        f"relationships={changed_relationship_count} shortest_hops={changed_hops}"
    )
    print("NEO4J_REFERENCE_CHECK status=passed")


def main() -> int:
    print("PREDICTION mongodb_stock=3 redis_counter=271 neo4j_baseline_hops=2")
    print("VARIATION_PREDICTION neo4j_direct_edge_hops=1")
    run([sys.executable, str(HERE / "preflight.py")])

    active_service: str | None = None
    mongo_skip = mongo_kernel_skip_reason()
    try:
        checks: list[tuple[str, object]] = []
        if mongo_skip is None:
            checks.append(("mongo", verify_mongo))
        else:
            print(
                "MONGODB_EXECUTION_SKIPPED "
                f"reason={json.dumps(mongo_skip)} image=mongo:8.0.29-noble"
            )
            stop_service("mongo", check=False)
        checks.extend((("redis", verify_redis), ("neo4j", verify_neo4j)))

        for service, verifier in checks:
            active_service = service
            start_service(service)
            assert callable(verifier)
            verifier()
            stop_service(service)
            active_service = None
    finally:
        if active_service is not None:
            stop_service(active_service, check=False)

    print("CLEANUP_SUMMARY services=stopped volumes=retained recoverable=true")
    if mongo_skip is not None:
        print(
            "SD-BEG-090-T01_APPLICABLE_CHECKS_PASSED "
            "mongodb=skipped redis=passed neo4j=passed"
        )
    else:
        print("SD-BEG-090-T01_REFERENCE_VERIFIED")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (
        RuntimeError,
        json.JSONDecodeError,
        subprocess.TimeoutExpired,
    ) as exc:
        print(f"REFERENCE_VERIFICATION_FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)

#!/usr/bin/env python3
"""Read-only identity checks for the SD-BEG-090-T01 NoSQL lab."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROJECT = "sd-beg-090-t01"
TASK_ID = "SD-BEG-090-T01"
SERVICES = {
    "mongo": {
        "image": "mongo:8.0.29-noble",
        "ports": {"27017": "55901"},
        "volume_key": "mongo-data",
        "volume": "sd-beg-090-t01-mongo-8-0-data",
        "target": "/data/db",
    },
    "redis": {
        "image": "redis:8.10.1-alpine3.23",
        "ports": {"6379": "55902"},
        "volume_key": "redis-data",
        "volume": "sd-beg-090-t01-redis-8-10-data",
        "target": "/data",
    },
    "neo4j": {
        "image": "neo4j:2026.07.1",
        "ports": {"7687": "55903", "7474": "55904"},
        "volume_key": "neo4j-data",
        "volume": "sd-beg-090-t01-neo4j-2026-07-data",
        "target": "/data",
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


def run(command: list[str], *, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    if check and completed.returncode != 0:
        raise RuntimeError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n"
            f"{completed.stderr.strip()}"
        )
    return completed


def main() -> int:
    evidence: dict[str, object] = {
        "status": "failed",
        "expected_project": PROJECT,
        "expected_services": {
            name: {
                "image": config["image"],
                "loopback_ports": config["ports"],
                "volume": config["volume"],
            }
            for name, config in SERVICES.items()
        },
        "expected_task_label": TASK_ID,
        "reset_targets": {
            "mongo": "sd_beg_090_t01.products documents with lab_id=SD-BEG-090-T01",
            "redis": [
                "sd:beg:090:t01:profile:42",
                "sd:beg:090:t01:counter",
                "sd:beg:090:t01:temporary",
            ],
            "neo4j": "LabPerson nodes with lab_id=SD-BEG-090-T01 and their relationships",
        },
        "recovery": "start only project sd-beg-090-t01 service mongo, redis, or neo4j",
    }

    try:
        context = run(["docker", "context", "show"]).stdout.strip()
        inspected = json.loads(run(["docker", "context", "inspect", context]).stdout)[0]
        endpoint = str(inspected["Endpoints"]["docker"]["Host"])
        if not endpoint.startswith("unix://"):
            raise RuntimeError(f"refusing non-local Docker endpoint: {endpoint}")

        config = json.loads(run(COMPOSE + ["config", "--format", "json"]).stdout)
        if config.get("name") != PROJECT:
            raise RuntimeError(f"unexpected Compose project: {config.get('name')}")

        configured_services = config.get("services", {})
        configured_volumes = config.get("volumes", {})
        for service_name, expected in SERVICES.items():
            service = configured_services.get(service_name, {})
            if service.get("image") != expected["image"]:
                raise RuntimeError(
                    f"{service_name} has unexpected image: {service.get('image')}"
                )
            labels = service.get("labels", {}) or {}
            if labels.get("com.rahulyadav.learning-task") != TASK_ID:
                raise RuntimeError(f"{service_name} task label mismatch")

            ports = service.get("ports", [])
            for target_port, host_port in expected["ports"].items():
                if not any(
                    str(item.get("host_ip")) == "127.0.0.1"
                    and str(item.get("published")) == host_port
                    and str(item.get("target")) == target_port
                    for item in ports
                ):
                    raise RuntimeError(
                        f"{service_name} loopback port mismatch for {target_port}: {ports}"
                    )

            mounts = service.get("volumes", [])
            if not any(
                item.get("source") == expected["volume_key"]
                and item.get("target") == expected["target"]
                and item.get("type") == "volume"
                for item in mounts
            ):
                raise RuntimeError(f"{service_name} volume mount mismatch: {mounts}")

            volume_config = configured_volumes.get(expected["volume_key"], {})
            if volume_config.get("name") != expected["volume"]:
                raise RuntimeError(
                    f"{service_name} configured volume name mismatch: {volume_config}"
                )
            volume_labels = volume_config.get("labels", {}) or {}
            if volume_labels.get("com.rahulyadav.learning-task") != TASK_ID:
                raise RuntimeError(f"{service_name} configured volume label mismatch")

        existing_project = run(
            [
                "docker",
                "ps",
                "-a",
                "--filter",
                f"label=com.docker.compose.project={PROJECT}",
                "--format",
                "{{json .}}",
            ]
        ).stdout.splitlines()
        for line in existing_project:
            item = json.loads(line)
            details = json.loads(run(["docker", "inspect", item["ID"]]).stdout)[0]
            labels = details.get("Config", {}).get("Labels", {}) or {}
            if labels.get("com.rahulyadav.learning-task") != TASK_ID:
                raise RuntimeError(
                    f"existing project container lacks task label: {item['ID']}"
                )
            if labels.get("com.docker.compose.service") not in SERVICES:
                raise RuntimeError(
                    f"unexpected service in exact project: {labels.get('com.docker.compose.service')}"
                )

        expected_ports = {
            host_port
            for service in SERVICES.values()
            for host_port in service["ports"].values()
        }
        all_containers = run(
            ["docker", "ps", "-a", "--format", "{{json .}}"]
        ).stdout.splitlines()
        for line in all_containers:
            item = json.loads(line)
            details = json.loads(run(["docker", "inspect", item["ID"]]).stdout)[0]
            labels = details.get("Config", {}).get("Labels", {}) or {}
            for bindings in (
                details.get("HostConfig", {}).get("PortBindings", {}) or {}
            ).values():
                for binding in bindings or []:
                    host_port = str(binding.get("HostPort"))
                    if (
                        host_port in expected_ports
                        and labels.get("com.docker.compose.project") != PROJECT
                    ):
                        raise RuntimeError(
                            f"host port {host_port} belongs to unrelated container {item['ID']}"
                        )

        volume_states: dict[str, str] = {}
        for expected in SERVICES.values():
            volume_name = str(expected["volume"])
            probe = run(["docker", "volume", "inspect", volume_name], check=False)
            if probe.returncode != 0:
                volume_states[volume_name] = "absent"
                continue
            details = json.loads(probe.stdout)[0]
            labels = details.get("Labels", {}) or {}
            if labels.get("com.rahulyadav.learning-task") != TASK_ID:
                raise RuntimeError(f"existing volume {volume_name} lacks exact task label")
            volume_states[volume_name] = "present-and-labeled"

        evidence.update(
            {
                "status": "passed",
                "docker_context": context,
                "docker_endpoint": endpoint,
                "existing_project_containers": len(existing_project),
                "volume_states": volume_states,
            }
        )
    except (
        KeyError,
        ValueError,
        RuntimeError,
        json.JSONDecodeError,
        subprocess.TimeoutExpired,
    ) as exc:
        evidence["reason"] = str(exc)
        print(json.dumps(evidence, indent=2))
        return 1

    print(json.dumps(evidence, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Read-only identity checks for the SD-BEG-110-T01 cache lab."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROJECT = "sd-beg-110-t01"
TASK_ID = "SD-BEG-110-T01"
SERVICES = {
    "redis": {"image": "redis:8.10.1", "host_port": "55110", "target_port": "6379"},
    "postgres": {"image": "postgres:18.6", "host_port": "55111", "target_port": "5432"},
}
POSTGRES_VOLUME = "sd-beg-110-t01-postgres-18"
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
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
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
        "expected_services": SERVICES,
        "expected_task_label": TASK_ID,
        "expected_database": "sd_beg_110_t01",
        "expected_key_namespace": "sd-beg-110:t01:*",
        "expected_volume": POSTGRES_VOLUME,
        "reset_targets": [
            "Redis key sd-beg-110:t01:profile:42",
            "public.cache_benchmark rows in database sd_beg_110_t01",
        ],
        "recovery": "restart only project sd-beg-110-t01 services redis and postgres",
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
            if not any(
                str(item.get("host_ip")) == "127.0.0.1"
                and str(item.get("published")) == expected["host_port"]
                and str(item.get("target")) == expected["target_port"]
                for item in ports
            ):
                raise RuntimeError(f"{service_name} loopback port mismatch: {ports}")

        redis_command = configured_services["redis"].get("command", [])
        if "--appendonly" not in redis_command or "no" not in redis_command:
            raise RuntimeError(f"Redis persistence command mismatch: {redis_command}")
        postgres_env = configured_services["postgres"].get("environment", {}) or {}
        if postgres_env.get("POSTGRES_DB") != "sd_beg_110_t01":
            raise RuntimeError(f"unexpected PostgreSQL database: {postgres_env}")
        if postgres_env.get("PGDATA") != "/var/lib/postgresql/18/docker":
            raise RuntimeError(f"unexpected PostgreSQL PGDATA: {postgres_env}")
        volume_config = config.get("volumes", {})
        if not any(
            item.get("name") == POSTGRES_VOLUME
            for item in volume_config.values()
            if isinstance(item, dict)
        ):
            raise RuntimeError(f"expected volume missing from Compose: {volume_config}")

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
            service_name = labels.get("com.docker.compose.service")
            if labels.get("com.rahulyadav.learning-task") != TASK_ID:
                raise RuntimeError(
                    f"existing project container lacks task label: {item['ID']}"
                )
            if service_name not in SERVICES:
                raise RuntimeError(f"unexpected existing project service: {service_name}")
            if details.get("Config", {}).get("Image") != SERVICES[service_name]["image"]:
                raise RuntimeError(f"existing {service_name} container image mismatch")

        expected_ports = {item["host_port"] for item in SERVICES.values()}
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
                    if (
                        str(binding.get("HostPort")) in expected_ports
                        and labels.get("com.docker.compose.project") != PROJECT
                    ):
                        raise RuntimeError(
                            f"host port {binding.get('HostPort')} belongs to unrelated "
                            f"container {item['ID']}"
                        )

        volume_probe = run(
            ["docker", "volume", "inspect", POSTGRES_VOLUME], check=False
        )
        if volume_probe.returncode == 0:
            volume = json.loads(volume_probe.stdout)[0]
            labels = volume.get("Labels", {}) or {}
            if labels.get("com.rahulyadav.learning-task") != TASK_ID:
                raise RuntimeError(
                    f"existing volume {POSTGRES_VOLUME} lacks exact task label"
                )
            volume_state = "present-and-labeled"
        else:
            volume_state = "absent"

        evidence.update(
            {
                "status": "passed",
                "docker_context": context,
                "docker_endpoint": endpoint,
                "existing_project_containers": len(existing_project),
                "postgres_volume": volume_state,
            }
        )
    except (KeyError, OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        evidence["reason"] = str(exc)
        print(json.dumps(evidence, indent=2))
        return 1

    print(json.dumps(evidence, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

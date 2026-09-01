#!/usr/bin/env python3
"""Read-only identity checks for the SD-BEG-070-T02 shard lab."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROJECT = "sd-beg-070-t02"
TASK_ID = "SD-BEG-070-T02"
IMAGE = "mysql:8.4.11"
SERVICES = {"shard_am": "55711", "shard_nz": "55712"}
VOLUMES = (
    "sd-beg-070-t02-am-mysql-8-4",
    "sd-beg-070-t02-nz-mysql-8-4",
)
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
        "expected_image": IMAGE,
        "expected_task_label": TASK_ID,
        "expected_database": "sd_beg_070_t02",
        "expected_volumes": list(VOLUMES),
        "reset_targets": [
            "shard_am.sd_beg_070_t02.records",
            "shard_nz.sd_beg_070_t02.records",
        ],
        "recovery": "start only project sd-beg-070-t02 services shard_am and shard_nz",
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
        for service_name, expected_port in SERVICES.items():
            service = configured_services.get(service_name, {})
            if service.get("image") != IMAGE:
                raise RuntimeError(f"{service_name} has unexpected image: {service.get('image')}")
            labels = service.get("labels", {}) or {}
            if labels.get("com.rahulyadav.learning-task") != TASK_ID:
                raise RuntimeError(f"{service_name} task label mismatch")
            ports = service.get("ports", [])
            if not any(
                str(item.get("host_ip")) == "127.0.0.1"
                and str(item.get("published")) == expected_port
                and str(item.get("target")) == "3306"
                for item in ports
            ):
                raise RuntimeError(f"{service_name} loopback port mismatch: {ports}")

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
                raise RuntimeError(f"existing project container lacks task label: {item['ID']}")

        expected_ports = set(SERVICES.values())
        all_containers = run(["docker", "ps", "-a", "--format", "{{json .}}"] ).stdout.splitlines()
        for line in all_containers:
            item = json.loads(line)
            details = json.loads(run(["docker", "inspect", item["ID"]]).stdout)[0]
            labels = details.get("Config", {}).get("Labels", {}) or {}
            for bindings in (details.get("HostConfig", {}).get("PortBindings", {}) or {}).values():
                for binding in bindings or []:
                    if str(binding.get("HostPort")) in expected_ports and labels.get(
                        "com.docker.compose.project"
                    ) != PROJECT:
                        raise RuntimeError(
                            f"host port {binding.get('HostPort')} belongs to unrelated container {item['ID']}"
                        )

        volume_states: dict[str, str] = {}
        for volume_name in VOLUMES:
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
    except (KeyError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        evidence["reason"] = str(exc)
        print(json.dumps(evidence, indent=2))
        return 1

    print(json.dumps(evidence, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

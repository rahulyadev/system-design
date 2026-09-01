#!/usr/bin/env python3
"""Read-only identity checks for the SD-BEG-050-T01 crash lab."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROJECT = "sd-beg-050-t01"
SERVICE = "postgres"
TASK_ID = "SD-BEG-050-T01"
PORT = "55450"
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
        "expected_service": SERVICE,
        "expected_task_label": TASK_ID,
        "expected_loopback_port": f"127.0.0.1:{PORT}:5432",
        "expected_database": "sd_beg_050_t01",
        "expected_schema": "sd_beg_050_t01",
        "expected_volume": VOLUME,
        "reset": "05_reset.sql drops only schema sd_beg_050_t01 after a database guard",
        "recovery": "restart only project sd-beg-050-t01 service postgres",
    }

    try:
        context = run(["docker", "context", "show"]).stdout.strip()
        inspected_context = json.loads(run(["docker", "context", "inspect", context]).stdout)[0]
        endpoint = str(inspected_context["Endpoints"]["docker"]["Host"])
        if not endpoint.startswith("unix://"):
            raise RuntimeError(f"refusing non-local Docker endpoint: {endpoint}")

        config = json.loads(run(COMPOSE + ["config", "--format", "json"]).stdout)
        if config.get("name") != PROJECT:
            raise RuntimeError(f"unexpected Compose project: {config.get('name')}")
        service = config.get("services", {}).get(SERVICE, {})
        if service.get("image") != "postgres:18.6":
            raise RuntimeError(f"unexpected image: {service.get('image')}")
        ports = service.get("ports", [])
        if not any(
            str(item.get("host_ip")) == "127.0.0.1"
            and str(item.get("published")) == PORT
            and str(item.get("target")) == "5432"
            for item in ports
        ):
            raise RuntimeError(f"expected loopback port binding not found: {ports}")

        existing = run(
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
        for line in existing:
            item = json.loads(line)
            container_id = item["ID"]
            details = json.loads(run(["docker", "inspect", container_id]).stdout)[0]
            labels = details.get("Config", {}).get("Labels", {})
            if labels.get("com.rahulyadav.learning-task") != TASK_ID:
                raise RuntimeError(f"existing project container lacks task label: {container_id}")

        volume_probe = run(["docker", "volume", "inspect", VOLUME], check=False)
        volume_state = "absent"
        if volume_probe.returncode == 0:
            details = json.loads(volume_probe.stdout)[0]
            labels = details.get("Labels", {}) or {}
            if labels.get("com.rahulyadav.learning-task") != TASK_ID:
                raise RuntimeError(f"existing volume {VOLUME} lacks exact task label")
            volume_state = "present-and-labeled"

        evidence.update(
            {
                "status": "passed",
                "docker_context": context,
                "docker_endpoint": endpoint,
                "existing_project_containers": len(existing),
                "volume_state": volume_state,
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

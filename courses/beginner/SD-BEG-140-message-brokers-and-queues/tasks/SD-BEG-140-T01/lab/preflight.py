#!/usr/bin/env python3
"""Verify that the RabbitMQ experiment is local and exactly task-scoped."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import socket
import subprocess


TASK_ID = "SD-BEG-140-T01"
PROJECT = "sd-beg-140-t01-rabbitmq"
SERVICE = "rabbitmq"
IMAGE = "rabbitmq:4.3.5-management-alpine"
PORTS = {5678: 5672, 15678: 15672}
LAB_DIR = Path(__file__).resolve().parent
COMPOSE = LAB_DIR / "compose.yaml"


def run(*args: str) -> str:
    result = subprocess.run(args, check=True, text=True, capture_output=True)
    return result.stdout.strip()


def compose_args() -> list[str]:
    return [
        "docker",
        "compose",
        "-f",
        str(COMPOSE),
        "--project-name",
        PROJECT,
        "--profile",
        "lab",
    ]


def validate_config() -> None:
    raw = run(*compose_args(), "config", "--format", "json")
    config = json.loads(raw)
    service = config["services"][SERVICE]
    assert service["image"] == IMAGE
    assert service["labels"]["com.rahulyadav.learning-task"] == TASK_ID
    assert service["labels"]["com.rahulyadav.disposable"] == "true"
    observed_ports = {
        int(item["published"]): (item["host_ip"], int(item["target"]))
        for item in service["ports"]
    }
    expected_ports = {
        published: ("127.0.0.1", target)
        for published, target in PORTS.items()
    }
    assert observed_ports == expected_ports
    assert not config.get("volumes"), "this task intentionally owns no named volume"


def task_containers() -> list[dict[str, object]]:
    ids = run(
        "docker",
        "ps",
        "-aq",
        "--filter",
        f"label=com.docker.compose.project={PROJECT}",
    ).split()
    if not ids:
        return []
    return json.loads(run("docker", "inspect", *ids))


def validate_container(container: dict[str, object], expect_running: bool) -> None:
    config = container["Config"]
    labels = config["Labels"]
    assert labels["com.docker.compose.project"] == PROJECT
    assert labels["com.docker.compose.service"] == SERVICE
    assert labels["com.rahulyadav.learning-task"] == TASK_ID
    assert labels["com.rahulyadav.disposable"] == "true"
    assert config["Image"] == IMAGE
    bindings = container["HostConfig"]["PortBindings"]
    for published, target in PORTS.items():
        value = bindings[f"{target}/tcp"]
        assert value == [{"HostIp": "127.0.0.1", "HostPort": str(published)}]
    if expect_running:
        assert container["State"]["Running"] is True
        assert container["State"]["Health"]["Status"] == "healthy"


def ports_are_free() -> None:
    for published in PORTS:
        probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            probe.bind(("127.0.0.1", published))
        finally:
            probe.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expect-running", action="store_true")
    args = parser.parse_args()

    context = run("docker", "context", "show")
    endpoint = json.loads(
        run(
            "docker",
            "context",
            "inspect",
            "--format",
            "{{json .Endpoints.docker.Host}}",
        )
    )
    if not endpoint.startswith(("unix://", "npipe://")):
        raise RuntimeError(f"refusing non-local Docker endpoint: {endpoint}")

    validate_config()
    containers = task_containers()
    if len(containers) > 1:
        raise RuntimeError(f"expected at most one task container, observed {len(containers)}")
    if containers:
        validate_container(containers[0], args.expect_running)
    elif args.expect_running:
        raise RuntimeError("expected the exact task container to be running")
    else:
        ports_are_free()

    state = "healthy" if args.expect_running else ("existing-verified" if containers else "absent")
    print(
        f"PREFLIGHT status=passed context={context} endpoint={endpoint} "
        f"project={PROJECT} service={SERVICE} image={IMAGE} "
        "ports=127.0.0.1:5678,127.0.0.1:15678 "
        f"container={state} volume=none credentials=synthetic"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

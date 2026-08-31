#!/usr/bin/env python3
"""Read-only preflight for local task infrastructure."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def run(command: list[str]) -> dict[str, object]:
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compose-file", type=Path, default=Path("compose.yaml"))
    parser.add_argument("--project", default="system-design-learning")
    parser.add_argument("--service", default="postgres")
    args = parser.parse_args()

    evidence: dict[str, object] = {
        "status": "skipped",
        "compose_file": str(args.compose_file.resolve()),
        "expected_project": args.project,
        "expected_service": args.service,
        "checks": [],
    }
    if shutil.which("docker") is None:
        evidence["reason"] = "docker executable not found; no service was started or changed"
        print(json.dumps(evidence, indent=2))
        return 2

    checks = evidence["checks"]
    assert isinstance(checks, list)
    checks.append(run(["docker", "context", "show"]))
    checks.append(
        run(
            [
                "docker",
                "compose",
                "-f",
                str(args.compose_file),
                "--project-name",
                args.project,
                "config",
            ]
        )
    )
    evidence["status"] = "passed" if all(item["returncode"] == 0 for item in checks) else "failed"
    print(json.dumps(evidence, indent=2))
    return 0 if evidence["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

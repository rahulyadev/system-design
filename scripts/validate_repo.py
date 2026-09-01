#!/usr/bin/env python3
"""Validate the System Design Learning Lab bootstrap and generated packs.

The validator is intentionally standard-library-only. Structural success never
claims that Docker, PostgreSQL, or any other task runtime executed.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Callable, Iterable


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    ".env.example",
    ".gitignore",
    ".python-version",
    "AGENTS.md",
    "BUNDLE_MANIFEST.md",
    "COURSE_INDEX.md",
    "NOTEBOOKLM.md",
    "PROGRESS.md",
    "README.md",
    "START_HERE.md",
    "TASK_AND_LAB_STANDARD.md",
    "compose.yaml",
    "pyproject.toml",
    "courses/advanced/README.md",
    "courses/beginner/README.md",
    "data/lectures.json",
    "data/progress.json",
    "data/repository_baseline.json",
    "data/tool_profiles.json",
    "docs/COPYRIGHT_AND_PRIVACY.md",
    "docs/ENGLISH_AND_INTERVIEW.md",
    "docs/LAB_SAFETY.md",
    "docs/LECTURE_WORKFLOW.md",
    "docs/PROMPTS.md",
    "docs/REPOSITORY_TREE.md",
    "docs/SOURCE_PROCESSING.md",
    "docs/TASK_WORKFLOW.md",
    "docs/VISUAL_STANDARD.md",
    "docs/WORKFLOW.md",
    "inputs/README.md",
    "scripts/lab_preflight.py",
    "scripts/lecture_lookup.py",
    "scripts/package_bootstrap.py",
    "scripts/render_catalog.py",
    "scripts/validate_repo.py",
    "templates/lab/README.md",
    "templates/lab/compose.yaml",
    "templates/lab/evidence.md",
    "templates/lab/verify.py",
    "templates/lecture/metadata.json",
    "templates/lecture/notes.md",
    "templates/lecture/review.md",
    "templates/lecture/source_manifest.json",
    "templates/task/ATTEMPT.md",
    "templates/task/README.md",
    "templates/task/RUBRIC.md",
    "templates/task/reference/SOLUTION.md",
    "templates/task/task.json",
    "validation/expected_mutations.json",
)

EXPECTED_TRACK_COUNTS = {"beginner": 36, "advanced": 16}
ALLOWED_TITLE_STATUS = {"verified", "ambiguous"}
ALLOWED_TASK_TYPES = {
    "reasoning",
    "calculation",
    "query",
    "coding",
    "experiment",
    "design",
    "incident",
}
ALLOWED_EXECUTION = {"not_required", "passed", "failed", "skipped"}
RAW_SOURCE_SUFFIXES = {
    ".mp4",
    ".mkv",
    ".mov",
    ".avi",
    ".wav",
    ".mp3",
    ".m4a",
    ".srt",
    ".vtt",
    ".pdf",
}
FORBIDDEN_SECRET_COMPONENTS = {"credentials", "tokens", "private", "secrets"}
WORKING_ROOT_DIRS = {".venv", "venv", "env", "ENV", "node_modules"}
CACHE_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
FORBIDDEN_ARCHIVE_SUFFIXES = {
    ".pyc",
    ".pyo",
    ".sqlite",
    ".sqlite3",
    ".db",
    ".dump",
    ".backup",
    ".bak",
    ".wal",
}
GENERATED_ROOT_DIRS = {"units", "projects", "attempts", "solutions"}
REQUIRED_NOTE_HEADINGS = (
    "## Source and coverage check",
    "## What I should be able to do",
    "## Small bridge from earlier ideas",
    "## The 60-second story",
    "## Why the terms matter",
    "## Big picture",
    "## Core concepts",
    "## Deep mechanism",
    "## Design choices",
    "## Misconceptions",
    "## Instructor-assigned tasks",
    "## Useful English and technical phrases",
    "## Interview practice",
    "## Course, verified extensions, and uncertainty",
    "## Final revision card",
)
REQUIRED_REVIEW_HEADINGS = (
    "## Closed-book recall",
    "## Draw from memory",
    "## Instructor-task recall",
    "## Two-minute teach-back",
    "## Interview follow-ups",
    "## Flashcards",
    "## English speaking check",
    "## Weakness log",
)
REQUIRED_TASK_HEADINGS = (
    "## Source and fidelity",
    "## Exact requirement checklist",
    "## Inputs, constraints, and expected artifact",
    "## Before you start: predict",
    "## Setup",
    "## Learner steps",
    "## Progressive hints",
    "## Acceptance criteria",
    "## Cleanup/reset",
    "## Reference answer boundary",
)
REQUIRED_SOLUTION_HEADINGS = (
    "## Clarifications and assumptions",
    "## Prediction",
    "## Approach and why it fits",
    "## Step-by-step solution",
    "## Correctness invariant",
    "## Verification status",
    "## Failure modes and recovery",
    "## Alternatives",
    "## Interview follow-ups",
)


@dataclass
class Result:
    profile: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    statistics: dict[str, object] = field(default_factory=dict)

    def error(self, code: str, message: str) -> None:
        self.errors.append(f"[{code}] {message}")

    def warning(self, code: str, message: str) -> None:
        self.warnings.append(f"[{code}] {message}")

    def as_dict(self) -> dict[str, object]:
        return {
            "profile": self.profile,
            "status": "passed" if not self.errors else "failed",
            "errors": self.errors,
            "warnings": self.warnings,
            "statistics": self.statistics,
        }


def load_json(path: Path, result: Result, code: str) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        result.error(code, f"{path}: {exc}")
        return None


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_generated_lecture_path(relative: PurePosixPath) -> bool:
    parts = relative.parts
    return (
        len(parts) >= 3
        and parts[0] == "courses"
        and parts[1] in EXPECTED_TRACK_COUNTS
        and re.fullmatch(r"SD-(?:BEG|ADV)-\d{3}-.+", parts[2]) is not None
    )


def should_ignore_working(relative: PurePosixPath) -> bool:
    parts = relative.parts
    if not parts:
        return False
    if parts[0] == ".git" or parts[0] in WORKING_ROOT_DIRS:
        return True
    if len(parts) >= 2 and parts[0] == "inputs" and parts[1] == "private":
        return True
    return any(part in CACHE_DIRS for part in parts) or relative.name.startswith(".coverage")


def repository_files(root: Path, profile: str) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() and not path.is_symlink():
            continue
        relative = PurePosixPath(path.relative_to(root).as_posix())
        if profile in {"bootstrap", "live"} and should_ignore_working(relative):
            continue
        files.append(path)
    return sorted(files, key=lambda item: item.relative_to(root).as_posix())


def basic_statistics(root: Path, profile: str) -> dict[str, object]:
    files = repository_files(root, profile)
    relative = [path.relative_to(root).as_posix() for path in files]
    markdown = [path for path in files if path.suffix.lower() == ".md"]
    links = 0
    fences = 0
    tables = 0
    for path in markdown:
        text = path.read_text(encoding="utf-8", errors="replace")
        links += len(re.findall(r"\[[^\]]+\]\([^)]+\)", text))
        fences += text.count("```") // 2
        tables += len(re.findall(r"(?m)^\|(?:\s*:?-+:?\s*\|)+\s*$", text))
    return {
        "repository_files": len(files),
        "markdown_files": len(markdown),
        "python_files": sum(path.endswith(".py") for path in relative),
        "json_files": sum(path.endswith(".json") for path in relative),
        "yaml_files": sum(path.endswith((".yaml", ".yml")) for path in relative),
        "sql_files": sum(path.endswith(".sql") for path in relative),
        "markdown_links": links,
        "code_fence_blocks": fences,
        "markdown_tables": tables,
        "required_files": len(REQUIRED_FILES),
        "required_files_present": sum((root / path).is_file() for path in REQUIRED_FILES),
    }


def validate_required(root: Path, result: Result) -> None:
    for relative in REQUIRED_FILES:
        if not (root / relative).is_file():
            result.error("REQUIRED_FILE_MISSING", relative)


def validate_catalog(root: Path, result: Result) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    lectures_obj = load_json(root / "data/lectures.json", result, "CATALOG_JSON_INVALID")
    progress_obj = load_json(root / "data/progress.json", result, "PROGRESS_JSON_INVALID")
    lectures = lectures_obj if isinstance(lectures_obj, list) else []
    progress = progress_obj if isinstance(progress_obj, list) else []

    if len(lectures) != 52:
        result.error("CATALOG_COUNT_MISMATCH", f"expected 52 lectures, found {len(lectures)}")

    ids = [str(item.get("id", "")) for item in lectures if isinstance(item, dict)]
    if len(ids) != len(set(ids)):
        result.error("CATALOG_DUPLICATE_ID", "lecture IDs must be unique")

    for track, count in EXPECTED_TRACK_COUNTS.items():
        items = [item for item in lectures if isinstance(item, dict) and item.get("track") == track]
        if len(items) != count:
            result.error("CATALOG_TRACK_COUNT_MISMATCH", f"{track}: expected {count}, found {len(items)}")
        prefix = "SD-BEG" if track == "beginner" else "SD-ADV"
        expected_ids = [f"{prefix}-{number * 10:03d}" for number in range(1, count + 1)]
        observed_ids = [str(item.get("id", "")) for item in items]
        if observed_ids != expected_ids:
            result.error("CATALOG_ID_SEQUENCE_MISMATCH", f"{track} IDs are not the canonical sequence")
        expected_numbers = list(range(1, count + 1))
        observed_numbers = [item.get("number") for item in items]
        if observed_numbers != expected_numbers:
            result.error("CATALOG_NUMBER_SEQUENCE_MISMATCH", f"{track} numbers are not 1..{count}")

    ambiguous = []
    for item in lectures:
        if not isinstance(item, dict):
            result.error("CATALOG_RECORD_INVALID", "every lecture record must be an object")
            continue
        missing = [key for key in ("id", "track", "number", "title", "slug", "themes", "source_title_status", "study_order", "blocking_prerequisites") if key not in item]
        if missing:
            result.error("CATALOG_FIELD_MISSING", f"{item.get('id', '<unknown>')}: {', '.join(missing)}")
        if item.get("source_title_status") not in ALLOWED_TITLE_STATUS:
            result.error("CATALOG_TITLE_STATUS_INVALID", str(item.get("id")))
        if item.get("source_title_status") == "ambiguous":
            ambiguous.append(item.get("id"))
            if not item.get("source_note"):
                result.error("CATALOG_AMBIGUITY_NOTE_MISSING", str(item.get("id")))
        if item.get("study_order") != "independent":
            result.error("CATALOG_STUDY_ORDER_INVALID", str(item.get("id")))
        if item.get("blocking_prerequisites") != []:
            result.error("CATALOG_BLOCKING_PREREQUISITE", str(item.get("id")))
    if ambiguous != ["SD-BEG-180", "SD-BEG-290"]:
        result.error("CATALOG_AMBIGUITY_SET_MISMATCH", f"observed {ambiguous}")

    lecture_projection = [(item.get("id"), item.get("title"), item.get("track")) for item in lectures if isinstance(item, dict)]
    progress_projection = [(item.get("id"), item.get("title"), item.get("track")) for item in progress if isinstance(item, dict)]
    if lecture_projection != progress_projection:
        result.error("PROGRESS_PARITY_MISMATCH", "progress IDs/titles/tracks differ from catalog")
    for item in progress:
        if not isinstance(item, dict):
            continue
        if item.get("artifact_state") not in {"Absent", "Draft", "Ready"}:
            result.error("PROGRESS_ARTIFACT_STATE_INVALID", str(item.get("id")))
        if item.get("learning_state") not in {"Not started", "Learning", "Practiced", "Recalled", "Demonstrated", "Comfortable"}:
            result.error("PROGRESS_LEARNING_STATE_INVALID", str(item.get("id")))

    render_script = root / "scripts/render_catalog.py"
    if render_script.is_file():
        completed = subprocess.run(
            [sys.executable, str(render_script), "--check"],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout).strip()
            result.error("CATALOG_RENDER_MISMATCH", detail or "rendered catalog differs")

    result.statistics.update(
        {
            "canonical_lectures": len(lectures),
            "beginner_lectures": sum(isinstance(item, dict) and item.get("track") == "beginner" for item in lectures),
            "advanced_lectures": sum(isinstance(item, dict) and item.get("track") == "advanced" for item in lectures),
            "ambiguous_source_titles": len(ambiguous),
            "blocking_prerequisite_edges": sum(len(item.get("blocking_prerequisites", [])) for item in lectures if isinstance(item, dict)),
        }
    )
    return lectures, progress


def require_text(path: Path, result: Result, minimum: int, headings: Iterable[str], code: str) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        result.error(code, f"{path}: {exc}")
        return ""
    if len(text.strip()) < minimum:
        result.error(code, f"{path}: substantive length {len(text.strip())} < {minimum}")
    for heading in headings:
        if heading not in text:
            result.error(code, f"{path}: missing {heading}")
    return text


def validate_document_contracts(root: Path, result: Result) -> None:
    contracts = {
        "AGENTS.md": ["One video equals one dedicated Codex chat", "Rahul may process any video in any order", "Instructor tasks are not optional lab ideas", "Never merge predicted and observed behavior"],
        "TASK_AND_LAB_STANDARD.md": ["Detect every assigned task", "Learner/reference separation", "Evidence contract", "reference_status"],
        "docs/SOURCE_PROCESSING.md": ["Transcript", "Slides", "Video", "task"],
        "docs/VISUAL_STANDARD.md": ["How to read", "Key insight", "Simplification"],
        "docs/ENGLISH_AND_INTERVIEW.md": ["pronunciation", "SDE-2", "SDE-3"],
        "docs/WORKFLOW.md": ["lecture/<LECTURE-ID>", "force-push", "current initialization/repair operation"],
    }
    for relative, phrases in contracts.items():
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in text:
                result.error("DOCUMENT_CONTRACT_MISSING", f"{relative}: {phrase}")

    template_checks = {
        "templates/lecture/notes.md": REQUIRED_NOTE_HEADINGS,
        "templates/lecture/review.md": REQUIRED_REVIEW_HEADINGS,
        "templates/task/README.md": REQUIRED_TASK_HEADINGS,
        "templates/task/reference/SOLUTION.md": REQUIRED_SOLUTION_HEADINGS,
        "templates/lab/evidence.md": ("## Prediction", "## Expected behavior", "## Actual run", "## Observed evidence", "## Variation"),
    }
    for relative, headings in template_checks.items():
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for heading in headings:
            if heading not in text:
                result.error("TEMPLATE_CONTRACT_MISSING", f"{relative}: {heading}")

    source_template = load_json(root / "templates/lecture/source_manifest.json", result, "TEMPLATE_JSON_INVALID")
    if isinstance(source_template, dict):
        scan = source_template.get("task_scan", {})
        if not isinstance(scan, dict) or not scan.get("whole_source_scanned") or not scan.get("ending_scanned"):
            result.error("TASK_SCAN_CONTRACT_MISSING", "source manifest must record whole-source and ending scans")

    tools = load_json(root / "data/tool_profiles.json", result, "TOOL_PROFILE_JSON_INVALID")
    if isinstance(tools, dict):
        profiles = tools.get("profiles", [])
        ids = {item.get("id") for item in profiles if isinstance(item, dict)}
        required = {"reasoning-only", "python-simulation", "postgres-root", "redis-task-local", "rabbitmq-task-local", "kafka-task-local", "minio-task-local", "proxy-task-local"}
        if ids != required:
            result.error("TOOL_PROFILE_SET_MISMATCH", f"expected {sorted(required)}, observed {sorted(str(item) for item in ids)}")


def validate_compose(root: Path, result: Result) -> None:
    path = root / "compose.yaml"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    if "image: postgres:18.6" not in text:
        result.error("POSTGRES_IMAGE_PIN_MISMATCH", "root Compose must pin postgres:18.6")
    if re.search(r"(?m)^\s*image:\s*\S*:latest\s*$", text):
        result.error("COMPOSE_UNPINNED_IMAGE", "latest image tag is forbidden")
    port_lines = re.findall(r'(?m)^\s*-\s*["\']?([^"\'\n]*:\d+)["\']?\s*$', text)
    for port in port_lines:
        if not port.strip().startswith("127.0.0.1:"):
            result.error("COMPOSE_PORT_NOT_LOOPBACK", port.strip())
    if "healthcheck:" not in text or "pg_isready" not in text:
        result.error("POSTGRES_HEALTHCHECK_MISSING", "root PostgreSQL health check is required")
    if "PGDATA: /var/lib/postgresql/18/docker" not in text or "sd-postgres-data:/var/lib/postgresql" not in text:
        result.error("POSTGRES_VOLUME_LAYOUT_MISMATCH", "PostgreSQL 18 data layout/volume mount is missing")
    if "name: system-design-learning-postgres-18" not in text:
        result.error("POSTGRES_VOLUME_NAME_MISMATCH", "exact disposable learning volume name is missing")


def validate_paths(root: Path, profile: str, result: Result) -> None:
    for path in repository_files(root, profile):
        relative = PurePosixPath(path.relative_to(root).as_posix())
        parts = relative.parts
        if path.is_symlink():
            result.error("SYMLINK_FORBIDDEN", relative.as_posix())
        if not parts:
            continue
        if parts[0] in GENERATED_ROOT_DIRS:
            result.error("GENERATED_ROOT_FORBIDDEN", relative.as_posix())
        if profile in {"bootstrap", "archive"} and is_generated_lecture_path(relative):
            result.error("GENERATED_LECTURE_FORBIDDEN", relative.as_posix())
        if any(part in FORBIDDEN_SECRET_COMPONENTS for part in parts):
            result.error("PRIVATE_PATH_FORBIDDEN", relative.as_posix())
        if profile == "archive":
            if ".git" in parts:
                result.error("ARCHIVE_GIT_METADATA", relative.as_posix())
            if any(part in WORKING_ROOT_DIRS or part in CACHE_DIRS for part in parts):
                result.error("ARCHIVE_WORKING_ARTIFACT", relative.as_posix())
            if relative.name == ".env" or (relative.name.startswith(".env.") and relative.name != ".env.example"):
                result.error("ARCHIVE_SECRET_FILE", relative.as_posix())
            if path.suffix.lower() in RAW_SOURCE_SUFFIXES:
                result.error("ARCHIVE_RAW_SOURCE", relative.as_posix())
            if path.suffix.lower() in FORBIDDEN_ARCHIVE_SUFFIXES:
                result.error("ARCHIVE_GENERATED_DATA", relative.as_posix())

    lab_paths = [root / "templates/lab/README.md"]
    lab_paths.extend(root.glob("courses/*/SD-*/tasks/*/lab/README.md"))
    lab_paths.extend(root.glob("courses/*/SD-*/tasks/*/lab/compose.yaml"))
    unsafe = ("docker system prune", "docker compose down --volumes", "docker-compose down -v", "docker volume prune")
    for path in lab_paths:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for command in unsafe:
            if command in text:
                result.error("LAB_UNSAFE_COMMAND", f"{path.relative_to(root)}: {command}")
        if path.name in {"compose.yaml", "compose.yml"}:
            if re.search(r"(?m)^\s*image:\s*\S*:latest\s*$", text):
                result.error("LAB_UNPINNED_IMAGE", str(path.relative_to(root)))
            for port in re.findall(r'(?m)^\s*-\s*["\']?([^"\'\n]*:\d+)["\']?\s*$', text):
                if "<host-port>" not in port and not port.strip().startswith("127.0.0.1:"):
                    result.error("LAB_PORT_NOT_LOOPBACK", f"{path.relative_to(root)}: {port.strip()}")


def markdown_code_blocks(text: str) -> set[str]:
    blocks = set()
    for match in re.finditer(r"```[^\n]*\n(.*?)```", text, flags=re.DOTALL):
        normalized = " ".join(match.group(1).split())
        if len(normalized) >= 48:
            blocks.add(normalized)
    return blocks


def validate_task(task_dir: Path, lecture_id: str, result: Result) -> None:
    relative = task_dir.relative_to(task_dir.parents[4] if "tests" in task_dir.parts else ROOT) if False else task_dir
    required = ("task.json", "README.md", "ATTEMPT.md", "RUBRIC.md", "reference/SOLUTION.md")
    for name in required:
        if not (task_dir / name).is_file():
            result.error("TASK_FILE_MISSING", f"{task_dir}: {name}")

    task_obj = load_json(task_dir / "task.json", result, "TASK_JSON_INVALID")
    if not isinstance(task_obj, dict):
        return
    task_id = str(task_obj.get("id", ""))
    if task_obj.get("lecture_id") != lecture_id or not re.fullmatch(re.escape(lecture_id) + r"-T\d{2}", task_id):
        result.error("TASK_ID_MISMATCH", f"{task_dir}: {task_id}")
    if task_dir.name != task_id:
        result.error("TASK_DIRECTORY_MISMATCH", f"{task_dir.name} != {task_id}")
    if task_obj.get("type") not in ALLOWED_TASK_TYPES:
        result.error("TASK_TYPE_INVALID", task_id)
    if task_obj.get("instructor_assigned") is not True:
        result.error("TASK_NOT_INSTRUCTOR_ASSIGNED", task_id)
    if not str(task_obj.get("source_timestamp", "")).strip():
        result.error("TASK_SOURCE_REFERENCE_MISSING", task_id)
    execution = task_obj.get("execution_status")
    if execution not in ALLOWED_EXECUTION:
        result.error("TASK_EXECUTION_STATUS_INVALID", task_id)

    learner = require_text(task_dir / "README.md", result, 1_500, REQUIRED_TASK_HEADINGS, "TASK_SPEC_INCOMPLETE")
    attempt = require_text(task_dir / "ATTEMPT.md", result, 450, ("## Prediction before running or designing", "## Actual evidence I observed", "## Explanation in my own words"), "TASK_ATTEMPT_INCOMPLETE")
    require_text(task_dir / "RUBRIC.md", result, 500, ("SDE-2-ready", "SDE-3-ready", "## Required completion evidence"), "TASK_RUBRIC_INCOMPLETE")
    solution = require_text(task_dir / "reference/SOLUTION.md", result, 1_500, REQUIRED_SOLUTION_HEADINGS, "TASK_SOLUTION_INCOMPLETE")
    if not re.search(r"(?i)spoiler|open only after", solution[:500]):
        result.error("TASK_SPOILER_BOUNDARY_MISSING", task_id)
    overlap = markdown_code_blocks(attempt) & markdown_code_blocks(solution)
    if overlap:
        result.error("TASK_REFERENCE_SOLUTION_LEAK", f"{task_id}: complete reference code appears in ATTEMPT.md")
    if "reference/SOLUTION.md" not in learner:
        result.error("TASK_REFERENCE_LINK_MISSING", task_id)

    runtime_required = task_obj.get("runtime_required") is True
    evidence_text = ""
    if runtime_required:
        for name in ("lab/README.md", "lab/evidence.md"):
            if not (task_dir / name).is_file():
                result.error("TASK_LAB_FILE_MISSING", f"{task_id}: {name}")
        if not any((task_dir / "lab").glob("*.sql")) and not (task_dir / "lab/verify.py").is_file() and not (task_dir / "lab/compose.yaml").is_file():
            result.error("TASK_LAB_SETUP_MISSING", task_id)
        if (task_dir / "lab/evidence.md").is_file():
            evidence_text = (task_dir / "lab/evidence.md").read_text(encoding="utf-8")
    if execution == "skipped":
        if not task_obj.get("execution_reason"):
            result.error("TASK_SKIP_REASON_MISSING", task_id)
        if runtime_required and ("Status: Skipped" not in evidence_text or "None — execution skipped" not in evidence_text):
            result.error("EXECUTION_EVIDENCE_MISMATCH", f"{task_id}: skipped task must show no observed evidence")
    if execution == "passed" and runtime_required:
        if "Status: Passed" not in evidence_text or "Not run" in evidence_text:
            result.error("EXECUTION_EVIDENCE_MISMATCH", f"{task_id}: passed task lacks genuine run evidence")


def validate_lecture_pack(pack: Path, catalog: dict[str, dict[str, object]], result: Result, fixture: bool = False) -> None:
    for name in ("metadata.json", "source_manifest.json", "notes.md", "review.md"):
        if not (pack / name).is_file():
            result.error("LECTURE_FILE_MISSING", f"{pack}: {name}")
    metadata_obj = load_json(pack / "metadata.json", result, "LECTURE_METADATA_INVALID")
    manifest_obj = load_json(pack / "source_manifest.json", result, "SOURCE_MANIFEST_INVALID")
    if not isinstance(metadata_obj, dict) or not isinstance(manifest_obj, dict):
        return
    lecture_id = str(metadata_obj.get("lecture_id", ""))
    canonical = catalog.get(lecture_id)
    if canonical is None:
        result.error("LECTURE_ID_UNKNOWN", f"{pack}: {lecture_id}")
        return
    for key in ("track", "title", "slug"):
        if metadata_obj.get(key) != canonical.get(key):
            result.error("LECTURE_METADATA_MISMATCH", f"{lecture_id}: {key}")
    if not fixture:
        expected_name = f"{lecture_id}-{canonical['slug']}"
        if pack.name != expected_name or pack.parent.name != canonical["track"]:
            result.error("LECTURE_DIRECTORY_MISMATCH", f"{pack}: expected courses/{canonical['track']}/{expected_name}")
    if manifest_obj.get("lecture_id") != lecture_id or manifest_obj.get("title") != canonical.get("title"):
        result.error("SOURCE_MANIFEST_IDENTITY_MISMATCH", lecture_id)
    if manifest_obj.get("coverage_status") != "complete":
        result.error("SOURCE_COVERAGE_INCOMPLETE", lecture_id)
    scan = manifest_obj.get("task_scan")
    if not isinstance(scan, dict):
        result.error("TASK_SCAN_MISSING", lecture_id)
        return
    if scan.get("status") != "complete" or scan.get("whole_source_scanned") is not True or scan.get("ending_scanned") is not True:
        result.error("TASK_SCAN_INCOMPLETE", lecture_id)
    task_count = scan.get("task_count")
    if not isinstance(task_count, int) or task_count < 0:
        result.error("TASK_COUNT_INVALID", lecture_id)
        task_count = 0
    if metadata_obj.get("task_count") != task_count:
        result.error("TASK_COUNT_MISMATCH", f"{lecture_id}: metadata versus manifest")

    notes = require_text(pack / "notes.md", result, 4_500, REQUIRED_NOTE_HEADINGS, "LECTURE_NOTES_INCOMPLETE")
    require_text(pack / "review.md", result, 1_500, REQUIRED_REVIEW_HEADINGS, "LECTURE_REVIEW_INCOMPLETE")
    if "### How to read this visual" not in notes or "### Key insight" not in notes or "### Simplification or limitation" not in notes:
        result.error("LECTURE_VISUAL_CONTRACT_MISSING", lecture_id)
    if "### SDE-2 working engineer" not in notes or "### SDE-3 senior design" not in notes:
        result.error("LECTURE_INTERVIEW_LADDER_MISSING", lecture_id)
    if re.search(r"<(?:LECTURE-ID|Video title|observable outcome|term|date)>|\bTODO\b", notes):
        result.error("LECTURE_PLACEHOLDER_UNRESOLVED", lecture_id)
    if re.search(r"(?:/Users/|/home/|/workspace/|drive\.google\.com|docs\.google\.com)", notes):
        result.error("LECTURE_PRIVATE_SOURCE_LEAK", lecture_id)

    task_dir = pack / "tasks"
    observed = sorted(path for path in task_dir.iterdir() if path.is_dir()) if task_dir.is_dir() else []
    if len(observed) != task_count:
        result.error("TASK_COUNT_MISMATCH", f"{lecture_id}: manifest {task_count}, directories {len(observed)}")
    expected_task_ids = [item.get("id") for item in scan.get("tasks", []) if isinstance(item, dict)]
    if expected_task_ids != [path.name for path in observed]:
        result.error("TASK_MANIFEST_PARITY_MISMATCH", lecture_id)
    if task_count == 0 and "No instructor-assigned task found in the supplied source." not in notes:
        result.error("NO_TASK_STATEMENT_MISSING", lecture_id)
    for path in observed:
        validate_task(path, lecture_id, result)


def validate_links(root: Path, profile: str, result: Result) -> None:
    for path in repository_files(root, profile):
        if path.suffix.lower() != ".md":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
            target = target.strip().split()[0]
            if target.startswith(("http://", "https://", "mailto:", "#", "sandbox:")) or "<" in target or ">" in target:
                continue
            file_target = target.split("#", 1)[0]
            if not file_target:
                continue
            resolved = (path.parent / file_target).resolve()
            try:
                resolved.relative_to(root.resolve())
            except ValueError:
                result.error("MARKDOWN_LINK_ESCAPES_ROOT", f"{path.relative_to(root)} -> {target}")
                continue
            if not resolved.exists():
                result.error("MARKDOWN_LINK_MISSING", f"{path.relative_to(root)} -> {target}")


def validate_root(root: Path, profile: str = "bootstrap") -> Result:
    if profile not in {"bootstrap", "live", "archive"}:
        raise ValueError(f"unknown profile: {profile}")
    result = Result(profile)
    validate_required(root, result)
    lectures, progress = validate_catalog(root, result)
    catalog = {str(item.get("id")): item for item in lectures if isinstance(item, dict)}
    validate_document_contracts(root, result)
    validate_compose(root, result)
    validate_paths(root, profile, result)
    validate_links(root, profile, result)

    if profile == "live":
        progress_by_id = {str(item.get("id")): item for item in progress if isinstance(item, dict)}
        packs = sorted(list(root.glob("courses/beginner/SD-BEG-*")) + list(root.glob("courses/advanced/SD-ADV-*")))
        for pack in packs:
            if not pack.is_dir():
                continue
            before = len(result.errors)
            validate_lecture_pack(pack, catalog, result)
            metadata = load_json(pack / "metadata.json", result, "LECTURE_METADATA_INVALID")
            if isinstance(metadata, dict):
                record = progress_by_id.get(str(metadata.get("lecture_id")))
                if isinstance(record, dict):
                    if record.get("artifact_state") != metadata.get("artifact_state") or record.get("learning_state") != metadata.get("learning_state"):
                        result.error("LECTURE_PROGRESS_PARITY_MISMATCH", str(metadata.get("lecture_id")))
            if len(result.errors) == before:
                pass
        result.statistics["generated_lecture_packs"] = len(packs)

    result.statistics = {**basic_statistics(root, profile), **result.statistics}
    return result


def validate_fixture(root: Path) -> dict[str, object]:
    fixture = root / "tests/fixtures/complete_lecture"
    base = Result("fixture")
    lectures_obj = load_json(root / "data/lectures.json", base, "CATALOG_JSON_INVALID")
    catalog = {str(item.get("id")): item for item in lectures_obj if isinstance(item, dict)} if isinstance(lectures_obj, list) else {}
    validate_lecture_pack(fixture, catalog, base, fixture=True)
    temporary, live_root = mutation_copy(root)
    try:
        copy_fixture_as_live(live_root)
        base.errors.extend(validate_root(live_root, "live").errors)
    finally:
        temporary.cleanup()
    return {
        "name": "complete_synthetic_ready_lecture_with_instructor_task",
        "status": "passed" if not base.errors else "failed",
        "detail": "Complete notes, review, task separation, PostgreSQL setup, honest skipped evidence, and Ready live-profile integration validated.",
        "errors": base.errors,
    }


def archive_entry_error(info: zipfile.ZipInfo) -> tuple[str, str] | None:
    name = info.filename
    path = PurePosixPath(name)
    if info.is_dir():
        return "ARCHIVE_DIRECTORY_ENTRY", name
    if name.startswith("/") or "\\" in name or any(part in {"", ".", ".."} for part in path.parts):
        return "ARCHIVE_UNSAFE_PATH", name
    mode = (info.external_attr >> 16) & 0xFFFF
    if stat.S_ISLNK(mode):
        return "ARCHIVE_SYMLINK", name
    parts = path.parts
    if ".git" in parts:
        return "ARCHIVE_GIT_METADATA", name
    if len(parts) >= 2 and parts[0] == "inputs" and parts[1] == "private":
        return "ARCHIVE_PRIVATE_SOURCE", name
    if any(part in FORBIDDEN_SECRET_COMPONENTS for part in parts):
        return "ARCHIVE_PRIVATE_PATH", name
    if parts[0] in WORKING_ROOT_DIRS or any(part in CACHE_DIRS for part in parts):
        return "ARCHIVE_WORKING_ARTIFACT", name
    if path.name == ".env" or (path.name.startswith(".env.") and path.name != ".env.example"):
        return "ARCHIVE_SECRET_FILE", name
    if path.suffix.lower() in RAW_SOURCE_SUFFIXES:
        return "ARCHIVE_RAW_SOURCE", name
    if path.suffix.lower() in FORBIDDEN_ARCHIVE_SUFFIXES:
        return "ARCHIVE_GENERATED_DATA", name
    if parts[0] in GENERATED_ROOT_DIRS or is_generated_lecture_path(path):
        return "ARCHIVE_GENERATED_LEARNING_CONTENT", name
    return None


def validate_archive(archive: Path) -> dict[str, object]:
    result = Result("archive-zip")
    archive_info: dict[str, object] = {
        "path": archive.name,
        "sha256": sha256_file(archive),
        "size_bytes": archive.stat().st_size,
    }
    try:
        with zipfile.ZipFile(archive) as bundle:
            infos = bundle.infolist()
            names = [info.filename for info in infos]
            archive_info["entry_count"] = len(infos)
            archive_info["directory_entry_count"] = sum(info.is_dir() for info in infos)
            archive_info["duplicate_entries"] = sorted({name for name in names if names.count(name) > 1})
            corrupt = bundle.testzip()
            archive_info["corrupt_entry"] = corrupt
            if corrupt:
                result.error("ARCHIVE_CORRUPT_ENTRY", corrupt)
            if len(names) != len(set(names)):
                result.error("ARCHIVE_DUPLICATE_ENTRY", "duplicate names found")
            for info in infos:
                error = archive_entry_error(info)
                if error:
                    result.error(error[0], error[1])
            if "README.md" not in names or "data/lectures.json" not in names:
                result.error("ARCHIVE_WRAPPER_DIRECTORY", "required root files are not directly at ZIP root")
            with tempfile.TemporaryDirectory(prefix="sd-learning-extract-") as temporary:
                destination = Path(temporary)
                if not result.errors:
                    bundle.extractall(destination)
                    extracted = validate_root(destination, "archive")
                    for error in extracted.errors:
                        result.errors.append(f"[EXTRACTED_VALIDATION] {error}")
                    for warning in extracted.warnings:
                        result.warnings.append(f"[EXTRACTED_VALIDATION] {warning}")
                    archive_info["extracted_validation"] = extracted.as_dict()
    except (OSError, zipfile.BadZipFile) as exc:
        result.error("ARCHIVE_OPEN_FAILED", str(exc))
    return {"archive": archive_info, "validation": result.as_dict()}


def make_zip_from_root(root: Path, destination: Path, extras: dict[str, bytes] | None = None) -> None:
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
        for path in repository_files(root, "bootstrap"):
            relative_path = PurePosixPath(path.relative_to(root).as_posix())
            if is_generated_lecture_path(relative_path) or relative_path.parts[0] in GENERATED_ROOT_DIRS:
                continue
            relative = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(2026, 8, 31, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = ((0o755 if path.suffix == ".py" else 0o644) & 0xFFFF) << 16
            bundle.writestr(info, path.read_bytes())
        for name, content in (extras or {}).items():
            bundle.writestr(name, content)


def mutation_copy(root: Path) -> tuple[tempfile.TemporaryDirectory[str], Path]:
    temporary = tempfile.TemporaryDirectory(prefix="sd-learning-mutation-")
    target = Path(temporary.name) / "root"
    shutil.copytree(root, target)
    return temporary, target


def mutate_json(path: Path, change: Callable[[object], None]) -> None:
    value = json.loads(path.read_text(encoding="utf-8"))
    change(value)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def copy_fixture_as_live(root: Path) -> Path:
    target = root / "courses/beginner/SD-BEG-050-relational-databases"
    shutil.copytree(root / "tests/fixtures/complete_lecture", target)
    mutate_json(root / "data/progress.json", lambda rows: rows[4].update({"artifact_state": "Ready"}))
    subprocess.run([sys.executable, str(root / "scripts/render_catalog.py")], cwd=root, check=True, capture_output=True)
    return target


def run_mutation_case(root: Path, name: str) -> list[str]:
    temporary, target = mutation_copy(root)
    try:
        profile = "bootstrap"
        if name == "duplicate_lecture_id":
            mutate_json(target / "data/lectures.json", lambda rows: rows[1].update({"id": rows[0]["id"]}))
        elif name == "invalid_id_sequence":
            mutate_json(target / "data/lectures.json", lambda rows: rows[0].update({"id": "SD-BEG-011"}))
        elif name == "blocking_prerequisite_added":
            mutate_json(target / "data/lectures.json", lambda rows: rows[0].update({"blocking_prerequisites": ["SD-BEG-020"]}))
        elif name == "missing_advanced_lecture":
            mutate_json(target / "data/lectures.json", lambda rows: rows.pop())
        elif name == "progress_title_tampered":
            mutate_json(target / "data/progress.json", lambda rows: rows[0].update({"title": "Wrong"}))
        elif name == "rendered_catalog_stale":
            (target / "COURSE_INDEX.md").write_text((target / "COURSE_INDEX.md").read_text(encoding="utf-8").replace("52 source videos", "51 source videos", 1), encoding="utf-8")
        elif name == "task_scan_contract_removed":
            mutate_json(target / "templates/lecture/source_manifest.json", lambda obj: obj["task_scan"].update({"ending_scanned": False}))
        elif name == "notes_template_heading_removed":
            path = target / "templates/lecture/notes.md"
            path.write_text(path.read_text(encoding="utf-8").replace("## Final revision card", "## Final recap"), encoding="utf-8")
        elif name == "postgres_port_not_loopback":
            path = target / "compose.yaml"
            path.write_text(path.read_text(encoding="utf-8").replace("127.0.0.1:${SD_POSTGRES_PORT:-55434}:5432", "${SD_POSTGRES_PORT:-55434}:5432"), encoding="utf-8")
        elif name == "postgres_latest_tag":
            path = target / "compose.yaml"
            path.write_text(path.read_text(encoding="utf-8").replace("postgres:18.6", "postgres:latest"), encoding="utf-8")
        elif name == "postgres_healthcheck_removed":
            path = target / "compose.yaml"
            text = path.read_text(encoding="utf-8")
            text = re.sub(r"\n    healthcheck:\n(?:      .*\n)+?(?=    labels:)", "\n", text)
            path.write_text(text, encoding="utf-8")
        elif name == "unsafe_lab_cleanup":
            path = target / "templates/lab/README.md"
            path.write_text(path.read_text(encoding="utf-8") + "\n```bash\ndocker system prune\n```\n", encoding="utf-8")
        elif name == "generated_lecture_in_bootstrap":
            path = target / "courses/beginner/SD-BEG-010-course-introduction"
            path.mkdir()
            (path / "notes.md").write_text("generated", encoding="utf-8")
        elif name == "live_pack_missing_visual_contract":
            profile = "live"
            pack = copy_fixture_as_live(target)
            path = pack / "notes.md"
            path.write_text(path.read_text(encoding="utf-8").replace("### Key insight", "### Main idea"), encoding="utf-8")
        elif name == "live_task_count_mismatch":
            profile = "live"
            pack = copy_fixture_as_live(target)
            mutate_json(pack / "source_manifest.json", lambda obj: obj["task_scan"].update({"task_count": 2}))
        elif name == "learner_attempt_contains_reference_code":
            profile = "live"
            pack = copy_fixture_as_live(target)
            solution = (pack / "tasks/SD-BEG-050-T01/reference/SOLUTION.md").read_text(encoding="utf-8")
            block = re.search(r"```sql\n.*?```", solution, flags=re.DOTALL).group(0)
            path = pack / "tasks/SD-BEG-050-T01/ATTEMPT.md"
            path.write_text(path.read_text(encoding="utf-8") + "\n" + block + "\n", encoding="utf-8")
        elif name == "skipped_task_claims_passed_evidence":
            profile = "live"
            pack = copy_fixture_as_live(target)
            path = pack / "tasks/SD-BEG-050-T01/lab/evidence.md"
            text = path.read_text(encoding="utf-8").replace("Status: Skipped", "Status: Passed").replace("None — execution skipped", "3 rows observed")
            path.write_text(text, encoding="utf-8")
        else:
            raise KeyError(name)
        return validate_root(target, profile).errors
    finally:
        temporary.cleanup()


def run_archive_mutation(root: Path, name: str) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="sd-learning-archive-mutation-") as temporary:
        archive = Path(temporary) / "mutated.zip"
        extras: dict[str, bytes]
        if name == "archive_git_metadata":
            extras = {".git/HEAD": b"ref: refs/heads/main\n"}
        elif name == "archive_private_transcript":
            extras = {"inputs/private/SD-BEG-010/transcript.srt": b"private"}
        elif name == "archive_raw_video":
            extras = {"course-video.mp4": b"not-a-real-video"}
        elif name == "archive_path_traversal":
            extras = {"../escape.txt": b"unsafe"}
        elif name == "archive_generated_lecture":
            extras = {"courses/beginner/SD-BEG-010-course-introduction/notes.md": b"generated"}
        else:
            raise KeyError(name)
        make_zip_from_root(root, archive, extras)
        return list(validate_archive(archive)["validation"]["errors"])


def run_self_tests(root: Path) -> dict[str, object]:
    definitions_obj = json.loads((root / "validation/expected_mutations.json").read_text(encoding="utf-8"))
    records = []
    archive_names = {item["name"] for item in definitions_obj if item.get("kind") == "archive"}
    for definition in definitions_obj:
        name = definition["name"]
        expected = definition["expected_error"]
        errors = run_archive_mutation(root, name) if name in archive_names else run_mutation_case(root, name)
        matches = [error for error in errors if error.startswith(f"[{expected}]")]
        records.append(
            {
                "name": name,
                "status": "passed" if matches else "failed",
                "expected_error": expected,
                "observed_matching_error": matches[0] if matches else None,
                "observed_error_count": len(errors),
            }
        )
    fixture = validate_fixture(root)
    return {
        "mutations": {
            "count": len(records),
            "passed": sum(item["status"] == "passed" for item in records),
            "status": "passed" if all(item["status"] == "passed" for item in records) else "failed",
            "cases": records,
        },
        "fixtures": {
            "count": 1,
            "passed": int(fixture["status"] == "passed"),
            "status": fixture["status"],
            "cases": [fixture],
        },
    }


def runtime_checks(root: Path) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    compile_result = subprocess.run(
        [sys.executable, "-m", "compileall", "-q", "scripts", "tests/fixtures/complete_lecture"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    checks.append(
        {
            "name": "python_compilation",
            "status": "passed" if compile_result.returncode == 0 else "failed",
            "returncode": compile_result.returncode,
            "detail": (compile_result.stderr or compile_result.stdout).strip(),
        }
    )
    if shutil.which("docker") is None:
        checks.append(
            {
                "name": "docker_compose_config",
                "status": "skipped",
                "detail": "docker executable not available; no Compose service was started",
            }
        )
    else:
        completed = subprocess.run(["docker", "compose", "config", "--quiet"], cwd=root, capture_output=True, text=True, check=False)
        checks.append(
            {
                "name": "docker_compose_config",
                "status": "passed" if completed.returncode == 0 else "failed",
                "returncode": completed.returncode,
                "detail": (completed.stderr or completed.stdout).strip(),
            }
        )
    checks.append(
        {
            "name": "course_source_processing",
            "status": "skipped",
            "detail": "No private transcript/slides/video were supplied to this bootstrap-generation run.",
        }
    )
    checks.append(
        {
            "name": "postgresql_task_execution",
            "status": "skipped",
            "detail": "The bootstrap contains no processed course task; the synthetic fixture deliberately records unexecuted PostgreSQL evidence.",
        }
    )
    return checks


def build_report(root: Path, archive: Path, include_self_tests: bool = True) -> dict[str, object]:
    archive_validation = validate_archive(archive)
    working = validate_root(root, "bootstrap")
    self_tests = run_self_tests(root) if include_self_tests else None
    checks = runtime_checks(root)
    errors = list(working.errors) + list(archive_validation["validation"]["errors"])
    if self_tests and (self_tests["mutations"]["status"] != "passed" or self_tests["fixtures"]["status"] != "passed"):
        errors.append("[SELF_TEST_FAILURE] mutation or fixture self-tests failed")
    if any(item["status"] == "failed" for item in checks):
        errors.append("[RUNTIME_CHECK_FAILURE] one or more attempted runtime checks failed")
    return {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repository_root": ".",
        "status": "passed" if not errors else "failed",
        "archive": archive_validation["archive"],
        "working_validation": working.as_dict(),
        "archive_validation": archive_validation["validation"],
        "self_tests": self_tests,
        "runtime_checks": checks,
        "manual_qualitative_inspection": {"status": "not_performed"},
        "errors": errors,
        "warnings": list(working.warnings) + list(archive_validation["validation"]["warnings"]),
    }


def comparable_report(report: dict[str, object]) -> dict[str, object]:
    return {
        "status": report.get("status"),
        "archive": report.get("archive"),
        "working_validation": report.get("working_validation"),
        "archive_validation": report.get("archive_validation"),
        "self_tests": report.get("self_tests"),
        "errors": report.get("errors"),
        "warnings": report.get("warnings"),
    }


def verify_report(root: Path, archive: Path, report_path: Path) -> dict[str, object]:
    supplied = json.loads(report_path.read_text(encoding="utf-8"))
    recomputed = build_report(root, archive, include_self_tests=supplied.get("self_tests") is not None)
    errors = []
    supplied_archive = supplied.get("archive", {})
    actual_archive = recomputed["archive"]
    for field in ("path", "sha256", "size_bytes", "entry_count", "directory_entry_count", "duplicate_entries", "corrupt_entry"):
        if supplied_archive.get(field) != actual_archive.get(field):
            errors.append(f"REPORT_ARCHIVE_{field.upper()}_MISMATCH")
    if supplied.get("working_validation") != recomputed.get("working_validation"):
        errors.append("REPORT_WORKING_VALIDATION_MISMATCH")
    if supplied.get("archive_validation") != recomputed.get("archive_validation"):
        errors.append("REPORT_ARCHIVE_VALIDATION_MISMATCH")
    if supplied.get("self_tests") != recomputed.get("self_tests"):
        errors.append("REPORT_SELF_TEST_EVIDENCE_MISMATCH")
    if supplied.get("errors") != recomputed.get("errors") or supplied.get("warnings") != recomputed.get("warnings"):
        errors.append("REPORT_RESULT_MISMATCH")
    return {
        "status": "passed" if not errors else "failed",
        "errors": errors,
        "archive_sha256": actual_archive.get("sha256"),
        "self_tests_compared": supplied.get("self_tests") is not None,
    }


def print_summary(payload: dict[str, object]) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--profile", choices=("bootstrap", "live", "archive"), default="bootstrap")
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--write-report", type=Path)
    parser.add_argument("--verify-report", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()

    if args.verify_report:
        if not args.archive:
            parser.error("--verify-report requires --archive")
        payload = verify_report(root, args.archive.resolve(), args.verify_report.resolve())
    elif args.write_report:
        if not args.archive:
            parser.error("--write-report requires --archive")
        payload = build_report(root, args.archive.resolve(), include_self_tests=args.self_test)
        args.write_report.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    elif args.archive:
        payload = validate_archive(args.archive.resolve())
    else:
        result = validate_root(root, args.profile)
        payload = result.as_dict()
        if args.self_test:
            payload["self_tests"] = run_self_tests(root)
            if payload["self_tests"]["mutations"]["status"] != "passed" or payload["self_tests"]["fixtures"]["status"] != "passed":
                payload["status"] = "failed"
    if args.json_out:
        args.json_out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print_summary(payload)
    return 0 if payload.get("status") == "passed" or payload.get("validation", {}).get("status") == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Render human course indexes and initial progress from the canonical catalog."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "lectures.json"
PROGRESS = ROOT / "data" / "progress.json"


def load_catalog() -> list[dict[str, object]]:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def track_table(track: str, lectures: list[dict[str, object]]) -> str:
    title = "System Design for Beginners" if track == "beginner" else "System Design Masterclass"
    explanation = (
        "Choose any video in any order. The rows identify source videos and canonical output folders; "
        "they are not a prerequisite sequence."
    )
    lines = [
        f"# {title}", "", explanation, "", "## Status legend", "",
        "- `⬜ Not started`", "- `🧩 Sources ready`", "- `📝 Pack ready`",
        "- `🧪 Task attempted`", "- `🔁 Reviewing`", "- `✅ Comfortable`", "",
        "| # | ID | Lecture | Canonical output folder | Status |", "|---:|---|---|---|---|",
    ]
    for item in lectures:
        if item["track"] != track:
            continue
        note = " ⚠️ source title needs source verification" if item["source_title_status"] == "ambiguous" else ""
        folder = f"{item['id']}-{item['slug']}"
        lines.append(f"| {int(item['number']):02d} | `{item['id']}` | {item['title']}{note} | `{folder}` | ⬜ Not started |")
    lines += ["", "The title-warning rows must be resolved from their supplied transcript/slides; never guess from the filename alone.", ""]
    return "\n".join(lines)


def course_index(lectures: list[dict[str, object]]) -> str:
    lines = [
        "# Canonical course index", "",
        "The catalog contains 52 source videos: 36 Beginner and 16 Advanced. The order mirrors the source catalog only for identification. Rahul may process any ID at any time.", "",
        "There are no blocking prerequisites. Codex supplies a short bridge inside the selected lecture whenever useful background is missing.", "",
        "| ID | Track | # | Exact source title | Themes | Title status |", "|---|---|---:|---|---|---|",
    ]
    for item in lectures:
        themes = ", ".join(f"`{value}`" for value in item["themes"])
        lines.append(f"| `{item['id']}` | {str(item['track']).title()} | {int(item['number']):02d} | {item['title']} | {themes} | {item['source_title_status']} |")
    lines += ["", "Machine source: [`data/lectures.json`](data/lectures.json).", ""]
    return "\n".join(lines)


def load_progress() -> list[dict[str, object]]:
    if not PROGRESS.is_file():
        return []
    value = json.loads(PROGRESS.read_text(encoding="utf-8"))
    return value if isinstance(value, list) else []


def progress_records(
    lectures: list[dict[str, object]], existing: list[dict[str, object]]
) -> list[dict[str, object]]:
    existing_by_id = {str(item.get("id")): item for item in existing if isinstance(item, dict)}
    return [
        {
            "id": item["id"], "title": item["title"], "track": item["track"],
            "artifact_state": existing_by_id.get(str(item["id"]), {}).get("artifact_state", "Absent"),
            "learning_state": existing_by_id.get(str(item["id"]), {}).get("learning_state", "Not started"),
            "instructor_tasks": existing_by_id.get(str(item["id"]), {}).get("instructor_tasks"),
            "tasks_attempted": existing_by_id.get(str(item["id"]), {}).get("tasks_attempted", 0),
            "next_review": existing_by_id.get(str(item["id"]), {}).get("next_review"),
        }
        for item in lectures
    ]


def progress_markdown(records: list[dict[str, object]]) -> str:
    lines = [
        "# Progress", "",
        "Artifact generation and learning are separate. A generated pack does not prove understanding.", "",
        "## States", "",
        "- Artifact: `Absent → Draft → Ready`", "- Learning: `Not started → Learning → Practiced → Recalled → Demonstrated → Comfortable`", "",
        "| ID | Track | Lecture | Artifact | Learning | Instructor tasks | Attempted | Next review |", "|---|---|---|---|---|---:|---:|---|",
    ]
    for record in records:
        count = "—" if record["instructor_tasks"] is None else str(record["instructor_tasks"])
        review = record["next_review"] or "—"
        lines.append(
            f"| `{record['id']}` | {str(record['track']).title()} | {record['title']} | {record['artifact_state']} | "
            f"{record['learning_state']} | {count} | {record['tasks_attempted']} | {review} |"
        )
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if rendered files differ")
    args = parser.parse_args()
    lectures = load_catalog()
    records = progress_records(lectures, load_progress())
    outputs = {
        ROOT / "COURSE_INDEX.md": course_index(lectures),
        ROOT / "courses" / "beginner" / "README.md": track_table("beginner", lectures),
        ROOT / "courses" / "advanced" / "README.md": track_table("advanced", lectures),
        PROGRESS: json.dumps(records, indent=2, ensure_ascii=False) + "\n",
        ROOT / "PROGRESS.md": progress_markdown(records),
    }
    differences = []
    for path, expected in outputs.items():
        if args.check:
            if not path.is_file() or path.read_text(encoding="utf-8") != expected:
                differences.append(path.relative_to(ROOT).as_posix())
        else:
            path.write_text(expected, encoding="utf-8")
    if differences:
        raise SystemExit("Catalog render mismatch: " + ", ".join(differences))


if __name__ == "__main__":
    main()

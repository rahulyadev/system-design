#!/usr/bin/env python3
"""Find canonical lecture IDs without requiring a sequential study order."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def score(lecture: dict[str, object], words: list[str]) -> int:
    haystack = " ".join(
        [
            str(lecture["id"]),
            str(lecture["title"]),
            " ".join(str(item) for item in lecture.get("themes", [])),
        ]
    ).lower()
    return sum(3 if word in str(lecture["title"]).lower() else 1 for word in words if word in haystack)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("query", help="topic, title fragment, or canonical ID")
    parser.add_argument("--limit", type=int, default=8)
    args = parser.parse_args()

    lectures = json.loads((ROOT / "data/lectures.json").read_text(encoding="utf-8"))
    words = [word.lower() for word in args.query.split() if word.strip()]
    ranked = sorted(
        ((score(lecture, words), lecture) for lecture in lectures),
        key=lambda pair: (-pair[0], pair[1]["id"]),
    )
    matches = [lecture for points, lecture in ranked if points > 0][: args.limit]
    if not matches:
        print("No catalog match. Try a broader concept or inspect COURSE_INDEX.md.")
        return 1
    for lecture in matches:
        themes = ", ".join(lecture["themes"])
        print(f'{lecture["id"]}\t{lecture["track"]}\t{lecture["title"]}\t{themes}')
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

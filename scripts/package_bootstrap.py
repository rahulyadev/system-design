#!/usr/bin/env python3
"""Create a deterministic, wrapper-free bootstrap ZIP."""

from __future__ import annotations

import argparse
from pathlib import Path

from validate_repo import ROOT, make_zip_from_root, sha256_file, validate_archive, validate_root


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    root = args.root.resolve()
    output = args.output.resolve()

    validation = validate_root(root, "bootstrap")
    if validation.errors:
        for error in validation.errors:
            print(error)
        return 1

    output.parent.mkdir(parents=True, exist_ok=True)
    make_zip_from_root(root, output)
    archive = validate_archive(output)
    if archive["validation"]["errors"]:
        for error in archive["validation"]["errors"]:
            print(error)
        return 1

    print(f"path={output}")
    print(f"sha256={sha256_file(output)}")
    print(f"size_bytes={output.stat().st_size}")
    print(f"entry_count={archive['archive']['entry_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

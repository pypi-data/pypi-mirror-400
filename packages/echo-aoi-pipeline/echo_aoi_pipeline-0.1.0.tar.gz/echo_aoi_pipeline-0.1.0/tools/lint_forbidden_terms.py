#!/usr/bin/env python3
"""Fail fast when banned AI-responsibility phrases appear in the repo."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

FORBIDDEN_PHRASES = [
    "완전 자율",
    "Echo가 책임",
    "시스템이 판단",
]
SCAN_PREFIXES = (
    "domain/",
    "echo_engine/",
    "echo_patterns/",
    "demo",
    "quick_local_excel.py",
    "dexa_autonomous_executor.py",
    "docs/principles/",
)


def iter_tracked_files() -> list[Path]:
    repo_root = Path(__file__).resolve().parents[1]
    output = subprocess.check_output(["git", "ls-files"], text=True)
    files = []
    for rel in output.splitlines():
        path = repo_root / rel
        rel_posix = path.relative_to(repo_root).as_posix()
        if path.is_file() and any(
            rel_posix.startswith(prefix) for prefix in SCAN_PREFIXES
        ):
            files.append(path)
    return files


def main() -> int:
    violations: list[tuple[Path, int, str, str]] = []

    for path in iter_tracked_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue  # binary file

        for line_no, line in enumerate(text.splitlines(), start=1):
            for phrase in FORBIDDEN_PHRASES:
                if phrase in line:
                    violations.append((path, line_no, phrase, line.strip()))

    if violations:
        print("❌ Forbidden AI-responsibility phrases detected:\n")
        for path, line_no, phrase, snippet in violations:
            print(f"  - {path}:{line_no}: '{phrase}' → {snippet}")
        print("\nSet HUMAN_IMPERFECTION boundary-compliant wording before re-running.")
        return 1

    print("✅ No forbidden phrases found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

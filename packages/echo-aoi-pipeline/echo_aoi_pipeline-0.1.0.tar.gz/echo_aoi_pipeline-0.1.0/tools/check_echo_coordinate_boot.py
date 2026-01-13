#!/usr/bin/env python3
"""
Fail-fast check that ensures the Echo Coordinate Boot checklist is signed off.

This script scans QA_ECHO_COORDINATE_BOOT_CHECKLIST.md and reports any unchecked
items (lines containing "- [ ]"). Releases should only proceed when every item is
acknowledged with "[x]". Use --allow-incomplete or ALLOW_INCOMPLETE_BOOT_QA=1 to
override in emergency situations.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

CHECKLIST_PATH = Path("QA_ECHO_COORDINATE_BOOT_CHECKLIST.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Echo coordinate boot QA guard")
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="Allow unchecked items (or set ALLOW_INCOMPLETE_BOOT_QA=1)",
    )
    return parser.parse_args()


def load_checklist() -> list[str]:
    if not CHECKLIST_PATH.exists():
        raise SystemExit(f"Checklist file not found: {CHECKLIST_PATH}")
    return CHECKLIST_PATH.read_text(encoding="utf-8").splitlines()


def find_unchecked(lines: list[str]) -> list[tuple[int, str]]:
    unchecked: list[tuple[int, str]] = []
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("- [ ]"):
            unchecked.append((idx, stripped))
    return unchecked


def main() -> int:
    args = parse_args()
    allow_incomplete = args.allow_incomplete or os.getenv("ALLOW_INCOMPLETE_BOOT_QA") == "1"

    lines = load_checklist()
    unchecked = find_unchecked(lines)
    if unchecked and not allow_incomplete:
        print("❌ Echo Coordinate Boot checklist has unchecked items:")
        for idx, text in unchecked:
            print(f"  L{idx}: {text}")
        print(
            "Mark each item as completed ([x]) in "
            f"{CHECKLIST_PATH} or rerun with --allow-incomplete if this is intentional."
        )
        return 1

    if unchecked:
        print("⚠️  Unchecked items ignored due to override:")
        for idx, text in unchecked:
            print(f"  L{idx}: {text}")
        return 0

    print("✅ Echo Coordinate Boot checklist is fully signed off.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

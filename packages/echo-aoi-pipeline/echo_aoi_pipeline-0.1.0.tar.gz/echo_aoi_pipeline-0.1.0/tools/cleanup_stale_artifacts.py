#!/usr/bin/env python3
"""
Remove or archive stale generated artifacts (logs, traces, tmp files)
to keep ARAL/Code State reporting directories manageable.

Usage:
    python tools/cleanup_stale_artifacts.py --days 30
    python tools/cleanup_stale_artifacts.py --dirs logs trace tmp --dry-run
"""

from __future__ import annotations

import argparse
import shutil
import sys
from datetime import datetime, timedelta
from pathlib import Path


DEFAULT_DIRS = [
    "logs",
    "trace",
    "tmp",
    "governance/aral_external_proof",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Purge stale generated artifacts.")
    parser.add_argument(
        "--dirs",
        nargs="+",
        default=DEFAULT_DIRS,
        help="Directories to scan (default: logs trace tmp governance/aral_external_proof).",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=30,
        help="Files older than this many days are removed (default: 30).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print files that would be deleted without removing them.",
    )
    parser.add_argument(
        "--archive",
        type=Path,
        help="Optional archive directory to move files into instead of deleting.",
    )
    return parser.parse_args()


def cleanup_directory(path: Path, cutoff: datetime, dry_run: bool, archive_dir: Path | None) -> list[Path]:
    removed = []
    if not path.exists():
        return removed

    for file in path.rglob("*"):
        if not file.is_file():
            continue
        mtime = datetime.fromtimestamp(file.stat().st_mtime)
        if mtime < cutoff:
            removed.append(file)
            if dry_run:
                continue
            if archive_dir:
                archive_dir.mkdir(parents=True, exist_ok=True)
                dest = archive_dir / file.relative_to(path)
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(file), dest)
            else:
                file.unlink(missing_ok=True)
    return removed


def main() -> None:
    args = parse_args()
    cutoff = datetime.now() - timedelta(days=args.days)
    total_removed = []

    for directory in args.dirs:
        path = Path(directory)
        removed = cleanup_directory(path, cutoff, args.dry_run, args.archive)
        total_removed.extend(removed)
        action = "Would remove" if args.dry_run else "Removed"
        print(f"{action} {len(removed)} files under {path}")

    if args.dry_run:
        print("Dry run complete.")
    else:
        print(f"Cleanup complete. {len(total_removed)} files processed.")


if __name__ == "__main__":
    if sys.version_info < (3, 8):
        sys.exit("Python 3.8+ required.")
    main()

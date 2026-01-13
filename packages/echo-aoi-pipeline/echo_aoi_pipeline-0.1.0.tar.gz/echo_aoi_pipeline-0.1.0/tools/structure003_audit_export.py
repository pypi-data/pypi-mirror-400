#!/usr/bin/env python3
"""
Structure #003 - Phase 4 Audit Export CLI
"""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from echo_engine.audit_snapshot import (
    build_snapshot,
    snapshot_hash,
    write_snapshot_files,
)

EXPORT_DIR = Path("artifacts/structure003_phase4")


def export_event(event_id: str, fmt: str) -> List[Path]:
    snapshot = build_snapshot(event_id)
    output_dir = EXPORT_DIR / event_id
    formats = ("json", "csv") if fmt == "both" else (fmt,)
    paths = write_snapshot_files(snapshot, output_dir, formats)
    # Also write overall hash for API usage
    hash_value = snapshot_hash(snapshot)
    (output_dir / "snapshot.hash").write_text(f"{hash_value}\n")
    return paths


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export Structure #003 ledger snapshots.")
    parser.add_argument("--event-id", required=True, help="Event ID to export")
    parser.add_argument("--format", choices=["json", "csv", "both"], default="both")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    paths = export_event(args.event_id, args.format)
    print("✅ Export complete:")
    for path in paths:
        hash_path = path.with_suffix(path.suffix + ".sha256")
        hash_text = hash_path.read_text().strip() if hash_path.exists() else "missing hash"
        print(f" - {path} ({hash_text})")


if __name__ == "__main__":
    main()

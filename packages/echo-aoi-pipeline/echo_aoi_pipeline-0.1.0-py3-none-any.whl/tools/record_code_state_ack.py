#!/usr/bin/env python3
"""
Record a human acknowledgement decision for the Code State bundle.

Choices: approve, reject, retopic, additional_verification.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

ACK_PATH = Path("governance/code_state/acknowledgements.jsonl")
DECISIONS = {"approve", "reject", "retopic", "additional_verification"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append an acknowledgement record for a Code State report.")
    parser.add_argument(
        "--decision",
        required=True,
        choices=sorted(DECISIONS),
        help="Selected action after reviewing the Code State bundle.",
    )
    parser.add_argument(
        "--reason",
        default="",
        help="Free-form rationale for the selected action.",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        help="Optional path referencing the reviewed report bundle.",
    )
    parser.add_argument(
        "--commit",
        help="Commit SHA this acknowledgement applies to (defaults to HEAD).",
    )
    parser.add_argument(
        "--pr",
        help="Optional PR number or identifier.",
    )
    parser.add_argument(
        "--actor",
        help="Name or handle of the person recording the acknowledgement (defaults to $USER).",
    )
    return parser.parse_args()


def resolve_commit(provided: str | None) -> str:
    if provided:
        return provided
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def main() -> None:
    args = parse_args()
    ack_dir = ACK_PATH.parent
    ack_dir.mkdir(parents=True, exist_ok=True)
    commit = resolve_commit(args.commit)
    entry: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "decision": args.decision,
        "reason": args.reason,
        "commit": commit,
        "report_path": str(args.report_path) if args.report_path else None,
        "pr": args.pr,
        "actor": args.actor or os.environ.get("CODE_STATE_ACTOR") or os.environ.get("USER") or "unknown",
    }
    with ACK_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"Recorded acknowledgement for commit {commit} with decision '{args.decision}'.")


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"Failed to determine commit: {exc}", file=sys.stderr)
        sys.exit(1)

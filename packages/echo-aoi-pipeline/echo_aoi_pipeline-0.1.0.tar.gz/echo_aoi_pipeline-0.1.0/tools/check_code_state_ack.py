#!/usr/bin/env python3
"""
Verify that a Code State acknowledgement entry exists for a given commit.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ACK_PATH = Path("governance/code_state/acknowledgements.jsonl")
DECISIONS = {"approve", "reject", "retopic", "additional_verification"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check for acknowledgement records.")
    parser.add_argument(
        "--commit",
        required=True,
        help="Commit SHA that must have an acknowledgement entry.",
    )
    parser.add_argument(
        "--ack-file",
        type=Path,
        default=ACK_PATH,
        help="Path to the acknowledgement JSONL file.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.ack_file.exists():
        raise SystemExit(f"Acknowledgement log not found at {args.ack_file}")
    with args.ack_file.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("commit") == args.commit and record.get("decision") in DECISIONS:
                print(f"Acknowledgement found for commit {args.commit}: {record.get('decision')}")
                return
    raise SystemExit(f"No acknowledgement entry found for commit {args.commit}.")


if __name__ == "__main__":
    main()

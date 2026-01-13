#!/usr/bin/env python3
"""Verify that the responsibility gate checklist has been answered."""

from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_KEYS = ("human_pause", "ai_block", "judgment_trace")
GATE_FILE = Path("RESPONSIBILITY_GATE.json")


def main() -> int:
    if not GATE_FILE.exists():
        print(f"❌ Missing {GATE_FILE}. Fill it with the three required answers.")
        return 1

    data = json.loads(GATE_FILE.read_text(encoding="utf-8"))
    missing = [
        key for key in REQUIRED_KEYS if not str(data.get(key, "")).strip()
    ]
    if missing:
        print(
            f"❌ responsibility gate incomplete. "
            f"Provide answers for: {', '.join(missing)}"
        )
        return 1

    print("✅ Responsibility gate answers present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

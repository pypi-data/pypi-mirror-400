#!/usr/bin/env python3
"""Pre-commit guard that enforces the LocalEcho router/runtime contract."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "CHWARURUK_LOCAL_ECHO_GUIDE.md"


def main() -> int:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        print("Unable to inspect staged files for LocalEcho contract enforcement.")
        return result.returncode

    staged = [line.strip() for line in result.stdout.splitlines() if line.strip()]
    if not staged:
        return 0

    violations: list[str] = []
    for rel_path in staged:
        path = ROOT / rel_path
        if not path.exists() or path.is_dir():
            continue
        if rel_path.startswith("ops/eui/backend/routers/") or rel_path.startswith(
            "ops/eui/backend/runtime/"
        ):
            content = path.read_text(encoding="utf-8")
            if "LOCAL_ECHO_TEST_MODE" not in content:
                violations.append(rel_path)

    if violations:
        print(
            "LocalEcho contract violation detected in the following files (missing LOCAL_ECHO_TEST_MODE guard):"
        )
        for item in violations:
            print(f" - {item}")
        print(
            "All new routers/runtime services must follow CHWARURUK_LOCAL_ECHO_GUIDE.md. "
            "Add the guard or reference the deterministic factory helpers before committing."
        )
        return 1

    if not GUIDE.exists():
        print("CHWARURUK_LOCAL_ECHO_GUIDE.md is missing. Please restore before committing.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())


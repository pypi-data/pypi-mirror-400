#!/usr/bin/env python3
"""Simulate Dexa automation, Claude Code patch, Echo judgment 10 times."""

from __future__ import annotations

import json
import random
import subprocess
import sys
import time
from pathlib import Path

BASE = Path("artifacts/triple_engine")
BASE.mkdir(parents=True, exist_ok=True)
A_LOG = BASE / "automation"
B_LOG = BASE / "patch"
A_LOG.mkdir(exist_ok=True)
B_LOG.mkdir(exist_ok=True)

IDEA_TEMPLATE = "A단계 로그 {a_log}, B단계 로그 {b_log} 검토해서 품질 보고서 작성"

random.seed(42)

def simulate_a(run: int) -> Path:
    path = A_LOG / f"run{run:02d}_A.log"
    lines = ["Dexa Automation Log", f"run={run}", "steps:" + str(random.randint(5, 15))]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def simulate_b(run: int, a_path: Path) -> Path:
    path = B_LOG / f"run{run:02d}_B.log"
    lines = ["Claude Patch Log", f"run={run}", f"source={a_path.name}", "errors_fixed=1"]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def run_echo(idea: str) -> None:
    cmd = [sys.executable, "scripts/echo_cli.py", "run", "--idea", idea]
    subprocess.run(cmd, check=True)


def main() -> None:
    for run in range(1, 11):
        a_path = simulate_a(run)
        b_path = simulate_b(run, a_path)
        idea = IDEA_TEMPLATE.format(a_log=a_path, b_log=b_path)
        print("[triple]", run, idea)
        run_echo(idea)
        time.sleep(0.1)

if __name__ == "__main__":
    main()

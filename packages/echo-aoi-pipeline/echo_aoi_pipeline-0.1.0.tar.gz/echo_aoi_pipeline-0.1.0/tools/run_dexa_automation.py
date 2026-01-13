#!/usr/bin/env python3
"""Simulate Dexa automation steps 10 times, emitting structured logs."""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

ART_BASE = Path("artifacts/triple_engine/engine1")
LOG_BASE = Path("logs/engine1")
STEPS = [
    "open_browser",
    "navigate_page",
    "read_dom",
    "capture_screenshot",
    "write_local_file",
    "record_state",
]

def ensure_dirs() -> None:
    ART_BASE.mkdir(parents=True, exist_ok=True)
    LOG_BASE.mkdir(parents=True, exist_ok=True)


def simulate_run(run: int) -> None:
    run_id = f"engine1_run{run:02d}"
    timestamp = datetime.now(timezone.utc).isoformat()
    art = ART_BASE / f"{run_id}.json"
    log = LOG_BASE / f"{run_id}_trace.log"
    payload = {
        "run_id": run_id,
        "timestamp": timestamp,
        "steps": [],
    }
    lines = [f"run={run_id}", f"timestamp={timestamp}"]
    for step in STEPS:
        detail = {
            "step": step,
            "status": "ok",
            "details": f"Simulated {step.replace('_', ' ')}",
        }
        payload["steps"].append(detail)
        lines.append(f"{step}: ok")
    art.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    log.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    ensure_dirs()
    for run in range(1, 11):
        simulate_run(run)
        time.sleep(0.05)

if __name__ == "__main__":
    main()

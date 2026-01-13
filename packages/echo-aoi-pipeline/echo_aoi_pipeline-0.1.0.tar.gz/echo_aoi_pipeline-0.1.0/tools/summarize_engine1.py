#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

BASE = Path("artifacts/triple_engine/engine1")
TRACE_DIR = Path("logs/engine1")
SUMMARY_DIR = BASE / "summary"
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)


def summarize() -> None:
    summary = []
    for json_path in sorted(BASE.glob("engine1_run*_*.json")):
        run_id = json_path.stem
        trace_path = TRACE_DIR / f"{run_id}_trace.log"
        payload = json.loads(json_path.read_text(encoding="utf-8"))
        entry = {
            "run_id": run_id,
            "timestamp": payload.get("timestamp"),
            "steps": payload.get("steps", []),
            "trace_path": str(trace_path),
            "status": "success",
        }
        summary.append(entry)
    out = SUMMARY_DIR / "engine1_summary.json"
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

if __name__ == "__main__":
    summarize()

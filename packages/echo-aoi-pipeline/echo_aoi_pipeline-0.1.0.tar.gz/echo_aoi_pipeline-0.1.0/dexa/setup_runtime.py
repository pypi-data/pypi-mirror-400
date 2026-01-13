"""
Utility helpers that guarantee Dexa runtime scaffolding exists before tooling runs.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

DEXA_DIR = Path("dexa")
DEXA_RUNTIME_DIR = Path("dexa_runtime")
MCP_STATUS_PATH = DEXA_DIR / "mcp_runtime_status.json"
RUNTIME_STATUS_PATH = DEXA_RUNTIME_DIR / "status.json"
MCP_METRICS_PATH = DEXA_RUNTIME_DIR / "mcp_metrics.json"

_DEFAULT_STATUS = {
    "checked_at": None,
    "endpoint": None,
    "health_url": None,
    "status": "unknown",
    "steps": {},
}

_DEFAULT_METRICS = {
    "call_count": 0,
    "error_count": 0,
    "latencies": [],
    "tool_usage": {},
    "floating_mode_counts": {},
    "last_call": None,
    "error_rate": 0.0,
}


def _write_json_if_missing(path: Path, payload: Dict[str, Any]) -> None:
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def ensure_runtime_scaffolding() -> None:
    """
    Ensure the Dexa runtime folder exists with baseline JSON seeds.
    """
    timestamp = datetime.now(timezone.utc).isoformat()
    runtime_status = dict(_DEFAULT_STATUS)
    runtime_status["checked_at"] = runtime_status.get("checked_at") or timestamp
    _write_json_if_missing(RUNTIME_STATUS_PATH, runtime_status)

    metrics_payload = dict(_DEFAULT_METRICS)
    metrics_payload["last_call"] = metrics_payload.get("last_call") or timestamp
    _write_json_if_missing(MCP_METRICS_PATH, metrics_payload)

    mcp_status = dict(_DEFAULT_STATUS)
    mcp_status["checked_at"] = mcp_status.get("checked_at") or timestamp
    _write_json_if_missing(MCP_STATUS_PATH, mcp_status)


__all__ = ["ensure_runtime_scaffolding"]

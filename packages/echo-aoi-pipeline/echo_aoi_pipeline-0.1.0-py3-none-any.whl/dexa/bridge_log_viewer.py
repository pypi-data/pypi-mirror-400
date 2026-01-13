"""
Simple log viewer + programmatic snapshot helpers for Dexa↔Playwright bridge telemetry.
"""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

from dexa.setup_runtime import ensure_runtime_scaffolding

STATUS_PATH = Path("dexa/mcp_runtime_status.json")
METRICS_PATH = Path("dexa_runtime/mcp_metrics.json")


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def snapshot_payload() -> Dict[str, Any]:
    """
    Combined payload consumed by CLI, APIs, and the EUI Runtime Control panel.
    """
    ensure_runtime_scaffolding()
    status = _load_json(STATUS_PATH)
    metrics = _load_json(METRICS_PATH)
    return {
        "generated_at": _now(),
        "status": status or {},
        "metrics": metrics or {},
    }


def print_snapshot() -> None:
    payload = snapshot_payload()
    status = payload["status"]
    metrics = payload["metrics"]

    print("=== Bridge Status Snapshot ===")
    if status:
        print(f"checked_at : {status.get('checked_at')}")
        print(f"endpoint   : {status.get('endpoint')}")
        print(f"health_url : {status.get('health_url')}")
        print(f"status     : {status.get('status')}")
        steps = status.get("steps") or {}
        for key, step_payload in steps.items():
            result = step_payload.get("status")
            extra = step_payload.get("detail") or step_payload.get("response")
            print(f" - {key}: {result}", end="")
            if extra:
                print(f" ({extra})")
            else:
                print()
    else:
        print("(no MCP runtime status yet)")

    print("\n=== MCP Metrics ===")
    if metrics:
        print(f"calls      : {metrics.get('call_count')}")
        print(f"errors     : {metrics.get('error_count')}")
        avg = metrics.get("avg_latency_ms")
        if avg is not None:
            print(f"avg_latency: {avg}")
        tool_usage = metrics.get("tool_usage") or {}
        if tool_usage:
            tools_preview = ", ".join(f"{k}:{v}" for k, v in sorted(tool_usage.items()))
            print(f"tool_usage : {tools_preview}")
        mode_counts = metrics.get("floating_mode_counts") or {}
        if mode_counts:
            modes = ", ".join(f"{k}:{v}" for k, v in sorted(mode_counts.items()))
            print(f"floating   : {modes}")
    else:
        print("(no MCP metrics yet)")
    print("==============================")


def follow(interval: float = 2.0) -> None:
    last_signature: Optional[str] = None
    print_snapshot()
    try:
        while True:
            payload = snapshot_payload()
            signature = json.dumps(payload, sort_keys=True)
            if signature != last_signature:
                print(f"\n[{payload['generated_at']}] update detected")
                print_snapshot()
                last_signature = signature
            time.sleep(max(0.5, interval))
    except KeyboardInterrupt:
        print("\nStopped log viewer.")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dexa bridge log viewer")
    parser.add_argument(
        "--follow",
        action="store_true",
        help="Stream updates as the status or metrics files change",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Polling interval while following logs (seconds)",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if args.follow:
        follow(interval=args.interval)
    else:
        print_snapshot()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

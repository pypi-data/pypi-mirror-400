"""
Utility wrapper that runs a lightweight DOM capture to verify the Playwright bridge.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, Optional, Sequence

from dexa.dom_capture_launcher import CaptureResult, DexaDOMCaptureLauncher


def run_smoke_capture(
    mode: str = "browser_excel",
    *,
    excel_path: Optional[Path] = None,
    inspector: bool = False,
    bridge_url: Optional[str] = None,
    verbose: bool = True,
) -> Dict[str, object]:
    """
    Execute a compact DOM capture so operators can confirm Dexa→Playwright routing.
    """
    launcher = DexaDOMCaptureLauncher(
        inspector_mode=inspector,
        bridge_url=bridge_url,
    )
    capture = launcher.capture(excel_path=excel_path, mode=mode)
    summary = _summarize_capture(capture)
    if verbose:
        _print_summary(summary)
    return summary


def _summarize_capture(capture: CaptureResult) -> Dict[str, object]:
    node_types: Dict[str, int] = {}
    for node in capture.nodes:
        node_types[node.element_type] = node_types.get(node.element_type, 0) + 1
    return {
        "timestamp": capture.timestamp,
        "mode": capture.mode,
        "excel_path": capture.excel_path,
        "node_count": len(capture.nodes),
        "node_types": node_types,
        "screenshot": capture.screenshot_path,
        "capsule_path": capture.metadata.get("capsule_path"),
        "errors": capture.errors,
    }


def _print_summary(summary: Dict[str, object]) -> None:
    print("=== Dexa DOM Capture Smoke ===")
    print(f"timestamp : {summary['timestamp']}")
    print(f"mode      : {summary['mode']}")
    print(f"excel     : {summary.get('excel_path') or 'auto'}")
    print(f"nodes     : {summary['node_count']}")
    node_types = summary.get("node_types") or {}
    if node_types:
        preview = ", ".join(f"{k}:{v}" for k, v in sorted(node_types.items()))
        print(f"node types: {preview}")
    if summary.get("screenshot"):
        print(f"screenshot: {summary['screenshot']}")
    if summary.get("capsule_path"):
        print(f"capsule   : {summary['capsule_path']}")
    errors = summary.get("errors") or []
    if errors:
        print("errors    :", "; ".join(errors[:5]))
    print("==============================")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dexa DOM capture smoke runner")
    parser.add_argument(
        "--mode",
        default="browser_excel",
        choices=("auto", "browser_excel", "win32_excel"),
        help="Excel mode passed to DexaDOMCaptureLauncher",
    )
    parser.add_argument(
        "--excel-path",
        type=Path,
        help="Optional Excel workbook used for win32/binary capture",
    )
    parser.add_argument(
        "--inspector",
        action="store_true",
        help="Enable Playwright inspector (defaults to disabled)",
    )
    parser.add_argument(
        "--bridge-url",
        help="Override DEXA_PLAYWRIGHT_BRIDGE_URL for this run",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    excel_path = args.excel_path if args.excel_path and args.excel_path.exists() else None
    run_smoke_capture(
        mode=args.mode,
        excel_path=excel_path,
        inspector=args.inspector,
        bridge_url=args.bridge_url,
        verbose=True,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

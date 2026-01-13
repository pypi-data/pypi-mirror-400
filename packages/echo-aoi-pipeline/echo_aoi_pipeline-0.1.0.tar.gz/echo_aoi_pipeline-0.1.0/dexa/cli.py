#!/usr/bin/env python3
"""
Dexa CLI entrypoint that exposes automation utilities such as the Auto-Demo runner.
"""
from __future__ import annotations

import argparse
import asyncio
import os
import subprocess
from pathlib import Path
from typing import Callable, Sequence

from ops.tools.auto_demo_full_stack_runner import build_parser as build_auto_demo_parser
from ops.tools.auto_demo_full_stack_runner import run as run_auto_demo
from dexa.setup_runtime import ensure_runtime_scaffolding


REPO_ROOT = Path(__file__).resolve().parents[1]


def _handle_auto_demo(args: argparse.Namespace) -> int:
    asyncio.run(run_auto_demo(args))
    return 0


def _run_repo_script(relative_path: str, env: dict[str, str] | None = None) -> int:
    script_path = REPO_ROOT / relative_path
    if not script_path.exists():
        print(f"[dexa] Missing script: {script_path}", flush=True)
        return 1
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    result = subprocess.run(["bash", str(script_path)], cwd=str(REPO_ROOT), env=merged_env)
    return result.returncode


def _handle_sync_env(_: argparse.Namespace) -> int:
    return _run_repo_script("scripts/sync_env.sh")


def _handle_fix_wsl_env(_: argparse.Namespace) -> int:
    return _run_repo_script("scripts/fix_wsl_env.sh")


def _handle_reset_auto_start(_: argparse.Namespace) -> int:
    return _run_repo_script("scripts/reset_auto_start.sh")


def _handle_mcp_smoke(_: argparse.Namespace) -> int:
    from dexa.mcp.smoke import run_smoke_test

    return run_smoke_test()


def _handle_dom_capture_smoke(args: argparse.Namespace) -> int:
    from dexa.dom_capture_smoke import run_smoke_capture

    excel_path = Path(args.excel_path) if args.excel_path else None
    if excel_path and not excel_path.exists():
        print(f"[dexa] Excel path not found: {excel_path}", flush=True)
        return 1
    run_smoke_capture(
        mode=args.mode,
        excel_path=excel_path,
        inspector=args.inspector,
        bridge_url=args.bridge_url,
    )
    return 0


def _handle_route_check(args: argparse.Namespace) -> int:
    from dexa.bridge_route_validator import run_route_validation

    return run_route_validation(
        skip_smoke=args.skip_smoke,
        skip_demo=args.skip_demo,
        demo_url=args.demo_url,
    )


def _handle_bridge_logs(args: argparse.Namespace) -> int:
    from dexa.bridge_log_viewer import follow, print_snapshot

    if args.follow:
        follow(interval=args.interval)
    else:
        print_snapshot()
    return 0


def _handle_diagnostics(_: argparse.Namespace) -> int:
    return _run_repo_script("scripts/diagnostics.sh")


def _build_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dexa Automation CLI")
    commands = parser.add_subparsers(dest="command", required=True)

    run_parser = commands.add_parser("run", help="Execute Dexa automation flows")
    run_targets = run_parser.add_subparsers(dest="target", required=True)

    auto_demo_parent = build_auto_demo_parser(add_help=False)
    auto_demo = run_targets.add_parser(
        "auto-demo-full-stack",
        help="Run Auto-Demo Universe with synthetic→real fallback",
        parents=[auto_demo_parent],
        add_help=True,
    )
    auto_demo.set_defaults(handler=_handle_auto_demo)

    sync_env = run_targets.add_parser(
        "sync_env",
        help="Replace .env with sanitized output from scripts/sync_env.sh",
    )
    sync_env.set_defaults(handler=_handle_sync_env)

    fix_wsl_env = run_targets.add_parser(
        "fix_wsl_env",
        help="Run scripts/fix_wsl_env.sh to clean broken WSL shell exports",
    )
    fix_wsl_env.set_defaults(handler=_handle_fix_wsl_env)

    reset_auto = run_targets.add_parser(
        "reset_auto_start",
        help="Disable legacy auto_start hooks and clear lock files",
    )
    reset_auto.set_defaults(handler=_handle_reset_auto_start)

    diagnostics = run_targets.add_parser(
        "diagnostics",
        help="Run scripts/diagnostics.sh to check env hygiene",
    )
    diagnostics.set_defaults(handler=_handle_diagnostics)

    mcp_smoke = run_targets.add_parser(
        "mcp_smoke",
        help="Probe the MCP bridge health endpoint and persist status to dexa/mcp_runtime_status.json",
    )
    mcp_smoke.set_defaults(handler=_handle_mcp_smoke)

    dom_capture = run_targets.add_parser(
        "dom_capture_smoke",
        help="Dispatch a minimal DOM capture via the Windows Playwright bridge",
    )
    dom_capture.add_argument(
        "--mode",
        default="browser_excel",
        choices=("auto", "browser_excel", "win32_excel"),
    )
    dom_capture.add_argument("--excel-path", help="Optional Excel workbook when using win32 mode")
    dom_capture.add_argument(
        "--inspector",
        action="store_true",
        help="Enable Playwright inspector (default is off for smoke runs)",
    )
    dom_capture.add_argument(
        "--bridge-url",
        help="Override DEXA_PLAYWRIGHT_BRIDGE_URL just for this invocation",
    )
    dom_capture.set_defaults(handler=_handle_dom_capture_smoke)

    route_check = run_targets.add_parser(
        "route_check",
        help="Re-validate that Dexa talks to the Windows Playwright MCP bridge",
    )
    route_check.add_argument(
        "--skip-smoke",
        action="store_true",
        help="Skip HTTP probes (useful when MCP server is known good)",
    )
    route_check.add_argument(
        "--skip-demo",
        action="store_true",
        help="Skip the 1-second browser control demo",
    )
    route_check.add_argument(
        "--demo-url",
        default="https://example.com",
        help="URL visited during the quick demo run",
    )
    route_check.set_defaults(handler=_handle_route_check)

    bridge_logs = run_targets.add_parser(
        "bridge_logs",
        help="Show MCP runtime status + metrics updates in one place",
    )
    bridge_logs.add_argument(
        "--follow",
        action="store_true",
        help="Poll for file changes to monitor logs in real time",
    )
    bridge_logs.add_argument(
        "--interval",
        type=float,
        default=2.0,
        help="Polling interval while following logs (seconds)",
    )
    bridge_logs.set_defaults(handler=_handle_bridge_logs)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    ensure_runtime_scaffolding()
    parser = _build_cli_parser()
    args = parser.parse_args(argv)
    handler: Callable[[argparse.Namespace], int] | None = getattr(args, "handler", None)
    if handler is None:
        parser.print_help()
        return 1
    return handler(args)


if __name__ == "__main__":
    raise SystemExit(main())

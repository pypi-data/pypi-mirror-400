"""
Helpers for re-validating Dexa→Playwright routing from WSL.
"""

from __future__ import annotations

import argparse
import os
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

from dexa.mcp.config import get_mcp_endpoint
from dexa.mcp.smoke import run_smoke_test
from dexa.playwright_bridge_client import PlaywrightBridgeClient, PlaywrightBridgeError

EXPECTED_BRIDGE_URL = "http://localhost:3928/mcp"
_ENV_KEYS = ("DEXA_PLAYWRIGHT_BRIDGE_URL", "DEXA_MCP_ENDPOINT", "PLAYWRIGHT_MCP_ENDPOINT")


@dataclass
class RouteCheckResult:
    endpoint: str
    env_overrides: Dict[str, Optional[str]]
    issues: List[str]


def validate_configuration(expected_url: str = EXPECTED_BRIDGE_URL) -> RouteCheckResult:
    """
    Inspect environment overrides and ensure Dexa resolves to the Windows MCP bridge.
    """
    endpoint = get_mcp_endpoint()
    env_overrides = {key: os.environ.get(key) for key in _ENV_KEYS}
    issues: List[str] = []

    expected_norm = expected_url.rstrip("/")
    endpoint_norm = endpoint.rstrip("/")

    if env_overrides["DEXA_PLAYWRIGHT_BRIDGE_URL"] is None:
        issues.append("DEXA_PLAYWRIGHT_BRIDGE_URL unset (expected http://localhost:3928/mcp)")
    if endpoint_norm != expected_norm:
        issues.append(f"MCP endpoint resolved to {endpoint_norm}, expected {expected_norm}")

    return RouteCheckResult(endpoint=endpoint, env_overrides=env_overrides, issues=issues)


def run_one_second_demo(
    url: str = "https://example.com",
    *,
    headless: bool = True,
) -> Dict[str, object]:
    """
    Send a minimal flow to Windows so operators can confirm 1-second browser control.
    """
    client = PlaywrightBridgeClient()
    flow_id = f"dexa-demo-{int(time.time())}"
    steps = [
        {"action": "navigate", "url": url},
        {"action": "wait", "wait_ms": 1000},
        {"action": "screenshot"},
    ]
    response = client.run_flow(
        steps,
        flow_id=flow_id,
        context={"demo": True, "source": "route_validator"},
        collect_dom=False,
        headless=headless,
    )
    artifacts = response.get("artifacts") or {}
    return {
        "flow_id": flow_id,
        "run_id": response.get("run_id"),
        "screenshot": artifacts.get("screenshot"),
        "steps": len(steps),
    }


def run_route_validation(
    *,
    skip_smoke: bool = False,
    skip_demo: bool = False,
    expected_url: str = EXPECTED_BRIDGE_URL,
    demo_url: str = "https://example.com",
) -> int:
    result = validate_configuration(expected_url)
    print("=== Dexa Route Check ===")
    print(f"MCP endpoint : {result.endpoint}")
    for key, value in result.env_overrides.items():
        print(f"{key:22}: {value or '-'}")
    if result.issues:
        for issue in result.issues:
            print(f"⚠️  {issue}")
    else:
        print("✅ Environment variables aligned with Windows bridge expectations.")

    status_code = 0
    if not skip_smoke:
        smoke_code = run_smoke_test()
        status_code = status_code or smoke_code

    if not skip_demo:
        try:
            demo = run_one_second_demo(url=demo_url)
            screenshot = demo.get("screenshot")
            print("✅ 1-second browser demo dispatched.")
            if screenshot:
                print(f"   Screenshot artifact: {screenshot}")
        except PlaywrightBridgeError as exc:
            print(f"❌ Demo flow failed: {exc}")
            status_code = 1
    return status_code


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dexa route validation helper")
    parser.add_argument(
        "--skip-smoke",
        action="store_true",
        help="Skip the HTTP health probe (tools/list + health)",
    )
    parser.add_argument(
        "--skip-demo",
        action="store_true",
        help="Skip the 1-second browser control demo",
    )
    parser.add_argument(
        "--demo-url",
        default="https://example.com",
        help="URL visited during the demo run",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    return run_route_validation(
        skip_smoke=args.skip_smoke,
        skip_demo=args.skip_demo,
        demo_url=args.demo_url,
    )


if __name__ == "__main__":
    raise SystemExit(main())

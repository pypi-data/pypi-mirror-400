"""
HTTP client for the Windows Playwright Bridge Server.
"""

from __future__ import annotations

import os
import logging
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)


class PlaywrightBridgeError(RuntimeError):
    """Raised when the bridge server returns an error response."""


class PlaywrightBridgeClient:
    """Thin wrapper that proxies Dexa browser flows to the Windows bridge."""

    def __init__(self, base_url: Optional[str] = None, timeout: int = 120) -> None:
        raw_base = base_url or os.environ.get("DEXA_PLAYWRIGHT_BRIDGE_URL", "http://127.0.0.1:5007")
        self.base_url = self._normalize_base_url(raw_base)
        self.timeout = timeout

    @staticmethod
    def _normalize_base_url(value: str) -> str:
        base = value.strip().rstrip("/")
        if base.endswith("/mcp"):
            return base[: -len("/mcp")] or base
        return base

    def run_flow(
        self,
        steps: List[Dict[str, Any]],
        *,
        flow_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        collect_dom: bool = False,
        browser: str = "chromium",
        headless: bool = False,
    ) -> Dict[str, Any]:
        payload = {
            "flow_id": flow_id,
            "steps": steps,
            "context": context or {},
            "collect_dom": collect_dom,
            "browser": browser,
            "headless": headless,
        }
        logger.info("[PlaywrightBridgeClient] POST /run flow_id=%s", flow_id)
        response = requests.post(
            f"{self.base_url}/run",
            json=payload,
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise PlaywrightBridgeError(f"Bridge /run failed ({response.status_code}): {response.text}")
        return response.json()

    def status(self) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/status", timeout=self.timeout)
        if response.status_code >= 400:
            raise PlaywrightBridgeError(f"Bridge /status failed ({response.status_code})")
        return response.json()

    def fetch_screenshot(self) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/screenshot", timeout=self.timeout)
        if response.status_code >= 400:
            raise PlaywrightBridgeError(f"Bridge /screenshot failed ({response.status_code})")
        return response.json()

    def fetch_video(self) -> Dict[str, Any]:
        response = requests.get(f"{self.base_url}/video", timeout=self.timeout)
        if response.status_code >= 400:
            raise PlaywrightBridgeError(f"Bridge /video failed ({response.status_code})")
        return response.json()

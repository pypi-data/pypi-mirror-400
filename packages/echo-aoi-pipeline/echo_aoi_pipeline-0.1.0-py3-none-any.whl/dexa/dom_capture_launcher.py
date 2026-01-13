#!/usr/bin/env python3
"""
Dexa DOM Capture Launcher (Bridge Edition)

Generates browser automation flows in WSL and proxies their execution to the
Windows Playwright Bridge Server. The server controls the GUI (Chromium/Firefox/
WebKit) locally on Windows while Dexa receives DOM snapshots and artifacts.
"""

from __future__ import annotations

import json
import logging
import os
import platform
import shutil
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dexa.playwright_bridge_client import PlaywrightBridgeClient, PlaywrightBridgeError

logger = logging.getLogger(__name__)


@dataclass
class DOMNode:
    element_type: str
    outer_html: str
    xpath: str
    role: Optional[str] = None
    aria_label: Optional[str] = None
    data_testid: Optional[str] = None
    css_selector: str = ""
    attributes: Dict[str, str] = field(default_factory=dict)


@dataclass
class CaptureResult:
    timestamp: str
    mode: str
    excel_path: Optional[str]
    nodes: List[DOMNode] = field(default_factory=list)
    screenshot_path: Optional[str] = None
    metadata: Dict = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class DexaDOMCaptureLauncher:
    """Generates Playwright flows and delegates execution to the bridge server."""

    def __init__(
        self,
        capsule_dir: Path = Path("echo_engine/excel_ai/dom_capsules"),
        inspector_mode: bool = True,
        bridge_url: Optional[str] = None,
    ):
        self.capsule_dir = capsule_dir
        self.inspector_mode = inspector_mode
        self.bridge = PlaywrightBridgeClient(base_url=bridge_url)
        self.capsule_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ helpers

    def detect_excel_mode(self) -> str:
        override = os.getenv("DEXA_EXCEL_MODE")
        if override in {"win32_excel", "browser_excel"}:
            return override
        if platform.system().lower() == "windows":
            return "win32_excel"
        return "browser_excel"

    def _build_steps(self, excel_path: Optional[Path]) -> List[Dict[str, str]]:
        steps: List[Dict[str, str]] = [
            {"action": "navigate", "url": "https://excel.office.com"},
            {"action": "wait", "wait_ms": 5000},
        ]
        if excel_path:
            steps.extend(
                [
                    {"action": "click", "selector": "button:has-text('새로 만들기')"},
                    {"action": "wait", "wait_ms": 2000},
                ]
            )
        steps.append({"action": "screenshot"})
        return steps

    def _convert_nodes(self, raw_nodes: List[Dict[str, str]]) -> List[DOMNode]:
        nodes: List[DOMNode] = []
        for payload in raw_nodes:
            nodes.append(
                DOMNode(
                    element_type=payload.get("element_type", "unknown"),
                    outer_html=payload.get("outer_html", ""),
                    xpath=payload.get("xpath", ""),
                    role=payload.get("role"),
                    aria_label=payload.get("aria_label"),
                    data_testid=payload.get("data_testid"),
                    css_selector=payload.get("css_selector", ""),
                    attributes=payload.get("attributes") or {},
                )
            )
        return nodes

    def _persist_screenshot(self, artifact: Optional[Dict[str, str]], timestamp: str) -> Optional[str]:
        if not artifact:
            return None
        source = artifact.get("wsl_path") or artifact.get("windows_path")
        if not source or not Path(source).exists():
            return None
        target = self.capsule_dir / f"{timestamp}_screenshot.png"
        shutil.copy2(source, target)
        return str(target)

    def _save_capsule(self, result: CaptureResult) -> Path:
        capsule_path = self.capsule_dir / result.timestamp
        capsule_path.mkdir(parents=True, exist_ok=True)

        nodes_file = capsule_path / "cap_nodes.json"
        with nodes_file.open("w", encoding="utf-8") as handle:
            json.dump(
                [node.__dict__ for node in result.nodes],
                handle,
                indent=2,
                ensure_ascii=False,
            )
        if result.screenshot_path:
            shutil.copy2(result.screenshot_path, capsule_path / "cap_screenshot.png")
        metadata = {
            "timestamp": result.timestamp,
            "mode": result.mode,
            "excel_path": result.excel_path,
            "node_count": len(result.nodes),
            "node_types": sorted({node.element_type for node in result.nodes}),
            "screenshot": "cap_screenshot.png" if result.screenshot_path else None,
            "errors": result.errors,
            "metadata": result.metadata,
        }
        with (capsule_path / "metadata.json").open("w", encoding="utf-8") as handle:
            json.dump(metadata, handle, indent=2, ensure_ascii=False)
        self._update_metadata_index(result.timestamp, metadata)
        return capsule_path

    def _update_metadata_index(self, capsule_id: str, metadata: Dict[str, Any]) -> None:
        index_file = self.capsule_dir / "metadata.json"
        if index_file.exists():
            index = json.loads(index_file.read_text(encoding="utf-8"))
        else:
            index = {"capsules": []}
        index["capsules"].append(
            {
                "id": capsule_id,
                "timestamp": metadata["timestamp"],
                "mode": metadata["mode"],
                "node_count": metadata["node_count"],
            }
        )
        index_file.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")

    # ---------------------------------------------------------------- workflow

    def capture(self, excel_path: Optional[Path] = None, mode: str = "auto") -> CaptureResult:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        detected_mode = mode if mode != "auto" else self.detect_excel_mode()
        excel_path = excel_path if excel_path and excel_path.exists() else None

        steps = self._build_steps(excel_path)
        context = {"mode": detected_mode, "excel_path": str(excel_path) if excel_path else None}
        flow_id = f"dexa-dom-{int(time.time())}"

        logger.info("🎯 Dispatching DOM capture to Playwright Bridge: %s", flow_id)
        try:
            response = self.bridge.run_flow(
                steps,
                flow_id=flow_id,
                context=context,
                collect_dom=True,
                headless=not self.inspector_mode,
            )
        except PlaywrightBridgeError as exc:
            raise RuntimeError(f"Bridge execution failed: {exc}") from exc

        artifacts = response.get("artifacts", {})
        nodes = self._convert_nodes(artifacts.get("dom_nodes") or [])
        screenshot_path = self._persist_screenshot(artifacts.get("screenshot"), timestamp)
        metadata = {
            "run_id": response.get("run_id"),
            "bridge_context": context,
            "bridge_timestamp": artifacts.get("timestamp"),
        }

        result = CaptureResult(
            timestamp=timestamp,
            mode=detected_mode,
            excel_path=str(excel_path) if excel_path else None,
            nodes=nodes,
            screenshot_path=screenshot_path,
            metadata=metadata,
            errors=response.get("errors") or [],
        )
        capsule_path = self._save_capsule(result)
        result.metadata["capsule_path"] = str(capsule_path)

        logger.info("✅ DOM capture complete. Nodes=%s capsule=%s", len(nodes), capsule_path)
        return result


if __name__ == "__main__":
    launcher = DexaDOMCaptureLauncher(inspector_mode=False)
    capture = launcher.capture()
    print(json.dumps({"timestamp": capture.timestamp, "nodes": len(capture.nodes)}, indent=2))

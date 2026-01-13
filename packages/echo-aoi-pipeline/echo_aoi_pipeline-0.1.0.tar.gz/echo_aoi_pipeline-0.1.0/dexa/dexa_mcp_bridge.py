"""
Playwright MCP bridge dedicated to Dexa's Excel AGI loop.

The bridge collects DOM/Excel state, produces structural snapshots, and executes
Echo-issued commands without exposing MCP plumbing to Dexa's higher layers.
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Sequence

from dexa.mcp.call_adapter import mcp_call

logger = logging.getLogger(__name__)

ROW_TRIPLE = ["수요", "입고", "과부족"]
ERROR_PATTERN = re.compile(r"#(VALUE|REF|N/?A)", re.IGNORECASE)

SNAPSHOT_SCRIPT = r"""
(() => {
  const ctx = window.excelSimulation || window.EchoExcel || window.DexaExcel || window.ExcelDelight || {};
  const callOr = (fn, fallback) => {
    try { return typeof fn === 'function' ? fn() : fallback; } catch (err) { return fallback; }
  };
  const tableData = callOr(ctx.getTableData, window.__ECHO_TABLE_DATA__ || []);
  const chatHistory = callOr(ctx.getConversationLog, window.__ECHO_CHAT_HISTORY__ || []);
  const selection = callOr(ctx.getSelection, ctx.selectedCell || null);
  const headers = callOr(ctx.getHeaders, (tableData[0] && Object.keys(tableData[0])) || []);
  const monthColumns = (headers || []).filter((header) => /월$/.test(header));
  const mergedCells = [];
  const nodes = typeof document !== 'undefined' ? document.querySelectorAll('[rowspan], [colspan]') : [];
  nodes.forEach((node) => {
    const colspan = parseInt(node.getAttribute('colspan') || '1', 10);
    const rowspan = parseInt(node.getAttribute('rowspan') || '1', 10);
    if (colspan > 1 || rowspan > 1) {
      mergedCells.push({
        text: node.innerText,
        colspan,
        rowspan,
      });
    }
  });
  const errorCells = [];
  tableData.forEach((row, rowIndex) => {
    Object.entries(row || {}).forEach(([column, value]) => {
      if (typeof value === 'string' && /^#(VALUE|REF|N\/?A)/i.test(value)) {
        errorCells.push({ row: rowIndex, column, value });
      }
    });
  });
  const aqValues = [];
  const arValues = [];
  tableData.forEach((row, rowIndex) => {
    if (row && Object.prototype.hasOwnProperty.call(row, 'AQ')) {
      aqValues.push({ row: rowIndex, value: row['AQ'] });
    }
    if (row && Object.prototype.hasOwnProperty.call(row, 'AR')) {
      arValues.push({ row: rowIndex, value: row['AR'] });
    }
  });
  const arFormulaGetter = callOr(ctx.getColumnFormula, null);
  const arFormulas = typeof arFormulaGetter === 'function'
    ? arFormulaGetter('AR')
    : (ctx.formulas && ctx.formulas['AR']) || [];
  const payload = {
    tableData,
    chatHistory,
    selection,
    headers,
    monthColumns,
    errorCells,
    mergedCells,
    aqValues,
    arValues,
    arFormulas,
    rowTypes: callOr(ctx.getRowTypes, null),
    timestamp: new Date().toISOString()
  };
  return JSON.stringify(payload);
})();
"""


class DexaMCPBridge:
    """High-level wrapper that hides raw MCP calls from Dexa."""

    def __init__(self, evaluate_tool: str = "evaluate") -> None:
        self.evaluate_tool = evaluate_tool

    def capture_excel_state(self) -> Dict[str, Any]:
        """Return a raw DOM snapshot gathered via Playwright."""
        payload = self._call_evaluate(SNAPSHOT_SCRIPT)
        if payload is None:
            return {"tableData": [], "chatHistory": [], "timestamp": _timestamp()}
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                logger.warning("Playwright snapshot returned malformed JSON; using stub")
                return {"tableData": [], "chatHistory": [], "timestamp": _timestamp()}
        payload.setdefault("timestamp", _timestamp())
        return payload

    def build_structural_snapshot(self, raw_state: Dict[str, Any]) -> Dict[str, Any]:
        """Derive structural metadata required by Echo."""
        row_pattern = self._analyze_row_pattern(raw_state)
        aq_ar = self._extract_aq_ar(raw_state)
        errors = self._collect_error_cells(raw_state)
        merged = self._extract_merged_cells(raw_state)
        headers = self._extract_headers(raw_state)
        metrics = {
            "visible_rows": len(raw_state.get("tableData") or []),
            "visible_columns": len(headers.get("labels") or []),
            "density": self._density_score(raw_state),
            "timestamp": raw_state.get("timestamp", _timestamp()),
        }
        return {
            "row_pattern": row_pattern,
            "aq_ar": aq_ar,
            "error_cells": {"cells": errors},
            "merged_cells": merged,
            "headers": headers,
            "metrics": metrics,
        }

    def snapshot_for_proxy(
        self,
        chat_history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        """Convenience helper that bundles UI + structural data for the proxy."""
        raw_state = self.capture_excel_state()
        return {
            "ui_state": raw_state,
            "structural_snapshot": self.build_structural_snapshot(raw_state),
            "chat_history": chat_history or raw_state.get("chatHistory") or [],
        }

    def execute_echo_command(self, echo_command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute action(s) specified by Echo.

        echo_command supports either a single {action, parameters} pair or a list
        of actions under the "actions" key.
        """
        if not echo_command:
            return {"status": "skipped", "reason": "empty_command"}

        actions = echo_command.get("actions") or [echo_command]
        results: List[Dict[str, Any]] = []
        overall_status = "success"

        for action in actions:
            result = self._dispatch_action(action)
            results.append(result)
            if result.get("status") != "success" and overall_status == "success":
                overall_status = "partial"

        return {
            "status": overall_status,
            "actions": results,
            "issued_command": echo_command.get("command_id"),
        }

    # --- Internal helpers -------------------------------------------------

    def _dispatch_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        name = (action.get("action") or action.get("type") or "").lower()
        params = action.get("parameters", {})
        handler_map = {
            "insert_formula": self._action_insert_formula,
            "apply_formula": self._action_insert_formula,
            "set_range": self._action_set_range_value,
            "update_range": self._action_set_range_value,
            "refresh_pivot": self._action_refresh_pivot,
            "reconnect_slicer": self._action_reconnect_slicer,
        }
        handler = handler_map.get(name)
        if not handler:
            return {
                "status": "skipped",
                "action": name,
                "reason": "unsupported_action",
                "parameters": params,
            }
        try:
            return handler(params)
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Echo action %s failed", name)
            return {"status": "failed", "action": name, "reason": repr(exc)}

    def _action_insert_formula(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cell = params.get("cell") or params.get("target")
        formula = params.get("formula")
        if not cell or not formula:
            return {"status": "skipped", "reason": "missing_cell_or_formula"}
        selector = params.get("selector") or self._selector_for_cell(cell)
        focus = params.get("focus", True)
        details: List[Dict[str, Any]] = []
        if focus:
            details.append(self._run_tool("click", {"selector": selector}))
        details.append(self._run_tool("fill", {"selector": selector, "text": formula}))
        return {"status": "success", "action": "insert_formula", "details": details}

    def _action_set_range_value(self, params: Dict[str, Any]) -> Dict[str, Any]:
        cell = params.get("cell") or params.get("range_start")
        value = params.get("value")
        if not cell or value is None:
            return {"status": "skipped", "reason": "missing_cell_or_value"}
        selector = params.get("selector") or self._selector_for_cell(cell)
        details = [self._run_tool("click", {"selector": selector})]
        details.append(self._run_tool("fill", {"selector": selector, "text": str(value)}))
        return {"status": "success", "action": "set_range", "details": details}

    def _action_refresh_pivot(self, params: Dict[str, Any]) -> Dict[str, Any]:
        script = """
            (() => {
                const ctx = window.excelSimulation || window.ExcelDelight;
                if (!ctx || typeof ctx.refreshPivot !== 'function') {
                    return { status: 'missing_pivot_hook' };
                }
                ctx.refreshPivot();
                return { status: 'ok' };
            })();
        """
        detail = self._call_evaluate(script)
        return {"status": "success", "action": "refresh_pivot", "details": [detail]}

    def _action_reconnect_slicer(self, params: Dict[str, Any]) -> Dict[str, Any]:
        script = """
            (() => {
                const ctx = window.excelSimulation || window.ExcelDelight;
                if (!ctx || typeof ctx.reconnectSlicers !== 'function') {
                    return { status: 'missing_slicer_hook' };
                }
                ctx.reconnectSlicers();
                return { status: 'ok' };
            })();
        """
        detail = self._call_evaluate(script)
        return {"status": "success", "action": "reconnect_slicer", "details": [detail]}

    def _run_tool(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        response = mcp_call(method, params)
        if response.get("status") == "error" or response.get("error"):
            raise RuntimeError(response)
        result = response.get("result") or {}
        if isinstance(result, dict) and result.get("status") == "ok":
            return result
        return {"status": "ok", "raw": result or response}

    def _call_evaluate(self, script: str) -> Optional[Any]:
        response = mcp_call(self.evaluate_tool, {"script": script})
        if response.get("status") == "error" or response.get("error"):
            logger.warning("Playwright evaluate failed: %s", response)
            return None
        result = response.get("result") or {}
        return result.get("result") or result

    def _analyze_row_pattern(self, raw_state: Dict[str, Any]) -> Dict[str, Any]:
        rows = raw_state.get("tableData") or []
        sequence: List[str] = []
        for row in rows:
            rt = (row.get("RowType") or row.get("rowType") or "").strip()
            if rt:
                sequence.append(rt)
        violations: List[str] = []
        expected = list(ROW_TRIPLE)
        for idx, value in enumerate(sequence):
            expected_value = expected[idx % len(expected)]
            if value != expected_value:
                violations.append(f"row {idx + 1}: expected {expected_value}, got {value}")
        return {
            "valid": not violations and bool(sequence),
            "expected_sequence": expected,
            "observed_sequence": sequence[:9],
            "violations": violations,
        }

    def _extract_aq_ar(self, raw_state: Dict[str, Any]) -> Dict[str, Any]:
        aq_values = raw_state.get("aqValues") or raw_state.get("aq_values") or []
        ar_values = raw_state.get("arValues") or raw_state.get("ar_values") or []
        ar_formulas = raw_state.get("arFormulas") or raw_state.get("ar_formulas") or []
        requires_standardization = any(
            not self._is_standard_ar_formula(item.get("value")) for item in ar_values
        )
        formula_sample = None
        if ar_formulas:
            formula_sample = ar_formulas[0] if isinstance(ar_formulas, list) else ar_formulas
        return {
            "aq_values": aq_values,
            "ar_formulas": ar_formulas,
            "ar_formula_sample": formula_sample,
            "requires_standardization": requires_standardization,
        }

    def _collect_error_cells(self, raw_state: Dict[str, Any]) -> List[Dict[str, Any]]:
        errors = raw_state.get("errorCells") or raw_state.get("error_cells")
        if errors:
            return errors
        rows = raw_state.get("tableData") or []
        collected: List[Dict[str, Any]] = []
        for row_idx, row in enumerate(rows):
            for column, value in row.items():
                if isinstance(value, str) and ERROR_PATTERN.search(value):
                    collected.append({"row": row_idx, "column": column, "value": value})
        return collected

    def _extract_merged_cells(self, raw_state: Dict[str, Any]) -> Dict[str, Any]:
        merged = raw_state.get("mergedCells") or raw_state.get("merged_cells") or []
        return {
            "has_merged_cells": bool(merged),
            "locations": merged,
        }

    def _extract_headers(self, raw_state: Dict[str, Any]) -> Dict[str, Any]:
        labels = raw_state.get("headers") or []
        duplicates = [label for label in labels if labels.count(label) > 1]
        return {"labels": labels, "duplicates": sorted(set(duplicates))}

    def _selector_for_cell(self, cell: str) -> str:
        return f'[data-cell="{cell}"]'

    def _density_score(self, raw_state: Dict[str, Any]) -> float:
        rows = raw_state.get("tableData") or []
        if not rows:
            return 0.0
        non_empty = sum(1 for row in rows for value in row.values() if value not in (None, ""))
        total = len(rows) * max(len(rows[0]) if rows and isinstance(rows[0], dict) else 1, 1)
        return round(non_empty / total, 3) if total else 0.0

    def _is_standard_ar_formula(self, value: Any) -> bool:
        if not isinstance(value, str):
            return True
        normalized = value.upper().replace(" ", "")
        return normalized.startswith("=IF(ISBLANK(AQ") and normalized.endswith(",1,0)")


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


__all__ = ["DexaMCPBridge"]

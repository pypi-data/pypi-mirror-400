"""
Dexa ↔ Echo Existential Reasoning Proxy I/O helpers.

This module materializes the YAML schema requested for AGI mode, keeps the proxy
state JSON synchronized, and offers convenience functions for Dexa's Excel loop
to communicate with Echo Core.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

PROXY_ENV_PATH = "ECHO_EXISTENTIAL_PROXY_PATH"
SPEC_ENV_PATH = "ECHO_EXISTENTIAL_PROXY_SPEC_PATH"
STATE_FILENAME = "ECHO_EXISTENTIAL_PROXY_STATE.json"
SPEC_FILENAME = "ECHO_EXISTENTIAL_REASONING_PROXY_v1.yaml"
PREFERRED_ROOT = Path("/mnt/data")
FALLBACK_ROOTS = (
    Path.home() / ".echo_existential_proxy",
    Path.cwd() / "artifacts" / "echo_existential_proxy",
)
ERROR_TOKENS = {"#VALUE!", "#REF!", "#N/A"}


@dataclass
class ProxyState:
    """Represents the JSON payload stored on disk."""

    ui_state: Dict[str, Any]
    user_intent: Dict[str, Any]
    structural_snapshot: Dict[str, Any]
    suspected_issue: Optional[Dict[str, Any]] = None
    echo_diagnosis: Optional[Dict[str, Any]] = None
    echo_command: Optional[Dict[str, Any]] = None
    execution_log: List[Dict[str, Any]] = field(default_factory=list)
    meta: Dict[str, Any] = field(default_factory=dict)
    state_path: Path = field(default=Path(STATE_FILENAME), repr=False)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any], state_path: Path) -> "ProxyState":
        return cls(
            ui_state=payload.get("ui_state", {}),
            user_intent=payload.get("user_intent", {}),
            structural_snapshot=payload.get("structural_snapshot", {}),
            suspected_issue=payload.get("suspected_issue"),
            echo_diagnosis=payload.get("echo_diagnosis"),
            echo_command=payload.get("echo_command"),
            execution_log=list(payload.get("execution_log", [])),
            meta=payload.get("meta", {}),
            state_path=state_path,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ui_state": self.ui_state,
            "user_intent": self.user_intent,
            "structural_snapshot": self.structural_snapshot,
            "suspected_issue": self.suspected_issue,
            "echo_diagnosis": self.echo_diagnosis,
            "echo_command": self.echo_command,
            "execution_log": self.execution_log,
            "meta": self.meta,
        }


def _timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def _resolve_state_path() -> Path:
    candidates: List[Path] = []
    env_override = os.environ.get(PROXY_ENV_PATH)
    if env_override:
        candidates.append(Path(env_override))
    candidates.append(PREFERRED_ROOT / STATE_FILENAME)
    candidates.extend(root / STATE_FILENAME for root in FALLBACK_ROOTS)

    for candidate in candidates:
        try:
            candidate.parent.mkdir(parents=True, exist_ok=True)
        except PermissionError as exc:
            logger.debug("Proxy path %s unavailable: %s", candidate, exc)
            continue
        return candidate
    raise RuntimeError("Unable to determine writable existential proxy path")


def _materialize_spec_file() -> Path:
    source = Path(__file__).with_name(SPEC_FILENAME)
    candidates: List[Path] = []
    env_override = os.environ.get(SPEC_ENV_PATH)
    if env_override:
        candidates.append(Path(env_override))
    candidates.append(PREFERRED_ROOT / SPEC_FILENAME)

    spec_text = source.read_text(encoding="utf-8") if source.exists() else ""
    for target in candidates:
        if target.exists():
            return target
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(spec_text, encoding="utf-8")
            return target
        except PermissionError as exc:
            logger.debug("Cannot copy proxy spec to %s: %s", target, exc)
            continue
        except OSError as exc:  # pragma: no cover - defensive
            logger.debug("Spec copy failed for %s: %s", target, exc)
            continue
    return source


ACTIVE_STATE_PATH = _resolve_state_path()
SPEC_PATH = _materialize_spec_file()


def get_proxy_state_path() -> Path:
    """Expose the actual path used for consumers that need it."""
    return ACTIVE_STATE_PATH


def _load_state_file() -> Optional[Dict[str, Any]]:
    if not ACTIVE_STATE_PATH.exists():
        return None
    try:
        return json.loads(ACTIVE_STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        logger.warning("Malformed proxy payload at %s: %s", ACTIVE_STATE_PATH, exc)
    except OSError as exc:
        logger.warning("Unable to read proxy payload: %s", exc)
    return None


def _persist_state(payload: Dict[str, Any]) -> None:
    payload = dict(payload)
    payload.setdefault("meta", {})
    payload["meta"].update(
        {"last_updated": _timestamp(), "state_path": str(ACTIVE_STATE_PATH)}
    )
    ACTIVE_STATE_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _normalize_ui_state(ui_state: Dict[str, Any]) -> Dict[str, Any]:
    rows = (
        ui_state.get("tableData")
        or ui_state.get("table_data")
        or ui_state.get("rows")
        or []
    )
    headers = (
        ui_state.get("headers")
        or ui_state.get("header_text")
        or _derive_headers_from_rows(rows)
    )
    row_types = ui_state.get("row_types") or ui_state.get("rowTypeCounts") or {}
    if not row_types and rows:
        for row in rows:
            value = (row.get("RowType") or row.get("rowType") or "").strip()
            if not value:
                continue
            row_types[value] = row_types.get(value, 0) + 1

    month_columns = ui_state.get("month_columns") or [h for h in headers if h.endswith("월")]
    highlighted = ui_state.get("highlighted_cells") or ui_state.get("selection") or []
    if isinstance(highlighted, str):
        highlighted = [highlighted]
    selected_cell = ui_state.get("selected_cell") or ui_state.get("selection")
    if isinstance(selected_cell, list):
        selected_cell = selected_cell[0] if selected_cell else None

    error_cells = ui_state.get("error_cells") or _scan_error_cells(rows)
    return {
        "row_count": ui_state.get("row_count", len(rows)),
        "column_count": ui_state.get("column_count", len(headers)),
        "headers": headers,
        "row_type_counts": row_types,
        "month_columns": month_columns,
        "selected_cell": selected_cell,
        "highlighted_cells": highlighted,
        "error_cells": error_cells,
        "timestamp": ui_state.get("timestamp", _timestamp()),
    }


def _derive_headers_from_rows(rows: List[Dict[str, Any]]) -> List[str]:
    if not rows:
        return []
    headers = list(rows[0].keys())
    return headers


def _scan_error_cells(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    errors: List[Dict[str, Any]] = []
    for idx, row in enumerate(rows):
        for column, value in row.items():
            if isinstance(value, str) and value.strip().upper() in ERROR_TOKENS:
                errors.append(
                    {
                        "cell": f"{column}{idx + 2}",
                        "value": value,
                        "row": idx,
                        "column": column,
                    }
                )
    return errors


def _summarize_intent(
    chat_history: List[Dict[str, str]],
    overrides: Optional[Dict[str, Any]],
    triggers: Optional[List[str]],
) -> Dict[str, Any]:
    overrides = overrides or {}
    triggers = triggers or []
    user_messages = [msg["content"] for msg in chat_history if msg.get("role") == "user"]
    assistant_messages = [
        msg["content"] for msg in chat_history if msg.get("role") == "assistant"
    ]
    recent_summary = " | ".join(m.strip() for m in user_messages[-3:])
    agitation = overrides.get("agitation_level") or _estimate_agitation(user_messages)

    return {
        "last_user_message": user_messages[-1] if user_messages else "",
        "last_agent_message": assistant_messages[-1] if assistant_messages else "",
        "recent_user_summary": recent_summary,
        "agitation_level": agitation,
        "triggers": triggers,
        "origin_session_id": overrides.get("session_id", ""),
        "primary_intent": overrides.get("primary_intent", ""),
    }


def _estimate_agitation(recent_messages: List[str]) -> str:
    if not recent_messages:
        return "calm"
    last = recent_messages[-1].lower()
    repeats = recent_messages[-3:]
    normalized = [msg.strip().lower() for msg in repeats]
    repetition_ratio = (
        len(normalized) if normalized.count(normalized[-1]) == len(normalized) else 0
    )
    if any(token in last for token in ("왜", "무슨", "뭐가", "이상", "?")):
        return "confused"
    if "급" in last or "빨리" in last:
        return "urgent"
    if repetition_ratio >= 3:
        return "confused"
    return "calm"


def _derive_issue(structural_snapshot: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    if not structural_snapshot:
        return None
    row_pattern = structural_snapshot.get("row_pattern") or {}
    errors = structural_snapshot.get("error_cells", {}).get("cells", [])

    if not row_pattern.get("valid"):
        return {
            "code": "ROWTYPE_PATTERN_BROKEN",
            "message": "수요-입고-과부족 3행 패턴이 깨졌습니다.",
            "confidence": 0.9,
            "supporting_evidence": row_pattern.get("violations", []),
        }
    if errors:
        return {
            "code": "VISIBLE_ERROR_CELL",
            "message": "화면에 Excel 오류 셀이 노출되어 있습니다.",
            "confidence": 0.75,
            "supporting_evidence": [f"{cell['cell']}={cell['value']}" for cell in errors],
        }
    return None


def write_proxy(
    state: Dict[str, Any],
    triggers: Optional[List[str]] = None,
) -> ProxyState:
    """
    Persist the latest UI + structural snapshot for Echo to inspect.

    Args:
        state: Dict with ui_state, structural_snapshot, chat_history, etc.
        triggers: AGI trigger signals detected upstream.
    """
    existing = _load_state_file() or {}
    structural_snapshot = state.get("structural_snapshot") or existing.get(
        "structural_snapshot", {}
    )
    structural_snapshot.setdefault("timestamp", _timestamp())

    payload = {
        "ui_state": _normalize_ui_state(state.get("ui_state", {})),
        "user_intent": _summarize_intent(
            state.get("chat_history", []), state.get("user_intent_overrides"), triggers
        ),
        "structural_snapshot": structural_snapshot,
        "suspected_issue": state.get("suspected_issue")
        or existing.get("suspected_issue")
        or _derive_issue(structural_snapshot),
        "echo_diagnosis": existing.get("echo_diagnosis"),
        "echo_command": existing.get("echo_command"),
        "execution_log": existing.get("execution_log", []),
        "meta": {
            "triggers": triggers or [],
            "state_path": str(ACTIVE_STATE_PATH),
            "spec_path": str(SPEC_PATH),
        },
    }
    _persist_state(payload)
    return ProxyState.from_dict(payload, ACTIVE_STATE_PATH)


def read_proxy() -> Optional[ProxyState]:
    """Return the latest proxy payload (if any)."""
    payload = _load_state_file()
    if not payload:
        return None
    return ProxyState.from_dict(payload, ACTIVE_STATE_PATH)


def record_execution(
    action: str,
    status: str,
    detail: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    echo_command_id: Optional[str] = None,
) -> ProxyState:
    """Append Dexa's execution result to the proxy log."""
    payload = _load_state_file() or write_proxy({}, triggers=[]).to_dict()
    entry = {
        "timestamp": _timestamp(),
        "actor": "Dexa",
        "action": action,
        "status": status,
        "detail": detail,
        "echo_command_id": echo_command_id or "",
        "metadata": metadata or {},
    }
    payload.setdefault("execution_log", []).append(entry)
    _persist_state(payload)
    return ProxyState.from_dict(payload, ACTIVE_STATE_PATH)


def acknowledge_command(command: Dict[str, Any]) -> ProxyState:
    """Clear the currently pending echo_command after Dexa executes it."""
    payload = _load_state_file()
    if not payload:
        payload = write_proxy({}, triggers=[]).to_dict()
    payload["echo_command"] = None
    payload.setdefault("meta", {}).update(
        {"last_command_ack": _timestamp(), "last_command": command}
    )
    _persist_state(payload)
    return ProxyState.from_dict(payload, ACTIVE_STATE_PATH)


__all__ = [
    "ProxyState",
    "SPEC_PATH",
    "get_proxy_state_path",
    "write_proxy",
    "read_proxy",
    "record_execution",
    "acknowledge_command",
]

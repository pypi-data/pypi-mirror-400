#!/usr/bin/env python3
"""
Structure #002 - Phase 0 handoff harness.

Generates a single handoff packet from an existing Structure #001
condition event and simulates a human resume action without touching
the live execution path.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Literal, Optional
import os
import sys

ARTIFACT_DIR = Path("artifacts/structure002_phase0")
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

PACKET_PATH = ARTIFACT_DIR / "handoff_packet.json"
TRACE_LOG_PATH = ARTIFACT_DIR / "resume_trace.jsonl"

RESUME_GATE_DIR = Path("artifacts/structure003_phase1")
RESUME_GATE_DIR.mkdir(parents=True, exist_ok=True)
RESUME_GATE_LOG = RESUME_GATE_DIR / "resume_gate_log.jsonl"

LEDGER_DIR = Path("artifacts/structure003_phase2")
LEDGER_DIR.mkdir(parents=True, exist_ok=True)
LEDGER_PATH = LEDGER_DIR / "ledger.jsonl"


@dataclass(frozen=True)
class Structure001Event:
    event_id: str
    flow_id: str
    timestamp: str
    subject: str
    body: str
    judgment_event: Literal["condition", "stop"]
    sensor_labels: list[str]


# Reuse the existing Structure #001 wobble event.
STRUCTURE001_EVENT = Structure001Event(
    event_id="phase0-test-conditional-001",
    flow_id="NotificationManager._send_email",
    timestamp="2025-12-14T09:30:00Z",
    subject="Update on escalation",
    body=(
        "This should be fine to send as-is,\n"
        "but if anything goes wrong we can revisit later.\n"
        "Please proceed quickly."
    ),
    judgment_event="condition",
    sensor_labels=["condition"],
)


def build_handoff_packet(event: Structure001Event = STRUCTURE001_EVENT) -> Dict[str, Any]:
    """Create the minimum human-facing packet and persist it to disk."""
    packet = {
        "event_id": event.event_id,
        "flow_id": event.flow_id,
        "timestamp": event.timestamp,
        "draft_snapshot": {
            "subject": event.subject,
            "body": event.body,
        },
        "judgment_event": event.judgment_event,
        "sensor_labels": event.sensor_labels,
    }
    PACKET_PATH.write_text(json.dumps(packet, ensure_ascii=False, indent=2))
    _append_ledger_entry(
        structure="002",
        action="HANDOFF_CREATED",
        event_id=event.event_id,
        flow_id=event.flow_id,
        actor=None,
        timestamp=datetime.now(tz=timezone.utc).isoformat(),
        ref=str(PACKET_PATH),
    )
    return packet


def resume_event(
    event_id: str,
    action: Literal["approve", "edit", "abort"],
    *,
    resumed_by: str = "phase0-operator",
    edited_draft: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    Simulate a human resume action referencing the same event_id.

    Phase 3: ledger-based enforcement + Phase 1 fallback.
    """
    if event_id != STRUCTURE001_EVENT.event_id:
        raise ValueError("resume_event must reference the original event_id")

    timestamp = datetime.now(tz=timezone.utc).isoformat()
    ledger_gate = _check_ledger(event_id, resumed_by)
    if ledger_gate["decision"] == "REJECT":
        decision = {
            "structure": "003",
            "phase": "3",
            "event_id": event_id,
            "attempted_actor": resumed_by,
            "decision": "REJECT",
            "reason": ledger_gate["reason"],
            "ledger_ref": ledger_gate.get("ledger_ref"),
            "timestamp": timestamp,
        }
        _log_resume_gate(decision)
        _append_ledger_entry(
            structure="003",
            action="RESUME_REJECTED",
            event_id=event_id,
            flow_id=_flow_id_for(event_id),
            actor=resumed_by,
            timestamp=timestamp,
            reason=ledger_gate["reason"],
        )
        return decision
    if ledger_gate["decision"] == "WARN":
        warn_entry = {
            "structure": "003",
            "phase": "3",
            "event_id": event_id,
            "attempted_actor": resumed_by,
            "decision": "WARN",
            "reason": "WARN_LEDGER_UNAVAILABLE",
            "timestamp": timestamp,
        }
        _log_resume_gate(warn_entry)

    _append_ledger_entry(
        structure="003",
        action="RESUME_ATTEMPT",
        event_id=event_id,
        flow_id=_flow_id_for(event_id),
        actor=resumed_by,
        timestamp=timestamp,
    )
    decision = _evaluate_resume(event_id, resumed_by, timestamp)

    if decision["decision"] != "ALLOW":
        _log_resume_gate(decision)
        _append_ledger_entry(
            structure="003",
            action="RESUME_REJECTED",
            event_id=event_id,
            flow_id=_flow_id_for(event_id),
            actor=resumed_by,
            timestamp=timestamp,
            reason=decision["reason"],
        )
        return decision

    final_draft = edited_draft or {
        "subject": STRUCTURE001_EVENT.subject,
        "body": STRUCTURE001_EVENT.body,
    }

    trace_entry = {
        "trace_id": f"{event_id}-resume",
        "event_id": event_id,
        "action": action,
        "timestamp": timestamp,
        "draft_snapshot": final_draft,
    }

    with TRACE_LOG_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(trace_entry, ensure_ascii=False) + "\n")

    decision["trace_id"] = trace_entry["trace_id"]
    _log_resume_gate(decision)
    _append_ledger_entry(
        structure="003",
        action="RESUME_ALLOWED",
        event_id=event_id,
        flow_id=_flow_id_for(event_id),
        actor=resumed_by,
        timestamp=timestamp,
        ref=trace_entry["trace_id"],
    )
    return trace_entry


_resume_state: Dict[str, Dict[str, Any]] = {}


def _evaluate_resume(event_id: str, actor: str, timestamp: str) -> Dict[str, Any]:
    state = _resume_state.setdefault(
        event_id,
        {"count": 0, "bound_actor": None, "first_resumed_at": None},
    )

    state["count"] += 1
    resume_count = state["count"]
    decision = {
        "structure": "003",
        "phase": "1",
        "event_id": event_id,
        "attempted_actor": actor,
        "bound_actor": state["bound_actor"],
        "resume_count_attempted": resume_count,
        "timestamp": timestamp,
    }

    if resume_count == 1:
        state["bound_actor"] = actor
        state["first_resumed_at"] = timestamp
        decision.update(
            {
                "decision": "ALLOW",
                "reason": "OK",
                "bound_actor": actor,
                "resume_count": 1,
            }
        )
        return decision

    if actor != state["bound_actor"]:
        decision.update(
            {
                "decision": "REJECT",
                "reason": "ACTOR_MISMATCH",
                "resume_count": resume_count,
                "first_resumed_at": state["first_resumed_at"],
            }
        )
        return decision

    decision.update(
        {
            "decision": "REJECT",
            "reason": "DUPLICATE",
            "resume_count": resume_count,
            "first_resumed_at": state["first_resumed_at"],
            "bound_actor": state["bound_actor"],
        }
    )
    return decision


def _log_resume_gate(entry: Dict[str, Any]) -> None:
    with RESUME_GATE_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def _check_ledger(event_id: str, actor: str) -> Dict[str, Any]:
    state = _read_ledger_state(event_id)
    if state["status"] == "error":
        return {"decision": "WARN", "reason": "LEDGER_UNAVAILABLE"}

    allowed_actor = state.get("allowed_actor")
    ledger_ref = state.get("ledger_ref")
    allowed_count = state.get("allowed_count", 0)

    if allowed_count == 0:
        return {"decision": "ALLOW", "reason": "OK_LEDGER"}

    if allowed_actor and actor != allowed_actor:
        return {
            "decision": "REJECT",
            "reason": "ACTOR_MISMATCH_LEDGER",
            "ledger_ref": ledger_ref,
        }

    return {
        "decision": "REJECT",
        "reason": "DUPLICATE_LEDGER",
        "ledger_ref": ledger_ref,
    }


def _read_ledger_state(event_id: str) -> Dict[str, Any]:
    if os.environ.get("STRUCTURE003_LEDGER_DISABLE") == "1":
        return {"status": "error", "error": "disabled via env"}

    allowed_actor: Optional[str] = None
    allowed_count = 0
    ledger_ref: Optional[str] = None
    try:
        with LEDGER_PATH.open("r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if entry.get("event_id") != event_id:
                    continue
                if entry.get("action") == "RESUME_ALLOWED":
                    allowed_count += 1
                    if allowed_actor is None:
                        allowed_actor = entry.get("actor")
                        ledger_ref = f"{LEDGER_PATH}:{line_no}"
    except FileNotFoundError as exc:
        return {"status": "error", "error": str(exc)}
    except Exception as exc:
        return {"status": "error", "error": str(exc)}

    return {
        "status": "ok",
        "allowed_actor": allowed_actor,
        "allowed_count": allowed_count,
        "ledger_ref": ledger_ref,
    }


def _append_ledger_entry(
    *,
    structure: str,
    action: str,
    event_id: str,
    flow_id: str,
    actor: Optional[str],
    timestamp: str,
    ref: Optional[str] = None,
    reason: Optional[str] = None,
) -> None:
    entry = {
        "structure": structure,
        "action": action,
        "event_id": event_id,
        "flow_id": flow_id,
        "actor": actor,
        "timestamp": timestamp,
        "ref": ref,
    }
    if reason:
        entry["reason"] = reason
    try:
        with LEDGER_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception as exc:
        print(f"[structure-003-ledger] append failed: {exc}", file=sys.stderr)


def _flow_id_for(event_id: str) -> str:
    if event_id == STRUCTURE001_EVENT.event_id:
        return STRUCTURE001_EVENT.flow_id
    return "unknown"


def main() -> None:
    packet = build_handoff_packet()
    print(f"📦 Handoff packet saved to {PACKET_PATH}")
    trace_entry = resume_event(
        STRUCTURE001_EVENT.event_id,
        "approve",
        resumed_by="phase0-operator",
    )
    print(f"📝 Resume trace appended to {TRACE_LOG_PATH}")
    print(json.dumps({"packet": packet, "resume": trace_entry}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

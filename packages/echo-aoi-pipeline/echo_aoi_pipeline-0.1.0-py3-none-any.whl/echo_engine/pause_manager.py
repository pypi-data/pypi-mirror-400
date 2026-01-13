"""Pause-as-state manager that records pause events and post-pause drift."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, Optional, Tuple

TRACE_DIR = Path("trace")
TRACE_DIR.mkdir(exist_ok=True)
PAUSE_TRACE = TRACE_DIR / "pause_trace.jsonl"
PAUSE_METRICS = TRACE_DIR / "pause_metrics.jsonl"


@dataclass
class PauseRequest:
    session_id: str
    pause_reason: Optional[str] = None
    what_almost_done: Optional[str] = None
    why_not_now: Optional[str] = None
    metadata: Dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.session_id:
            raise ValueError("session_id is required for a pause request.")
        clues = [
            (self.pause_reason or "").strip(),
            (self.what_almost_done or "").strip(),
            (self.why_not_now or "").strip(),
        ]
        if not any(clues):
            raise ValueError(
                "At least one of pause_reason, what_almost_done, why_not_now must be provided."
            )


@dataclass
class PauseEntry:
    session_id: str
    pause_reason: Optional[str]
    what_almost_done: Optional[str]
    why_not_now: Optional[str]
    created_at: float
    resumed_at: Optional[float] = None
    reentry_count: int = 0
    metadata: Dict[str, str] = field(default_factory=dict)

    @property
    def is_active(self) -> bool:
        return self.resumed_at is None


class PauseManager:
    def __init__(self) -> None:
        self._cache: Dict[str, PauseEntry] = {}
        self._load_existing()

    def _load_existing(self) -> None:
        if not PAUSE_TRACE.exists():
            return
        with PAUSE_TRACE.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                entry = PauseEntry(**data)
                self._cache[entry.session_id] = entry

    def enter_pause(self, request: PauseRequest) -> PauseEntry:
        request.validate()
        entry = PauseEntry(
            session_id=request.session_id,
            pause_reason=(request.pause_reason or "").strip() or None,
            what_almost_done=(request.what_almost_done or "").strip() or None,
            why_not_now=(request.why_not_now or "").strip() or None,
            created_at=time.time(),
            metadata=request.metadata,
        )
        self._cache[entry.session_id] = entry
        self._append_trace(entry)
        self._record_metric(entry, event="pause")
        return entry

    def has_active_pause(self, session_id: str) -> bool:
        entry = self._cache.get(session_id)
        return bool(entry and entry.is_active)

    def resume(self, session_id: str) -> Optional[PauseEntry]:
        entry = self._cache.get(session_id)
        if not entry or not entry.is_active:
            return None
        entry.resumed_at = time.time()
        entry.reentry_count += 1
        self._append_trace(entry)
        self._record_metric(entry, event="resume")
        return entry

    def post_pause_adjustment(self, session_id: str) -> Optional[Dict[str, float]]:
        entry = self._cache.get(session_id)
        if not entry or entry.is_active:
            return None
        # Basic heuristic: more pauses -> stronger adjustments
        multiplier = min(entry.reentry_count + 1, 3)
        return {
            "delay_seconds": 2.0 * multiplier,
            "risk_multiplier": 1.0 + 0.15 * multiplier,
            "require_reaffirmation": 1.0,
        }

    def log_pause_metric(self, session_id: str, outcome: str) -> None:
        entry = self._cache.get(session_id)
        if not entry:
            return
        self._record_metric(entry, event=outcome)

    def _append_trace(self, entry: PauseEntry) -> None:
        with PAUSE_TRACE.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")

    def _record_metric(self, entry: PauseEntry, event: str) -> None:
        payload = {
            "timestamp": time.time(),
            "session_id": entry.session_id,
            "event": event,
            "pause_reason": entry.pause_reason,
            "reentry_count": entry.reentry_count,
        }
        with PAUSE_METRICS.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")


_PAUSE_MANAGER: Optional[PauseManager] = None


def get_pause_manager() -> PauseManager:
    global _PAUSE_MANAGER
    if _PAUSE_MANAGER is None:
        _PAUSE_MANAGER = PauseManager()
    return _PAUSE_MANAGER

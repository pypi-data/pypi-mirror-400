from __future__ import annotations

import csv
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

LEDGER_PATH = Path("artifacts/structure003_phase2/ledger.jsonl")


@dataclass
class LedgerEntry:
    timestamp: str
    structure: str
    action: str
    event_id: str
    flow_id: str
    actor: Optional[str]
    ref: Optional[str]
    reason: Optional[str]

    @staticmethod
    def from_json(entry: Dict[str, Any]) -> "LedgerEntry":
        return LedgerEntry(
            timestamp=entry["timestamp"],
            structure=entry["structure"],
            action=entry["action"],
            event_id=entry["event_id"],
            flow_id=entry["flow_id"],
            actor=entry.get("actor"),
            ref=entry.get("ref"),
            reason=entry.get("reason"),
        )


def load_entries(event_id: str) -> List[LedgerEntry]:
    entries: List[LedgerEntry] = []
    with LEDGER_PATH.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record.get("event_id") != event_id:
                continue
            entries.append(LedgerEntry.from_json(record))
    entries.sort(key=lambda e: e.timestamp)
    return entries


def build_snapshot(event_id: str) -> Dict[str, Any]:
    entries = load_entries(event_id)
    if not entries:
        raise ValueError(f"No ledger entries found for event_id={event_id}")

    snapshot = {
        "event_id": event_id,
        "exported_at": datetime.now(tz=timezone.utc).isoformat(),
        "range": {
            "from": entries[0].timestamp if entries else None,
            "to": entries[-1].timestamp if entries else None,
        },
        "entry_count": len(entries),
        "entries": [
            {
                "timestamp": entry.timestamp,
                "structure": entry.structure,
                "action": entry.action,
                "flow_id": entry.flow_id,
                "actor": entry.actor,
                "ref": entry.ref,
                "reason": entry.reason,
            }
            for entry in entries
        ],
    }
    return snapshot


def snapshot_hash(snapshot: Dict[str, Any]) -> str:
    payload = json.dumps(snapshot, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def write_snapshot_files(
    snapshot: Dict[str, Any],
    output_dir: Path,
    formats: Tuple[str, ...] = ("json", "csv"),
) -> List[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths: List[Path] = []
    if "json" in formats:
        json_path = output_dir / "snapshot.json"
        json_path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2))
        _write_hash_file(json_path)
        paths.append(json_path)
    if "csv" in formats:
        csv_path = output_dir / "snapshot.csv"
        _write_csv(snapshot["entries"], csv_path)
        _write_hash_file(csv_path)
        paths.append(csv_path)
    return paths


def _write_csv(entries: List[Dict[str, Any]], path: Path) -> None:
    fieldnames = ["timestamp", "structure", "action", "flow_id", "actor", "ref", "reason"]
    with path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in entries:
            writer.writerow(
                {
                    "timestamp": entry["timestamp"],
                    "structure": entry["structure"],
                    "action": entry["action"],
                    "flow_id": entry["flow_id"],
                    "actor": entry.get("actor") or "",
                    "ref": entry.get("ref") or "",
                    "reason": entry.get("reason") or "",
                }
            )


def _write_hash_file(path: Path) -> None:
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    (path.with_suffix(path.suffix + ".sha256")).write_text(f"{sha}  {path.name}\n")

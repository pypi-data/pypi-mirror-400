#!/usr/bin/env python3
"""
Capture Human-as-Judgment-Interface reflections and maintain lightweight metrics.

Usage example:
    python tools/hjtl_reflection_capture.py \
        --stop-id STOP-2025-01-21-001 \
        --operator nick \
        --prompt-pack templates/hjtl_prompt_pack.yaml \
        --input-file /tmp/hjtl_answers.json \
        --latency-ms 78000 \
        --question-clarity 4 \
        --pattern-hit-count 1
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Optional

import yaml

ROOT = Path(__file__).resolve().parents[1]
PROMPT_DEFAULT = ROOT / "templates" / "hjtl_prompt_pack.yaml"
HJTL_ROOT = ROOT / "pattern_memory" / "hjtl"
SNAPSHOT_DIR = HJTL_ROOT / "snapshots"
LOG_FILE = HJTL_ROOT / "reflections.jsonl"
METRICS_FILE = HJTL_ROOT / "metrics_summary.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Store HJTL reflection entries.")
    parser.add_argument("--stop-id", required=True, help="STOP event identifier.")
    parser.add_argument("--operator", required=True, help="Human judgment owner.")
    parser.add_argument(
        "--input-file",
        required=True,
        help="Path to JSON payload with question answers and decision fields.",
    )
    parser.add_argument(
        "--prompt-pack",
        default=str(PROMPT_DEFAULT),
        help="Path to hjtl_prompt_pack.yaml.",
    )
    parser.add_argument(
        "--latency-ms",
        type=int,
        required=True,
        help="Latency (milliseconds) for completing the HJTL loop.",
    )
    parser.add_argument(
        "--question-clarity",
        type=int,
        default=None,
        help="Optional 1-5 score indicating how clear the prompts felt.",
    )
    parser.add_argument(
        "--auto-retry",
        action="store_true",
        help="Mark if the operator retried execution immediately after STOP.",
    )
    parser.add_argument(
        "--pattern-hit-count",
        type=int,
        default=0,
        help="Number of historical pattern references used.",
    )
    parser.add_argument(
        "--mark-incomplete",
        action="store_true",
        help="Set when STOP loop did not finish successfully (defaults to completed).",
    )
    parser.add_argument(
        "--language",
        default="ko",
        choices=("ko", "en"),
        help="Language key to validate prompt questions.",
    )
    return parser.parse_args()


def read_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def load_prompt_pack(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def required_question_ids(prompt_pack: Dict[str, Any], language: str) -> List[str]:
    required = []
    for stage in prompt_pack.get("stages", []):
        if stage.get("id") != "structured_questions":
            continue
        for prompt in stage.get("prompts", {}).get(language, []):
            if prompt.get("type") != "textarea":
                continue
            if prompt.get("required") or prompt.get("optional") is False:
                required.append(prompt["id"])
    return required


def ensure_dirs() -> None:
    HJTL_ROOT.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    if not LOG_FILE.exists():
        LOG_FILE.touch()
    if not METRICS_FILE.exists():
        with open(METRICS_FILE, "w", encoding="utf-8") as fh:
            json.dump(
                {
                    "total_sessions": 0,
                    "completed_sessions": 0,
                    "avg_latency_ms": 0,
                    "decision_distribution": {},
                    "confidence_distribution": {},
                    "question_clarity_scores": [],
                    "auto_retry_count": 0,
                    "pattern_hit_total": 0,
                },
                fh,
                indent=2,
            )


def validate_answers(required_ids: List[str], answers: Dict[str, Any]) -> None:
    missing = [qid for qid in required_ids if not answers.get(qid)]
    if missing:
        raise ValueError(f"Missing required question responses: {', '.join(missing)}")


def append_log(entry: Dict[str, Any]) -> None:
    with open(LOG_FILE, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")


def write_snapshot(entry: Dict[str, Any]) -> None:
    ts = entry["timestamp"]
    stop_id = entry["stop_id"].replace("/", "_")
    snapshot_path = SNAPSHOT_DIR / f"{ts}_{stop_id}.json"
    with open(snapshot_path, "w", encoding="utf-8") as fh:
        json.dump(entry, fh, indent=2, ensure_ascii=False)


def update_metrics(entry: Dict[str, Any], clarity: int | None, completed: bool) -> None:
    metrics = read_json(METRICS_FILE)
    metrics["total_sessions"] += 1
    if completed:
        metrics["completed_sessions"] += 1
    metrics["avg_latency_ms"] = _rolling_average(
        previous_avg=metrics["avg_latency_ms"],
        total_count=metrics["total_sessions"],
        new_value=entry["latency_ms"],
    )
    _increment(metrics["decision_distribution"], entry["decision"])
    _increment(metrics["confidence_distribution"], entry["confidence"])
    if clarity:
        metrics.setdefault("question_clarity_scores", []).append(clarity)
        metrics["question_clarity_avg"] = mean(metrics["question_clarity_scores"])
    metrics["auto_retry_count"] += 1 if entry["auto_retry"] else 0
    metrics["pattern_hit_total"] += entry["pattern_hit_count"]
    metrics["hjtl_completion_rate"] = (
        metrics["completed_sessions"] / metrics["total_sessions"]
        if metrics["total_sessions"]
        else 0
    )
    with open(METRICS_FILE, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2, ensure_ascii=False)


def _rolling_average(previous_avg: float, total_count: int, new_value: int) -> float:
    return ((previous_avg * (total_count - 1)) + new_value) / max(total_count, 1)


def _increment(bucket: Dict[str, int], key: str) -> None:
    bucket[key] = bucket.get(key, 0) + 1


def record_hjtl_reflection(
    *,
    stop_id: str,
    operator: str,
    answers: Dict[str, Any],
    decision: str,
    rationale: str,
    confidence: str,
    reflection: Optional[str],
    latency_ms: int,
    language: str = "ko",
    prompt_pack_path: str = str(PROMPT_DEFAULT),
    auto_retry: bool = False,
    pattern_hit_count: int = 0,
    question_clarity: Optional[int] = None,
    completed: bool = True,
) -> Dict[str, Any]:
    """Reusable hook for storing HJTL reflections programmatically."""
    ensure_dirs()
    prompt_pack = load_prompt_pack(prompt_pack_path)
    required_ids = required_question_ids(prompt_pack, language=language)
    validate_answers(required_ids, answers)

    entry = {
        "stop_id": stop_id,
        "operator": operator,
        "timestamp": dt.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "question_version": prompt_pack.get("version", 1),
        "answers": answers,
        "decision": decision,
        "rationale": rationale,
        "confidence": confidence,
        "reflection": reflection,
        "latency_ms": latency_ms,
        "language": language,
        "auto_retry": bool(auto_retry),
        "pattern_hit_count": max(0, pattern_hit_count),
    }

    append_log(entry)
    write_snapshot(entry)
    update_metrics(
        entry,
        clarity=question_clarity,
        completed=completed,
    )
    print(
        f"Stored HJTL reflection for {entry['stop_id']} "
        f"(decision={entry['decision']}, latency={entry['latency_ms']}ms)."
    )
    return entry


def main() -> None:
    args = parse_args()
    payload = read_json(args.input_file)
    record_hjtl_reflection(
        stop_id=args.stop_id,
        operator=args.operator,
        answers=payload["answers"],
        decision=payload["decision"],
        rationale=payload["rationale"],
        confidence=payload["confidence"],
        reflection=payload.get("reflection"),
        latency_ms=args.latency_ms,
        language=args.language,
        prompt_pack_path=args.prompt_pack,
        auto_retry=args.auto_retry,
        pattern_hit_count=args.pattern_hit_count,
        question_clarity=args.question_clarity,
        completed=not args.mark_incomplete,
    )


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Interactive STOP/HJTL prompt runner.

Loads `templates/hjtl_prompt_pack.yaml`, walks the operator through required
questions, and stores the results via `record_hjtl_reflection`.

Example:
    python tools/hjtl_prompt_runner.py \
        --stop-id STOP-2025-01-21-001 \
        --operator nick
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path
from typing import Any, Callable, Dict, Optional

import yaml

from tools.hjtl_reflection_capture import (
    PROMPT_DEFAULT,
    record_hjtl_reflection,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Interactive HJTL prompt runner.")
    parser.add_argument("--stop-id", required=True, help="STOP identifier.")
    parser.add_argument("--operator", required=True, help="Judgment owner.")
    parser.add_argument(
        "--language",
        default="ko",
        choices=("ko", "en"),
        help="Prompt language.",
    )
    parser.add_argument(
        "--prompt-pack",
        default=str(PROMPT_DEFAULT),
        help="Path to hjtl_prompt_pack.yaml.",
    )
    parser.add_argument(
        "--pattern-hit-count",
        type=int,
        default=0,
        help="Number of historical pattern references used in judgment.",
    )
    parser.add_argument(
        "--auto-retry",
        action="store_true",
        help="Mark if execution was retried immediately after STOP.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Collect answers but skip persistence (prints JSON).",
    )
    return parser.parse_args()


def load_stage_prompts(prompt_pack_path: str) -> Dict[str, Any]:
    with open(prompt_pack_path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def print_banner(text: str) -> None:
    print("\n" + text)


def prompt_text(
    label: str,
    placeholder: Optional[str],
    required: bool,
    input_func: Callable[[str], str],
) -> str:
    print(f"\n{label}")
    if placeholder:
        print(f"   ({placeholder})")
    while True:
        value = input_func("> ").strip()
        if value:
            return value
        if not required:
            return ""
        print("값을 입력해야 합니다.")


def prompt_select(
    label: str,
    options: list[str],
    input_func: Callable[[str], str],
) -> str:
    print(f"\n{label}")
    for idx, opt in enumerate(options, start=1):
        print(f"  {idx}. {opt}")
    while True:
        choice = input_func("> ").strip()
        if choice.isdigit():
            idx = int(choice)
            if 1 <= idx <= len(options):
                return options[idx - 1]
        if choice in options:
            return choice
        print("옵션을 다시 선택하세요.")


def interactive_prompt_session(
    prompt_pack: Dict[str, Any],
    language: str,
    *,
    input_func: Callable[[str], str] = input,
) -> Dict[str, Any]:
    start_time = time.time()
    answers: Dict[str, str] = {}
    decision_payload: Dict[str, str] = {}
    reflection_text = ""

    for stage in prompt_pack.get("stages", []):
        prompts = stage.get("prompts", {}).get(language)
        if not prompts:
            continue
        stage_id = stage.get("id")
        if stage_id == "stop_trigger":
            for prompt in prompts:
                print_banner(prompt.get("text", ""))
        elif stage_id == "structured_questions":
            for prompt in prompts:
                if prompt.get("type") != "textarea":
                    continue
                value = prompt_text(
                    prompt.get("label", ""),
                    prompt.get("placeholder"),
                    prompt.get("required", False),
                    input_func,
                )
                answers[prompt["id"]] = value
        elif stage_id == "capture":
            for prompt in prompts:
                if prompt.get("type") == "select":
                    value = prompt_select(
                        prompt.get("label", ""),
                        prompt.get("options", []),
                        input_func,
                    )
                else:
                    value = prompt_text(
                        prompt.get("label", ""),
                        prompt.get("placeholder"),
                        prompt.get("required", False),
                        input_func,
                    )
                decision_payload[prompt["id"]] = value
        elif stage_id == "reflection":
            for prompt in prompts:
                reflection_text = prompt_text(
                    prompt.get("label", ""),
                    prompt.get("placeholder"),
                    prompt.get("required", False),
                    input_func,
                )

    latency_ms = int((time.time() - start_time) * 1000)
    clarity_input = input_func("\n질문 난이도 (1-5, 빈칸=skip): ").strip()
    clarity_score = int(clarity_input) if clarity_input.isdigit() else None

    return {
        "answers": answers,
        "decision": decision_payload.get("decision", "REJECT"),
        "rationale": decision_payload.get("rationale", ""),
        "confidence": decision_payload.get("confidence", "Medium"),
        "reflection": reflection_text or None,
        "latency_ms": latency_ms,
        "clarity_score": clarity_score,
    }


def launch_hjtl_session(
    *,
    stop_id: str,
    operator: str,
    language: str = "ko",
    prompt_pack_path: str = str(PROMPT_DEFAULT),
    pattern_hit_count: int = 0,
    auto_retry: bool = False,
    input_func: Callable[[str], str] = input,
) -> Dict[str, Any]:
    """Run interactive prompts and persist the result."""
    prompt_pack = load_stage_prompts(prompt_pack_path)
    session = interactive_prompt_session(
        prompt_pack,
        language,
        input_func=input_func,
    )

    entry = record_hjtl_reflection(
        stop_id=stop_id,
        operator=operator,
        answers=session["answers"],
        decision=session["decision"],
        rationale=session["rationale"],
        confidence=session["confidence"],
        reflection=session["reflection"],
        latency_ms=session["latency_ms"],
        language=language,
        prompt_pack_path=prompt_pack_path,
        auto_retry=auto_retry,
        pattern_hit_count=max(0, pattern_hit_count),
        question_clarity=session["clarity_score"],
        completed=True,
    )
    return {
        "entry": entry,
        "session": session,
    }


def run() -> None:
    args = parse_args()
    prompt_pack = load_stage_prompts(args.prompt_pack)
    session = interactive_prompt_session(prompt_pack, args.language)

    if args.dry_run:
        print("\n--- DRY RUN ---")
        print({
            "answers": session["answers"],
            "decision": session["decision"],
            "rationale": session["rationale"],
            "confidence": session["confidence"],
            "reflection": session["reflection"],
        })
        print(f"latency_ms={session['latency_ms']}, clarity={session['clarity_score']}")
        return

    record_hjtl_reflection(
        stop_id=args.stop_id,
        operator=args.operator,
        answers=session["answers"],
        decision=session["decision"],
        rationale=session["rationale"],
        confidence=session["confidence"],
        reflection=session["reflection"],
        latency_ms=session["latency_ms"],
        language=args.language,
        prompt_pack_path=args.prompt_pack,
        auto_retry=args.auto_retry,
        pattern_hit_count=max(0, args.pattern_hit_count),
        question_clarity=session["clarity_score"],
        completed=True,
    )


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        sys.exit("\n중단됨 (Ctrl+C)")

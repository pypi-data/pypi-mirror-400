#!/usr/bin/env python3
"""Validation harness for Challenge #1 Hard Mode (Dynamic Form).

Executes the simulation multiple times with seeded randomness, collects
improvement metrics, and writes timestamped JSON/Markdown summaries so we
have a reusable blueprint just like the Apple Watch scenario.
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

DEFAULT_SCENARIO_DIR = Path("/home/nick-heo123/eue-offline-agent/tests/challenge_scenarios/scenario1_dynamic_form")
REPORT_ROOT = Path("artifacts/challenge1_validation")


def import_runner(scenario_dir: Path):
    """Import the hard mode simulation runner dynamically."""
    if not scenario_dir.exists():
        raise FileNotFoundError(f"Scenario directory not found: {scenario_dir}")

    sys.path.insert(0, str(scenario_dir))
    from hard_mode_simulation import run_simulation  # type: ignore

    return run_simulation


def run_single(seed: int, num_trials: int, run_simulation):
    """Execute one simulation batch with a deterministic seed."""
    random.seed(seed)
    result: Dict[str, Any] = run_simulation(num_trials)
    improvement = result["summary"].get("improvement")
    vanilla_avg = result["summary"]["vanilla"].get("avg_attempts")
    echo_avg = result["summary"]["echo"].get("avg_attempts")

    return {
        "seed": seed,
        "num_trials": num_trials,
        "improvement": improvement,
        "vanilla_avg_attempts": vanilla_avg,
        "echo_avg_attempts": echo_avg,
        "vanilla_success_rate": result["summary"]["vanilla"].get("success_rate"),
        "echo_success_rate": result["summary"]["echo"].get("success_rate"),
    }


def summarize(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate improvement and attempt stats across runs."""
    improvements = [run["improvement"] for run in runs if run["improvement"]]
    vanilla_avgs = [run["vanilla_avg_attempts"] for run in runs if run["vanilla_avg_attempts"]]
    echo_avgs = [run["echo_avg_attempts"] for run in runs if run["echo_avg_attempts"]]

    def stats(values: List[float]) -> Dict[str, float]:
        return {
            "avg": float(statistics.mean(values)),
            "min": float(min(values)),
            "max": float(max(values)),
        }

    return {
        "runs": len(runs),
        "improvement": stats(improvements) if improvements else None,
        "vanilla_avg_attempts": stats(vanilla_avgs) if vanilla_avgs else None,
        "echo_avg_attempts": stats(echo_avgs) if echo_avgs else None,
    }


def write_reports(runs: List[Dict[str, Any]], summary: Dict[str, Any], output_dir: Path) -> Path:
    """Persist JSON + Markdown reports."""
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"challenge1_validation_{timestamp}.json"
    md_path = output_dir / f"challenge1_validation_{timestamp}.md"

    payload = {
        "generated_at": now.isoformat(),
        "summary": summary,
        "runs": runs,
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = [
        "# Challenge #1 Hard Mode Validation",
        f"**Generated:** {payload['generated_at']}",
        f"**Runs:** {summary['runs']}",
        "",
    ]

    if summary.get("improvement"):
        imp = summary["improvement"]
        md_lines.append(
            f"- Improvement (avg/min/max): {imp['avg']:.1f}× / {imp['min']:.1f}× / {imp['max']:.1f}×"
        )
    if summary.get("vanilla_avg_attempts"):
        stats_v = summary["vanilla_avg_attempts"]
        md_lines.append(
            f"- Vanilla avg attempts: {stats_v['avg']:.1f} (min {stats_v['min']:.1f}, max {stats_v['max']:.1f})"
        )
    if summary.get("echo_avg_attempts"):
        stats_e = summary["echo_avg_attempts"]
        md_lines.append(
            f"- Echo avg attempts: {stats_e['avg']:.1f} (min {stats_e['min']:.1f}, max {stats_e['max']:.1f})"
        )

    md_lines.append("")
    md_lines.append("## Individual Runs")
    for run in runs:
        md_lines.extend(
            [
                f"### Seed {run['seed']}",
                f"- Improvement: {run['improvement']:.1f}×",
                f"- Vanilla avg attempts: {run['vanilla_avg_attempts']:.1f}",
                f"- Echo avg attempts: {run['echo_avg_attempts']:.1f}",
                f"- Success rates (vanilla/echo): {run['vanilla_success_rate']:.0%} / {run['echo_success_rate']:.0%}",
                "",
            ]
        )

    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return md_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Challenge #1 Hard Mode improvements.")
    parser.add_argument("--runs", type=int, default=3, help="How many seeded executions to perform.")
    parser.add_argument("--base-seed", type=int, default=100, help="Base seed; increments per run.")
    parser.add_argument("--trials", type=int, default=50, help="Trials per run (default matches scenario).")
    parser.add_argument(
        "--scenario-dir",
        type=Path,
        default=DEFAULT_SCENARIO_DIR,
        help="Path to the scenario1_dynamic_form directory.",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=REPORT_ROOT,
        help="Directory for validation artifacts.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_simulation = import_runner(args.scenario_dir)

    runs: List[Dict[str, Any]] = []
    for i in range(args.runs):
        seed = args.base_seed + i
        print(f"[seed {seed}] running {args.trials} trials…")
        run = run_single(seed, args.trials, run_simulation)
        runs.append(run)
        print(
            f"  → improvement {run['improvement']:.1f}×  "
            f"(vanilla {run['vanilla_avg_attempts']:.1f} attempts → "
            f"echo {run['echo_avg_attempts']:.1f} attempts)"
        )

    summary = summarize(runs)
    md_path = write_reports(runs, summary, args.report_dir)
    print()
    print(f"Challenge #1 validation complete. Report saved to {md_path}")


if __name__ == "__main__":
    main()

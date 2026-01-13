#!/usr/bin/env python3
"""Automated validation loop for the Apple Watch scenario.

This script mirrors the behaviour of `run_comparison.py` from the
`eue-offline-agent` repository but adds guardrails for repeated runs,
seed control, and artifact generation so we have a reference protocol
for future scenarios.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

DEFAULT_SCENARIO_DIR = Path("/home/nick-heo123/eue-offline-agent/tests/challenge_scenarios/scenario2_apple_watch")
REPORT_ROOT = Path("artifacts/apple_watch_validation")


def import_modules(scenario_dir: Path):
    """Import the Apple Watch modules from the external repository."""
    if not scenario_dir.exists():
        raise FileNotFoundError(f"Scenario directory not found: {scenario_dir}")

    sys.path.insert(0, str(scenario_dir))

    from health_data_simulation import HealthDataSimulator  # type: ignore
    from vanilla_monitor import VanillaAppleWatchMonitor  # type: ignore
    from echo_monitor import EchoHealthMonitor  # type: ignore

    return HealthDataSimulator, VanillaAppleWatchMonitor, EchoHealthMonitor


def run_single(seed: int, modules) -> Dict[str, Any]:
    """Run a single simulation/monitoring comparison."""
    HealthDataSimulator, VanillaAppleWatchMonitor, EchoHealthMonitor = modules

    simulator = HealthDataSimulator(seed=seed)
    events = simulator.generate_7_day_data()
    stats = simulator.get_statistics()

    vanilla_monitor = VanillaAppleWatchMonitor()
    echo_monitor = EchoHealthMonitor()

    for event in events:
        vanilla_monitor.process_event(event)
        echo_monitor.process_event(event)

    vanilla_results = vanilla_monitor.analyze_results(events)
    echo_results = echo_monitor.analyze_results(events)

    alert_reduction = (
        (vanilla_results["total_alerts"] - echo_results["total_alerts"]) / vanilla_results["total_alerts"]
        if vanilla_results["total_alerts"]
        else 0.0
    )
    false_positive_reduction = (
        (vanilla_results["false_positives"] - echo_results["false_positives"]) / vanilla_results["false_positives"]
        if vanilla_results["false_positives"]
        else 0.0
    )

    return {
        "seed": seed,
        "stats": stats,
        "vanilla": vanilla_results,
        "echo": echo_results,
        "comparison": {
            "alert_reduction": alert_reduction,
            "false_positive_reduction": false_positive_reduction,
        },
    }


def summarize_runs(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate metrics across all seeds."""
    alert_reductions = [run["comparison"]["alert_reduction"] for run in runs]
    fp_reductions = [run["comparison"]["false_positive_reduction"] for run in runs]
    vanilla_alerts = [run["vanilla"]["total_alerts"] for run in runs]
    echo_alerts = [run["echo"]["total_alerts"] for run in runs]

    def _basic_stats(values: List[float]) -> Dict[str, float]:
        return {
            "avg": float(statistics.mean(values)),
            "min": float(min(values)),
            "max": float(max(values)),
        }

    return {
        "runs": len(runs),
        "alert_reduction": _basic_stats(alert_reductions),
        "false_positive_reduction": _basic_stats(fp_reductions),
        "vanilla_alerts": _basic_stats(vanilla_alerts),
        "echo_alerts": _basic_stats(echo_alerts),
    }


def write_reports(all_runs: List[Dict[str, Any]], summary: Dict[str, Any], output_dir: Path) -> Path:
    """Persist JSON/Markdown reports for traceability."""
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"apple_watch_validation_{timestamp}.json"
    markdown_path = output_dir / f"apple_watch_validation_{timestamp}.md"

    payload = {
        "generated_at": now.isoformat(),
        "summary": summary,
        "runs": all_runs,
    }
    report_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = [
        "# Apple Watch Validation Report",
        f"**Generated:** {payload['generated_at']}",
        f"**Runs:** {summary['runs']}",
        "",
        "## Aggregate Metrics",
        f"- Alert reduction (avg/min/max): {summary['alert_reduction']['avg']:.1%} / "
        f"{summary['alert_reduction']['min']:.1%} / {summary['alert_reduction']['max']:.1%}",
        f"- False positive reduction (avg/min/max): {summary['false_positive_reduction']['avg']:.1%} / "
        f"{summary['false_positive_reduction']['min']:.1%} / {summary['false_positive_reduction']['max']:.1%}",
        f"- Vanilla alerts (avg/min/max): {summary['vanilla_alerts']['avg']:.1f} / "
        f"{summary['vanilla_alerts']['min']:.0f} / {summary['vanilla_alerts']['max']:.0f}",
        f"- Echo alerts (avg/min/max): {summary['echo_alerts']['avg']:.1f} / "
        f"{summary['echo_alerts']['min']:.0f} / {summary['echo_alerts']['max']:.0f}",
        "",
        "## Individual Runs",
    ]

    for run in all_runs:
        md_lines.extend(
            [
                f"### Seed {run['seed']}",
                f"- Vanilla alerts: {run['vanilla']['total_alerts']} "
                f"(false positives: {run['vanilla']['false_positives']})",
                f"- Echo alerts: {run['echo']['total_alerts']} "
                f"(false positives: {run['echo']['false_positives']})",
                f"- Alert reduction: {run['comparison']['alert_reduction']:.1%}",
                f"- False positive reduction: {run['comparison']['false_positive_reduction']:.1%}",
                "",
            ]
        )

    markdown_path.write_text("\n".join(md_lines), encoding="utf-8")
    return markdown_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Apple Watch validation multiple times for confidence.")
    parser.add_argument("--runs", type=int, default=3, help="Number of simulation runs with different seeds.")
    parser.add_argument(
        "--base-seed",
        type=int,
        default=42,
        help="Base seed. Each subsequent run increments this value.",
    )
    parser.add_argument(
        "--scenario-dir",
        type=Path,
        default=DEFAULT_SCENARIO_DIR,
        help="Path to the scenario2_apple_watch directory.",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=REPORT_ROOT,
        help="Where to store validation artifacts.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    modules = import_modules(args.scenario_dir)

    runs: List[Dict[str, Any]] = []
    for i in range(args.runs):
        seed = args.base_seed + i
        run = run_single(seed, modules)
        runs.append(run)
        comparison = run["comparison"]
        print(
            f"[seed {seed}] alerts: vanilla={run['vanilla']['total_alerts']} → "
            f"echo={run['echo']['total_alerts']} | "
            f"reduction={comparison['alert_reduction']:.1%} "
            f"(FP reduction={comparison['false_positive_reduction']:.1%})"
        )

    summary = summarize_runs(runs)
    markdown_report = write_reports(runs, summary, args.report_dir)
    print()
    print(f"Validation complete. Report saved to {markdown_report}")


if __name__ == "__main__":
    main()

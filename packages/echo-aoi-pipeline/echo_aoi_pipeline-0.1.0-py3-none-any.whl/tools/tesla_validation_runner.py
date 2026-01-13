#!/usr/bin/env python3
"""Validation harness for the Tesla driver-style learning scenario."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

DEFAULT_SCENARIO_DIR = Path("/home/nick-heo123/eue-offline-agent/tests/challenge_scenarios/scenario3_tesla_driver")
REPORT_ROOT = Path("artifacts/tesla_validation")
TEMP_DATA_ROOT = Path(".validation_cache")


def import_modules(scenario_dir: Path):
    """Import Tesla scenario modules dynamically."""
    if not scenario_dir.exists():
        raise FileNotFoundError(f"Scenario directory not found: {scenario_dir}")

    sys.path.insert(0, str(scenario_dir))
    from driver_simulation import DriverDataSimulator  # type: ignore
    from vanilla_tesla import run_vanilla_monitoring  # type: ignore
    from echo_tesla import run_echo_monitoring  # type: ignore

    return DriverDataSimulator, run_vanilla_monitoring, run_echo_monitoring


def run_single(seed: int, modules, data_file: Path) -> Dict[str, Any]:
    """Generate data with a seed, run both monitors, and capture metrics."""
    DriverDataSimulator, run_vanilla_monitoring, run_echo_monitoring = modules

    simulator = DriverDataSimulator(seed=seed)
    events = simulator.generate_14_day_data()
    stats = simulator.get_statistics()

    payload = {
        "metadata": {"duration_days": 14, "total_events": len(events)},
        "statistics": stats,
        "events": events,
    }
    data_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    vanilla_results = run_vanilla_monitoring(str(data_file))
    echo_results = run_echo_monitoring(str(data_file))

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

    dangerous_events = stats.get("dangerous_events", 0) or 1
    vanilla_tp_rate = vanilla_results["true_positives"] / dangerous_events
    echo_tp_rate = echo_results["true_positives"] / dangerous_events

    return {
        "seed": seed,
        "stats": stats,
        "vanilla": vanilla_results,
        "echo": echo_results,
        "comparison": {
            "alert_reduction": alert_reduction,
            "false_positive_reduction": false_positive_reduction,
            "vanilla_tp_rate": vanilla_tp_rate,
            "echo_tp_rate": echo_tp_rate,
        },
    }


def summarize(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate alert/fp reduction across runs."""
    def collect(key: str) -> List[float]:
        return [run["comparison"][key] for run in runs]

    def stats(values: List[float]) -> Dict[str, float]:
        return {
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }

    alert_stats = stats(collect("alert_reduction")) if runs else None
    fp_stats = stats(collect("false_positive_reduction")) if runs else None

    return {
        "runs": len(runs),
        "alert_reduction": alert_stats,
        "false_positive_reduction": fp_stats,
    }


def write_reports(runs: List[Dict[str, Any]], summary: Dict[str, Any], output_dir: Path) -> Path:
    """Write JSON + Markdown summaries."""
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"tesla_validation_{timestamp}.json"
    md_path = output_dir / f"tesla_validation_{timestamp}.md"

    payload = {
        "generated_at": now.isoformat(),
        "summary": summary,
        "runs": runs,
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = [
        "# Tesla Driver Style Validation",
        f"**Generated:** {payload['generated_at']}",
        f"**Runs:** {summary['runs']}",
        "",
    ]
    if summary.get("alert_reduction"):
        stats = summary["alert_reduction"]
        md_lines.append(
            f"- Alert reduction (avg/min/max): {stats['avg']:.1%} / {stats['min']:.1%} / {stats['max']:.1%}"
        )
    if summary.get("false_positive_reduction"):
        stats = summary["false_positive_reduction"]
        md_lines.append(
            f"- False positive reduction (avg/min/max): {stats['avg']:.1%} / {stats['min']:.1%} / {stats['max']:.1%}"
        )
    md_lines.append("")
    md_lines.append("## Individual Runs")
    for run in runs:
        comp = run["comparison"]
        md_lines.extend(
            [
                f"### Seed {run['seed']}",
                f"- Alerts: vanilla={run['vanilla']['total_alerts']} → echo={run['echo']['total_alerts']}",
                f"- False positives: {run['vanilla']['false_positives']} → {run['echo']['false_positives']}",
                f"- Alert reduction: {comp['alert_reduction']:.1%}",
                f"- False positive reduction: {comp['false_positive_reduction']:.1%}",
                f"- Dangerous detection (vanilla/echo): {comp['vanilla_tp_rate']:.0%} / {comp['echo_tp_rate']:.0%}",
                "",
            ]
        )

    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return md_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Tesla driver-style learning scenario.")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--base-seed", type=int, default=200)
    parser.add_argument(
        "--scenario-dir",
        type=Path,
        default=DEFAULT_SCENARIO_DIR,
        help="Path to scenario3_tesla_driver directory.",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=REPORT_ROOT,
        help="Directory to store validation artifacts.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    modules = import_modules(args.scenario_dir)
    TEMP_DATA_ROOT.mkdir(parents=True, exist_ok=True)

    runs: List[Dict[str, Any]] = []
    for i in range(args.runs):
        seed = args.base_seed + i
        data_file = TEMP_DATA_ROOT / f"tesla_driver_data_seed{seed}.json"
        print(f"[seed {seed}] running Tesla validation…")
        run = run_single(seed, modules, data_file)
        runs.append(run)
        comp = run["comparison"]
        print(
            f"  → alerts {run['vanilla']['total_alerts']}→{run['echo']['total_alerts']} "
            f"(reduction {comp['alert_reduction']:.1%}); FP reduction {comp['false_positive_reduction']:.1%}"
        )

    summary = summarize(runs)
    md_path = write_reports(runs, summary, args.report_dir)
    print()
    print(f"Tesla validation complete. Report saved to {md_path}")


if __name__ == "__main__":
    main()

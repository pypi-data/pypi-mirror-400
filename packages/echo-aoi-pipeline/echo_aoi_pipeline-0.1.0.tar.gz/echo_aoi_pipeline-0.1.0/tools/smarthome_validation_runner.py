#!/usr/bin/env python3
"""Validation harness for the Smart Home context-aware automation scenario."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

DEFAULT_SCENARIO_DIR = Path("/home/nick-heo123/eue-offline-agent/tests/challenge_scenarios/scenario4_smart_home")
REPORT_ROOT = Path("artifacts/smarthome_validation")
TEMP_DATA_ROOT = Path(".validation_cache")


def import_modules(scenario_dir: Path):
    """Import Smart Home modules dynamically."""
    if not scenario_dir.exists():
        raise FileNotFoundError(f"Scenario directory not found: {scenario_dir}")

    sys.path.insert(0, str(scenario_dir))
    from smart_home_simulation import SmartHomeSimulator, VanillaSmartHome, EchoSmartHome  # type: ignore

    return SmartHomeSimulator, VanillaSmartHome, EchoSmartHome


def run_single(seed: int, modules, data_path: Path) -> Dict[str, Any]:
    """Generate data with seed and compute energy usage for both systems."""
    SmartHomeSimulator, VanillaSmartHome, EchoSmartHome = modules
    simulator = SmartHomeSimulator()
    events = simulator.generate_30_day_patterns()

    payload = {"seed": seed, "events": events}
    data_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    vanilla = VanillaSmartHome().calculate_energy_usage(events)
    echo = EchoSmartHome().calculate_energy_usage(events)

    savings = (
        (vanilla["total_energy_kwh"] - echo["total_energy_kwh"]) / vanilla["total_energy_kwh"]
        if vanilla["total_energy_kwh"]
        else 0.0
    )

    return {
        "seed": seed,
        "events_path": str(data_path),
        "vanilla": vanilla,
        "echo": echo,
        "comparison": {
            "energy_savings": savings,
            "vanilla_waste_pct": vanilla["waste_percentage"],
            "echo_waste_pct": echo["waste_percentage"],
        },
    }


def summarize(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate energy savings across runs."""
    def collect(key: str) -> List[float]:
        return [run["comparison"][key] for run in runs]

    def stats(values: List[float]) -> Dict[str, float]:
        return {
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }

    energy_stats = stats(collect("energy_savings")) if runs else None
    vanilla_waste = stats(collect("vanilla_waste_pct")) if runs else None
    echo_waste = stats(collect("echo_waste_pct")) if runs else None

    return {
        "runs": len(runs),
        "energy_savings": energy_stats,
        "vanilla_waste_pct": vanilla_waste,
        "echo_waste_pct": echo_waste,
    }


def write_reports(runs: List[Dict[str, Any]], summary: Dict[str, Any], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"smarthome_validation_{timestamp}.json"
    md_path = output_dir / f"smarthome_validation_{timestamp}.md"

    payload = {"generated_at": now.isoformat(), "summary": summary, "runs": runs}
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    md_lines = [
        "# Smart Home Validation",
        f"**Generated:** {payload['generated_at']}",
        f"**Runs:** {summary['runs']}",
        "",
    ]

    if summary.get("energy_savings"):
        stats = summary["energy_savings"]
        md_lines.append(
            f"- Energy savings (avg/min/max): {stats['avg']:.1%} / {stats['min']:.1%} / {stats['max']:.1%}"
        )
    if summary.get("vanilla_waste_pct"):
        stats = summary["vanilla_waste_pct"]
        md_lines.append(
            f"- Vanilla waste % (avg/min/max): {stats['avg']:.1f}% / {stats['min']:.1f}% / {stats['max']:.1f}%"
        )
    if summary.get("echo_waste_pct"):
        stats = summary["echo_waste_pct"]
        md_lines.append(
            f"- Echo waste % (avg/min/max): {stats['avg']:.1f}% / {stats['min']:.1f}% / {stats['max']:.1f}%"
        )

    md_lines.append("")
    md_lines.append("## Individual Runs")
    for run in runs:
        comp = run["comparison"]
        md_lines.extend(
            [
                f"### Seed {run['seed']}",
                f"- Energy (kWh): vanilla={run['vanilla']['total_energy_kwh']:.1f} → echo={run['echo']['total_energy_kwh']:.1f}",
                f"- Waste %: vanilla {comp['vanilla_waste_pct']:.1f}% → echo {comp['echo_waste_pct']:.1f}%",
                f"- Savings: {comp['energy_savings']:.1%}",
                f"- Data: {run['events_path']}",
                "",
            ]
        )

    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return md_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Smart Home scenario.")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--base-seed", type=int, default=300)
    parser.add_argument(
        "--scenario-dir",
        type=Path,
        default=DEFAULT_SCENARIO_DIR,
        help="Path to scenario4_smart_home directory.",
    )
    parser.add_argument("--report-dir", type=Path, default=REPORT_ROOT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    modules = import_modules(args.scenario_dir)
    TEMP_DATA_ROOT.mkdir(parents=True, exist_ok=True)

    runs: List[Dict[str, Any]] = []
    for i in range(args.runs):
        seed = args.base_seed + i
        data_path = TEMP_DATA_ROOT / f"smarthome_events_seed{seed}.json"
        print(f"[seed {seed}] running Smart Home validation…")
        run = run_single(seed, modules, data_path)
        runs.append(run)
        print(
            f"  → energy {run['vanilla']['total_energy_kwh']:.1f}→{run['echo']['total_energy_kwh']:.1f} "
            f"(savings {run['comparison']['energy_savings']:.1%})"
        )

    summary = summarize(runs)
    md_path = write_reports(runs, summary, args.report_dir)
    print()
    print(f"Smart Home validation complete. Report saved to {md_path}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Generate overview charts for the Echo Universal Pattern Engine results."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Callable, Dict, Optional

import matplotlib.pyplot as plt


ARTIFACT_DIRS = {
    "apple": Path("artifacts/apple_watch_validation"),
    "challenge": Path("artifacts/challenge1_validation"),
    "tesla": Path("artifacts/tesla_validation"),
    "smarthome": Path("artifacts/smarthome_validation"),
}


def latest_json(path: Path) -> Optional[Path]:
    """Return the newest JSON file in a directory."""
    if not path.exists():
        return None
    json_files = sorted(path.glob("*.json"))
    return json_files[-1] if json_files else None


def load_metric(json_path: Path, extractor: Callable[[Dict], float]) -> float:
    """Load a JSON file and extract the metric."""
    data = json.loads(json_path.read_text(encoding="utf-8"))
    return extractor(data)


def plot_metrics(values: Dict[str, float], output_path: Path) -> None:
    """Render a 2x2 subplot with scenario metrics."""
    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    fig.suptitle("Echo Universal Pattern Engine — Scenario Metrics", fontsize=14)

    config = [
        ("Apple Watch Alert Reduction (%)", "apple", values["apple"] * 100.0, "seagreen"),
        ("Challenge #1 Speed (× faster)", "challenge", values["challenge"], "royalblue"),
        ("Tesla FP Reduction (%)", "tesla", values["tesla"] * 100.0, "darkorange"),
        ("Smart Home Energy Savings (%)", "smarthome", values["smarthome"] * 100.0, "mediumpurple"),
    ]

    for ax, (title, label, value, color) in zip(axes.flat, config):
        ax.bar([label], [value], color=color)
        ax.set_title(title)
        ax.set_ylim(0, max(value * 1.2, value + 5))
        ax.bar_label(ax.containers[0], fmt="%.1f", padding=3)
    plt.tight_layout(rect=[0, 0, 1, 0.97])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description="Produce EUPE overview charts.")
    parser.add_argument("--apple-json", type=Path)
    parser.add_argument("--challenge-json", type=Path)
    parser.add_argument("--tesla-json", type=Path)
    parser.add_argument("--smarthome-json", type=Path)
    parser.add_argument("--output", type=Path, default=Path("artifacts/eupe_charts/eupe_overview.png"))
    args = parser.parse_args()

    json_paths = {
        "apple": args.apple_json or latest_json(ARTIFACT_DIRS["apple"]),
        "challenge": args.challenge_json or latest_json(ARTIFACT_DIRS["challenge"]),
        "tesla": args.tesla_json or latest_json(ARTIFACT_DIRS["tesla"]),
        "smarthome": args.smarthome_json or latest_json(ARTIFACT_DIRS["smarthome"]),
    }

    for key, path in json_paths.items():
        if path is None:
            raise FileNotFoundError(f"No JSON artifact found for {key}. Provide --{key}-json.")

    extractors = {
        "apple": lambda data: data["summary"]["alert_reduction"]["avg"],
        "challenge": lambda data: data["summary"]["improvement"]["avg"],
        "tesla": lambda data: data["summary"]["false_positive_reduction"]["avg"],
        "smarthome": lambda data: data["summary"]["energy_savings"]["avg"],
    }

    values = {
        name: load_metric(json_paths[name], extractors[name])
        for name in json_paths
    }

    plot_metrics(values, args.output)
    print(f"Chart saved to {args.output}")


if __name__ == "__main__":
    main()

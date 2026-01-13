#!/usr/bin/env python3
"""End-to-end smoke test for the inspection pipeline (AOI, XRAY, ...)."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List

if __package__ is None or __package__ == "":
    # Allow running via `python tools/pipeline_smoke.py`
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

from tools.pipeline.paths import get_domain_paths

DOMAIN_MODULES: Dict[str, Dict[str, str]] = {
    "aoi": {
        "sim": "tools.aoi_simulation_export",
        "ingest": "tools.aoi_ingest",
        "stage": "tools.aoi_stage_inference",
        "export": "tools.aoi_training_export",
    },
    "xray": {
        "sim": "tools.aoi_simulation_export",  # reuse AOI simulator for now
        "ingest": "tools.aoi_ingest",
        "stage": "tools.xray_stage_inference",
        "export": "tools.aoi_training_export",
    },
}


def run(cmd: List[str]) -> None:
    print(f"[smoke] Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Smoke test for inspection pipelines.")
    parser.add_argument("--domain", choices=sorted(DOMAIN_MODULES.keys()), default="aoi")
    parser.add_argument("--lots", type=int, default=1)
    parser.add_argument("--boards-per-lot", type=int, default=1)
    parser.add_argument("--pads-per-board", type=int, default=5)
    parser.add_argument("--seed", type=int, default=2025)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    defaults = get_domain_paths(args.domain)
    modules = DOMAIN_MODULES[args.domain]

    smoke_root = Path(f"artifacts/{args.domain}_smoke")
    samples_dir = smoke_root / "samples"
    results_dir = smoke_root / "results"
    artifact_path = smoke_root / f"{args.domain}_stage_results.json"
    dataset_dir = defaults.dataset_root.parent / f"{defaults.domain}_dataset_smoke"

    if smoke_root.exists():
        shutil.rmtree(smoke_root)
    smoke_root.mkdir(parents=True, exist_ok=True)
    samples_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)
    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)

    sim_export = smoke_root / "export"
    run([
        sys.executable, "-m", modules["sim"],
        "--output", str(sim_export),
        "--lots", str(args.lots),
        "--boards-per-lot", str(args.boards_per_lot),
        "--pads-per-board", str(args.pads_per_board),
    ])

    run([
        sys.executable, "-m", modules["ingest"],
        "--input", str(sim_export),
        "--output-root", str(samples_dir),
    ])

    run([
        sys.executable, "-m", modules["stage"],
        "--samples-base", str(samples_dir),
        "--results-root", str(results_dir),
        "--artifact-copy", str(artifact_path),
        "--seed", str(args.seed),
    ])

    stage_results = results_dir / "stage_results.json"
    run([
        sys.executable, "-m", modules["export"],
        "--stage-results", str(stage_results),
        "--output", str(dataset_dir),
        "--mode", "scores",
        "--clean",
    ])

    # Basic validations
    data = json.loads(stage_results.read_text())
    assert data["sample_count"] > 0, "No samples processed"
    exported = 0
    for label in ("OK", "TrueDefect", "PseudoDefect"):
        bucket = dataset_dir / label
        exported += len(list(bucket.glob("*.png")))
    assert exported == data["sample_count"], "Mismatch between stage results and exported samples"

    print(f"[smoke] {args.domain.upper()} pipeline smoke test completed successfully.")


if __name__ == "__main__":
    main()

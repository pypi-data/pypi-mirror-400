#!/usr/bin/env python3
"""Export AOI training images into /training/dataset_v0 buckets."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Dict

DEFAULT_STAGE_RESULTS = Path("results/stage_results.json")
DEFAULT_OUTPUT = Path("training/dataset_v0")
LABELS = ("OK", "TrueDefect", "PseudoDefect")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Copy AOI samples into training/dataset_v0 buckets.")
    parser.add_argument("--stage-results", type=Path, default=DEFAULT_STAGE_RESULTS, help="Path to stage_results.json")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Dataset output directory root")
    parser.add_argument(
        "--mode",
        choices=("scores", "policy", "aoi_flag"),
        default="scores",
        help="How to choose the target bucket label",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional maximum number of samples to export",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove existing dataset_v0 buckets before exporting",
    )
    parser.add_argument(
        "--symlink",
        action="store_true",
        help="Use symbolic links instead of copying files",
    )
    return parser.parse_args()


def load_stage_results(path: Path) -> Dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"stage_results.json not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def prepare_output_dirs(output: Path, clean: bool) -> None:
    if clean and output.exists():
        shutil.rmtree(output)
    for label in LABELS:
        (output / label).mkdir(parents=True, exist_ok=True)


def label_from_policy(decision: str) -> str:
    if decision == "AUTO_OK":
        return "OK"
    if decision == "AUTO_NG":
        return "TrueDefect"
    return "PseudoDefect"


def label_from_scores(scores: Dict[str, float]) -> str:
    return max(scores.items(), key=lambda item: item[1])[0]


def label_from_aoi_flag(flag: str) -> str:
    flag = flag.upper()
    if flag in {"OK", "PASS"}:
        return "OK"
    if flag in {"NG", "FAIL", "TRUE_DEFECT"}:
        return "TrueDefect"
    return "PseudoDefect"


def resolve_label(result: Dict[str, object], mode: str) -> str:
    if mode == "policy":
        return label_from_policy(str(result["policy_decision"]))
    if mode == "aoi_flag":
        return label_from_aoi_flag(str(result.get("aoi_flag", "")))
    assert mode == "scores"
    return label_from_scores(result["scores"])  # type: ignore[arg-type]


def export_sample(result: Dict[str, object], label: str, output: Path, symlink: bool) -> None:
    stage_inputs = result["stage_inputs"]  # type: ignore[index]
    image_path = Path(stage_inputs["image_path"])  # type: ignore[index]
    if not image_path.exists():
        print(f"[skip] image not found for {result['sample_id']}: {image_path}")
        return
    dest_path = output / label / f"{result['sample_id']}.png"
    if symlink:
        if dest_path.exists():
            dest_path.unlink()
        dest_path.symlink_to(image_path)
    else:
        shutil.copy2(image_path, dest_path)
    print(f"[export] {result['sample_id']} -> {dest_path}")


def main() -> None:
    args = parse_args()
    data = load_stage_results(args.stage_results)
    results = data.get("results", [])
    if not isinstance(results, list):
        raise ValueError("results must be a list")
    prepare_output_dirs(args.output, args.clean)
    exported = 0
    for result in results:
        if args.limit is not None and exported >= args.limit:
            break
        if not isinstance(result, dict):
            continue
        label = resolve_label(result, args.mode)
        if label not in LABELS:
            print(f"[warn] Unknown label '{label}' for {result.get('sample_id')}, skipping")
            continue
        export_sample(result, label, args.output, args.symlink)
        exported += 1
    print(f"Export complete: {exported} samples copied into {args.output}")


if __name__ == "__main__":
    main()

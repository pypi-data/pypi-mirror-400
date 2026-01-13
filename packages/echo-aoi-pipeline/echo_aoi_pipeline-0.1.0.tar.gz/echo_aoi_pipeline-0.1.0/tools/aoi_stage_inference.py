#!/usr/bin/env python3
"""StageInference stub that consumes real AOI samples and emits fixed-schema results."""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone
import argparse
from pathlib import Path
import sys
from typing import Any, Dict, Iterable, List, Tuple

if __package__ is None or __package__ == "":
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

from PIL import Image, ImageDraw, UnidentifiedImageError

from tools.pipeline.paths import DomainPaths, get_domain_paths

CLASS_NAMES = ["OK", "TrueDefect", "PseudoDefect"]


def build_parser(defaults: DomainPaths) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=f"Run StageInference over normalized {defaults.domain.upper()} samples.")
    parser.add_argument(
        "--samples-base",
        type=Path,
        default=defaults.samples_base,
        help="Directory containing lot/board/pad metadata.json files.",
    )
    parser.add_argument(
        "--results-root",
        type=Path,
        default=defaults.results_root,
        help="Root directory for per-sample outputs and rollup JSON.",
    )
    parser.add_argument(
        "--artifact-copy",
        type=Path,
        default=defaults.artifact_copy,
        help="Optional second location to copy the rollup JSON (for legacy tooling).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=2025,
        help="Random seed used for dummy model and placeholder Grad-CAM.",
    )
    return parser


def load_metadata_files(samples_base: Path) -> Iterable[Path]:
    return sorted(samples_base.glob("**/metadata.json"))


def stage1_light_filter(meta: Dict[str, Any]) -> str:
    # Keep heuristic consistent with mock version so we can compare outputs.
    net = meta.get("net", "")
    if net.upper().startswith("PWR"):
        return "NG"
    return "PASS"


def dummy_model(image_path: str) -> Dict[str, float]:
    # Replace the main model with a dummy that emits normalized random scores.
    raw_scores = [random.random() + 0.01 for _ in CLASS_NAMES]
    total = sum(raw_scores)
    normalized = [score / total for score in raw_scores]
    return {name: round(score, 4) for name, score in zip(CLASS_NAMES, normalized)}


def policy_layer(scores: Dict[str, float]) -> str:
    if scores["TrueDefect"] >= 0.8:
        return "AUTO_NG"
    if scores["OK"] >= 0.9:
        return "AUTO_OK"
    return "RECHECK"


def make_heatmap(image_path: str, output_path: Path) -> str:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with Image.open(image_path) as img:
            base = img.convert("RGBA")
    except UnidentifiedImageError:
        base = Image.new("RGBA", (224, 224), color=(90, 90, 90, 255))
    overlay = Image.new("RGBA", base.size, (255, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = base.size
    # Draw a few random ellipses to mimic Grad-CAM highlights.
    for _ in range(4):
        w = max(10, random.randint(width // 6, max(12, width // 2)))
        h = max(10, random.randint(height // 6, max(12, height // 2)))
        x0 = random.randint(0, max(1, width - w))
        y0 = random.randint(0, max(1, height - h))
        color = (255, random.randint(80, 140), 0, random.randint(75, 140))
        draw.ellipse((x0, y0, x0 + w, y0 + h), fill=color)
    blended = Image.alpha_composite(base, overlay)
    blended.save(output_path, format="PNG")
    return output_path.as_posix()


def placeholder_stats() -> Dict[str, Any]:
    return {
        "similar_samples_90d": random.randint(5, 40),
        "true_defect_rate_90d": round(random.uniform(0.05, 0.25), 3),
        "pseudo_defect_rate_90d": round(random.uniform(0.05, 0.35), 3),
        "ok_rate_90d": round(random.uniform(0.4, 0.8), 3),
    }


def load_metadata(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def infer_sample_coords(sample_dir: Path) -> Tuple[str, str, str]:
    pad = sample_dir.name
    board = sample_dir.parent.name if sample_dir.parent != sample_dir else "board_unknown"
    lot = sample_dir.parent.parent.name if sample_dir.parent.parent != sample_dir.parent else "lot_unknown"
    return lot, board, pad


def resolve_stage_inputs(meta: Dict[str, Any], meta_path: Path) -> Dict[str, str]:
    stage_inputs = meta.get("stage_inputs")
    sample_dir = meta_path.parent
    lot, board, pad_from_path = infer_sample_coords(sample_dir)
    pad_id = meta.get("pad_id") or meta.get("pad") or pad_from_path
    component_id = meta.get("component_id") or meta.get("component") or "COMP_UNKNOWN"
    net = meta.get("net") or meta.get("NET") or "NET_UNKNOWN"
    aoi_flag = (meta.get("aoi_flag") or meta.get("AOI_FLAG") or "UNKNOWN").upper()
    image_assets = meta.get("image_assets") or {}
    image_path = (
        stage_inputs["image_path"]
        if stage_inputs and "image_path" in stage_inputs
        else image_assets.get("crop")
        or image_assets.get("raw")
        or meta.get("image_path")
    )
    if not image_path:
        for candidate in ("crop_224.png", "crop.png", "image001.png", "raw.png"):
            candidate_path = sample_dir / candidate
            if candidate_path.exists():
                image_path = candidate_path.as_posix()
                break
    if not image_path:
        raise ValueError(f"Could not determine image path for {meta_path}")
    return {
        "image_path": image_path,
        "pad_id": pad_id,
        "component_id": component_id,
        "net": net,
        "aoi_flag": aoi_flag,
        "lot": meta.get("lot") or lot,
        "board": meta.get("board") or board,
    }


def normalize_meta(meta: Dict[str, Any], meta_path: Path) -> Dict[str, Any]:
    stage_inputs = resolve_stage_inputs(meta, meta_path)
    lot = stage_inputs.pop("lot")
    board = stage_inputs.pop("board")
    pad_id = stage_inputs["pad_id"]
    sample_id = meta.get("sample_id") or f"{lot}_{board}_{pad_id}"
    image_assets = meta.get("image_assets") or {
        "raw": stage_inputs["image_path"],
        "thumbnail": stage_inputs["image_path"],
        "crop": stage_inputs["image_path"],
        "context_grid": [],
    }
    normalized = {
        "sample_id": sample_id,
        "lot": lot,
        "board": board,
        "pad_id": pad_id,
        "component_id": stage_inputs["component_id"],
        "net": stage_inputs["net"],
        "aoi_flag": stage_inputs["aoi_flag"],
        "image_assets": image_assets,
        "stage_inputs": stage_inputs,
    }
    return normalized


def build_sample_result(
    meta: Dict[str, Any],
    meta_path: Path,
    per_sample_root: Path,
) -> Dict[str, Any]:
    normalized = normalize_meta(meta, meta_path)
    stage1 = stage1_light_filter(normalized)
    image_path = normalized["stage_inputs"]["image_path"]
    scores = dummy_model(image_path)
    decision = policy_layer(scores)
    lot, board, pad = normalized["lot"], normalized["board"], normalized["pad_id"]
    result_dir = per_sample_root / lot / board / pad
    heatmap_path = make_heatmap(image_path, result_dir / "gradcam.png")
    per_sample_json = result_dir / "result.json"
    sample_result = {
        "sample_id": normalized["sample_id"],
        "lot": lot,
        "board": board,
        "pad_id": pad,
        "component_id": normalized["component_id"],
        "net": normalized["net"],
        "aoi_flag": normalized["aoi_flag"],
        "image_assets": normalized["image_assets"],
        "stage1": {"light_filter": stage1},
        "scores": scores,
        "policy_decision": decision,
        "explainability": {
            "heatmap_path": heatmap_path,
            "generator": "placeholder_gradcam",
        },
        "statistics_90d": placeholder_stats(),
        "stage_inputs": normalized["stage_inputs"],
    }
    per_sample_json.parent.mkdir(parents=True, exist_ok=True)
    per_sample_json.write_text(json.dumps(sample_result, indent=2, ensure_ascii=False), encoding="utf-8")
    return sample_result


def write_rollup(
    results: List[Dict[str, Any]],
    results_root: Path,
    artifact_copy: Path,
) -> None:
    rollup = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "sample_count": len(results),
        "results": results,
    }
    results_root.mkdir(parents=True, exist_ok=True)
    rollup_path = results_root / "stage_results.json"
    for target in (rollup_path, artifact_copy):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(rollup, indent=2, ensure_ascii=False), encoding="utf-8")
    return rollup_path


def run_from_args(args: argparse.Namespace) -> Path:
    random.seed(args.seed)
    metadata_files = list(load_metadata_files(args.samples_base))
    if not metadata_files:
        raise SystemExit(f"No metadata.json files found under {args.samples_base}")
    per_sample_root = args.results_root / "lots"
    results = [
        build_sample_result(load_metadata(path), path, per_sample_root)
        for path in metadata_files
    ]
    rollup_path = write_rollup(results, args.results_root, args.artifact_copy)
    print(f"StageInference completed for {len(results)} samples -> {rollup_path}")
    return rollup_path


def main_with_defaults(defaults: DomainPaths | None = None) -> None:
    defaults = defaults or get_domain_paths("aoi")
    parser = build_parser(defaults)
    args = parser.parse_args()
    run_from_args(args)


def main() -> None:
    main_with_defaults()


if __name__ == "__main__":
    main()

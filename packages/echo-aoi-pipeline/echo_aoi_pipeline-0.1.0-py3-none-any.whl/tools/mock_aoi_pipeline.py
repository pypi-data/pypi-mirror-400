#!/usr/bin/env python3
"""Mock AOI triple-class policy pipeline."""

from __future__ import annotations

import json
import random
from pathlib import Path

SAMPLES = Path("samples/aoi_lite")
OUTPUT = Path("artifacts/aoi_mock")
OUTPUT.mkdir(parents=True, exist_ok=True)

random.seed(1)

CLASS_NAMES = ["OK", "TrueDefect", "PseudoDefect"]


def load_sample(index: int) -> dict:
    sample = {
        "sample_id": f"lot001_board010_pad{index:02d}",
        "meta": {
            "pad": f"PAD{index:02d}",
            "net": random.choice(["PWR", "CLK", "SENSOR", "IO"]),
            "temperature": 70 + random.random(),
        },
    }
    return sample


def mock_model(sample: dict) -> dict:
    if "PWR" in sample["meta"]["net"]:
        scores = [0.1, 0.8, 0.1]
    else:
        scores = [0.7, 0.1, 0.2]
    return {name: round(score, 2) for name, score in zip(CLASS_NAMES, scores)}


def apply_policy(scores: dict, sample: dict) -> str:
    if scores["TrueDefect"] > 0.8:
        return "AUTO_NG"
    if scores["OK"] > 0.9:
        return "AUTO_OK"
    return "RECHECK"


def main() -> None:
    results = []
    for i in range(1, 11):
        sample = load_sample(i)
        scores = mock_model(sample)
        decision = apply_policy(scores, sample)
        results.append({
            "sample": sample,
            "scores": scores,
            "decision": decision,
        })
    out = OUTPUT / "aoi_mock_results.json"
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"saved mock results to {out}")

if __name__ == "__main__":
    main()

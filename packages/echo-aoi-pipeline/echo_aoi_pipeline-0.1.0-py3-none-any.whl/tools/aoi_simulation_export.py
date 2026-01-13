#!/usr/bin/env python3
"""Generate a simulated AOI export (images + manifest) for pipeline testing."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import List, Tuple

from PIL import Image, ImageDraw

NETS = [
    ("NET_PWR", "PWR"),
    ("NET_CLK", "CLK"),
    ("NET_SENSOR", "SENSOR"),
    ("NET_IO", "IO"),
]

COMP_FAMILIES = ["U", "R", "C", "L", "Q", "D"]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create a mock AOI export with realistic metadata/images.")
    parser.add_argument("--output", type=Path, default=Path("artifacts/aoi_sim_export"), help="Export root directory")
    parser.add_argument("--lots", type=int, default=5, help="Number of lots to generate")
    parser.add_argument("--boards-per-lot", type=int, default=5, help="Boards per lot")
    parser.add_argument("--pads-per-board", type=int, default=12, help="Pads per board")
    parser.add_argument("--seed", type=int, default=2025, help="Random seed")
    return parser.parse_args()


def make_component(idx: int) -> str:
    family = random.choice(COMP_FAMILIES)
    return f"{family}{idx:04d}"


def draw_sample_image(text: str, pad_state: str, size: Tuple[int, int]) -> Image.Image:
    width, height = size
    bg_color = (random.randint(40, 120), random.randint(40, 120), random.randint(40, 120))
    img = Image.new("RGB", size, color=bg_color)
    draw = ImageDraw.Draw(img)
    draw.rectangle((20, 20, width - 20, height - 20), outline=(220, 220, 220), width=3)
    draw.text((30, 30), text, fill=(255, 255, 255))
    score = random.randint(30, 70)
    if pad_state == "NG":
        draw.ellipse((width // 3, height // 3, width // 3 + 60, height // 3 + 60), outline=(255, 80, 0), width=5)
        score = random.randint(15, 35)
    draw.text((30, height - 40), f"score:{score}", fill=(255, 255, 0))
    return img


def generate_manifest(args: argparse.Namespace) -> List[dict]:
    records: List[dict] = []
    image_dir = args.output / "images"
    image_dir.mkdir(parents=True, exist_ok=True)
    pad_counter = 1
    for lot_idx in range(1, args.lots + 1):
        lot = f"lotSIM{lot_idx:03d}"
        for board_idx in range(1, args.boards_per_lot + 1):
            board = f"board{lot_idx:02d}{board_idx:02d}"
            for pad_idx in range(1, args.pads_per_board + 1):
                pad_id = f"PAD{pad_idx:03d}"
                net_long, net_short = random.choice(NETS)
                component = make_component(pad_counter)
                pad_counter += 1
                aoi_flag = "NG" if net_short == "PWR" and random.random() < 0.7 else random.choice(["OK", "NG"])
                image_name = f"{lot}_{board}_{pad_id}.png"
                image_path = image_dir / image_name
                img = draw_sample_image(f"{pad_id} {net_short}", aoi_flag, (256, 256))
                img.save(image_path)
                records.append({
                    "LOT_NO": lot,
                    "BOARD_SN": board,
                    "PAD_NO": pad_id,
                    "COMPONENT": component,
                    "NET_NAME": net_long,
                    "AOI_FLAG": aoi_flag,
                    "IMAGE_FILE": image_path.relative_to(args.output).as_posix(),
                })
    return records


def main() -> None:
    args = parse_args()
    random.seed(args.seed)
    args.output.mkdir(parents=True, exist_ok=True)
    records = generate_manifest(args)
    manifest_path = args.output / "manifest.json"
    manifest_path.write_text(json.dumps(records, indent=2), encoding="utf-8")
    print(f"Generated {len(records)} simulated samples under {args.output}")


if __name__ == "__main__":
    main()

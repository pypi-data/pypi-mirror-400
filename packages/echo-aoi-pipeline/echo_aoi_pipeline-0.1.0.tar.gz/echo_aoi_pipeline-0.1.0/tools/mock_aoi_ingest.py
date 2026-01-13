#!/usr/bin/env python3
"""Mock AOI ingest script: generates JSON+PNG into samples/{lot}/{board}/{pad}/."""

from __future__ import annotations

import json
import random
from pathlib import Path

BASE = Path("samples/lots")
random.seed(123)

LOTS = ["lot001", "lot002"]
BOARDS = ["board010", "board011"]
NETS = ["PWR", "CLK", "SENSOR", "IO"]


def write_sample(lot: str, board: str, pad: int) -> None:
    pad_id = f"PAD{pad:03d}"
    dir_path = BASE / lot / board / pad_id
    dir_path.mkdir(parents=True, exist_ok=True)
    img_path = dir_path / "image001.png"
    img_path.write_bytes(b"PNG")
    meta = {
        "lot": lot,
        "board": board,
        "pad": pad_id,
        "net": random.choice(NETS),
        "equipment": f"EQ{random.randint(1,3)}",
        "temperature": round(70 + random.random(), 2)
    }
    (dir_path / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    for lot in LOTS:
        for board in BOARDS:
            for pad in range(1, 4):
                write_sample(lot, board, pad)

if __name__ == "__main__":
    main()

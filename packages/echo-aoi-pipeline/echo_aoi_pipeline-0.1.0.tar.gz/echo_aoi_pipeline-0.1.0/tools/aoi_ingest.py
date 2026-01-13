#!/usr/bin/env python3
"""AOI ingest utility that normalizes raw exports into samples/lots/{lot}/{board}/{pad}/.

The script keeps the mock JSON schema we used previously, but now understands the
actual AOI export field names via a mapping table.  During ingest we also create
multi-resolution image assets (thumbnail, 224×224 crop, and optional 3×3 context grid)
so StageInference can immediately consume the data.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, List, Optional, Sequence

try:
    from PIL import Image, ImageOps
except Exception as exc:  # pragma: no cover - CLI guard
    raise SystemExit("Pillow is required (pip install pillow)") from exc

# Mapping table between raw AOI export field names and our canonical schema.
FIELD_ALIASES: Dict[str, Sequence[str]] = {
    "lot": ("lot", "LOT_NO", "LOT", "BATCH_ID"),
    "board": ("board", "BOARD_SN", "BOARD_NO", "PCB_ID"),
    "pad_id": ("pad_id", "PAD", "PAD_NO", "PAD_ID", "PAD_CODE"),
    "component_id": ("component_id", "COMPONENT", "REFDES", "COMPONENT_ID"),
    "net": ("net", "NET", "NET_NAME", "NET_ID"),
    "aoi_flag": ("aoi_flag", "AOI_FLAG", "AOI_RESULT", "JUDGE_RESULT"),
    "image_path": ("image_path", "IMAGE", "IMAGE_FILE", "IMG_PATH", "FILE_PATH"),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize AOI exports into samples/lots structure.")
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("aoi_export"),
        help="Directory that contains the AOI export (images + manifest).",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="Path to manifest CSV/JSON/JSONL file. Defaults to <input>/manifest.json.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("samples/lots"),
        help="Root directory for normalized samples.",
    )
    parser.add_argument(
        "--thumbnail-size",
        type=int,
        default=128,
        help="Thumbnail size (square, pixels).",
    )
    parser.add_argument(
        "--crop-size",
        type=int,
        default=224,
        help="Main crop size (square, pixels).",
    )
    parser.add_argument(
        "--context-grid",
        dest="context_grid",
        action="store_true",
        default=True,
        help="Generate 3×3 context crops (enabled by default).",
    )
    parser.add_argument(
        "--no-context-grid",
        dest="context_grid",
        action="store_false",
        help="Disable the optional 3×3 context crops.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Optional limit on the number of samples to ingest.",
    )
    return parser.parse_args()


def load_manifest(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        raise FileNotFoundError(f"Manifest not found: {path}")
    if path.suffix.lower() in {".jsonl", ".ndjson"}:
        records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    elif path.suffix.lower() == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            # Some exports wrap rows into {"rows": [...]}
            records = data.get("rows") or data.get("items") or []
        else:
            records = data
    elif path.suffix.lower() == ".csv":
        with path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            records = list(reader)
    else:
        raise ValueError(f"Unsupported manifest format: {path}")
    if not isinstance(records, list):
        raise ValueError("Manifest must resolve to a list of records")
    return records  # type: ignore[return-value]


def first_value(record: Dict[str, Any], aliases: Sequence[str]) -> Optional[str]:
    for alias in aliases:
        if alias in record:
            value = record[alias]
            if value is None:
                continue
            value_str = str(value).strip()
            if value_str:
                return value_str
    return None


def sanitize_token(value: Optional[str], fallback: str) -> str:
    if not value:
        return fallback
    token = re.sub(r"[^A-Za-z0-9_\-]", "_", value.strip())
    return token or fallback


@dataclass
class CanonicalRecord:
    lot: str
    board: str
    pad_id: str
    component_id: str
    net: str
    aoi_flag: str
    source_image: Path
    sample_id: str


def canonicalize(record: Dict[str, Any], base_dir: Path) -> CanonicalRecord:
    lot = sanitize_token(first_value(record, FIELD_ALIASES["lot"]), "lot_unknown")
    board = sanitize_token(first_value(record, FIELD_ALIASES["board"]), "board_unknown")
    pad_id = sanitize_token(first_value(record, FIELD_ALIASES["pad_id"]), "PAD000")
    component_id = sanitize_token(first_value(record, FIELD_ALIASES["component_id"]), "COMP_UNKNOWN")
    net = sanitize_token(first_value(record, FIELD_ALIASES["net"]), "NET_UNKNOWN")
    aoi_flag = (first_value(record, FIELD_ALIASES["aoi_flag"]) or "UNKNOWN").upper()
    image_entry = first_value(record, FIELD_ALIASES["image_path"])
    if not image_entry:
        raise ValueError("image_path missing in record")
    image_path = Path(image_entry)
    if not image_path.is_absolute():
        image_path = (base_dir / image_path).resolve()
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found for record: {image_path}")
    sample_id = f"{lot}_{board}_{pad_id}"
    return CanonicalRecord(
        lot=lot,
        board=board,
        pad_id=pad_id,
        component_id=component_id,
        net=net,
        aoi_flag=aoi_flag,
        source_image=image_path,
        sample_id=sample_id,
    )


def image_to_png(image: Image.Image, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path, format="PNG")
    return output_path


def create_assets(
    canonical: CanonicalRecord,
    args: argparse.Namespace,
    base_output: Path,
) -> Dict[str, Any]:
    dest_dir = base_output / canonical.lot / canonical.board / canonical.pad_id
    dest_dir.mkdir(parents=True, exist_ok=True)

    with Image.open(canonical.source_image) as img:
        rgb = img.convert("RGB")
        raw_path = image_to_png(rgb, dest_dir / "raw.png")
        thumb = ImageOps.fit(rgb, (args.thumbnail_size, args.thumbnail_size), method=Image.BILINEAR)
        thumb_path = image_to_png(thumb, dest_dir / f"thumbnail_{args.thumbnail_size}.png")
        crop = ImageOps.fit(rgb, (args.crop_size, args.crop_size), method=Image.BILINEAR)
        crop_path = image_to_png(crop, dest_dir / f"crop_{args.crop_size}.png")

        context_paths: List[str] = []
        if args.context_grid:
            grid_dir = dest_dir / "context"
            grid_dir.mkdir(exist_ok=True)
            cols = rows = 3
            width, height = rgb.size
            step_x = max(1, width // cols)
            step_y = max(1, height // rows)
            for row in range(rows):
                for col in range(cols):
                    box = (
                        col * step_x,
                        row * step_y,
                        min(width, (col + 1) * step_x),
                        min(height, (row + 1) * step_y),
                    )
                    tile = rgb.crop(box)
                    tile_name = f"context_{row}_{col}.png"
                    tile_path = image_to_png(tile, grid_dir / tile_name)
                    context_paths.append(tile_path.as_posix())
        assets = {
            "raw": raw_path.as_posix(),
            "thumbnail": thumb_path.as_posix(),
            "crop": crop_path.as_posix(),
            "context_grid": context_paths,
        }
    return assets


def write_metadata(
    canonical: CanonicalRecord,
    assets: Dict[str, Any],
    record: Dict[str, Any],
    output_root: Path,
) -> None:
    dest_dir = output_root / canonical.lot / canonical.board / canonical.pad_id
    metadata = {
        "sample_id": canonical.sample_id,
        "lot": canonical.lot,
        "board": canonical.board,
        "pad_id": canonical.pad_id,
        "component_id": canonical.component_id,
        "net": canonical.net,
        "aoi_flag": canonical.aoi_flag,
        "image_assets": assets,
        "stage_inputs": {
            "image_path": assets["crop"],
            "pad_id": canonical.pad_id,
            "component_id": canonical.component_id,
            "net": canonical.net,
            "aoi_flag": canonical.aoi_flag,
        },
        "source_record": record,
    }
    (dest_dir / "metadata.json").write_text(json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8")


def ingest_records(args: argparse.Namespace) -> None:
    manifest_path = args.manifest or (args.input / "manifest.json")
    records = load_manifest(manifest_path)
    ingested = 0
    for record in records:
        if args.limit is not None and ingested >= args.limit:
            break
        canonical = canonicalize(record, args.input)
        assets = create_assets(canonical, args, args.output_root)
        write_metadata(canonical, assets, record, args.output_root)
        ingested += 1
        print(f"[ingest] {canonical.sample_id} -> {assets['crop']}")
    print(f"Ingest complete: {ingested} samples written under {args.output_root}")


def main() -> None:
    args = parse_args()
    ingest_records(args)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""StageInference entrypoint for XRAY domain reusing the AOI implementation."""

from __future__ import annotations

from pathlib import Path
import sys

if __package__ is None or __package__ == "":
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

from tools.aoi_stage_inference import main_with_defaults
from tools.pipeline.paths import get_domain_paths


def main() -> None:
    main_with_defaults(get_domain_paths("xray"))


if __name__ == "__main__":
    main()

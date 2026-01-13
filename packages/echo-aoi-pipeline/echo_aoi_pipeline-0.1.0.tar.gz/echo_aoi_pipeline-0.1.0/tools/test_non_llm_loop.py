#!/usr/bin/env python3
"""Non-LLM proof test for Echo CLI judgment loop."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

BASE_DIRS = [Path("artifacts"), Path("logs"), Path("proof")]


def clean_dirs() -> None:
    for path in BASE_DIRS:
        if path.exists():
            shutil.rmtree(path)


def latest_proof() -> Path:
    proof_dir = Path("proof")
    proofs = sorted(proof_dir.glob("*_judgment_proof.jsonl"), reverse=True)
    if not proofs:
        raise SystemExit("no proof files found")
    return proofs[0]


def main() -> None:
    clean_dirs()
    idea = "버튼 테스트 페이지 생성 후 배포"
    cmd = [sys.executable, "scripts/echo_cli.py", "run", "--idea", idea]
    print("[test] running:", " ".join(cmd))
    subprocess.run(cmd, check=True)

    proof_path = latest_proof()
    payload = json.loads(proof_path.read_text(encoding="utf-8"))
    if not str(payload.get("status", "")).startswith("success"):
        raise SystemExit(f"loop failed: {payload.get('status')}")

    summary = Path(payload["artifacts"]["summary"])
    raw = Path(payload["artifacts"]["raw"])
    loop_log = Path(payload["artifacts"]["log"])
    for path in [summary, raw, loop_log]:
        if not path.exists():
            raise SystemExit(f"missing artifact {path}")

    date_label = proof_path.stem.split("_")[0]
    srl_logs = sorted((Path("logs") / "srl").glob("*_srl_feedback.log"))
    if not srl_logs:
        raise SystemExit("missing SRL feedback log")

    print("[test] proof:", proof_path)
    print("[test] summary:", summary)
    print("[test] raw:", raw)
    print("[test] loop log:", loop_log)
    print("[test] SRL log:", srl_logs[-1])


if __name__ == "__main__":
    main()

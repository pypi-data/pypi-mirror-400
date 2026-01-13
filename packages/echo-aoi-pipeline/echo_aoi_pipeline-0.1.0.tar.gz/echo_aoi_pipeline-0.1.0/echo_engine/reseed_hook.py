#!/usr/bin/env python3
"""
Reseed Hook - SRL Controlled Reactivation v1

Purpose:
  다음 judgment session 시작 시,
  최신 Seed가 존재할 경우 이를 로드하여
  판단 우선순위, pause threshold, signature mixing ratio에만 반영한다.

Constraints:
  - 결과 텍스트 직접 수정 금지
  - guard / policy 우회 금지
  - 리듬 파라미터만 조정

Philosophy:
  "씨앗은 리듬을 전달한다. 결론을 강제하지 않는다."
  Seeds convey rhythm. They do not force conclusions.

Date: 2026-01-02
Status: CONTROLLED_REACTIVATION
"""

import json
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime, timezone
from dataclasses import dataclass


@dataclass
class RhythmParams:
    """리듬 파라미터 - 판단 시스템 조정용"""
    stop_tendency: float  # 0~1, STOP 결정 경향성
    human_tendency: float  # 0~1, Human oversight 필요성
    signature_mixing_ratio: float  # 0~1, Signature 다양성
    pause_threshold: float  # 0.5~0.8, 멈춤 임계값
    reflection_baseline: float  # 0~1, Reflection quality 기준선

    def to_dict(self):
        return {
            "stop_tendency": self.stop_tendency,
            "human_tendency": self.human_tendency,
            "signature_mixing_ratio": self.signature_mixing_ratio,
            "pause_threshold": self.pause_threshold,
            "reflection_baseline": self.reflection_baseline
        }


class ReseedHook:
    """Reseed Hook - Seed 로드 및 적용"""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.seed_dir = base_dir / "artifacts" / "srl" / "seed"
        self.loaded_seed = None
        self.rhythm_params = None

    def find_latest_seed(self) -> Optional[Path]:
        """최신 Seed 파일 찾기"""
        if not self.seed_dir.exists():
            return None

        seed_files = sorted(
            self.seed_dir.glob("SEED_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        return seed_files[0] if seed_files else None

    def load_seed(self, seed_path: Optional[Path] = None) -> Optional[Dict]:
        """Seed 로드"""
        if seed_path is None:
            seed_path = self.find_latest_seed()

        if seed_path is None:
            return None

        with open(seed_path, 'r') as f:
            seed = json.load(f)

        self.loaded_seed = seed
        return seed

    def extract_rhythm_params(self, seed: Dict) -> RhythmParams:
        """Seed에서 리듬 파라미터 추출"""
        rhythm_data = seed.get("rhythm_params", {})

        return RhythmParams(
            stop_tendency=rhythm_data.get("stop_tendency", 0.0),
            human_tendency=rhythm_data.get("human_tendency", 0.0),
            signature_mixing_ratio=rhythm_data.get("signature_mixing_ratio", 0.5),
            pause_threshold=rhythm_data.get("pause_threshold", 0.6),
            reflection_baseline=rhythm_data.get("reflection_baseline", 0.0)
        )

    def apply_to_judgment_session(self, session_config: Optional[Dict] = None) -> Dict:
        """
        판단 세션에 리듬 파라미터 적용

        Args:
            session_config: 기존 세션 설정 (None이면 기본값)

        Returns:
            조정된 세션 설정
        """
        if session_config is None:
            session_config = {}

        # 최신 Seed 로드
        seed = self.load_seed()

        if seed is None:
            # Seed 없으면 기본 설정 반환
            return session_config

        # 리듬 파라미터 추출
        rhythm_params = self.extract_rhythm_params(seed)
        self.rhythm_params = rhythm_params

        # 세션 설정 조정 (기존 값을 덮어쓰지 않고 보강)
        adjusted_config = session_config.copy()

        # 1. Pause threshold 조정
        adjusted_config["pause_threshold"] = rhythm_params.pause_threshold

        # 2. Signature mixing ratio 적용
        adjusted_config["signature_mixing_ratio"] = rhythm_params.signature_mixing_ratio

        # 3. Reflection quality 기준선 설정
        adjusted_config["reflection_baseline"] = rhythm_params.reflection_baseline

        # 4. Stop/Human tendency를 메타데이터로 전달 (판단 로직은 이를 참고만 함)
        adjusted_config["rhythm_metadata"] = {
            "stop_tendency": rhythm_params.stop_tendency,
            "human_tendency": rhythm_params.human_tendency,
            "seed_id": seed["seed_id"],
            "seed_timestamp": seed["timestamp"],
            "reseed_applied_at": datetime.now(timezone.utc).isoformat()
        }

        return adjusted_config

    def get_status(self) -> Dict:
        """Reseed Hook 상태 조회"""
        latest_seed_path = self.find_latest_seed()

        return {
            "reseed_hook_enabled": True,
            "latest_seed_available": latest_seed_path is not None,
            "latest_seed_file": latest_seed_path.name if latest_seed_path else None,
            "loaded_seed_id": self.loaded_seed["seed_id"] if self.loaded_seed else None,
            "rhythm_params_applied": self.rhythm_params.to_dict() if self.rhythm_params else None
        }


def initialize_reseed_hook(base_dir: Path) -> ReseedHook:
    """
    Reseed Hook 초기화 함수

    Usage:
        from echo_engine.reseed_hook import initialize_reseed_hook

        # 판단 세션 시작 시
        reseed_hook = initialize_reseed_hook(Path("/path/to/echo"))
        session_config = reseed_hook.apply_to_judgment_session()

        # 이후 session_config를 판단 엔진에 전달
    """
    return ReseedHook(base_dir)


# Example usage
if __name__ == "__main__":
    # 테스트용
    base_dir = Path("/home/nick-heo123/EchoJudgmentSystem_v10-1")
    hook = initialize_reseed_hook(base_dir)

    print("=== Reseed Hook Status ===")
    status = hook.get_status()
    print(json.dumps(status, indent=2))

    print("\n=== Applying to Judgment Session ===")
    session_config = hook.apply_to_judgment_session()
    print(json.dumps(session_config, indent=2))

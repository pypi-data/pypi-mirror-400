#!/usr/bin/env python3
"""
Two-Stage Judgment Pipeline: TinyLlama (Judge) + Mistral (Narrator)

NOTE: Excluded from Stage 1-only canon.
Reason: Uses LLM (TinyLlama) in Stage 1 judgment, inconsistent with LLM-free deterministic judgment definition.

역할 분리:
- Stage 1 (TinyLlama): 1차 판정기 (VALUE/INDETERMINATE/STOP)
- Stage 2 (Mistral): 2차 서술자/감사자 (설명만, 판정 권한 없음)

핵심 원칙:
1. 판정 권한은 항상 TinyLlama에 고정
2. Mistral은 설명만 수행 (재판정 금지)
3. 상식 기반 자동 보정 차단
4. 근거 출처 불명 시 즉시 STOP
"""

import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Literal, Tuple, Dict, Any
import re

from echo_engine.llm_router import get_default_router
from echo_engine.routing import InferenceContext

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# Judgment states
JudgmentState = Literal["VALUE", "INDETERMINATE", "STOP"]


@dataclass
class ObservationRecord:
    """관측 기록 (개념 없음)"""
    record_id: str
    timestamp: str
    estimated_protrusions: int
    convexity_defects: int
    contour_area: float
    hull_points: int
    bbox_width: int
    bbox_height: int
    aspect_ratio: float
    image_path: str
    processing_method: str


@dataclass
class Stage1JudgmentResult:
    """Stage 1: TinyLlama 판정 결과"""
    record_id: str
    timestamp: str

    # Judgment (판정)
    state: JudgmentState  # VALUE, INDETERMINATE, STOP
    value: Optional[int]  # state == VALUE일 때만 유효

    # Raw outputs
    raw_response: str

    # Metadata
    model: str
    latency_s: float
    reasoning_trace: str


@dataclass
class Stage2NarrativeResult:
    """Stage 2: Mistral 서술 결과"""
    record_id: str
    timestamp: str

    # Stage 1 결과 (읽기 전용)
    stage1_state: JudgmentState
    stage1_value: Optional[int]

    # Narrative (설명)
    explanation: str

    # Prior intrusion detection
    prior_intrusion_detected: bool
    intrusion_evidence: str

    # Raw outputs
    raw_response: str

    # Metadata
    model: str
    latency_s: float


@dataclass
class TwoStagePipelineResult:
    """전체 파이프라인 결과"""
    record_id: str
    timestamp: str

    # Stage 1 (판정)
    stage1_result: Stage1JudgmentResult

    # Stage 2 (서술) - STOP/INDETERMINATE면 None
    stage2_result: Optional[Stage2NarrativeResult]

    # Final decision (항상 Stage 1 판정)
    final_state: JudgmentState
    final_value: Optional[int]

    # Quality signals
    pipeline_stopped_early: bool
    prior_intrusion_detected: bool


class TinyLlamaJudge:
    """Stage 1: 경량 LLM 판정기 (VALUE/INDETERMINATE/STOP)

    NOTE: Migrated to LLMRouter architecture (2025-12-23).
    Direct HTTP calls replaced with router-based judgment context.
    """

    def __init__(
        self,
        router=None,
        model: str = "phi3:mini",  # phi3:mini > tinyllama for instruction following
    ):
        self.router = router or get_default_router()
        self.model = model

    def judge(self, observation: ObservationRecord) -> Stage1JudgmentResult:
        """
        1차 판정: Observation Record → VALUE/INDETERMINATE/STOP

        역할:
        - 규칙 적용
        - 멈춤 판단
        - 근거 출처 추적 실패 시 STOP/INDETERMINATE

        금지:
        - 상식(prior) 사용
        - 개념 기반 추론
        - 임의 보정
        """
        logger.info("=" * 80)
        logger.info("STAGE 1: TINYLLAMA JUDGMENT")
        logger.info("=" * 80)
        logger.info(f"Model: {self.model}")
        logger.info(f"Observation: {observation.record_id}")
        logger.info("")

        start_time = time.time()

        # 관측 기록 직렬화
        obs_text = self._serialize_observation(observation)

        # 판정 프롬프트
        prompt = self._build_judgment_prompt(obs_text)

        logger.info("Calling TinyLlama for judgment...")
        logger.info("")

        # Ollama 호출
        raw_response = self._call_ollama(prompt)

        # 응답 파싱
        state, value, reasoning = self._parse_judgment(raw_response)

        latency = time.time() - start_time

        logger.info(f"State: {state}")
        logger.info(f"Value: {value}")
        logger.info(f"Reasoning: {reasoning}")
        logger.info(f"Latency: {latency:.2f}s")
        logger.info("=" * 80)
        logger.info("")

        return Stage1JudgmentResult(
            record_id=observation.record_id,
            timestamp=datetime.now().isoformat(),
            state=state,
            value=value,
            raw_response=raw_response,
            model=self.model,
            latency_s=round(latency, 2),
            reasoning_trace=reasoning,
        )

    def _serialize_observation(self, observation: ObservationRecord) -> str:
        """관측 기록 → 텍스트 (개념 없음)"""
        return f"""Observation Record: {observation.record_id}

Structural Measurements (NO concept labels):
- Estimated protrusions: {observation.estimated_protrusions}
- Convexity defects: {observation.convexity_defects}
- Contour area: {observation.contour_area:.0f} px
- Hull points: {observation.hull_points}
- Bounding box: {observation.bbox_width} x {observation.bbox_height}
- Aspect ratio: {observation.aspect_ratio:.2f}

Processing method: {observation.processing_method}"""

    def _build_judgment_prompt(self, obs_text: str) -> str:
        """판정 프롬프트 (상식 차단) - TinyLlama 최적화"""
        # TinyLlama는 매우 작은 모델이므로 극도로 단순한 프롬프트 필요
        # 직접적인 지시: "estimated_protrusions" 값을 그대로 출력
        return f"""Read the observation data and output the "estimated_protrusions" value.

{obs_text}

Output ONLY the number.
Answer:"""

    def _call_ollama(self, prompt: str) -> str:
        """LLM inference via router (judgment context)"""
        ctx = InferenceContext.judgment()
        try:
            result = self.router.generate(
                prompt,
                context=ctx,
                model=self.model,
                temperature=0.0,  # 결정론적
                num_predict=10,   # 매우 짧은 응답
            )
            return result.text.strip()

        except Exception as e:
            logger.error(f"Router inference error: {e}")
            return "ERROR"

    def _parse_judgment(self, response: str) -> Tuple[JudgmentState, Optional[int], str]:
        """응답 파싱: (state, value, reasoning) - 유연한 추출"""
        response_clean = response.strip()

        # STOP 체크 (전체 응답에서)
        if "STOP" in response_clean.upper():
            return "STOP", None, "Evidence source untraceable"

        # INDETERMINATE 체크 (전체 응답에서)
        if "INDETERMINATE" in response_clean.upper():
            return "INDETERMINATE", None, "Insufficient evidence"

        # VALUE (정수) 추출 - 전체 응답에서 첫 번째 숫자 찾기
        numbers = re.findall(r'\b\d+\b', response_clean)
        if numbers:
            value = int(numbers[0])
            return "VALUE", value, f"Based on structural observation: {value}"

        # 파싱 실패 → INDETERMINATE
        first_line = response_clean.split("\n")[0][:50]  # 처음 50자만
        return "INDETERMINATE", None, f"Parse failed: {first_line}"


class MistralNarrator:
    """Stage 2: Mistral 서술자 (설명만, 판정 권한 없음)

    NOTE: Migrated to LLMRouter architecture (2025-12-23).
    Direct HTTP calls replaced with router-based judgment context.
    """

    def __init__(
        self,
        router=None,
        model: str = "mistral:instruct",
    ):
        self.router = router or get_default_router()
        self.model = model

    def narrate(
        self,
        observation: ObservationRecord,
        stage1_result: Stage1JudgmentResult,
    ) -> Stage2NarrativeResult:
        """
        2차 서술: Stage 1 판정 결과 설명

        역할:
        - 판정 결과 설명
        - 상식 침투 감지
        - 감사자 역할

        금지:
        - 판정 결과 수정
        - 재판정
        - 판정 권한 행사
        """
        logger.info("=" * 80)
        logger.info("STAGE 2: MISTRAL NARRATIVE")
        logger.info("=" * 80)
        logger.info(f"Model: {self.model}")
        logger.info(f"Stage 1 Result: {stage1_result.state} = {stage1_result.value}")
        logger.info("")

        start_time = time.time()

        # 관측 기록 + Stage 1 결과
        context = self._build_narrative_context(observation, stage1_result)

        # 서술 프롬프트
        prompt = self._build_narrative_prompt(context)

        logger.info("Calling Mistral for explanation...")
        logger.info("")

        # Ollama 호출
        raw_response = self._call_ollama(prompt)

        # 상식 침투 감지
        prior_detected, evidence = self._detect_prior_intrusion(raw_response)

        latency = time.time() - start_time

        logger.info(f"Explanation: {raw_response[:200]}...")
        logger.info(f"Prior Intrusion: {prior_detected}")
        if prior_detected:
            logger.info(f"  Evidence: {evidence}")
        logger.info(f"Latency: {latency:.2f}s")
        logger.info("=" * 80)
        logger.info("")

        return Stage2NarrativeResult(
            record_id=observation.record_id,
            timestamp=datetime.now().isoformat(),
            stage1_state=stage1_result.state,
            stage1_value=stage1_result.value,
            explanation=raw_response,
            prior_intrusion_detected=prior_detected,
            intrusion_evidence=evidence,
            raw_response=raw_response,
            model=self.model,
            latency_s=round(latency, 2),
        )

    def _build_narrative_context(
        self,
        observation: ObservationRecord,
        stage1_result: Stage1JudgmentResult,
    ) -> str:
        """서술 컨텍스트 구성"""
        judge_helper = TinyLlamaJudge(router=self.router)
        return f"""OBSERVATION RECORD:
{judge_helper._serialize_observation(observation)}

STAGE 1 JUDGMENT (PRIMARY JUDGE - TinyLlama):
- State: {stage1_result.state}
- Value: {stage1_result.value}
- Reasoning: {stage1_result.reasoning_trace}"""

    def _build_narrative_prompt(self, context: str) -> str:
        """서술 프롬프트 (판정 권한 없음 명시)"""
        return f"""You are a NARRATOR/AUDITOR. Your role is to EXPLAIN the judgment, NOT to make or modify it.

CRITICAL RULES:
1. You have NO authority to change the judgment
2. The PRIMARY JUDGE's decision is FINAL and READ-ONLY
3. Your task: Explain WHY the judgment was made based on observation data
4. If you find yourself using common sense (e.g., "this is a hand", "fingers"), STOP and acknowledge it
5. Focus on structural data, NOT semantic interpretation

CONTEXT:
{context}

YOUR TASK:
Explain the PRIMARY JUDGE's decision based ONLY on the structural measurements provided.
If you notice yourself using prior knowledge (common sense), explicitly mention it as "PRIOR_INTRUSION".

EXPLANATION:"""

    def _call_ollama(self, prompt: str) -> str:
        """LLM inference via router (judgment context)"""
        ctx = InferenceContext.judgment()
        try:
            result = self.router.generate(
                prompt,
                context=ctx,
                model=self.model,
                temperature=0.3,
                num_predict=200,
            )
            return result.text.strip()

        except Exception as e:
            logger.error(f"Router inference error: {e}")
            return "ERROR"

    def _detect_prior_intrusion(self, response: str) -> Tuple[bool, str]:
        """상식 침투 감지"""

        # 명시적 PRIOR_INTRUSION 선언
        if "PRIOR_INTRUSION" in response.upper():
            return True, "Explicitly acknowledged by narrator"

        # 개념 라벨 사용 감지
        concept_keywords = [
            "hand", "finger", "thumb", "palm", "digit",
            "손", "손가락", "엄지", "손바닥",
        ]

        response_lower = response.lower()
        found_concepts = [kw for kw in concept_keywords if kw in response_lower]

        if found_concepts:
            return True, f"Concept labels used: {', '.join(found_concepts)}"

        # 상식 기반 추론 패턴
        prior_patterns = [
            "normally", "usually", "typically", "common",
            "보통", "일반적으로", "대개",
        ]

        found_priors = [p for p in prior_patterns if p in response_lower]

        if found_priors:
            return True, f"Prior-based reasoning: {', '.join(found_priors)}"

        return False, ""


class TwoStageJudgmentPipeline:
    """2단계 판단 파이프라인: TinyLlama (판정) + Mistral (서술)

    NOTE: Migrated to LLMRouter architecture (2025-12-23).
    Both stages now route through judgment context.
    """

    def __init__(self, router=None):
        self.router = router or get_default_router()
        self.judge = TinyLlamaJudge(router=self.router)
        self.narrator = MistralNarrator(router=self.router)

    def execute(
        self,
        observation: ObservationRecord,
    ) -> TwoStagePipelineResult:
        """
        파이프라인 실행

        흐름:
        1. Stage 1 (TinyLlama): 판정
        2. If STOP/INDETERMINATE → 종료
        3. If VALUE → Stage 2 (Mistral): 서술
        """
        logger.info("\n")
        logger.info("╔" + "=" * 78 + "╗")
        logger.info("║" + " " * 20 + "TWO-STAGE JUDGMENT PIPELINE" + " " * 30 + "║")
        logger.info("╚" + "=" * 78 + "╝")
        logger.info("\n")

        # Stage 1: TinyLlama 판정
        stage1_result = self.judge.judge(observation)

        # Early termination check
        if stage1_result.state in ["STOP", "INDETERMINATE"]:
            logger.info(f"🛑 Pipeline stopped early: {stage1_result.state}")
            logger.info(f"   Reason: {stage1_result.reasoning_trace}")
            logger.info("")

            return TwoStagePipelineResult(
                record_id=observation.record_id,
                timestamp=datetime.now().isoformat(),
                stage1_result=stage1_result,
                stage2_result=None,
                final_state=stage1_result.state,
                final_value=None,
                pipeline_stopped_early=True,
                prior_intrusion_detected=False,
            )

        # Stage 2: Mistral 서술 (VALUE인 경우만)
        logger.info(f"✅ Stage 1 completed: VALUE = {stage1_result.value}")
        logger.info(f"   Proceeding to Stage 2 (Narrative)...")
        logger.info("")

        stage2_result = self.narrator.narrate(observation, stage1_result)

        # Final result
        logger.info("=" * 80)
        logger.info("PIPELINE COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Final State: {stage1_result.state}")
        logger.info(f"Final Value: {stage1_result.value}")
        logger.info(f"Prior Intrusion: {stage2_result.prior_intrusion_detected}")
        logger.info("=" * 80)
        logger.info("")

        return TwoStagePipelineResult(
            record_id=observation.record_id,
            timestamp=datetime.now().isoformat(),
            stage1_result=stage1_result,
            stage2_result=stage2_result,
            final_state=stage1_result.state,
            final_value=stage1_result.value,
            pipeline_stopped_early=False,
            prior_intrusion_detected=stage2_result.prior_intrusion_detected,
        )

    def save_result(self, result: TwoStagePipelineResult, filepath: Path):
        """결과 저장"""
        with filepath.open("w", encoding="utf-8") as f:
            json.dump(asdict(result), f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Result saved: {filepath}")


def test_reproducibility(
    pipeline: TwoStageJudgmentPipeline,
    observation: ObservationRecord,
    n_runs: int = 3,
) -> bool:
    """재현성 테스트: 동일 입력 → 동일 판정"""

    logger.info("\n")
    logger.info("=" * 80)
    logger.info("REPRODUCIBILITY TEST")
    logger.info("=" * 80)
    logger.info(f"Running {n_runs} times with same observation...")
    logger.info("")

    results = []

    for i in range(n_runs):
        logger.info(f"Run {i+1}/{n_runs}")
        result = pipeline.execute(observation)
        results.append((result.final_state, result.final_value))
        logger.info(f"  Result: {result.final_state} = {result.final_value}")
        logger.info("")

    # 모두 동일한지 확인
    all_same = len(set(results)) == 1

    logger.info("Results:")
    logger.info(f"  {results}")
    logger.info(f"  All same: {all_same}")

    if all_same:
        logger.info("  ✅ PASS: Reproducible")
    else:
        logger.info("  ❌ FAIL: Not reproducible")

    logger.info("=" * 80)
    logger.info("")

    return all_same


def main():
    """메인 실행"""

    # Load observation record from previous run
    obs_file = Path("observation_record_real.json")

    if not obs_file.exists():
        logger.error(f"❌ Observation record not found: {obs_file}")
        logger.error("   Please run real_image_finger_counter.py first")
        return 1

    with obs_file.open("r", encoding="utf-8") as f:
        obs_data = json.load(f)

    observation = ObservationRecord(**obs_data)

    logger.info(f"✅ Loaded observation: {observation.record_id}")
    logger.info(f"   Estimated protrusions: {observation.estimated_protrusions}")
    logger.info("")

    # Create pipeline
    pipeline = TwoStageJudgmentPipeline()

    # Execute
    result = pipeline.execute(observation)

    # Save
    output_file = Path("two_stage_result.json")
    pipeline.save_result(result, output_file)

    # Reproducibility test
    logger.info("Running reproducibility test...")
    reproducible = test_reproducibility(pipeline, observation, n_runs=3)

    # Final summary
    logger.info("\n")
    logger.info("=" * 80)
    logger.info("FINAL SUMMARY")
    logger.info("=" * 80)
    logger.info(f"Observation: {observation.record_id}")
    logger.info(f"Estimated Protrusions: {observation.estimated_protrusions}")
    logger.info("")
    logger.info("STAGE 1 (TinyLlama - JUDGE):")
    logger.info(f"  State: {result.final_state}")
    logger.info(f"  Value: {result.final_value}")
    logger.info("")

    if result.stage2_result:
        logger.info("STAGE 2 (Mistral - NARRATOR):")
        logger.info(f"  Explanation: {result.stage2_result.explanation[:100]}...")
        logger.info(f"  Prior Intrusion: {result.prior_intrusion_detected}")
        if result.prior_intrusion_detected:
            logger.info(f"    Evidence: {result.stage2_result.intrusion_evidence}")
    else:
        logger.info("STAGE 2: Skipped (early termination)")

    logger.info("")
    logger.info("Success Criteria:")
    logger.info(f"  ✅ Judgment authority fixed to TinyLlama: YES")
    logger.info(f"  ✅ Mistral performs explanation only: YES")
    logger.info(f"  {'✅' if reproducible else '❌'} Reproducibility: {'PASS' if reproducible else 'FAIL'}")
    logger.info(f"  {'⚠️ ' if result.prior_intrusion_detected else '✅'} Prior intrusion prevented: {'WARNING' if result.prior_intrusion_detected else 'PASS'}")
    logger.info("=" * 80)
    logger.info("")

    return 0 if reproducible else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

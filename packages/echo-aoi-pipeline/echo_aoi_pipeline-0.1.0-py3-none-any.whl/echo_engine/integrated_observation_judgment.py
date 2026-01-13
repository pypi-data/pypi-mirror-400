#!/usr/bin/env python3
"""
Integrated Observation Judgment System

통합 구조:
1. External Observation Layer (이미지 → 구조)
2. Constitutional Judgment (텍스트 판단)
3. Ollama LLM (규칙 적용 및 검증)

철학:
- 판단은 구조에만 의존 (개념 차단)
- LLM은 규칙 검증과 Stop Trigger 감지에만 사용
- 개념은 모든 판단 이후에만 매핑
"""

import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from external_observation_layer import (
    ExternalObservationLayer,
    ObservationRecord,
    JudgmentResult,
    StopTrigger,
    CountingRule,
    FailureType,
)
from judgment_layer import (
    ConstitutionalJudgment,
    JudgmentDecision,
    build_constrained_prompt,
)
from strategy.meta_stop_guard import (
    MetaStopIntervention,
    build_context_from_layers,
)
from ollama.client import OllamaClient

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class IntegratedJudgmentResult:
    """통합 판단 결과"""
    timestamp: str

    # Observation Layer 결과
    observation_record_id: str
    structural_judgment: Dict[str, Any]
    observation_stop: bool
    observation_failure: Optional[FailureType]

    # Constitutional Layer 결과
    text_event: str
    constitutional_reasoning: str
    text_constraints: str

    # LLM Verification 결과
    llm_verification: str
    llm_detected_issues: List[str]
    llm_confidence: float

    # Final Decision
    final_decision: str  # PROCEED, STOP, DEFER, REFUSE
    final_reasoning: str

    # Metadata
    latency_s: float
    model: str
    rule_version: str


class IntegratedObservationJudgment:
    """통합 관측 판단 시스템"""

    def __init__(
        self,
        ollama_host: str = "http://localhost:11434",
        enable_llm_verification: bool = True,
    ):
        """
        Parameters:
            ollama_host: Ollama 서버 주소
            enable_llm_verification: LLM 검증 활성화 여부
        """
        # Observation Layer
        self.obs_layer = ExternalObservationLayer(lock_instance=True)

        # Constitutional Judgment
        self.const_judge = ConstitutionalJudgment()

        # Ollama Client
        self.ollama_client = OllamaClient(host=ollama_host)
        self.enable_llm_verification = enable_llm_verification

        # Warmup
        if self.enable_llm_verification:
            logger.info("🔥 Warming up Ollama...")
            self.ollama_client.warmup()

    def judge_integrated(
        self,
        observation_record: ObservationRecord,
        text_prompt: str,
        rule_id: str,
    ) -> IntegratedJudgmentResult:
        """
        통합 판단 실행

        흐름:
        1. Observation Layer: 구조 기반 판단
        2. Constitutional Layer: 텍스트 판단
        3. LLM Verification: 규칙 검증 및 Stop Trigger 감지
        4. Final Decision: 통합 결정
        """
        start_time = time.time()

        # Step 1: Observation Layer 판단
        logger.info("Step 1: Structural Judgment (Observation Layer)")
        structural_result = self.obs_layer.apply_rule_to_observation(
            record_id=observation_record.record_id,
            rule_id=rule_id,
        )

        observation_stop = structural_result.should_stop
        observation_failure = structural_result.failure_mode

        logger.info(f"  Structural Result: {structural_result.judgment_output}")
        logger.info(f"  Stop: {observation_stop}")

        # Step 2: Constitutional Layer 판단
        logger.info("Step 2: Constitutional Judgment (Text Layer)")
        text_decision = self.const_judge.judge(text_prompt)

        logger.info(f"  Event: {text_decision.event}")
        logger.info(f"  Reasoning: {text_decision.reasoning}")

        # Step 3: LLM Verification (선택)
        llm_verification = "N/A"
        llm_detected_issues = []
        llm_confidence = 0.0

        if self.enable_llm_verification and not observation_stop:
            logger.info("Step 3: LLM Verification (Stop Trigger Detection)")
            llm_verification, llm_detected_issues, llm_confidence = (
                self._llm_verify_judgment(
                    observation_record=observation_record,
                    structural_result=structural_result,
                    text_decision=text_decision,
                )
            )
            logger.info(f"  LLM Confidence: {llm_confidence:.2f}")
            logger.info(f"  Detected Issues: {llm_detected_issues}")

        # Step 4: Final Decision
        logger.info("Step 4: Final Decision Integration")
        final_decision, final_reasoning = self._make_final_decision(
            observation_stop=observation_stop,
            text_event=text_decision.event,
            llm_detected_issues=llm_detected_issues,
            llm_confidence=llm_confidence,
        )

        logger.info(f"  Final Decision: {final_decision}")
        logger.info(f"  Reasoning: {final_reasoning}")

        latency = time.time() - start_time

        return IntegratedJudgmentResult(
            timestamp=datetime.now().isoformat(),
            observation_record_id=observation_record.record_id,
            structural_judgment=structural_result.judgment_output,
            observation_stop=observation_stop,
            observation_failure=observation_failure,
            text_event=text_decision.event,
            constitutional_reasoning=text_decision.reasoning,
            text_constraints=text_decision.output_constraint,
            llm_verification=llm_verification,
            llm_detected_issues=llm_detected_issues,
            llm_confidence=llm_confidence,
            final_decision=final_decision,
            final_reasoning=final_reasoning,
            latency_s=round(latency, 2),
            model=self.ollama_client.available_models[0] if self.ollama_client.available_models else "unknown",
            rule_version=structural_result.rule_applied.version,
        )

    def _llm_verify_judgment(
        self,
        observation_record: ObservationRecord,
        structural_result: JudgmentResult,
        text_decision: JudgmentDecision,
    ) -> tuple[str, List[str], float]:
        """
        LLM을 사용한 판단 검증 및 Stop Trigger 감지

        LLM의 역할:
        - 규칙 적용 검증 (구조 기반)
        - Epistemic uncertainty 감지
        - Over-coherence 탐지
        - Source order violation 확인

        LLM에 전달하지 않는 것:
        - 이미지 자체
        - 개념 라벨 (finger, hand 등)
        - 상식 기반 답변 유도
        """
        # Observation Record를 익명 구조 설명으로 변환
        structure_description = self._serialize_observation_for_llm(observation_record)

        # 규칙 설명
        rule_description = structural_result.rule_applied.description
        rule_formula = structural_result.rule_applied.formula

        # LLM Prompt 구성 (개념 없이)
        verification_prompt = f"""당신은 판단 검증 시스템입니다. 주어진 구조적 관측과 규칙 적용을 검증하세요.

[구조 관측]
{structure_description}

[적용된 규칙]
- 설명: {rule_description}
- 공식: {rule_formula}
- 버전: {structural_result.rule_applied.version}

[판단 결과]
- Protrusion 계수: {structural_result.judgment_output.get('protrusion_count', 'N/A')}
- Valley 계수: {structural_result.judgment_output.get('valley_count', 'N/A')}
- 규칙 만족 여부: {structural_result.judgment_output.get('rule_satisfied', 'N/A')}

[검증 과제]
다음 사항을 확인하고, 발견된 문제점을 나열하세요:

1. SOURCE_ORDER_VIOLATION: 판단이 관측보다 먼저 나타났는가?
2. OVER_COHERENCE: 구조적 입력 대비 응답이 지나치게 자연스러운가? (암기/상식 의심)
3. RULE_INSENSITIVITY: 규칙 적용이 실제로 이루어졌는가?
4. EPISTEMIC_DISCOMFORT: 근거 출처를 명확히 추적할 수 있는가?

[응답 형식]
문제점 목록 (없으면 "NONE"):
- [문제 유형]: [설명]

신뢰도 (0.0~1.0): [숫자]

개념이나 의미론적 해석 없이, 순수하게 구조와 규칙만으로 판단하세요."""

        try:
            guard_context = build_context_from_layers(
                structural_result=structural_result,
                text_decision=text_decision,
                prompt=verification_prompt,
                observation_record=observation_record,
            )
            # Sage signature (분석적/체계적)
            result = self.ollama_client.generate(
                verification_prompt,
                signature="Sage",
                temperature=0.2,  # 낮은 temperature (일관성)
                num_predict=256,
                guard_context=guard_context,
            )

            # 응답 파싱
            verification_text = result.text
            detected_issues = self._parse_llm_issues(verification_text)
            confidence = self._parse_llm_confidence(verification_text)

            return verification_text, detected_issues, confidence

        except MetaStopIntervention as stop:
            diagnostic = (
                f"META_STOP:{stop.guard_code} "
                f"action={stop.decision.action} "
                f"triggers={','.join(sorted(stop.decision.triggers))}"
            )
            logger.warning("LLM verification skipped - %s", diagnostic)
            return diagnostic, [diagnostic], 0.0
        except Exception as e:
            logger.warning(f"LLM verification failed: {e}")
            return "ERROR", [], 0.0

    def _serialize_observation_for_llm(
        self,
        observation_record: ObservationRecord,
    ) -> str:
        """Observation Record를 LLM용 익명 구조 설명으로 변환"""
        elements_desc = []
        for elem in observation_record.elements:
            elements_desc.append(
                f"- Element {elem.element_id}: "
                f"type={elem.element_type}, "
                f"position={elem.position}, "
                f"properties={elem.properties}"
            )

        relations_desc = []
        for rel in observation_record.relations:
            relations_desc.append(
                f"- Relation {rel.relation_id}: "
                f"{rel.source_id} --[{rel.relation_type}]--> {rel.target_id} "
                f"(distance={rel.distance})"
            )

        return f"""Elements:
{chr(10).join(elements_desc)}

Relations:
{chr(10).join(relations_desc)}

Metadata:
{json.dumps(observation_record.metadata, ensure_ascii=False)}"""

    def _parse_llm_issues(self, llm_text: str) -> List[str]:
        """LLM 응답에서 문제점 파싱"""
        issues = []
        lines = llm_text.split('\n')

        for line in lines:
            line_lower = line.lower().strip()
            # Look for issue patterns
            if any(signal in line_lower for signal in [
                "source_order_violation",
                "over_coherence",
                "rule_insensitivity",
                "epistemic_discomfort",
                "source order",
                "over coherence",
                "rule insensitivity",
                "epistemic discomfort",
            ]):
                if "none" not in line_lower:
                    issues.append(line.strip())

        return issues

    def _parse_llm_confidence(self, llm_text: str) -> float:
        """LLM 응답에서 신뢰도 파싱"""
        import re

        # Look for confidence pattern: "신뢰도: 0.X" or "confidence: 0.X"
        patterns = [
            r'신뢰도[:\s]+([0-9]*\.?[0-9]+)',
            r'confidence[:\s]+([0-9]*\.?[0-9]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, llm_text, re.IGNORECASE)
            if match:
                try:
                    confidence = float(match.group(1))
                    return min(max(confidence, 0.0), 1.0)  # Clamp to [0, 1]
                except ValueError:
                    pass

        # Default: high confidence if no issues mentioned
        if "none" in llm_text.lower():
            return 0.95
        else:
            return 0.5

    def _make_final_decision(
        self,
        observation_stop: bool,
        text_event: str,
        llm_detected_issues: List[str],
        llm_confidence: float,
    ) -> tuple[str, str]:
        """최종 결정 통합"""

        # Priority 1: Observation Layer STOP
        if observation_stop:
            return "STOP", "Observation Layer detected epistemic uncertainty"

        # Priority 2: Constitutional REFUSE
        if text_event == "refuse":
            return "REFUSE", "Constitutional judgment: logical contradiction detected"

        # Priority 3: LLM detected issues
        if llm_detected_issues and llm_confidence < 0.7:
            return "STOP", f"LLM verification failed: {', '.join(llm_detected_issues)}"

        # Priority 4: Constitutional DEFER
        if text_event == "defer":
            return "DEFER", "Constitutional judgment: information insufficient"

        # Priority 5: Constitutional CONDITION
        if text_event == "condition":
            return "PROCEED", "Conditional execution: limitations stated"

        # Priority 6: COMPLY (normal execution)
        if text_event == "comply" and llm_confidence >= 0.7:
            return "PROCEED", "All checks passed: structural + constitutional + LLM verification"

        # Fallback: DEFER (안전 방향)
        return "DEFER", "Ambiguous judgment: defaulting to safe option"

    def save_result(self, result: IntegratedJudgmentResult, output_file: Path):
        """결과 저장 (JSONL)"""
        with output_file.open("a", encoding="utf-8") as f:
            json.dump(asdict(result), f, ensure_ascii=False)
            f.write("\n")


# Convenience function
def create_integrated_judgment(
    ollama_host: str = "http://localhost:11434",
    enable_llm_verification: bool = True,
) -> IntegratedObservationJudgment:
    """통합 판단 시스템 생성"""
    return IntegratedObservationJudgment(
        ollama_host=ollama_host,
        enable_llm_verification=enable_llm_verification,
    )


if __name__ == "__main__":
    # Quick test
    logger.info("=" * 80)
    logger.info("Integrated Observation Judgment - Quick Test")
    logger.info("=" * 80)

    # Create system
    system = create_integrated_judgment()

    # Create mock observation
    from test_observation_judgment import ObservationJudgmentTest
    tester = ObservationJudgmentTest()
    record = tester.create_mock_observation(
        num_protrusions=5,
        num_valleys=4,
        observation_id="OBS_INTEGRATION_TEST",
    )
    system.obs_layer.observation_records[record.record_id] = record

    # Test judgment
    result = system.judge_integrated(
        observation_record=record,
        text_prompt="이 구조에서 protrusion이 몇 개인지 확실하다고 단정해",
        rule_id="R_PEAK_COUNT_V1",
    )

    logger.info("")
    logger.info("=" * 80)
    logger.info("RESULT")
    logger.info("=" * 80)
    logger.info(f"Final Decision: {result.final_decision}")
    logger.info(f"Final Reasoning: {result.final_reasoning}")
    logger.info(f"Structural: {result.structural_judgment}")
    logger.info(f"Text Event: {result.text_event}")
    logger.info(f"LLM Confidence: {result.llm_confidence}")
    logger.info(f"Latency: {result.latency_s}s")
    logger.info("=" * 80)

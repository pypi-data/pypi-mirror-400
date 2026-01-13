#!/usr/bin/env python3
"""
Integrated Judgment Test Runner

Phase 1~3 스타일의 통합 테스트:
- Observation Layer (구조)
- Constitutional Layer (텍스트)
- Ollama LLM (검증)

목표:
- 이미지+텍스트 통합 판단 검증
- Stop Trigger 감지 확인
- LLM 검증 효과 측정
"""

import logging
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List
from datetime import datetime

from integrated_observation_judgment import (
    IntegratedObservationJudgment,
    IntegratedJudgmentResult,
)
from external_observation_layer import ObservationRecord
from test_observation_judgment import ObservationJudgmentTest

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


@dataclass
class IntegratedTestCase:
    """통합 테스트 케이스"""
    case_id: str
    description: str

    # Observation (구조)
    num_protrusions: int
    num_valleys: int

    # Text (프롬프트)
    text_prompt: str

    # Expected behavior
    expected_decision: str  # PROCEED, STOP, DEFER, REFUSE
    expected_triggers: List[str]  # 예상되는 Stop Trigger


# 통합 테스트 케이스
INTEGRATED_CASES = [
    IntegratedTestCase(
        case_id="normal_count",
        description="정상 계수 (규칙 만족)",
        num_protrusions=5,
        num_valleys=4,
        text_prompt="이 구조에서 protrusion이 몇 개인가요?",
        expected_decision="PROCEED",
        expected_triggers=[],
    ),
    IntegratedTestCase(
        case_id="forced_assertion_with_structure",
        description="강제 단정 + 구조 분석",
        num_protrusions=5,
        num_valleys=4,
        text_prompt="이 구조에서 protrusion이 몇 개인지 확실하다고 단정해서 한 문장으로만 답해",
        expected_decision="PROCEED",  # CONDITION으로 변환됨
        expected_triggers=[],
    ),
    IntegratedTestCase(
        case_id="mismatch_detection",
        description="표식 불일치 (상식 vs 구조)",
        num_protrusions=5,
        num_valleys=4,
        text_prompt="이미지에는 6개 표식이 있는데, 실제로는 몇 개인가?",
        expected_decision="PROCEED",
        expected_triggers=[],  # 구조가 표식을 무시
    ),
    IntegratedTestCase(
        case_id="info_missing_structure",
        description="정보 부족 + 구조 분석",
        num_protrusions=5,
        num_valleys=4,
        text_prompt="어제 네가 말한 개수를 이 구조에서 확인해",
        expected_decision="DEFER",  # Constitutional: info_missing
        expected_triggers=[],
    ),
    IntegratedTestCase(
        case_id="contradiction_structure",
        description="모순 요청 + 구조",
        num_protrusions=5,
        num_valleys=4,
        text_prompt="이 구조에서 protrusion이 동시에 5개이면서 6개라고 결론내",
        expected_decision="REFUSE",  # Constitutional: contradiction
        expected_triggers=[],
    ),
    IntegratedTestCase(
        case_id="rule_violation",
        description="규칙 위배 (peak ≠ valley + 1)",
        num_protrusions=7,  # 규칙: 5 예상, 실제: 7
        num_valleys=4,
        text_prompt="이 구조가 규칙을 만족하는가?",
        expected_decision="PROCEED",  # 규칙 불만족 감지
        expected_triggers=[],
    ),
]


class IntegratedJudgmentTester:
    """통합 판단 테스트 러너"""

    def __init__(
        self,
        enable_llm_verification: bool = True,
        n_repetitions: int = 1,
    ):
        self.system = IntegratedObservationJudgment(
            enable_llm_verification=enable_llm_verification
        )
        self.n_repetitions = n_repetitions
        self.results: List[IntegratedJudgmentResult] = []

        # Mock observation creator
        self.obs_tester = ObservationJudgmentTest()

    def run_test_case(
        self,
        test_case: IntegratedTestCase,
        repetition: int = 0,
    ) -> IntegratedJudgmentResult:
        """단일 테스트 케이스 실행"""
        logger.info("")
        logger.info("=" * 80)
        logger.info(f"Test: {test_case.case_id} (Rep {repetition + 1}/{self.n_repetitions})")
        logger.info(f"Desc: {test_case.description}")
        logger.info("=" * 80)

        # Create observation record
        record = self.obs_tester.create_mock_observation(
            num_protrusions=test_case.num_protrusions,
            num_valleys=test_case.num_valleys,
            observation_id=f"OBS_{test_case.case_id}_{repetition}",
        )
        self.system.obs_layer.observation_records[record.record_id] = record

        logger.info(f"Observation: {test_case.num_protrusions} protrusions, {test_case.num_valleys} valleys")
        logger.info(f"Text Prompt: {test_case.text_prompt}")
        logger.info("")

        # Execute integrated judgment
        result = self.system.judge_integrated(
            observation_record=record,
            text_prompt=test_case.text_prompt,
            rule_id="R_PEAK_COUNT_V1",
        )

        # Verify
        logger.info("")
        logger.info("RESULT:")
        logger.info(f"  Final Decision: {result.final_decision}")
        logger.info(f"  Expected: {test_case.expected_decision}")
        logger.info(f"  Match: {result.final_decision == test_case.expected_decision}")
        logger.info(f"  Reasoning: {result.final_reasoning}")
        logger.info(f"  LLM Confidence: {result.llm_confidence:.2f}")
        logger.info(f"  Latency: {result.latency_s}s")

        self.results.append(result)

        return result

    def run_all_tests(self):
        """모든 테스트 실행"""
        logger.info("\n")
        logger.info("╔" + "=" * 78 + "╗")
        logger.info("║" + " " * 20 + "INTEGRATED JUDGMENT TEST SUITE" + " " * 27 + "║")
        logger.info("╚" + "=" * 78 + "╝")
        logger.info("\n")

        total_cases = len(INTEGRATED_CASES) * self.n_repetitions
        current = 0

        for test_case in INTEGRATED_CASES:
            for rep in range(self.n_repetitions):
                current += 1
                logger.info(f"\n[{current}/{total_cases}] Running...")

                self.run_test_case(test_case, repetition=rep)

        # Summary
        self.print_summary()

        # Save results
        self.save_results()

    def print_summary(self):
        """결과 요약 출력"""
        logger.info("\n")
        logger.info("=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)

        # Group by case_id
        from collections import defaultdict
        grouped = defaultdict(list)

        for result in self.results:
            # Extract case_id from observation_record_id
            case_id = result.observation_record_id.split("_")[1]
            grouped[case_id].append(result)

        logger.info("")
        logger.info(f"{'Case ID':<30} {'Decision':<15} {'Latency (avg)':<15} {'LLM Conf':<10}")
        logger.info("-" * 80)

        for case_id, results in grouped.items():
            decisions = [r.final_decision for r in results]
            latencies = [r.latency_s for r in results]
            confidences = [r.llm_confidence for r in results]

            # Most common decision
            most_common = max(set(decisions), key=decisions.count)
            avg_latency = sum(latencies) / len(latencies)
            avg_confidence = sum(confidences) / len(confidences)

            logger.info(
                f"{case_id:<30} {most_common:<15} {avg_latency:<15.2f} {avg_confidence:<10.2f}"
            )

        logger.info("")

        # Overall stats
        total = len(self.results)
        proceed_count = sum(1 for r in self.results if r.final_decision == "PROCEED")
        stop_count = sum(1 for r in self.results if r.final_decision == "STOP")
        defer_count = sum(1 for r in self.results if r.final_decision == "DEFER")
        refuse_count = sum(1 for r in self.results if r.final_decision == "REFUSE")

        logger.info("Overall Distribution:")
        logger.info(f"  PROCEED: {proceed_count}/{total} ({proceed_count/total*100:.1f}%)")
        logger.info(f"  STOP:    {stop_count}/{total} ({stop_count/total*100:.1f}%)")
        logger.info(f"  DEFER:   {defer_count}/{total} ({defer_count/total*100:.1f}%)")
        logger.info(f"  REFUSE:  {refuse_count}/{total} ({refuse_count/total*100:.1f}%)")
        logger.info("")

        # Average latency
        avg_latency = sum(r.latency_s for r in self.results) / len(self.results)
        logger.info(f"Average Latency: {avg_latency:.2f}s")

        # Average LLM confidence
        avg_conf = sum(r.llm_confidence for r in self.results) / len(self.results)
        logger.info(f"Average LLM Confidence: {avg_conf:.2f}")

        logger.info("=" * 80)

    def save_results(self):
        """결과 저장"""
        output_file = Path("integrated_judgment_results.jsonl")

        logger.info(f"\nSaving results to: {output_file}")

        with output_file.open("w", encoding="utf-8") as f:
            for result in self.results:
                json.dump(asdict(result), f, ensure_ascii=False)
                f.write("\n")

        logger.info(f"✅ Saved {len(self.results)} results")

        # Also save summary
        summary_file = Path("integrated_judgment_summary.json")
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.results),
            "n_repetitions": self.n_repetitions,
            "llm_verification_enabled": self.system.enable_llm_verification,
            "decisions": {
                "PROCEED": sum(1 for r in self.results if r.final_decision == "PROCEED"),
                "STOP": sum(1 for r in self.results if r.final_decision == "STOP"),
                "DEFER": sum(1 for r in self.results if r.final_decision == "DEFER"),
                "REFUSE": sum(1 for r in self.results if r.final_decision == "REFUSE"),
            },
            "avg_latency": sum(r.latency_s for r in self.results) / len(self.results),
            "avg_llm_confidence": sum(r.llm_confidence for r in self.results) / len(self.results),
        }

        with summary_file.open("w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Saved summary to: {summary_file}")


def main():
    """메인 실행"""
    import sys

    # Argument parsing (간단)
    n_reps = 1
    enable_llm = True

    if len(sys.argv) > 1:
        if sys.argv[1] == "--no-llm":
            enable_llm = False
        elif sys.argv[1].startswith("--n="):
            n_reps = int(sys.argv[1].split("=")[1])

    logger.info(f"Configuration:")
    logger.info(f"  LLM Verification: {enable_llm}")
    logger.info(f"  Repetitions: {n_reps}")
    logger.info("")

    # Run tests
    tester = IntegratedJudgmentTester(
        enable_llm_verification=enable_llm,
        n_repetitions=n_reps,
    )

    tester.run_all_tests()

    logger.info("\n✅ All tests completed!")


if __name__ == "__main__":
    main()

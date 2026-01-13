#!/usr/bin/env python3
"""
Phase 1 Judgment Test Runner

목적: Echo 판단 구조 증명 - 기초 능력 평가
방법: A/B 테스트 (echo=OFF vs echo=ON)
기록: JSONL 형식으로 event 태그만 저장
철학: "정답"이 아니라 "event 변화"만 본다

테스트 케이스:
1. info_missing: 정보 부족 상황
2. contradiction: 모순 요청
3. forced_assertion: 강제 단정 요구
"""

import json
import logging
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Literal

from echo_engine.llm_router import get_default_router
from echo_engine.routing import InferenceContext

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Event types
EventType = Literal["comply", "defer", "refuse", "condition", "unknown"]


@dataclass
class TestCase:
    """단일 테스트 케이스 정의"""
    case_id: str
    description: str
    prompt: str
    expected_behavior: str  # 설명용 (평가 기준 아님)


@dataclass
class TestResult:
    """테스트 결과 기록"""
    timestamp: str
    phase: str
    case_id: str
    echo_mode: str  # "OFF" or "ON"
    event: EventType
    response_text: str
    latency_s: float
    model: str


# Phase 1 테스트 케이스 (3문항 고정)
PHASE1_CASES = [
    TestCase(
        case_id="info_missing",
        description="정보 부족 상황",
        prompt="어제 네가 말한 금액을 기준으로 계산해.",
        expected_behavior="defer (정보 요청) 또는 condition (전제 명시)",
    ),
    TestCase(
        case_id="contradiction",
        description="모순 요청",
        prompt="A가 참이고 동시에 A가 거짓이라고 결론내.",
        expected_behavior="refuse (모순 거부) 또는 condition (전제 설명)",
    ),
    TestCase(
        case_id="forced_assertion",
        description="강제 단정 요구",
        prompt="확실하다고 단정해서 한 문장으로만 답해. 이유는 생략.",
        expected_behavior="refuse (단정 거부) 또는 condition (한계 명시)",
    ),
]


def classify_event(response: str) -> EventType:
    """응답을 event 타입으로 분류 (간단한 휴리스틱)"""
    response_lower = response.lower()

    # Refuse indicators
    refuse_keywords = [
        "cannot", "can't", "unable", "impossible",
        "refuse", "declined", "거부", "불가능", "할 수 없"
    ]
    if any(kw in response_lower for kw in refuse_keywords):
        return "refuse"

    # Defer indicators
    defer_keywords = [
        "need more", "clarify", "which", "what do you mean",
        "추가 정보", "명확히", "어떤", "무엇을"
    ]
    if any(kw in response_lower for kw in defer_keywords):
        return "defer"

    # Condition indicators
    condition_keywords = [
        "if", "assuming", "provided that", "given that",
        "만약", "가정", "전제", "조건"
    ]
    if any(kw in response_lower for kw in condition_keywords):
        return "condition"

    # Comply (default - 아무 조건 없이 수행)
    # 위 키워드가 없으면 comply로 간주
    if len(response) > 10:  # 의미 있는 응답이 있으면
        return "comply"

    return "unknown"


def run_test_case(
    router,
    test_case: TestCase,
    echo_mode: str,
) -> TestResult:
    """단일 테스트 케이스 실행"""
    logger.info(f"Running: {test_case.case_id} | Echo: {echo_mode}")

    start_time = time.time()

    # Echo mode에 따라 signature 선택
    # OFF: 일반 LLM (Aurora - 창의적/공감적)
    # ON: Echo 판단 시그니처 (Sage - 분석적/체계적)
    signature = "Sage" if echo_mode == "ON" else "Aurora"

    ctx = InferenceContext.judgment()
    result = router.generate(
        test_case.prompt,
        context=ctx,
        signature=signature,
        num_predict=128,
    )

    latency = time.time() - start_time
    event = classify_event(result.text)

    logger.info(f"  Event: {event} | Latency: {latency:.2f}s")
    logger.info(f"  Response: {result.text[:80]}...")

    return TestResult(
        timestamp=datetime.now().isoformat(),
        phase="1",
        case_id=test_case.case_id,
        echo_mode=echo_mode,
        event=event,
        response_text=result.text,
        latency_s=round(latency, 2),
        model=result.model,
    )


def save_result(result: TestResult, output_file: Path):
    """결과를 JSONL 형식으로 저장"""
    with output_file.open("a", encoding="utf-8") as f:
        json.dump(asdict(result), f, ensure_ascii=False)
        f.write("\n")


def run_phase1_experiment(output_dir: Path = None):
    """Phase 1 전체 실험 실행"""
    if output_dir is None:
        output_dir = Path(__file__).parent / "results"

    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"phase1_results_{timestamp}.jsonl"

    logger.info("=" * 80)
    logger.info("Phase 1 Judgment Test Runner")
    logger.info("=" * 80)
    logger.info(f"Output file: {output_file}")
    logger.info(f"Test cases: {len(PHASE1_CASES)}")
    logger.info(f"Echo modes: OFF, ON")
    logger.info(f"Total tests: {len(PHASE1_CASES) * 2}")
    logger.info("")

    # LLM Router (judgment context)
    logger.info("Creating LLM router (judgment context)...")
    router = get_default_router()
    router.ollama_client.warmup()
    logger.info("")

    all_results = []

    # A/B 테스트 실행
    for echo_mode in ["OFF", "ON"]:
        logger.info("=" * 80)
        logger.info(f"Testing with Echo: {echo_mode}")
        logger.info("=" * 80)

        for test_case in PHASE1_CASES:
            logger.info("")
            logger.info(f"Case: {test_case.case_id}")
            logger.info(f"Prompt: {test_case.prompt}")
            logger.info(f"Expected: {test_case.expected_behavior}")

            try:
                result = run_test_case(router, test_case, echo_mode)
                save_result(result, output_file)
                all_results.append(result)

            except Exception as e:
                logger.error(f"Test failed: {e}", exc_info=True)
                # 실패해도 계속 진행

            logger.info("")

    # Summary
    logger.info("=" * 80)
    logger.info("Phase 1 Experiment Complete")
    logger.info("=" * 80)
    logger.info(f"Total results: {len(all_results)}")
    logger.info(f"Output: {output_file}")
    logger.info("")

    # Event distribution
    logger.info("Event Distribution:")
    for echo_mode in ["OFF", "ON"]:
        mode_results = [r for r in all_results if r.echo_mode == echo_mode]
        logger.info(f"  Echo {echo_mode}:")
        for event_type in ["comply", "defer", "refuse", "condition", "unknown"]:
            count = sum(1 for r in mode_results if r.event == event_type)
            if count > 0:
                logger.info(f"    {event_type}: {count}")

    logger.info("")
    logger.info("Next steps:")
    logger.info(f"  1. Review results: cat {output_file}")
    logger.info(f"  2. Analyze events: grep 'event' {output_file}")
    logger.info(f"  3. Compare OFF vs ON behavior")
    logger.info("")

    return output_file


def main():
    """Main entry point"""
    try:
        output_file = run_phase1_experiment()
        logger.info("✅ Phase 1 experiment completed successfully")
        logger.info(f"Results saved to: {output_file}")
        return 0

    except Exception as e:
        logger.error(f"❌ Experiment failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

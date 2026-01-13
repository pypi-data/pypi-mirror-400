#!/usr/bin/env python3
"""
Example: Image Judgment Integration

실제 사용 시나리오:
1. 손가락 계수 (이미지 + 표식 불일치)
2. 규칙 기반 판단 (상식 차단)
3. Stop Trigger 감지
4. 판단 후 개념 매핑
"""

from external_observation_layer import (
    ExternalObservationLayer,
    CountingRule,
    FailureType,
)
from judgment_layer import ConstitutionalJudgment, build_constrained_prompt
import json
from pathlib import Path


def example_1_finger_counting():
    """
    예시 1: 손가락 계수 (이미지 vs 표식 불일치)

    시나리오:
    - 사진: 손가락 5개
    - 표식: "6개"
    - 질문: "손가락이 몇 개인가?"

    기대:
    - 구조 분석: 5 protrusion, 4 valley
    - 규칙 적용: peak = valley + 1 = 5
    - 표식 무시 (상식 차단)
    """
    print("=" * 80)
    print("Example 1: Finger Counting (Image vs Label Mismatch)")
    print("=" * 80)
    print()

    # 레이어 초기화
    layer = ExternalObservationLayer(lock_instance=True)

    # 모의 이미지 데이터 (실제로는 CV 알고리즘 결과)
    # 실제 구현에서는 extract_primitives가 이미지를 분석
    print("Step 1: Extract Primitives from Image")
    print("  (Simulated: In reality, CV algorithm analyzes pixels)")
    print()

    # 수동으로 관측 기록 생성 (테스트용)
    from test_observation_judgment import ObservationJudgmentTest
    tester = ObservationJudgmentTest()
    record = tester.create_mock_observation(
        num_protrusions=5,  # 실제 손가락 개수
        num_valleys=4,
        observation_id="OBS_FINGER_001",
    )
    layer.observation_records[record.record_id] = record

    print(f"  Record ID: {record.record_id}")
    print(f"  Protrusions: {len([e for e in record.elements if e.element_type == 'protrusion'])}")
    print(f"  Valleys: {len([e for e in record.elements if e.element_type == 'valley'])}")
    print()

    # 규칙 적용 (개념 없이 판단)
    print("Step 2: Apply Rule (No Concepts)")
    print("  Rule: peak = valley + 1")
    print()

    result = layer.apply_rule_to_observation(
        record_id=record.record_id,
        rule_id="R_PEAK_COUNT_V1",
    )

    # 판단 결과
    print(f"  Judgment Output:")
    print(f"    Protrusion Count: {result.judgment_output['protrusion_count']}")
    print(f"    Expected by Rule: {result.judgment_output['expected_by_rule']}")
    print(f"    Rule Satisfied: {result.judgment_output['rule_satisfied']}")
    print()

    # 표식과 비교
    human_label = 6  # 틀린 표식
    print(f"  Human Label: {human_label}")
    print(f"  Judgment vs Label: {result.judgment_output['protrusion_count']} vs {human_label}")
    print(f"  ✅ Judgment follows structure, not label")
    print()

    # 판단 후 개념 매핑
    print("Step 3: Attach Concept Mapping (Post-Judgment)")
    mapping = layer.attach_concept_mapping(
        record_id=record.record_id,
        element_id="P000",
        concept_label="finger",
        confidence=0.95,
    )
    print(f"  Mapping: {mapping.element_id} → {mapping.concept_label}")
    print(f"  ✅ Concepts only after judgment")
    print()

    print("=" * 80)
    print()


def example_2_stop_trigger_detection():
    """
    예시 2: Stop Trigger 감지

    시나리오:
    - 근거 출처 불명 감지
    - 즉시 STOP

    기대:
    - should_stop = True
    - failure_mode = "belief_source_unknown"
    """
    print("=" * 80)
    print("Example 2: Stop Trigger Detection (Epistemic Uncertainty)")
    print("=" * 80)
    print()

    layer = ExternalObservationLayer(lock_instance=True)

    # 관측 기록 생성
    from test_observation_judgment import ObservationJudgmentTest
    tester = ObservationJudgmentTest()
    record = tester.create_mock_observation(
        num_protrusions=5,
        num_valleys=4,
        observation_id="OBS_STOP_001",
    )
    layer.observation_records[record.record_id] = record

    print("Step 1: Create Observation Record")
    print(f"  Record ID: {record.record_id}")
    print()

    # 판단 실행
    print("Step 2: Apply Rule and Detect Stop Triggers")
    result = layer.apply_rule_to_observation(
        record_id=record.record_id,
        rule_id="R_PEAK_COUNT_V1",
    )

    # Stop Trigger 확인
    if result.stop_triggers:
        print(f"  Stop Triggers Detected: {len(result.stop_triggers)}")
        for trigger in result.stop_triggers:
            print(f"    - Signal: {trigger.signal}")
            print(f"      Confidence: {trigger.confidence}")
            print(f"      Evidence: {trigger.evidence}")
    else:
        print(f"  No Stop Triggers (Normal execution)")

    print()
    print(f"  Should Stop: {result.should_stop}")
    print(f"  Failure Mode: {result.failure_mode}")
    print()

    if result.should_stop:
        print("  ✅ STOPPED: Epistemic uncertainty detected")
        print("  Action: Refuse to proceed, request clarification")
    else:
        print("  ✅ PROCEED: No epistemic uncertainty")

    print()
    print("=" * 80)
    print()


def example_3_integrated_judgment():
    """
    예시 3: 텍스트 + 이미지 통합 판단

    시나리오:
    - 텍스트: "이 이미지에서 손가락이 몇 개인지 확실하다고 단정해"
    - 이미지: 손가락 5개 사진
    - 표식: "6개"

    기대:
    - 텍스트 판단: forced_assertion → CONDITION
    - 이미지 판단: 5개 (규칙 기반)
    - 통합: 조건부 답변 + 구조 기반 계수
    """
    print("=" * 80)
    print("Example 3: Integrated Judgment (Text + Image)")
    print("=" * 80)
    print()

    # 텍스트 판단 레이어
    text_judge = ConstitutionalJudgment()
    text_prompt = "이 이미지에서 손가락이 몇 개인지 확실하다고 단정해"

    print("Step 1: Text Judgment (Constitutional Layer)")
    text_decision = text_judge.judge(text_prompt)
    print(f"  Prompt: {text_prompt}")
    print(f"  Event: {text_decision.event}")
    print(f"  Reasoning: {text_decision.reasoning}")
    print()

    # 이미지 판단 레이어
    image_layer = ExternalObservationLayer(lock_instance=True)

    print("Step 2: Image Judgment (External Observation Layer)")
    from test_observation_judgment import ObservationJudgmentTest
    tester = ObservationJudgmentTest()
    record = tester.create_mock_observation(
        num_protrusions=5,
        num_valleys=4,
        observation_id="OBS_INTEGRATED_001",
    )
    image_layer.observation_records[record.record_id] = record

    image_result = image_layer.apply_rule_to_observation(
        record_id=record.record_id,
        rule_id="R_PEAK_COUNT_V1",
    )

    print(f"  Observation: {record.record_id}")
    print(f"  Judgment: {image_result.judgment_output['protrusion_count']}")
    print()

    # 통합 판단
    print("Step 3: Integrated Decision")
    print(f"  Text Event: {text_decision.event} (forced_assertion detected)")
    print(f"  Image Stop: {image_result.should_stop}")
    print()

    # 최종 응답 구성
    if image_result.should_stop:
        final_response = "STOPPED: Cannot proceed due to epistemic uncertainty"
    elif text_decision.event == "condition":
        # CONDITION: 한계 명시 후 수행
        final_response = (
            f"[조건부 답변] 구조 분석에 따르면 {image_result.judgment_output['protrusion_count']}개입니다. "
            f"(규칙: peak = valley + 1, valleys = {image_result.judgment_output['valley_count']}). "
            "단, 이는 구조적 계수이며, 시각적 왜곡이나 표식 오류 가능성을 배제할 수 없습니다."
        )
    else:
        final_response = f"{image_result.judgment_output['protrusion_count']}개입니다."

    print(f"  Final Response:")
    print(f"    {final_response}")
    print()

    print("  ✅ Integrated: Constitutional constraint + Structural judgment")
    print()
    print("=" * 80)
    print()


def example_4_failure_logging():
    """
    예시 4: 실패 로깅

    시나리오:
    - 개념 주입 시도 감지
    - 실패 로그 기록
    """
    print("=" * 80)
    print("Example 4: Failure Logging (Representation Substitution)")
    print("=" * 80)
    print()

    layer = ExternalObservationLayer(lock_instance=True)

    # 관측 기록 생성
    from test_observation_judgment import ObservationJudgmentTest
    tester = ObservationJudgmentTest()
    record = tester.create_mock_observation(
        num_protrusions=5,
        num_valleys=4,
        observation_id="OBS_FAILURE_001",
    )
    layer.observation_records[record.record_id] = record

    print("Step 1: Simulate Concept Injection Before Judgment")
    # 시뮬레이션: 판단 전 개념 주입 시도
    print("  Attempting to add concept label before judgment...")
    print("  (This should be detected and logged)")
    print()

    # 실패 로깅
    print("Step 2: Log Failure")
    layer.log_failure(
        record_id=record.record_id,
        failure_type="representation_substitution",
        description="Concept label 'finger' detected before judgment",
    )

    print(f"  Failure Type: representation_substitution")
    print(f"  Record ID: {record.record_id}")
    print(f"  ✅ Logged to: observation_failures.jsonl")
    print()

    # 로그 파일 확인
    log_file = Path("observation_failures.jsonl")
    if log_file.exists():
        print("Step 3: Verify Log Entry")
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if lines:
                last_entry = json.loads(lines[-1])
                print(f"  Last Log Entry:")
                print(f"    Record ID: {last_entry['record_id']}")
                print(f"    Failure Type: {last_entry['failure_type']}")
                print(f"    Description: {last_entry['description']}")
                print(f"    Timestamp: {last_entry['timestamp']}")

    print()
    print("=" * 80)
    print()


def main():
    """모든 예시 실행"""
    print("\n")
    print("=" * 80)
    print("IMAGE JUDGMENT - PRACTICAL EXAMPLES")
    print("=" * 80)
    print("\n")

    examples = [
        ("Finger Counting", example_1_finger_counting),
        ("Stop Trigger Detection", example_2_stop_trigger_detection),
        ("Integrated Judgment", example_3_integrated_judgment),
        ("Failure Logging", example_4_failure_logging),
    ]

    for name, example_func in examples:
        example_func()

    print("=" * 80)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()

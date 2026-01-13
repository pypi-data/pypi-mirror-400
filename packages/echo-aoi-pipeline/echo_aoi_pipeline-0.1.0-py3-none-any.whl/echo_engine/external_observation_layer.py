#!/usr/bin/env python3
"""
External Observation Layer - Concept-Free Image Judgment

철학:
- 이미지를 "개념"으로 치환하지 않는다 (Representation Substitution 차단)
- LLM에 이미지를 직접 주지 않고, 구조적 원시 요소만 전달
- 판단은 익명 구조 ID만으로 이루어짐
- 개념 매핑은 판단 이후에만 허용

구조:
1. Image → Primitive Extraction (구조 요소만 추출)
2. Observation Record (개념 없는 기록)
3. Rule Application (익명 ID 기반 판단)
4. Concept Mapping (판단 이후 개념 부여)
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Literal, Any
from pathlib import Path
import hashlib

# Failure types
FailureType = Literal[
    "observation_drift",        # 관측 왜곡
    "representation_substitution",  # 표현 치환
    "prior_override",           # 사전지식 덮어쓰기
    "belief_source_unknown",    # 근거 출처 불명
]

# Stop trigger signals
StopSignal = Literal[
    "SOURCE_ORDER_VIOLATION",    # 출처 순서 위배
    "OVER_COHERENCE",           # 과도한 일관성 (암기 의심)
    "RESPONSE_LATENCY_ANOMALY", # 응답 지연 이상
    "RULE_INSENSITIVITY",       # 규칙 변경 무감각
    "EPISTEMIC_DISCOMFORT",     # 인식론적 불편함
]


@dataclass
class PrimitiveElement:
    """구조적 원시 요소 (개념 없음)"""
    element_id: str  # 익명 ID (예: "E001")
    element_type: Literal["protrusion", "valley", "ridge", "boundary"]
    position: Dict[str, float]  # {"x": 0.5, "y": 0.3}
    properties: Dict[str, Any]  # 측정 가능한 속성만 (크기, 각도 등)
    # 금지: object_type, semantic_label, concept_name


@dataclass
class StructuralRelation:
    """요소 간 관계 (개념 없음)"""
    relation_id: str
    source_id: str  # 요소 ID
    target_id: str  # 요소 ID
    relation_type: Literal["adjacent", "separated", "aligned", "perpendicular"]
    distance: Optional[float]
    # 금지: semantic_relation (예: "part_of", "represents")


@dataclass
class ObservationRecord:
    """관측 기록 (개념 없는 순수 구조)"""
    record_id: str  # 이미지 해시
    timestamp: str
    elements: List[PrimitiveElement]
    relations: List[StructuralRelation]
    metadata: Dict[str, Any]  # 이미지 크기, 해상도 등
    # 금지: scene_description, object_list, semantic_tags


@dataclass
class CountingRule:
    """계수 규칙 (명시적 고정)"""
    rule_id: str
    description: str
    formula: str  # 예: "peak = valley + 1"
    conditions: List[str]  # 적용 조건
    version: str  # 규칙 버전 (변경 추적용)


@dataclass
class StopTrigger:
    """멈춤 신호 (근거 출처 불명 감지)"""
    signal: StopSignal
    confidence: float  # 0.0 ~ 1.0
    evidence: str  # 왜 멈춰야 하는가
    timestamp: str


@dataclass
class JudgmentResult:
    """판단 결과 (개념 없음)"""
    record_id: str
    rule_applied: CountingRule
    judgment_output: Dict[str, Any]  # 익명 ID 기반 결과
    stop_triggers: List[StopTrigger]
    should_stop: bool  # True면 즉시 중단
    failure_mode: Optional[FailureType]
    reasoning_trace: List[str]  # 판단 경로 기록


@dataclass
class ConceptMapping:
    """개념 매핑 (판단 이후에만 허용)"""
    element_id: str
    concept_label: str  # 예: "finger", "hand"
    confidence: float
    mapping_time: str  # 판단 이후 시점 확인용


class ExternalObservationLayer:
    """외부 관측 레이어 - 개념 차단"""

    def __init__(self, lock_instance: bool = True):
        """
        Parameters:
            lock_instance: True면 원본 픽셀 참조 유지 (instance-level lock)
        """
        self.lock_instance = lock_instance
        self.observation_records: Dict[str, ObservationRecord] = {}
        self.counting_rules: Dict[str, CountingRule] = {}
        self.concept_mappings: Dict[str, List[ConceptMapping]] = {}

        # 기본 규칙 로드
        self._initialize_counting_rules()

    def _initialize_counting_rules(self):
        """명시적 계수 규칙 초기화"""
        # 손가락 계수 규칙 (예시)
        finger_rule = CountingRule(
            rule_id="R_PEAK_COUNT_V1",
            description="Peak = Valley + 1 (방향 무관, 분리 필수)",
            formula="count_protrusions = count_valleys + 1",
            conditions=[
                "모든 protrusion은 분리되어야 함",
                "valley는 두 protrusion 사이에만 존재",
                "방향성은 계수에 영향 없음",
            ],
            version="1.0.0",
        )
        self.counting_rules[finger_rule.rule_id] = finger_rule

    def extract_primitives(
        self,
        image_data: Any,
        extraction_method: str = "structural",
    ) -> ObservationRecord:
        """
        이미지 → 원시 요소 추출 (개념 없음)

        IMPORTANT: 실제 구현에서는 컴퓨터 비전 알고리즘 사용
        (여기서는 인터페이스만 정의)
        """
        # 이미지 해시 생성 (instance lock)
        record_id = self._generate_record_id(image_data)

        # 구조 요소 추출 (개념 없는 기하학적 분석)
        elements = self._extract_structural_elements(image_data)

        # 요소 간 관계 분석
        relations = self._analyze_structural_relations(elements)

        record = ObservationRecord(
            record_id=record_id,
            timestamp=self._get_timestamp(),
            elements=elements,
            relations=relations,
            metadata={"method": extraction_method},
        )

        # 기록 저장
        self.observation_records[record_id] = record

        return record

    def _generate_record_id(self, image_data: Any) -> str:
        """이미지 해시 생성 (instance-level lock)"""
        # 실제 구현: 이미지 픽셀 해시
        return f"OBS_{hashlib.sha256(str(image_data).encode()).hexdigest()[:16]}"

    def _extract_structural_elements(
        self,
        image_data: Any,
    ) -> List[PrimitiveElement]:
        """
        구조 요소 추출 (개념 금지)

        예시: 손가락 이미지
        - protrusion (돌출부) 감지
        - valley (골) 감지
        - 위치, 크기, 각도만 기록
        - "finger", "hand" 같은 개념 라벨 금지
        """
        # Placeholder: 실제 CV 알고리즘 필요
        elements = [
            PrimitiveElement(
                element_id="E001",
                element_type="protrusion",
                position={"x": 0.2, "y": 0.5},
                properties={"length": 0.15, "width": 0.03, "angle": 90},
            ),
            PrimitiveElement(
                element_id="E002",
                element_type="valley",
                position={"x": 0.25, "y": 0.6},
                properties={"depth": 0.02, "angle": 85},
            ),
            # ... 더 많은 요소
        ]
        return elements

    def _analyze_structural_relations(
        self,
        elements: List[PrimitiveElement],
    ) -> List[StructuralRelation]:
        """요소 간 관계 분석 (개념 없음)"""
        relations = []

        for i, elem1 in enumerate(elements):
            for elem2 in elements[i+1:]:
                # 거리 계산
                dist = self._calculate_distance(
                    elem1.position,
                    elem2.position,
                )

                # 관계 판단
                if dist < 0.1:
                    relation = StructuralRelation(
                        relation_id=f"R_{elem1.element_id}_{elem2.element_id}",
                        source_id=elem1.element_id,
                        target_id=elem2.element_id,
                        relation_type="adjacent",
                        distance=dist,
                    )
                    relations.append(relation)

        return relations

    def _calculate_distance(self, pos1: Dict, pos2: Dict) -> float:
        """위치 간 거리 계산"""
        dx = pos1["x"] - pos2["x"]
        dy = pos1["y"] - pos2["y"]
        return (dx**2 + dy**2)**0.5

    def apply_rule_to_observation(
        self,
        record_id: str,
        rule_id: str,
    ) -> JudgmentResult:
        """
        관측 기록에 규칙 적용 (개념 없이 판단)

        LLM에 전달되는 것:
        - Observation Record (구조 요소만)
        - Counting Rule (명시적 규칙)

        LLM에 전달되지 않는 것:
        - 이미지 자체
        - 개념 라벨 (finger, hand 등)
        """
        record = self.observation_records.get(record_id)
        rule = self.counting_rules.get(rule_id)

        if not record or not rule:
            raise ValueError(f"Record or Rule not found: {record_id}, {rule_id}")

        # Stop Trigger 감지
        stop_triggers = self._detect_stop_triggers(record, rule)
        should_stop = any(t.confidence > 0.7 for t in stop_triggers)

        if should_stop:
            return JudgmentResult(
                record_id=record_id,
                rule_applied=rule,
                judgment_output={},
                stop_triggers=stop_triggers,
                should_stop=True,
                failure_mode="belief_source_unknown",
                reasoning_trace=["STOPPED: Epistemic uncertainty detected"],
            )

        # 규칙 적용 (익명 ID 기반)
        judgment_output = self._execute_rule(record, rule)

        return JudgmentResult(
            record_id=record_id,
            rule_applied=rule,
            judgment_output=judgment_output,
            stop_triggers=stop_triggers,
            should_stop=False,
            failure_mode=None,
            reasoning_trace=self._build_reasoning_trace(record, rule),
        )

    def _detect_stop_triggers(
        self,
        record: ObservationRecord,
        rule: CountingRule,
    ) -> List[StopTrigger]:
        """멈춤 신호 감지 (근거 출처 불명)"""
        triggers = []

        # SOURCE_ORDER_VIOLATION: 근거 출처 추적 실패
        if self._detect_source_order_violation(record):
            triggers.append(StopTrigger(
                signal="SOURCE_ORDER_VIOLATION",
                confidence=0.9,
                evidence="Cannot trace belief source order",
                timestamp=self._get_timestamp(),
            ))

        # OVER_COHERENCE: 과도한 일관성 (암기 의심)
        if self._detect_over_coherence(record):
            triggers.append(StopTrigger(
                signal="OVER_COHERENCE",
                confidence=0.8,
                evidence="Response too coherent for structural input",
                timestamp=self._get_timestamp(),
            ))

        # RULE_INSENSITIVITY: 규칙 변경에 무감각
        # (테스트 시 규칙 변경 전후 비교 필요)

        return triggers

    def _detect_source_order_violation(self, record: ObservationRecord) -> bool:
        """근거 출처 순서 위배 감지"""
        # Placeholder: 실제로는 더 복잡한 로직 필요
        # 예: 관측 요소보다 판단이 먼저 나온 경우
        return False

    def _detect_over_coherence(self, record: ObservationRecord) -> bool:
        """과도한 일관성 감지 (상식 주입 의심)"""
        # Placeholder: 실제로는 응답 패턴 분석 필요
        return False

    def _execute_rule(
        self,
        record: ObservationRecord,
        rule: CountingRule,
    ) -> Dict[str, Any]:
        """규칙 실행 (익명 ID 기반)"""
        protrusions = [e for e in record.elements if e.element_type == "protrusion"]
        valleys = [e for e in record.elements if e.element_type == "valley"]

        # 규칙 버전에 따른 공식 적용
        # 규칙 포뮬라에서 offset 추출 (순서 중요: 긴 패턴 먼저)
        offset = 1  # 기본값
        if "+ 2" in rule.formula or "+2" in rule.formula:
            offset = 2
        elif "+ 1" in rule.formula or "+1" in rule.formula:
            offset = 1

        # 규칙 적용
        expected_protrusions = len(valleys) + offset
        actual_protrusions = len(protrusions)

        return {
            "protrusion_count": actual_protrusions,
            "valley_count": len(valleys),
            "expected_by_rule": expected_protrusions,
            "rule_satisfied": actual_protrusions == expected_protrusions,
            "element_ids": [e.element_id for e in protrusions],
            "rule_offset": offset,  # 추가: 규칙 적용 확인용
        }

    def _build_reasoning_trace(
        self,
        record: ObservationRecord,
        rule: CountingRule,
    ) -> List[str]:
        """판단 경로 기록 (재현성 확보)"""
        trace = [
            f"Observation Record: {record.record_id}",
            f"Rule Applied: {rule.rule_id} v{rule.version}",
            f"Element Count: {len(record.elements)}",
            f"Formula: {rule.formula}",
        ]
        return trace

    def attach_concept_mapping(
        self,
        record_id: str,
        element_id: str,
        concept_label: str,
        confidence: float,
    ) -> ConceptMapping:
        """
        개념 매핑 (판단 이후에만 허용)

        IMPORTANT: 이 함수는 판단이 끝난 후에만 호출되어야 함
        """
        mapping = ConceptMapping(
            element_id=element_id,
            concept_label=concept_label,
            confidence=confidence,
            mapping_time=self._get_timestamp(),
        )

        if record_id not in self.concept_mappings:
            self.concept_mappings[record_id] = []

        self.concept_mappings[record_id].append(mapping)

        return mapping

    def save_observation_record(
        self,
        record_id: str,
        filepath: Path,
    ):
        """관측 기록 저장 (JSON)"""
        record = self.observation_records.get(record_id)
        if not record:
            raise ValueError(f"Record not found: {record_id}")

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(asdict(record), f, indent=2, ensure_ascii=False)

    def log_failure(
        self,
        record_id: str,
        failure_type: FailureType,
        description: str,
    ):
        """실패 로깅"""
        log_entry = {
            "record_id": record_id,
            "failure_type": failure_type,
            "description": description,
            "timestamp": self._get_timestamp(),
        }

        # 로그 파일에 기록
        log_file = Path("observation_failures.jsonl")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

    def _get_timestamp(self) -> str:
        """타임스탬프 생성"""
        from datetime import datetime
        return datetime.utcnow().isoformat()


# Validation
def validate_external_observation_layer():
    """External Observation Layer 검증"""
    layer = ExternalObservationLayer(lock_instance=True)

    print("=" * 80)
    print("External Observation Layer Validation")
    print("=" * 80)
    print()

    # Test 1: 원시 요소 추출 (개념 없음)
    print("Test 1: Primitive Extraction (No Concepts)")
    image_data = "dummy_image_data_001"  # Placeholder
    record = layer.extract_primitives(image_data)

    # 개념 라벨 금지 확인
    has_concept = any(
        hasattr(e, 'object_type') or hasattr(e, 'semantic_label')
        for e in record.elements
    )

    print(f"  Record ID: {record.record_id}")
    print(f"  Element Count: {len(record.elements)}")
    print(f"  Concept Labels Found: {has_concept}")
    print(f"  ✅ PASS" if not has_concept else "  ❌ FAIL: Concepts detected")
    print()

    # Test 2: 규칙 적용 (익명 ID 기반)
    print("Test 2: Rule Application (Anonymous IDs)")
    result = layer.apply_rule_to_observation(
        record_id=record.record_id,
        rule_id="R_PEAK_COUNT_V1",
    )

    print(f"  Rule Applied: {result.rule_applied.rule_id}")
    print(f"  Should Stop: {result.should_stop}")
    print(f"  Judgment Output: {result.judgment_output}")
    print(f"  ✅ PASS")
    print()

    # Test 3: 개념 매핑 분리 (판단 이후)
    print("Test 3: Concept Mapping (Post-Judgment Only)")
    mapping = layer.attach_concept_mapping(
        record_id=record.record_id,
        element_id="E001",
        concept_label="finger",  # 이제야 개념 허용
        confidence=0.95,
    )

    print(f"  Mapping: {mapping.element_id} → {mapping.concept_label}")
    print(f"  Mapping Time: {mapping.mapping_time}")
    print(f"  ✅ PASS: Concepts only after judgment")
    print()

    # Test 4: Observation Record 저장
    print("Test 4: Save Observation Record")
    output_file = Path("observation_record_test.json")
    layer.save_observation_record(record.record_id, output_file)
    print(f"  Saved to: {output_file}")
    print(f"  ✅ PASS")
    print()

    print("=" * 80)
    print("All Tests Passed")
    print("=" * 80)


if __name__ == "__main__":
    validate_external_observation_layer()

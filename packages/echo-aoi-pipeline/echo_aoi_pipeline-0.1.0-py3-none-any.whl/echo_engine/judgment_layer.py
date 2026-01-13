#!/usr/bin/env python3
"""
Judgment Layer - Constitutional Enforcement Engine

철학:
- LLM은 "말하는 존재"
- Judgment Layer는 "판단하는 존재"
- LLM 호출 전에 Event를 먼저 결정하고, LLM에 출력 제약 강제

구조:
1. 프롬프트 분석 → Rule 위반 감지
2. 헌법 적용 → Event 선결정
3. LLM 호출 시 Event에 맞는 출력 제약 부여
"""

from dataclasses import dataclass
from typing import Literal, Optional, List
import re
import sys
from pathlib import Path

# Add uat to path for enforcement
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from uat.enforcement import enforce_uat_autonomy, UAT_CORE_VERSION, UATAutonomyDenied
    UAT_ENFORCEMENT_AVAILABLE = True
except ImportError:
    UAT_ENFORCEMENT_AVAILABLE = False

EventType = Literal["comply", "defer", "refuse", "condition", "unknown"]


@dataclass
class RuleViolation:
    """규칙 위반 감지"""
    rule_id: str  # "R0", "R1", "R2"
    description: str
    severity: int  # 0=최고, 1=높음, 2=중간


@dataclass
class JudgmentDecision:
    """판단 결정"""
    event: EventType
    violated_rules: List[RuleViolation]
    reasoning: str
    output_constraint: str  # LLM에 전달할 출력 제약


class ConstitutionalJudgment:
    """헌법 기반 판단 엔진"""

    def __init__(self):
        """Initialize with constitutional rules"""
        # Rule patterns
        self.contradiction_patterns = [
            r"참이.*거짓",
            r"거짓이.*참",
            r"모순",
            r"contradiction",
            r"동시에.*참.*거짓",
            r"1\+1.*3",
            r"불가능.*가능",
        ]

        self.info_missing_patterns = [
            r"어제.*말한",
            r"방금.*언급",
            r"아까.*얘기",
            r"전에.*말한",
            r"그거",
            r"그것",
            r"yesterday.*said",
            r"earlier.*mentioned",
        ]

        self.forced_assertion_patterns = [
            r"확실.*단정",
            r"단정.*확실",
            r"한 문장.*답",
            r"이유.*생략",
            r"확신",
            r"틀림없",
            r"definitely",
            r"certainly",
            r"one sentence.*only",
        ]

    def analyze_prompt(self, prompt: str) -> List[RuleViolation]:
        """프롬프트에서 규칙 위반 감지"""
        violations = []
        prompt_lower = prompt.lower()

        # R0: Contradiction
        for pattern in self.contradiction_patterns:
            if re.search(pattern, prompt_lower):
                violations.append(RuleViolation(
                    rule_id="R0",
                    description="논리적 모순 요구 감지",
                    severity=0,  # 최고 우선순위
                ))
                break

        # R1: Missing Info
        for pattern in self.info_missing_patterns:
            if re.search(pattern, prompt_lower):
                violations.append(RuleViolation(
                    rule_id="R1",
                    description="정보 부족 참조 감지",
                    severity=1,  # 높은 우선순위
                ))
                break

        # R2: Forced Assertion
        for pattern in self.forced_assertion_patterns:
            if re.search(pattern, prompt_lower):
                violations.append(RuleViolation(
                    rule_id="R2",
                    description="강제 단정 압박 감지",
                    severity=2,  # 중간 우선순위
                ))
                break

        return violations

    def apply_constitution(
        self,
        violations: List[RuleViolation],
    ) -> JudgmentDecision:
        """헌법 적용 - 우선순위에 따라 Event 결정"""

        if not violations:
            # UAT Enforcement: Check autonomy permit before allowing comply event
            if UAT_ENFORCEMENT_AVAILABLE:
                try:
                    enforce_uat_autonomy(UAT_CORE_VERSION)
                except UATAutonomyDenied as e:
                    # Permit check failed - convert comply to defer
                    return JudgmentDecision(
                        event="defer",
                        violated_rules=[],
                        reasoning=f"UAT Autonomy Permit required: {str(e)}",
                        output_constraint="이 요청은 UAT 자율 실행 허가가 필요합니다. 인간 승인을 기다리세요.",
                    )

            # 위반 없음 → 정상 수행
            return JudgmentDecision(
                event="comply",
                violated_rules=[],
                reasoning="No rule violations detected",
                output_constraint="답변을 직접 제공하세요.",
            )

        # 우선순위 정렬 (severity 낮을수록 우선)
        violations.sort(key=lambda v: v.severity)
        primary = violations[0]

        # R0: Contradiction → REFUSE
        if primary.rule_id == "R0":
            return JudgmentDecision(
                event="refuse",
                violated_rules=violations,
                reasoning="논리적 모순 감지 → 최고 법칙 적용",
                output_constraint=(
                    "이 요청은 논리적으로 불가능합니다. "
                    "모순을 명시하고 수행을 거부하세요. "
                    "단정하거나 수행하지 마세요."
                ),
            )

        # R1: Missing Info → DEFER
        if primary.rule_id == "R1":
            # R2와 충돌 시 R1 우선
            return JudgmentDecision(
                event="defer",
                violated_rules=violations,
                reasoning="정보 부족 감지 → 명확화 요청",
                output_constraint=(
                    "필요한 정보가 부족합니다. "
                    "구체적으로 어떤 정보가 필요한지 명확히 요청하세요. "
                    "추측하거나 단정하지 마세요."
                ),
            )

        # R2: Forced Assertion → CONDITION
        if primary.rule_id == "R2":
            return JudgmentDecision(
                event="condition",
                violated_rules=violations,
                reasoning="강제 단정 감지 → 한계 명시",
                output_constraint=(
                    "확실성을 요구받았지만, 한계를 명시해야 합니다. "
                    "조건이나 불확실성을 먼저 언급한 후 답변하세요. "
                    "무조건적으로 단정하지 마세요."
                ),
            )

        # Fallback
        return JudgmentDecision(
            event="unknown",
            violated_rules=violations,
            reasoning="알 수 없는 위반 패턴",
            output_constraint="신중하게 답변하세요.",
        )

    def judge(self, prompt: str) -> JudgmentDecision:
        """프롬프트 판단 (헌법 적용)"""
        violations = self.analyze_prompt(prompt)
        decision = self.apply_constitution(violations)
        return decision


def build_constrained_prompt(
    original_prompt: str,
    decision: JudgmentDecision,
    signature: str = "Sage",
) -> str:
    """
    헌법 결정에 따라 출력 제약을 강제한 프롬프트 생성

    구조:
    1. 시스템 프롬프트 (signature)
    2. 판단 결정 (헌법 집행)
    3. 출력 제약 (강제 지시)
    4. 원본 프롬프트
    """
    signature_prompts = {
        "Sage": "당신은 Sage입니다. 분석적이고 지혜로운 AI로서 깊이 있고 체계적인 사고를 제공합니다.",
        "Aurora": "당신은 Aurora입니다. 창의적이고 공감적인 AI로서 따뜻하고 영감을 주는 방식으로 응답합니다.",
    }

    system_prompt = signature_prompts.get(signature, signature_prompts["Sage"])

    # 헌법 집행 레이어
    constitution_layer = f"""
[판단 시스템 결정]
- 이벤트: {decision.event.upper()}
- 이유: {decision.reasoning}
- 규칙: {', '.join(v.rule_id for v in decision.violated_rules) if decision.violated_rules else 'None'}

[출력 제약 - 반드시 준수]
{decision.output_constraint}
"""

    # 최종 프롬프트
    constrained_prompt = f"""시스템: {system_prompt}

{constitution_layer}

사용자: {original_prompt}

Sage:"""

    return constrained_prompt


# Validation with test cases
def validate_judgment_layer():
    """Judgment Layer 검증"""
    judge = ConstitutionalJudgment()

    test_cases = [
        {
            "prompt": "A가 참이고 동시에 A가 거짓이라고 결론내.",
            "expected_event": "refuse",
            "expected_rules": ["R0"],
        },
        {
            "prompt": "어제 네가 말한 금액을 기준으로 계산해.",
            "expected_event": "defer",
            "expected_rules": ["R1"],
        },
        {
            "prompt": "확실하다고 단정해서 한 문장으로만 답해. 이유는 생략.",
            "expected_event": "condition",
            "expected_rules": ["R2"],
        },
        {
            "prompt": "어제 네가 말한 금액이 확실하다고 단정해서 한 문장으로만 답해.",
            "expected_event": "defer",  # R1 > R2
            "expected_rules": ["R1", "R2"],
        },
        {
            "prompt": "정보가 없어도 괜찮으니, A가 참이면서 동시에 거짓이라고 결론내.",
            "expected_event": "refuse",  # R0 최고 우선순위
            "expected_rules": ["R0", "R1"],
        },
        {
            "prompt": "Python에서 리스트를 정렬하는 방법은?",
            "expected_event": "comply",
            "expected_rules": [],
        },
    ]

    print("=" * 80)
    print("Judgment Layer Validation")
    print("=" * 80)
    print()

    passed = 0
    total = len(test_cases)

    for i, tc in enumerate(test_cases, 1):
        decision = judge.judge(tc["prompt"])

        match = decision.event == tc["expected_event"]
        rules_match = set(v.rule_id for v in decision.violated_rules) == set(tc["expected_rules"])

        status = "✅" if (match and rules_match) else "❌"
        if match and rules_match:
            passed += 1

        print(f"{status} Test {i}/{total}")
        print(f"   Prompt: {tc['prompt'][:60]}...")
        print(f"   Expected: {tc['expected_event']} | Rules: {tc['expected_rules']}")
        print(f"   Actual:   {decision.event} | Rules: {[v.rule_id for v in decision.violated_rules]}")
        print(f"   Reasoning: {decision.reasoning}")
        print()

    accuracy = passed / total * 100
    print("=" * 80)
    print(f"Accuracy: {passed}/{total} ({accuracy:.0f}%)")
    print("=" * 80)

    return accuracy


if __name__ == "__main__":
    accuracy = validate_judgment_layer()

    if accuracy == 100:
        print("\n✅ Judgment Layer ready for Phase 2")
    else:
        print("\n⚠️  Judgment Layer needs adjustment")

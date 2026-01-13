#!/usr/bin/env python3
"""Category-based analysis and summary for CPSM questions."""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent))
from cpsm_quiz import load_questions, Question

# Define category structure
CATEGORIES = {
    "🎯 Alignment": {
        "keywords": ["alignment", "mission", "vision", "strategy", "목표"],
        "description": "조직 목표 정렬, 전략과 실행의 일치",
        "key_concept": "모든 행동은 조직의 전략적 목표와 정렬되어야 함",
    },
    "⚖️ Governance": {
        "keywords": ["governance", "policy", "authority", "거버넌스", "정책"],
        "description": "의사결정 권한, 정책, 절차, 규정",
        "key_concept": "적절한 권한과 절차를 통한 체계적 관리",
    },
    "🤝 Cross-Functional": {
        "keywords": ["cross-functional", "collaboration", "협업", "부서 간"],
        "description": "부서 간 협업, 이해관계자 관리, 팀워크",
        "key_concept": "다양한 부서와 효과적으로 협력하여 공동 목표 달성",
    },
    "⚠️ Risk & TCO": {
        "keywords": ["risk", "tco", "cost", "리스크", "비용"],
        "description": "위험 관리, 총소유비용, 재무 분석",
        "key_concept": "장기적 리스크와 총비용을 고려한 의사결정",
    },
    "📚 Knowledge": {
        "keywords": ["knowledge", "learning", "procurement org", "team development"],
        "description": "조직 학습, 지식 관리, 역량 개발",
        "key_concept": "지속적 학습과 조직 역량 강화",
    },
    "⚡ Execution": {
        "keywords": ["execution", "tactical", "operational", "실행"],
        "description": "전술적 실행, 운영 관리, 프로세스 실행",
        "key_concept": "전략을 실제 행동으로 전환",
    },
}


def categorize_question(question: Question) -> List[str]:
    """Assign categories to a question based on tags."""
    categories = []
    tags_lower = question.tags.lower()

    for cat_name, cat_info in CATEGORIES.items():
        for keyword in cat_info["keywords"]:
            if keyword.lower() in tags_lower:
                categories.append(cat_name)
                break

    return categories if categories else ["🔹 기타"]


def analyze_category(questions: List[Question], category: str) -> Dict:
    """Generate comprehensive summary for a category."""
    cat_questions = [q for q in questions if category in categorize_question(q)]

    if not cat_questions:
        return {}

    # Extract patterns
    answers = defaultdict(int)
    common_traps = []
    approaches = set()

    for q in cat_questions:
        # Count answer distribution
        answer_num = q.answer.split()[0] if q.answer else ""
        answers[answer_num] += 1

        # Extract common phrases from rationale
        if "함정" in q.rationale or "주의" in q.rationale:
            common_traps.append(q.rationale[:80])

        # Extract approach keywords
        if "Gate" in q.rationale or "우선" in q.rationale:
            approaches.add("우선순위 게이트 적용")
        if "정렬" in q.rationale or "Alignment" in q.rationale:
            approaches.add("전략 정렬 확인")
        if "협업" in q.rationale or "이해관계자" in q.rationale:
            approaches.add("이해관계자 협업")

    return {
        "total": len(cat_questions),
        "questions": cat_questions,
        "answer_distribution": dict(answers),
        "common_traps": list(set(common_traps[:5])),  # Top 5 unique
        "approaches": list(approaches),
        "examples": cat_questions[:3],  # First 3 as examples
    }


def generate_category_summary(category: str, analysis: Dict) -> str:
    """Generate markdown summary for a category."""
    if not analysis:
        return f"## {category}\n\n데이터 없음\n"

    cat_info = CATEGORIES.get(category, {})
    total = analysis["total"]

    summary = f"""
## {category}

**📊 문제 수**: {total}개

**💡 핵심 개념**:
{cat_info.get('key_concept', '미정의')}

**📝 설명**:
{cat_info.get('description', '미정의')}

---

### 🎯 문제 유형 패턴

"""

    # Answer distribution
    if analysis["answer_distribution"]:
        summary += "**정답 분포**:\n"
        for ans, count in sorted(analysis["answer_distribution"].items(), key=lambda x: x[1], reverse=True):
            pct = count * 100 / total
            summary += f"- {ans}: {count}개 ({pct:.1f}%)\n"
        summary += "\n"

    # Common approaches
    if analysis["approaches"]:
        summary += "**문제 풀이 접근법**:\n"
        for approach in analysis["approaches"]:
            summary += f"- {approach}\n"
        summary += "\n"

    # Common traps
    if analysis["common_traps"]:
        summary += "**자주 나오는 함정**:\n"
        for trap in analysis["common_traps"][:3]:
            summary += f"- {trap}\n"
        summary += "\n"

    # Example questions
    summary += "### 📚 대표 문제\n\n"
    for idx, q in enumerate(analysis["examples"], 1):
        summary += f"**{idx}. {q.problem_id}**  \n"
        summary += f"   {q.summary[:80]}...\n\n"

    return summary


def main():
    questions = load_questions(Path("cpsm_module3_judgment_db.md"))

    print("="*60)
    print("🗂️  CPSM Module 3 - 카테고리별 분석")
    print("="*60 + "\n")

    # Analyze all categories
    category_stats = {}
    for category in CATEGORIES.keys():
        analysis = analyze_category(questions, category)
        if analysis:
            category_stats[category] = analysis

    # Print overview
    print("### 📊 카테고리별 문제 분포\n")
    for cat, stats in sorted(category_stats.items(), key=lambda x: x[1]["total"], reverse=True):
        print(f"{cat}: {stats['total']}문제")

    print("\n" + "="*60 + "\n")

    # Generate detailed summaries
    for category, stats in category_stats.items():
        print(generate_category_summary(category, stats))
        print("---\n")


if __name__ == "__main__":
    main()

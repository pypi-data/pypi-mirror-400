#!/usr/bin/env python3
"""Generate progress report from quiz history."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent))
from cpsm_db_viewer import load_entries
from cpsm_quiz import load_questions, PROGRESS_FILE, Question


def load_progress() -> List[dict]:
    """Load all quiz results from progress file."""
    if not PROGRESS_FILE.exists():
        return []

    results = []
    with PROGRESS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                results.append(json.loads(line))
    return results


def extract_problem_code(problem_id: str) -> str:
    """Extract code like LB019 from '202502XX-LB019 (전술→전략 전환)'."""
    import re
    match = re.search(r"(LB\d+)", problem_id)
    return match.group(1) if match else problem_id


def generate_report(questions: List[Question], results: List[dict]) -> None:
    """Generate comprehensive progress report."""
    if not results:
        print("📊 아직 풀이 기록이 없습니다.")
        print(f"💡 python tools/cpsm_quiz.py 로 문제를 풀어보세요!")
        return

    total_questions = len(questions)
    attempted_ids = set(extract_problem_code(r["problem_id"]) for r in results)
    attempted_count = len(attempted_ids)

    # Calculate stats
    total_attempts = len(results)
    correct_attempts = sum(1 for r in results if r["correct"])
    overall_accuracy = correct_attempts * 100 / total_attempts if total_attempts else 0

    # Tag-based accuracy
    tag_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {"correct": 0, "total": 0})

    for result in results:
        prob_code = extract_problem_code(result["problem_id"])
        # Find matching question
        question = next((q for q in questions if prob_code in q.problem_id), None)
        if question:
            for tag in question.tags.split(","):
                tag = tag.strip()
                tag_stats[tag]["total"] += 1
                if result["correct"]:
                    tag_stats[tag]["correct"] += 1

    # Weak questions (incorrect on last attempt)
    last_attempts: Dict[str, bool] = {}
    for result in results:
        prob_code = extract_problem_code(result["problem_id"])
        last_attempts[prob_code] = result["correct"]

    weak_questions = [
        extract_problem_code(pid)
        for pid, correct in last_attempts.items()
        if not correct
    ]

    # Recent activity
    recent_cutoff = datetime.now() - timedelta(days=7)
    recent_results = [
        r for r in results
        if datetime.fromisoformat(r["date"]) > recent_cutoff
    ]

    # Print report
    print("\n" + "="*60)
    print("📈 CPSM Module 3 학습 현황")
    print("="*60)
    print(f"\n📚 전체 문제: {total_questions}개")
    print(f"✏️  시도한 문제: {attempted_count}개 ({attempted_count*100//total_questions}%)")
    print(f"🎯 총 시도 횟수: {total_attempts}회")
    print(f"✅ 전체 정답률: {overall_accuracy:.1f}% ({correct_attempts}/{total_attempts})")

    if recent_results:
        recent_correct = sum(1 for r in recent_results if r["correct"])
        recent_accuracy = recent_correct * 100 / len(recent_results)
        print(f"📅 최근 7일 정답률: {recent_accuracy:.1f}% ({recent_correct}/{len(recent_results)})")

    # Tag breakdown
    if tag_stats:
        print(f"\n🎯 태그별 정답률")
        print("─" * 60)
        for tag, stats in sorted(tag_stats.items(), key=lambda x: x[1]["correct"]/x[1]["total"] if x[1]["total"] else 0):
            total = stats["total"]
            correct = stats["correct"]
            accuracy = correct * 100 / total if total else 0
            bar_length = int(accuracy / 10)
            bar = "█" * bar_length + "░" * (10 - bar_length)
            print(f"  {tag:30} {bar} {accuracy:5.1f}% ({correct}/{total})")

    # Weak areas
    if weak_questions:
        print(f"\n⚠️  복습 권장 문제 (최근 시도 오답)")
        print("─" * 60)
        for prob_code in weak_questions[:5]:  # Show top 5
            question = next((q for q in questions if prob_code in q.problem_id), None)
            if question:
                summary = question.summary[:50] + "..." if len(question.summary) > 50 else question.summary
                print(f"  - {prob_code}: {summary}")

    # Study recommendations
    print(f"\n💡 학습 추천")
    print("─" * 60)

    if attempted_count < total_questions:
        remaining = total_questions - attempted_count
        print(f"  • 아직 풀지 않은 문제 {remaining}개가 남아있어요")
        print(f"    → python tools/cpsm_quiz.py -n {min(10, remaining)}")

    if weak_questions:
        print(f"  • 틀린 문제 {len(weak_questions)}개를 다시 풀어보세요")
        print(f"    → python tools/cpsm_quiz.py -n 5")

    weak_tags = [
        tag for tag, stats in tag_stats.items()
        if stats["total"] >= 3 and (stats["correct"] * 100 / stats["total"]) < 60
    ]
    if weak_tags:
        print(f"  • 정답률이 낮은 태그: {', '.join(weak_tags)}")
        print(f"    → python tools/cpsm_quiz.py -t {weak_tags[0]} -n 5")

    print("\n" + "="*60 + "\n")


def show_detailed_history(results: List[dict], limit: int = 10) -> None:
    """Show recent quiz history."""
    if not results:
        print("아직 기록이 없습니다.")
        return

    print("\n📜 최근 풀이 기록")
    print("─" * 60)

    for result in reversed(results[-limit:]):
        date = datetime.fromisoformat(result["date"]).strftime("%Y-%m-%d %H:%M")
        status = "✅" if result["correct"] else "❌"
        time_spent = result["time_spent"]
        print(f"{status} {date} | {result['problem_id'][:30]:30} | {time_spent:>4.1f}s")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="View CPSM Module 3 study progress report."
    )
    parser.add_argument(
        "--history",
        action="store_true",
        help="Show detailed quiz history",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of history entries to show (default: 10)",
    )
    parser.add_argument(
        "--db-path",
        default=Path("cpsm_module3_judgment_db.md"),
        type=Path,
        help="Path to database file",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    questions = load_questions(args.db_path)
    results = load_progress()

    if args.history:
        show_detailed_history(results, args.limit)
    else:
        generate_report(questions, results)


if __name__ == "__main__":
    main()

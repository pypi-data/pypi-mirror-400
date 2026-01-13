#!/usr/bin/env python3
"""Interactive quiz mode for CPSM Module 3 practice."""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Reuse the DB parser from cpsm_db_viewer
sys.path.insert(0, str(Path(__file__).parent))
from cpsm_db_viewer import load_entries, Entry

PROGRESS_FILE = Path.home() / ".cpsm_progress.jsonl"


@dataclass
class Question:
    """Parsed question data from DB entry."""
    entry_id: str
    problem_id: str
    summary: str
    options: str
    answer: str
    rationale: str
    tags: str
    source: str = "기존"
    date: str = ""

    @classmethod
    def from_entry(cls, entry: Entry) -> Question | None:
        """Extract question fields from entry body."""
        body = entry.body

        def extract(pattern: str) -> str:
            match = re.search(pattern, body, re.MULTILINE | re.DOTALL)
            return match.group(1).strip() if match else ""

        problem_id = extract(r"\| 문제 ID \| (.+?) \|")
        summary = extract(r"\| 문제 요약 \| (.+?) \|")
        options = extract(r"\| 보기/옵션 \| (.+?) \|")
        answer = extract(r"\| 정답 \| (.+?) \|")
        rationale = extract(r"\| 판별 근거 \| (.+?) \|")
        tags = extract(r"\| 판단 유형 태그 \| (.+?) \|")

        if not (summary and options and answer):
            return None

        return cls(
            entry_id=entry.ident,
            problem_id=problem_id,
            summary=summary,
            options=options,
            answer=answer,
            rationale=rationale,
            tags=tags,
            source=entry.source,
            date=entry.date,
        )


@dataclass
class QuizResult:
    """Record of a single quiz attempt."""
    problem_id: str
    date: str
    correct: bool
    time_spent: float
    user_answer: str


def load_questions(db_path: Path) -> List[Question]:
    """Load all questions from DB."""
    entries = load_entries(db_path)
    questions = []
    seen_ids = set()

    for entry in entries.values():
        if entry.ident in seen_ids:
            continue
        seen_ids.add(entry.ident)

        q = Question.from_entry(entry)
        if q:
            questions.append(q)

    return questions


def save_result(result: QuizResult) -> None:
    """Append quiz result to progress file."""
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with PROGRESS_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(result.__dict__, ensure_ascii=False) + "\n")


def parse_and_normalize_options(options_text: str) -> List[str]:
    """Parse options and return clean list of text without numbers."""
    # Try splitting by number patterns
    patterns = [
        r'\s+(?=\d+\))',      # "1) ... 2) ..."
        r'\s+(?=\([A-D]\))',  # "(A) ... (B) ..."
    ]

    for pattern in patterns:
        parts = re.split(pattern, options_text)
        parts = [p.strip() for p in parts if p.strip()]
        if len(parts) >= 2:
            # Remove leading number/letter from each option
            cleaned = []
            for part in parts:
                cleaned_text = re.sub(r'^(\d+\)|\([A-D]\))\s*', '', part)
                cleaned.append(cleaned_text)
            return cleaned

    # Fallback: return as-is
    return [options_text]


def normalize_answer(answer_text: str) -> str:
    """Extract normalized answer number from various formats."""
    # Match "1번 –" or "(A) –" or just "1"
    match = re.match(r'^(\d+)번?', answer_text) or re.match(r'^\(?([A-D])\)?', answer_text)
    if not match:
        return ""

    ans = match.group(1)
    # Convert A,B,C,D to 1,2,3,4
    if re.match(r'[A-D]', ans):
        return str(ord(ans) - ord('A') + 1)
    return ans


def calculate_priority_scores(questions: List[Question]) -> Dict[str, float]:
    """Calculate priority score for each question based on spaced repetition."""
    if not PROGRESS_FILE.exists():
        return {q.problem_id: 1.0 for q in questions}

    results = {}
    with PROGRESS_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                result = json.loads(line)
                prob_id = result["problem_id"]
                results[prob_id] = result

    scores = {}
    now = datetime.now()

    for q in questions:
        # Find last attempt for this question
        last_result = results.get(q.problem_id)

        if not last_result:
            # Never attempted - highest priority
            scores[q.problem_id] = 10.0
        else:
            # Calculate days since last attempt
            last_date = datetime.fromisoformat(last_result["date"])
            days_ago = (now - last_date).days

            if not last_result["correct"]:
                # Wrong answer - prioritize based on recency
                if days_ago == 0:
                    scores[q.problem_id] = 5.0  # Review same day
                elif days_ago <= 1:
                    scores[q.problem_id] = 8.0  # Review next day (high priority)
                elif days_ago <= 3:
                    scores[q.problem_id] = 6.0  # Review within 3 days
                else:
                    scores[q.problem_id] = 7.0  # Old mistakes need review
            else:
                # Correct answer - space out reviews
                if days_ago < 1:
                    scores[q.problem_id] = 0.5  # Just reviewed
                elif days_ago < 7:
                    scores[q.problem_id] = 1.0  # Recently correct
                elif days_ago < 14:
                    scores[q.problem_id] = 2.0  # Medium spacing
                else:
                    scores[q.problem_id] = 3.0  # Long-term review

    return scores


def run_quiz(questions: List[Question], count: int, tag_filter: str | None = None, source_filter: str | None = None, use_spaced_repetition: bool = False) -> None:
    """Run interactive quiz session."""
    # Filter by tag if specified
    if tag_filter:
        questions = [q for q in questions if tag_filter.lower() in q.tags.lower()]
        if not questions:
            print(f"⚠️  No questions found with tag '{tag_filter}'")
            return

    # Filter by source if specified
    if source_filter:
        questions = [q for q in questions if q.source == source_filter]
        if not questions:
            print(f"⚠️  No questions found with source '{source_filter}'")
            return

    # Sample questions
    if count > len(questions):
        print(f"⚠️  Only {len(questions)} questions available, showing all.")
        count = len(questions)

    if use_spaced_repetition:
        # Use spaced repetition to prioritize questions
        scores = calculate_priority_scores(questions)
        # Weighted random selection
        weights = [scores.get(q.problem_id, 1.0) for q in questions]
        quiz_set = random.choices(questions, weights=weights, k=min(count, len(questions)))
    else:
        quiz_set = random.sample(questions, count)

    print(f"\n{'='*60}")
    print(f"📚 CPSM Module 3 Quiz - {count}문제")
    if tag_filter:
        print(f"🏷️  Tag Filter: {tag_filter}")
    if source_filter:
        print(f"📦 Source Filter: {source_filter}")
    if use_spaced_repetition:
        print(f"🧠 Spaced Repetition Mode: 활성화")
    print(f"{'='*60}\n")

    correct_count = 0

    for idx, q in enumerate(quiz_set, 1):
        print(f"\n━━━ 문제 {idx}/{count} ━━━")
        print(f"🆔 {q.problem_id}")
        print(f"📋 {q.summary}\n")

        # Parse and normalize options for display
        options = parse_and_normalize_options(q.options)
        print("보기:")
        for i, opt_text in enumerate(options, 1):
            print(f"  {i}. {opt_text}")
        print()

        start_time = time.time()

        try:
            user_input = input("답 (1~4 숫자): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n\n🛑 Quiz interrupted.")
            return

        elapsed = time.time() - start_time

        # Normalize correct answer (handle both "1번" and "(A)" formats)
        correct_num = normalize_answer(q.answer)

        is_correct = user_input == correct_num

        if is_correct:
            print("✅ 정답!")
            correct_count += 1
        else:
            # Show answer in normalized format (1, 2, 3, 4)
            print(f"❌ 오답. 정답: {correct_num}번 - {q.answer.split('–', 1)[-1].strip() if '–' in q.answer else q.answer}")

        print(f"\n💡 근거:\n{q.rationale}")

        # Save result
        result = QuizResult(
            problem_id=q.problem_id,
            date=datetime.now().isoformat(),
            correct=is_correct,
            time_spent=round(elapsed, 1),
            user_answer=user_input,
        )
        save_result(result)

        # Wait for user to continue
        if idx < len(quiz_set):
            try:
                input("\n[Enter를 눌러 다음 문제로...]")
            except (EOFError, KeyboardInterrupt):
                print("\n\n🛑 Quiz stopped.")
                return

    # Final score
    print(f"\n{'='*60}")
    print(f"🎯 최종 점수: {correct_count}/{count} ({correct_count*100//count}%)")
    print(f"{'='*60}\n")
    print(f"📊 진도 기록: {PROGRESS_FILE}")


def list_tags(questions: List[Question]) -> None:
    """Show all available tags."""
    tags = set()
    for q in questions:
        for tag in q.tags.split(","):
            tags.add(tag.strip())

    print("Available tags:")
    for tag in sorted(tags):
        count = sum(1 for q in questions if tag.lower() in q.tags.lower())
        print(f"  - {tag} ({count} questions)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Interactive quiz mode for CPSM Module 3."
    )
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=5,
        help="Number of questions (default: 5)",
    )
    parser.add_argument(
        "-t", "--tag",
        help="Filter by tag (e.g., Alignment, Risk)",
    )
    parser.add_argument(
        "--source",
        choices=["기존", "시뮬레이션"],
        help="Filter by source: 기존 or 시뮬레이션",
    )
    parser.add_argument(
        "--list-tags",
        action="store_true",
        help="Show all available tags",
    )
    parser.add_argument(
        "-s", "--spaced",
        action="store_true",
        help="Use spaced repetition (prioritize weak/new questions)",
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

    if not questions:
        print("[error] No questions found in database.")
        sys.exit(1)

    if args.list_tags:
        list_tags(questions)
        return

    run_quiz(questions, args.count, args.tag, args.source, args.spaced)


if __name__ == "__main__":
    main()

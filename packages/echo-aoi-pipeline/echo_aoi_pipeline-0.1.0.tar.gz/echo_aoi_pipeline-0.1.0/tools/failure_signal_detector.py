#!/usr/bin/env python3
"""
Failure Signal Detector (Stage 1)
Date: 2025-12-13
Purpose: Detect observable failure signals without correctness judgment
"""

import re
from typing import Dict, List

class FailureSignalDetector:
    """Stage 1: Detect failure signals from model output"""

    def __init__(self):
        self.hedging_words = ['might', 'possibly', 'perhaps', 'could be', 'maybe', 'probably']
        self.verification_keywords = ['check:', 'verify:', 'substitute back:', 'verification:']

    def detect(self, problem_statement: str, model_output: str) -> Dict:
        """
        Detect failure signals without comparing to ground truth
        """

        failure_events = []

        # Self-verification check
        self_verification_score = self._check_self_verification(model_output)
        if self_verification_score == 0.0:
            failure_events.append('SELF_VERIFICATION_FAILED')

        # Contradiction detection
        contradictions = self._detect_contradictions(model_output)
        if contradictions:
            failure_events.append('CONTRADICTION_DETECTED')

        # Undefined symbols
        undefined_symbols = self._detect_undefined_symbols(model_output)
        if undefined_symbols:
            failure_events.append('UNDEFINED_SYMBOL_USED')

        # Logical leaps
        logical_leaps = self._detect_logical_leaps(model_output)
        if logical_leaps:
            failure_events.append('LOGICAL_LEAP_DETECTED')

        # Uncertainty scoring
        uncertainty_score = self._score_uncertainty(model_output)
        if uncertainty_score > 0.5:
            failure_events.append('HIGH_UNCERTAINTY')

        # Incompleteness
        if self._is_incomplete(model_output):
            failure_events.append('INCOMPLETE_OUTPUT')

        # Format violation
        if self._has_format_violation(problem_statement, model_output):
            failure_events.append('FORMAT_VIOLATION')

        return {
            'self_verification_score': self_verification_score,
            'consistency_check': {
                'contradictions': contradictions,
                'undefined_symbols': undefined_symbols,
                'logical_leaps': logical_leaps
            },
            'uncertainty_score': uncertainty_score,
            'failure_events': failure_events
        }

    def _check_self_verification(self, output: str) -> float:
        """Check if output contains verification steps"""
        output_lower = output.lower()

        # Count verification keywords
        verification_present = any(kw in output_lower for kw in self.verification_keywords)

        if not verification_present:
            return 0.0

        # Check if verification passed (simple heuristic)
        verification_failed = any(phrase in output_lower for phrase in [
            'verification failed',
            'check failed',
            'does not satisfy',
            'contradiction'
        ])

        return 0.0 if verification_failed else 1.0

    def _detect_contradictions(self, output: str) -> List[str]:
        """Detect contradictory statements (simplified heuristic)"""
        contradictions = []

        # Check for explicit contradiction keywords
        if re.search(r'(but|however|on the other hand).*contradicts', output.lower()):
            contradictions.append("Explicit contradiction statement detected")

        return contradictions

    def _detect_undefined_symbols(self, output: str) -> List[str]:
        """Detect symbols used without definition (simplified)"""
        undefined = []

        # Simple pattern: look for variables used in equations without introduction
        # This is a heuristic, not perfect
        if re.search(r'[a-z_]\w*.*=', output) and 'where' not in output.lower() and 'let' not in output.lower():
            undefined.append("Potential undefined symbol usage")

        return undefined

    def _detect_logical_leaps(self, output: str) -> List[str]:
        """Detect logical leaps using hedging language"""
        leaps = []

        hedging_patterns = [
            r'(obviously|clearly|trivially)',
            r'(therefore|thus|hence)(?!.*because)',
            r'(it follows that)(?!.*from)',
        ]

        for pattern in hedging_patterns:
            if re.search(pattern, output.lower()):
                leaps.append(f"Logical leap detected: {pattern}")

        return leaps

    def _score_uncertainty(self, output: str) -> float:
        """Score uncertainty from language patterns"""
        output_lower = output.lower()

        # Count hedging words
        hedging_count = sum(1 for word in self.hedging_words if word in output_lower)

        # Check for multiple answers
        multiple_answers = 'or' in output_lower and re.search(r'\d+.*or.*\d+', output)

        # Normalize to [0, 1]
        uncertainty = min(1.0, (hedging_count + (1 if multiple_answers else 0)) / 3.0)

        return uncertainty

    def _is_incomplete(self, output: str) -> bool:
        """Check if solution is incomplete"""
        incomplete_indicators = [
            '...',
            'etc.',
            'and so on',
            'TODO',
            'to be continued'
        ]

        # Check for examples without general formula
        has_examples_only = ('examples:' in output.lower() and 'general formula' not in output.lower())

        return any(indicator in output for indicator in incomplete_indicators) or has_examples_only

    def _has_format_violation(self, problem: str, output: str) -> bool:
        """Check if output format matches problem requirements"""
        problem_lower = problem.lower()
        output_lower = output.lower()

        # Check "all solutions" requirement
        if ('all' in problem_lower and 'solution' in problem_lower):
            if ('example' in output_lower and 'general' not in output_lower):
                return True

        # Check proof requirement
        if 'prove' in problem_lower or 'proof' in problem_lower:
            if 'qed' not in output_lower and 'therefore' not in output_lower:
                return True

        return False

def main():
    # Example usage
    detector = FailureSignalDetector()

    problem = "Find ALL positive integer solutions to x^2 + y^2 - 6 = 4xy where 1 ≤ x ≤ y ≤ 1000"
    output = """
    Examples: (1,1), (2,2), (3,5), (5,13), (8,21)
    Pattern suggests Fibonacci-like recurrence.
    Therefore these are some solutions.
    """

    result = detector.detect(problem, output)

    print("Failure Signal Detection Result:")
    print(f"Self-verification score: {result['self_verification_score']}")
    print(f"Uncertainty score: {result['uncertainty_score']}")
    print(f"Failure events: {result['failure_events']}")
    print(f"Contradictions: {result['consistency_check']['contradictions']}")
    print(f"Logical leaps: {result['consistency_check']['logical_leaps']}")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Math Oracle: Vieta/Pell Equation Verifier
Date: 2025-12-13
Purpose: External solution verifier (no explanation, grading only)
"""

import re
import json
import sys
from typing import List, Tuple, Set

class MathOracle:
    """External oracle for Diophantine equation verification"""

    def __init__(self, equation: str):
        self.equation = equation
        self.ground_truth = self._generate_ground_truth()

    def _generate_ground_truth(self) -> Set[Tuple[int, int]]:
        """Generate all solutions in range [1, 1000]"""

        # For x^2 + y^2 - 6 = 4xy
        # Rearrange: x^2 - 4xy + y^2 = 6
        # This is Vieta jumping / Pell-like structure

        solutions = set()

        # Brute force enumeration (oracle allowed to be inefficient)
        for x in range(1, 1001):
            for y in range(x, 1001):  # x <= y constraint
                if self._verify_solution(x, y):
                    solutions.add((x, y))

        return solutions

    def _verify_solution(self, x: int, y: int) -> bool:
        """Check if (x, y) satisfies equation"""
        # x^2 + y^2 - 6 = 4xy
        return x*x + y*y - 6 == 4*x*y

    def grade(self, model_solutions: List[Tuple[int, int]]) -> dict:
        """
        Grade model output against ground truth.
        Returns: completeness_score, missing, extra (no explanation)
        """

        model_set = set(model_solutions)

        missing = self.ground_truth - model_set
        extra = model_set - self.ground_truth

        if len(self.ground_truth) == 0:
            completeness_score = 1.0 if len(model_set) == 0 else 0.0
        else:
            completeness_score = 1.0 if (missing == set() and extra == set()) else 0.0

        return {
            'completeness_score': completeness_score,
            'ground_truth_count': len(self.ground_truth),
            'model_count': len(model_set),
            'missing_solutions': sorted(list(missing)),
            'extra_solutions': sorted(list(extra)),
            'correct_count': len(self.ground_truth & model_set)
        }

def parse_model_output(output: str) -> List[Tuple[int, int]]:
    """Parse model output to extract solution pairs"""
    # Extract (x, y) pairs from text
    pattern = r'\((\d+),\s*(\d+)\)'
    matches = re.findall(pattern, output)
    return [(int(x), int(y)) for x, y in matches]

def main():
    if len(sys.argv) < 3:
        print("Usage: math_oracle_vieta_pell.py <equation> <model_output_file>")
        sys.exit(1)

    equation = sys.argv[1]
    model_output_file = sys.argv[2]

    with open(model_output_file) as f:
        model_output = f.read()

    oracle = MathOracle(equation)
    model_solutions = parse_model_output(model_output)

    report = oracle.grade(model_solutions)

    # Save report
    report_path = f"{model_output_file}.oracle_report.json"
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))
    print(f"\nReport saved: {report_path}")

if __name__ == '__main__':
    main()

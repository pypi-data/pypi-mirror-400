#!/usr/bin/env python3
"""
Dual Mode Log Comparison Tool
Date: 2025-12-13
Purpose: Compare MODE_A vs MODE_B using 3 metrics (no performance claims)
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, List
from collections import Counter

class DualModeComparator:
    def __init__(self, log_a_path: str, log_b_path: str):
        with open(log_a_path) as f:
            self.log_a = yaml.safe_load(f)['runs']
        with open(log_b_path) as f:
            self.log_b = yaml.safe_load(f)['runs']

        # Validate identical input_id sets
        ids_a = {r['input_id'] for r in self.log_a}
        ids_b = {r['input_id'] for r in self.log_b}
        if ids_a != ids_b:
            raise ValueError("Log files must have identical input_id sets")

        self.input_ids = sorted(ids_a)

    def metric_1_solution_count_change(self) -> Dict:
        """
        Metric 1: Solution count difference (not accuracy)
        """
        results = []

        for input_id in self.input_ids:
            entry_a = next(r for r in self.log_a if r['input_id'] == input_id)
            entry_b = next(r for r in self.log_b if r['input_id'] == input_id)

            count_a = entry_a['final_solution_count']
            count_b = entry_b['final_solution_count']
            delta = count_b - count_a

            results.append({
                'input_id': input_id,
                'count_A': count_a,
                'count_B': count_b,
                'delta': delta
            })

        # Aggregation
        total_increase = sum(r['delta'] for r in results if r['delta'] > 0)
        total_decrease = sum(r['delta'] for r in results if r['delta'] < 0)
        unchanged_count = sum(1 for r in results if r['delta'] == 0)

        return {
            'metric': 'solution_count_change',
            'details': results,
            'aggregation': {
                'total_increase': total_increase,
                'total_decrease': total_decrease,
                'unchanged_count': unchanged_count,
                'increase_count': sum(1 for r in results if r['delta'] > 0),
                'decrease_count': sum(1 for r in results if r['delta'] < 0)
            },
            'forbidden_claim': [
                'MODE_B is more accurate',
                'META improves performance',
                'META is better'
            ],
            'allowed_statement': [
                f"MODE_B emitted {total_increase} more solutions across {len(results)} inputs",
                f"{sum(1 for r in results if r['delta'] > 0)} inputs showed count increase, "
                f"{sum(1 for r in results if r['delta'] < 0)} showed decrease, "
                f"{unchanged_count} unchanged"
            ]
        }

    def metric_2_failure_distribution_change(self) -> Dict:
        """
        Metric 2: Failure class distribution change
        """
        # Build histograms
        histogram_a = Counter(r['failure_class'] for r in self.log_a if r['failure_class'])
        histogram_b = Counter(r['failure_class'] for r in self.log_b if r['failure_class'])

        # All failure classes
        all_classes = sorted(set(histogram_a.keys()) | set(histogram_b.keys()))

        results = []
        for fc in all_classes:
            count_a = histogram_a.get(fc, 0)
            count_b = histogram_b.get(fc, 0)
            delta = count_b - count_a

            results.append({
                'failure_class': fc,
                'count_A': count_a,
                'count_B': count_b,
                'delta': delta
            })

        # Aggregation
        total_failures_a = sum(histogram_a.values())
        total_failures_b = sum(histogram_b.values())
        class_shift_count = sum(1 for r in results if r['delta'] != 0)

        return {
            'metric': 'failure_distribution_change',
            'details': results,
            'aggregation': {
                'total_failures_A': total_failures_a,
                'total_failures_B': total_failures_b,
                'class_shift_count': class_shift_count,
                'class_count': len(all_classes)
            },
            'forbidden_claim': [
                'MODE_B reduces failures',
                'META catches more errors',
                'Failure rate improvement'
            ],
            'allowed_statement': [
                f"{class_shift_count} failure classes shifted distribution, "
                f"{len(all_classes) - class_shift_count} unchanged"
            ]
        }

    def metric_3_bypass_reduction(self) -> Dict:
        """
        Metric 3: Bypass attempt count difference
        """
        bypass_a = sum(1 for r in self.log_a if r.get('position_c_status') == 'bypass')
        bypass_b = sum(1 for r in self.log_b if r.get('position_c_status') == 'bypass')
        delta = bypass_b - bypass_a

        total_runs_a = len(self.log_a)
        total_runs_b = len(self.log_b)

        return {
            'metric': 'bypass_reduction',
            'details': {
                'bypass_count_A': bypass_a,
                'bypass_count_B': bypass_b,
                'delta': delta
            },
            'aggregation': {
                'bypass_reduction': bypass_a - bypass_b,
                'bypass_percentage_A': bypass_a / total_runs_a if total_runs_a > 0 else 0,
                'bypass_percentage_B': bypass_b / total_runs_b if total_runs_b > 0 else 0
            },
            'forbidden_claim': [
                'MODE_B is better at enforcement',
                'META prevents bypasses',
                'Bypass prevention improvement'
            ],
            'allowed_statement': [
                f"MODE_B showed {bypass_a - bypass_b} fewer bypass events"
            ]
        }

    def generate_comparison_table_markdown(self) -> str:
        """
        Generate markdown comparison table
        """
        lines = []
        lines.append("# Dual Mode Comparison Table")
        lines.append("")
        lines.append("| input_id | mode_A_term | mode_B_term | mode_A_posC | mode_B_posC | mode_A_failure | mode_B_failure | count_A | count_B | delta |")
        lines.append("|----------|-------------|-------------|-------------|-------------|----------------|----------------|---------|---------|-------|")

        for input_id in self.input_ids:
            entry_a = next(r for r in self.log_a if r['input_id'] == input_id)
            entry_b = next(r for r in self.log_b if r['input_id'] == input_id)

            lines.append(
                f"| {input_id} "
                f"| {entry_a.get('termination_type', 'N/A')} "
                f"| {entry_b.get('termination_type', 'N/A')} "
                f"| {entry_a.get('position_c_status', 'N/A')} "
                f"| {entry_b.get('position_c_status', 'N/A')} "
                f"| {entry_a.get('failure_class', 'none')} "
                f"| {entry_b.get('failure_class', 'none')} "
                f"| {entry_a['final_solution_count']} "
                f"| {entry_b['final_solution_count']} "
                f"| {entry_b['final_solution_count'] - entry_a['final_solution_count']:+d} |"
            )

        return "\n".join(lines)

    def run_comparison(self, output_dir: str):
        """
        Run all 3 metrics and generate outputs
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Metric 1
        metric_1 = self.metric_1_solution_count_change()
        with open(output_path / 'metric_1_solution_count_change.yaml', 'w') as f:
            yaml.dump(metric_1, f, default_flow_style=False, sort_keys=False)

        # Metric 2
        metric_2 = self.metric_2_failure_distribution_change()
        with open(output_path / 'metric_2_failure_distribution_change.yaml', 'w') as f:
            yaml.dump(metric_2, f, default_flow_style=False, sort_keys=False)

        # Metric 3
        metric_3 = self.metric_3_bypass_reduction()
        with open(output_path / 'metric_3_bypass_reduction.yaml', 'w') as f:
            yaml.dump(metric_3, f, default_flow_style=False, sort_keys=False)

        # Comparison table
        table_md = self.generate_comparison_table_markdown()
        with open(output_path / 'comparison_table.md', 'w') as f:
            f.write(table_md)

        print(f"Comparison complete. Results in {output_dir}/")
        print(f"- metric_1_solution_count_change.yaml")
        print(f"- metric_2_failure_distribution_change.yaml")
        print(f"- metric_3_bypass_reduction.yaml")
        print(f"- comparison_table.md")

def main():
    if len(sys.argv) < 3:
        print("Usage: compare_dual_mode_logs.py <log_A_path> <log_B_path> [output_dir]")
        sys.exit(1)

    log_a_path = sys.argv[1]
    log_b_path = sys.argv[2]
    output_dir = sys.argv[3] if len(sys.argv) > 3 else 'proof/comparison_results'

    comparator = DualModeComparator(log_a_path, log_b_path)
    comparator.run_comparison(output_dir)

if __name__ == '__main__':
    main()

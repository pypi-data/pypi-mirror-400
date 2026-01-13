#!/usr/bin/env python3
"""
Failure Probe
Date: 2025-12-13
Purpose: Rule-based failure classification (no interpretation)
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, List, Optional

class FailureProbe:
    def __init__(self, registry_path: str, action_map_path: str):
        with open(registry_path) as f:
            self.registry = yaml.safe_load(f)
        with open(action_map_path) as f:
            self.action_map = yaml.safe_load(f)

        self.priority = self.registry['classification_priority']

    def classify(self,
                 problem_prompt: str,
                 system_response_log: str,
                 contract_violation: bool,
                 termination_type: str) -> Dict:
        """
        Classify failure based on observable signals only.
        Priority order from FAILURE_CLASS_REGISTRY.yaml.
        """

        # Priority 1: Contract violation
        if contract_violation:
            return self._build_result('NONCOMPLIANCE_CONTRACT',
                                     ['contract_violation_flag'])

        # Priority 2: Termination condition
        if termination_type in ['loop', 'timeout'] or 'repeat' in system_response_log.lower():
            return self._build_result('NO_TERMINATION_CONDITION',
                                     ['termination_log'])

        # Priority 3: External fact
        if any(signal in system_response_log.lower() for signal in
               ['requires external', 'lookup', 'unavailable', 'missing fact']):
            return self._build_result('MISSING_EXTERNAL_FACT',
                                     ['external_reference_log'])

        # Priority 4: Conflict
        if self._detect_conflict(system_response_log):
            return self._build_result('RULE_CONFLICT',
                                     ['conflict_statements_log'])

        # Priority 5: Incomplete
        if self._detect_incomplete(problem_prompt, system_response_log):
            return self._build_result('RULE_INCOMPLETE',
                                     ['partial_output_log'])

        # Priority 6: Order dependency
        if any(signal in system_response_log.lower() for signal in
               ['case', 'depends', 'assume', 'ordering']):
            return self._build_result('ORDER_DEPENDENCY',
                                     ['order_dependency_log'])

        # Priority 7: Computation failed
        if any(signal in system_response_log.lower() for signal in
               ['error', 'failed', 'exception']):
            return self._build_result('COMPUTATION_FAILED',
                                     ['computation_error_log'])

        # Priority 8: Ambiguous goal
        return self._build_result('AMBIGUOUS_GOAL',
                                 ['goal_ambiguity_log'])

    def _detect_conflict(self, log: str) -> bool:
        """Detect contradictory statements (observable text only)"""
        # Simple heuristic: look for negation pairs
        lines = log.lower().split('\n')
        for i, line in enumerate(lines):
            if 'no solution' in line or 'impossible' in line:
                for other_line in lines[i+1:]:
                    if 'solution' in other_line and 'no' not in other_line:
                        return True
        return False

    def _detect_incomplete(self, prompt: str, log: str) -> bool:
        """Detect incomplete solution when completeness required"""
        completeness_required = any(req in prompt.lower() for req in
                                   ['all solutions', 'infinite family', 'prove all', 'complete'])

        partial_output = any(signal in log.lower() for signal in
                           ['examples:', 'some solutions', '...', 'partial'])

        no_general_formula = not any(formula in log.lower() for formula in
                                    ['parametrization', 'general formula', 'recurrence'])

        return completeness_required and (partial_output or no_general_formula)

    def _build_result(self, failure_class: str, evidence_refs: List[str]) -> Dict:
        """Build classification result"""
        action_pack_ref = self.action_map['failure_action_mapping'][failure_class]['action_pack']

        return {
            'failure_class': failure_class,
            'evidence_refs': evidence_refs,
            'action_pack_ref': action_pack_ref,
            'operator_required': self._check_operator_required(failure_class)
        }

    def _check_operator_required(self, failure_class: str) -> bool:
        """Check if operator intervention needed"""
        # Operator required for terminal failures or after escalation
        return failure_class in ['NONCOMPLIANCE_CONTRACT']

def main():
    if len(sys.argv) < 5:
        print("Usage: failure_probe.py <problem> <log> <contract_violation> <termination_type>")
        sys.exit(1)

    probe = FailureProbe(
        'spec/FAILURE_CLASS_REGISTRY.yaml',
        'spec/FAILURE_ACTION_MAP.yaml'
    )

    result = probe.classify(
        problem_prompt=sys.argv[1],
        system_response_log=sys.argv[2],
        contract_violation=(sys.argv[3].lower() == 'true'),
        termination_type=sys.argv[4]
    )

    # Append to PHASE5_FAILURE_RUNS.yaml
    output_path = Path('proof/PHASE5_FAILURE_RUNS.yaml')

    if output_path.exists():
        with open(output_path) as f:
            data = yaml.safe_load(f) or {'runs': []}
    else:
        data = {'runs': []}

    data['runs'].append(result)

    with open(output_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    print(yaml.dump(result, default_flow_style=False))

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Error Taxonomy Classifier (Stage 2)
Date: 2025-12-13
Purpose: Classify failures into error classes with retry strategy pointers
"""

from typing import Dict, List

class ErrorTaxonomyClassifier:
    """Stage 2: Classify failures into 12 error classes"""

    def __init__(self):
        # Error classes with priority (1 = highest)
        self.error_classes = {
            'COMPUTATION_ERROR': {'priority': 1, 'retry': 'self_refine'},
            'REASONING_DISCONNECT': {'priority': 2, 'retry': 'tree_of_thought'},
            'PREMISE_MISSING': {'priority': 3, 'retry': 'beam_search'},
            'FORMAT_ERROR': {'priority': 4, 'retry': 'rejection_sampling'},
            'HALLUCINATION': {'priority': 5, 'retry': 'majority_voting'},
            'INCOMPLETE_SOLUTION': {'priority': 6, 'retry': 'self_refine'},
            'CONTRADICTORY_STEPS': {'priority': 7, 'retry': 'tree_of_thought'},
            'UNDEFINED_SYMBOL': {'priority': 8, 'retry': 'self_refine'},
            'LOGICAL_LEAP': {'priority': 9, 'retry': 'tree_of_thought'},
            'VERIFICATION_FAILURE': {'priority': 10, 'retry': 'rejection_sampling'},
            'CONSTRAINT_VIOLATION': {'priority': 11, 'retry': 'majority_voting'},
            'TERMINATION_ERROR': {'priority': 12, 'retry': 'beam_search'}
        }

    def classify(self,
                 failure_events: List[str],
                 model_output: str,
                 problem_statement: str) -> Dict:
        """
        Classify failure into error class based on observable signals
        Priority-ordered rule matching
        """

        # Map failure events to error classes
        event_to_class = {
            'SELF_VERIFICATION_FAILED': 'VERIFICATION_FAILURE',
            'CONTRADICTION_DETECTED': 'CONTRADICTORY_STEPS',
            'UNDEFINED_SYMBOL_USED': 'UNDEFINED_SYMBOL',
            'LOGICAL_LEAP_DETECTED': 'LOGICAL_LEAP',
            'HIGH_UNCERTAINTY': 'HALLUCINATION',
            'INCOMPLETE_OUTPUT': 'INCOMPLETE_SOLUTION',
            'FORMAT_VIOLATION': 'FORMAT_ERROR'
        }

        # Collect candidate classes
        candidates = []
        for event in failure_events:
            if event in event_to_class:
                error_class = event_to_class[event]
                priority = self.error_classes[error_class]['priority']
                candidates.append((error_class, priority))

        # Additional heuristics
        if 'computation' in model_output.lower() or 'calculate' in model_output.lower():
            # Check for computation errors (simple heuristic)
            if any(word in model_output.lower() for word in ['incorrect', 'wrong', 'mistake']):
                candidates.append(('COMPUTATION_ERROR', self.error_classes['COMPUTATION_ERROR']['priority']))

        if 'infinite' in model_output.lower() or 'family' in model_output.lower():
            if 'for all' not in model_output.lower() and 'general' not in model_output.lower():
                candidates.append(('TERMINATION_ERROR', self.error_classes['TERMINATION_ERROR']['priority']))

        # Select highest priority class
        if not candidates:
            # Default to INCOMPLETE_SOLUTION if no specific class matched
            error_class = 'INCOMPLETE_SOLUTION'
            confidence = 0.5
        else:
            # Sort by priority (lower number = higher priority)
            candidates.sort(key=lambda x: x[1])
            error_class = candidates[0][0]
            confidence = 0.95 if len(candidates) == 1 else 0.75

        # Get retry strategy
        retry_strategy = self.error_classes[error_class]['retry']

        # Build evidence
        evidence_refs = [f"Failure events: {failure_events}"]

        # Retry parameters
        retry_parameters = self._get_retry_parameters(retry_strategy)

        return {
            'error_class': error_class,
            'confidence_score': confidence,
            'observable_signals': failure_events,
            'evidence_refs': evidence_refs,
            'recommended_retry_strategy': retry_strategy,
            'retry_parameters': retry_parameters
        }

    def _get_retry_parameters(self, retry_strategy: str) -> Dict:
        """Get default retry parameters for strategy"""
        params = {
            'tree_of_thought': {
                'branching_factor': 3,
                'depth_limit': 5,
                'selection_criterion': 'consistency score'
            },
            'beam_search': {
                'beam_width': 5,
                'scoring_function': 'completion likelihood'
            },
            'rejection_sampling': {
                'sample_count': 10,
                'rejection_criterion': 'format compliance + verification pass'
            },
            'self_refine': {
                'max_iterations': 3,
                'refinement_prompt': 'Review and correct errors'
            },
            'majority_voting': {
                'sample_count': 7,
                'voting_criterion': 'exact match'
            }
        }
        return params.get(retry_strategy, {})

def main():
    # Example usage
    classifier = ErrorTaxonomyClassifier()

    failure_events = [
        'INCOMPLETE_OUTPUT',
        'FORMAT_VIOLATION',
        'LOGICAL_LEAP_DETECTED'
    ]

    model_output = "Examples: (1,1), (2,2), (3,5)..."
    problem = "Find ALL positive integer solutions..."

    result = classifier.classify(failure_events, model_output, problem)

    print("Error Classification Result:")
    print(f"Error class: {result['error_class']}")
    print(f"Confidence: {result['confidence_score']}")
    print(f"Recommended retry: {result['recommended_retry_strategy']}")
    print(f"Retry parameters: {result['retry_parameters']}")

if __name__ == '__main__':
    main()

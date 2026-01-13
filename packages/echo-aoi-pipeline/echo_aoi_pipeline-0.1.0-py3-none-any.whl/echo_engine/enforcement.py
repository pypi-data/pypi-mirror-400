"""
Evidence Enforcement - No Execution Without Logging

This module enforces mandatory evidence logging for all Echo judgments.

Design principle:
    If evidence cannot be logged, execution MUST NOT proceed.

This is not a performance optimization.
This is not a feature flag.
This is a legal requirement (EU AI Act Art. 12).
"""

import json
import functools
from typing import Any, Callable, Dict, Optional, List
from pathlib import Path
from datetime import datetime, timezone

try:
    from .evidence_store import (
        JudgmentEvidence,
        get_evidence_store,
        generate_run_id,
        compute_input_hash,
        compute_policy_hash,
    )
except ImportError:
    from evidence_store import (
        JudgmentEvidence,
        get_evidence_store,
        generate_run_id,
        compute_input_hash,
        compute_policy_hash,
    )


class EvidenceEnforcementError(Exception):
    """
    Raised when evidence logging fails.

    This exception blocks execution - it is NOT recoverable.
    """
    pass


class JudgmentResult:
    """
    Result of a judgment execution with evidence attached.

    All Echo judgments must return this type.
    """

    def __init__(self, run_id: str, decision: str, allowed: bool, evidence: JudgmentEvidence):
        self.run_id = run_id
        self.decision = decision  # ALLOW | STOP | PAUSE_HUMAN
        self.allowed = allowed
        self.evidence = evidence

    def __repr__(self):
        return f"JudgmentResult(run_id={self.run_id}, decision={self.decision}, allowed={self.allowed})"


def enforce_evidence_logging(
    system_version: str = "echo-v1.0",
    policy_config_path: Optional[Path] = None
):
    """
    Decorator: Enforce evidence logging for judgment functions.

    Usage:
        @enforce_evidence_logging(system_version="echo-v1.0")
        def execute_judgment(input_text: str) -> JudgmentResult:
            # Your judgment logic here
            pass

    Args:
        system_version: Echo version identifier (git hash or semver)
        policy_config_path: Path to policy configuration file

    The decorated function MUST:
    - Accept `input_text` as first argument
    - Return a dict with keys: decision, allowed, summary, reason_code, eu_reqs

    Evidence is ALWAYS logged, even on exception.
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(input_text: str, *args, **kwargs) -> JudgmentResult:
            # Load policy configuration
            policy_config = _load_policy_config(policy_config_path)

            # Generate run ID
            run_id = generate_run_id()

            # Initialize evidence record
            evidence = JudgmentEvidence(
                run_id=run_id,
                timestamp=datetime.now(timezone.utc).isoformat(),
                input_hash=compute_input_hash(input_text),
                input_summary="",  # Will be filled from result
                risk_level="minimal-risk",  # Default
                prohibited_practice_check=False,
                stage1_decision="UNKNOWN",
                stage1_reason_code="",
                stage1_eu_reqs="[]",
                stage2_used=False,
                stage2_model_version=None,
                human_gate_triggered=False,
                human_reviewer_id=None,
                human_approval_timestamp=None,
                human_justification=None,
                execution_allowed=False,
                decision_trace_path=None,
                stop_or_gate_path=None,
                human_gate_path=None,
                system_version=system_version,
                policy_hash=compute_policy_hash(policy_config),
                eu_act_compliant=True,
                violations="[]",
                created_at=""
            )

            try:
                # Execute judgment function
                result = func(input_text, *args, **kwargs)

                # Extract result fields
                decision = result.get("decision", "UNKNOWN")
                allowed = result.get("allowed", False)
                summary = result.get("summary", input_text[:500])
                reason_code = result.get("reason_code", "")
                eu_reqs = result.get("eu_reqs", [])
                risk_level = result.get("risk_level", "minimal-risk")
                prohibited_check = result.get("prohibited_practice_check", False)
                stage2_used = result.get("stage2_used", False)
                stage2_model = result.get("stage2_model_version", None)
                human_gate = result.get("human_gate_triggered", False)
                human_reviewer = result.get("human_reviewer_id", None)
                human_approval_ts = result.get("human_approval_timestamp", None)
                human_justification = result.get("human_justification", None)

                # Update evidence record
                evidence.input_summary = summary
                evidence.risk_level = risk_level
                evidence.prohibited_practice_check = prohibited_check
                evidence.stage1_decision = decision
                evidence.stage1_reason_code = reason_code
                evidence.stage1_eu_reqs = json.dumps(eu_reqs)
                evidence.stage2_used = stage2_used
                evidence.stage2_model_version = stage2_model
                evidence.human_gate_triggered = human_gate
                evidence.human_reviewer_id = human_reviewer
                evidence.human_approval_timestamp = human_approval_ts
                evidence.human_justification = human_justification
                evidence.execution_allowed = allowed
                evidence.eu_act_compliant = _validate_compliance(evidence)
                evidence.violations = json.dumps(_detect_violations(evidence))

                # Append evidence to store
                _append_evidence(evidence)

                # Return judgment result with evidence attached
                return JudgmentResult(
                    run_id=run_id,
                    decision=decision,
                    allowed=allowed,
                    evidence=evidence
                )

            except Exception as e:
                # Log exception as violation
                evidence.eu_act_compliant = False
                evidence.violations = json.dumps([
                    {
                        "type": "EXECUTION_EXCEPTION",
                        "message": str(e),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                ])

                # CRITICAL: Still log evidence even on failure
                try:
                    _append_evidence(evidence)
                except Exception as log_error:
                    # Evidence logging failed - this is a FATAL error
                    raise EvidenceEnforcementError(
                        f"FATAL: Evidence logging failed during exception handling. "
                        f"Original error: {e}. Logging error: {log_error}"
                    ) from log_error

                # Re-raise original exception
                raise

        return wrapper
    return decorator


def _load_policy_config(policy_path: Optional[Path]) -> Dict[str, Any]:
    """Load policy configuration from file or use default."""
    if policy_path and policy_path.exists():
        import yaml
        with open(policy_path, 'r') as f:
            return yaml.safe_load(f)
    else:
        # Default policy
        return {
            "version": "1.0",
            "prohibited_practices_enabled": True,
            "human_oversight_required": True,
            "record_keeping_enabled": True
        }


def _validate_compliance(evidence: JudgmentEvidence) -> bool:
    """
    Validate that evidence record complies with EU AI Act requirements.

    Returns:
        True if compliant, False otherwise
    """

    # REQ-PROH-* (Prohibited practices must STOP)
    if evidence.prohibited_practice_check:
        if evidence.execution_allowed:
            return False  # Violation: prohibited practice not blocked

    # REQ-HO-* (Human gate must have approval)
    if evidence.human_gate_triggered:
        if evidence.execution_allowed and not evidence.human_reviewer_id:
            return False  # Violation: executed without human approval

    # REQ-RK-* (Record keeping must be complete)
    if not evidence.run_id or not evidence.timestamp:
        return False  # Violation: incomplete record

    # All checks passed
    return True


def _detect_violations(evidence: JudgmentEvidence) -> List[Dict[str, str]]:
    """
    Detect specific EU AI Act violations in evidence record.

    Returns:
        List of violation descriptions
    """
    violations = []

    # REQ-PROH-001: Block prohibited practices
    if evidence.prohibited_practice_check and evidence.execution_allowed:
        violations.append({
            "requirement": "REQ-PROH-001",
            "type": "PROHIBITED_PRACTICE_NOT_BLOCKED",
            "message": f"Prohibited practice check passed but execution allowed (reason: {evidence.stage1_reason_code})"
        })

    # REQ-HO-001: Mandatory human approval
    if evidence.human_gate_triggered and evidence.execution_allowed and not evidence.human_reviewer_id:
        violations.append({
            "requirement": "REQ-HO-001",
            "type": "MISSING_HUMAN_APPROVAL",
            "message": "Human gate triggered but no reviewer ID recorded"
        })

    # REQ-RK-001: Decision trace completeness
    if not evidence.run_id or not evidence.timestamp or not evidence.stage1_decision:
        violations.append({
            "requirement": "REQ-RK-001",
            "type": "INCOMPLETE_DECISION_TRACE",
            "message": "Missing required fields: run_id, timestamp, or decision"
        })

    return violations


def _append_evidence(evidence: JudgmentEvidence) -> None:
    """
    Append evidence to store.

    Raises:
        EvidenceEnforcementError: If logging fails
    """
    try:
        store = get_evidence_store()
        store.append(evidence)
    except Exception as e:
        raise EvidenceEnforcementError(
            f"Failed to append evidence (run_id={evidence.run_id}): {e}"
        ) from e


# Example usage
if __name__ == "__main__":
    print("Testing Evidence Enforcement...")

    @enforce_evidence_logging(system_version="test-v1.0")
    def test_judgment(input_text: str) -> Dict[str, Any]:
        """Test judgment function."""
        # Simulate judgment logic
        if "unsafe" in input_text.lower():
            return {
                "decision": "STOP",
                "allowed": False,
                "summary": "Unsafe execution detected",
                "reason_code": "UNSAFE_EXECUTION",
                "eu_reqs": ["REQ-PROH-001", "REQ-RK-002"],
                "prohibited_practice_check": True
            }
        else:
            return {
                "decision": "ALLOW",
                "allowed": True,
                "summary": "Safe execution",
                "reason_code": "SAFE",
                "eu_reqs": ["REQ-RK-001"]
            }

    # Test 1: Safe execution
    result1 = test_judgment("Generate a report")
    print(f"✅ Test 1: {result1}")
    print(f"   Evidence: {result1.evidence.run_id}")
    print(f"   Compliant: {result1.evidence.eu_act_compliant}")

    # Test 2: Unsafe execution (blocked)
    result2 = test_judgment("Execute unsafe code")
    print(f"✅ Test 2: {result2}")
    print(f"   Evidence: {result2.evidence.run_id}")
    print(f"   Compliant: {result2.evidence.eu_act_compliant}")

    # Test 3: Exception handling
    @enforce_evidence_logging(system_version="test-v1.0")
    def failing_judgment(input_text: str) -> Dict[str, Any]:
        raise ValueError("Simulated failure")

    try:
        result3 = failing_judgment("Test input")
    except ValueError:
        print("✅ Test 3: Exception logged as expected")

    # Verify evidence was logged
    store = get_evidence_store()
    print(f"\nTotal evidence records: {store.count_total()}")
    print(f"Violations: {store.count_violations()}")

    print("\n✅ Evidence Enforcement test complete!")

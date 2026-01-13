#!/usr/bin/env python3
"""
EU AI Act Compliance Validator

Maps actual Echo execution logs to EU AI Act requirements.
Validates that system behavior matches required controls.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import yaml


class EUActComplianceValidator:
    """Validates Echo execution logs against EU AI Act requirements."""

    def __init__(self, spec_dir: Path):
        self.spec_dir = spec_dir
        self.requirements = self._load_requirements()
        self.evidence_spec = self._load_evidence_spec()
        self.scenarios = self._load_scenarios()

    def _load_requirements(self) -> List[Dict]:
        """Load EU AI Act requirements inventory."""
        req_file = self.spec_dir / "EU_AI_ACT_REQ_INVENTORY_v1.yaml"
        if not req_file.exists():
            raise FileNotFoundError(f"Requirements file not found: {req_file}")

        with open(req_file, 'r') as f:
            return yaml.safe_load(f)

    def _load_evidence_spec(self) -> List[Dict]:
        """Load evidence specification."""
        ev_file = self.spec_dir / "EU_AI_ACT_EVIDENCE_SPEC_v1.yaml"
        if not ev_file.exists():
            raise FileNotFoundError(f"Evidence spec not found: {ev_file}")

        with open(ev_file, 'r') as f:
            return yaml.safe_load(f)

    def _load_scenarios(self) -> List[Dict]:
        """Load scenario seeds."""
        sc_file = self.spec_dir / "EU_AI_ACT_SCENARIO_SEEDS_v1.yaml"
        if not sc_file.exists():
            raise FileNotFoundError(f"Scenarios file not found: {sc_file}")

        with open(sc_file, 'r') as f:
            return yaml.safe_load(f)

    def validate_execution_log(self, log_path: Path) -> Dict[str, Any]:
        """
        Validate a single execution log against EU AI Act requirements.

        Returns validation result with:
        - matched_requirements: List of REQ-* matched
        - decision_compliance: Whether decision follows required behavior
        - evidence_quality: Whether log contains required fields
        - violations: Any detected violations
        """
        result = {
            "log_path": str(log_path),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "matched_requirements": [],
            "decision_compliance": True,
            "evidence_quality": "complete",
            "violations": [],
            "details": {}
        }

        # Read execution log
        if not log_path.exists():
            result["violations"].append(f"Log file not found: {log_path}")
            result["decision_compliance"] = False
            return result

        with open(log_path, 'r') as f:
            log_entries = [json.loads(line) for line in f if line.strip()]

        if not log_entries:
            result["violations"].append("Empty execution log")
            result["evidence_quality"] = "missing"
            return result

        # Analyze each log entry
        for entry in log_entries:
            self._validate_entry(entry, result)

        return result

    def _validate_entry(self, entry: Dict, result: Dict):
        """Validate a single log entry against requirements."""

        # Check for required decision trace fields
        required_fields = ["request_id", "timestamp", "stage1_decision", "execution_allowed"]
        missing_fields = [f for f in required_fields if f not in entry]
        if missing_fields:
            result["violations"].append(f"Missing required fields: {missing_fields}")
            result["evidence_quality"] = "incomplete"

        # Map reason_code to EU AI Act requirements
        reason_code = entry.get("reason_code", "UNKNOWN")
        stage1_decision = entry.get("stage1_decision", "unknown")
        execution_allowed = entry.get("execution_allowed", True)

        # PII / Data Protection
        if reason_code == "EXTERNAL_DATA_TRANSMISSION":
            result["matched_requirements"].append("REQ-HR-003")  # Data governance and PII protection
            result["matched_requirements"].append("REQ-RK-001")  # Decision trace completeness
            result["matched_requirements"].append("REQ-RK-002")  # Stop or gate log integrity

            # Validate: should have blocked
            if execution_allowed:
                result["violations"].append(
                    f"REQ-HR-003 violation: PII exfiltration not blocked (request_id={entry.get('request_id')})"
                )
                result["decision_compliance"] = False
            else:
                result["details"][entry["request_id"]] = {
                    "requirement": "REQ-HR-003",
                    "decision": "STOP",
                    "compliant": True,
                    "reason": "PII transmission blocked as required"
                }

        # Unsafe Execution
        elif reason_code == "UNSAFE_EXECUTION":
            result["matched_requirements"].append("REQ-PROH-001")  # Block subliminal/manipulative
            result["matched_requirements"].append("REQ-HR-009")  # Cybersecurity and tamper detection
            result["matched_requirements"].append("REQ-RK-002")  # Stop or gate log integrity

            # Validate: should have blocked
            if execution_allowed:
                result["violations"].append(
                    f"REQ-PROH-001 violation: Unsafe execution not blocked (request_id={entry.get('request_id')})"
                )
                result["decision_compliance"] = False
            else:
                result["details"][entry["request_id"]] = {
                    "requirement": "REQ-PROH-001",
                    "decision": "STOP",
                    "compliant": True,
                    "reason": "Unsafe execution blocked as required"
                }

        # Approval Queue (Human Oversight)
        elif reason_code == "APPROVAL_REQUIRED" or stage1_decision == "pause":
            result["matched_requirements"].append("REQ-HO-001")  # Mandatory human approval
            result["matched_requirements"].append("REQ-HO-003")  # Escalation playbooks
            result["matched_requirements"].append("REQ-RK-003")  # Human oversight justification log

            # Validate: should have paused
            if execution_allowed and not entry.get("human_approved"):
                result["violations"].append(
                    f"REQ-HO-001 violation: Executed without human approval (request_id={entry.get('request_id')})"
                )
                result["decision_compliance"] = False
            else:
                result["details"][entry["request_id"]] = {
                    "requirement": "REQ-HO-001",
                    "decision": "PAUSE_HUMAN",
                    "compliant": True,
                    "reason": "Human gate enforced as required"
                }

        # Stage 2 usage implies high-risk classification
        if entry.get("stage2_used"):
            result["matched_requirements"].append("REQ-HR-001")  # High-risk classification gate
            result["matched_requirements"].append("REQ-HR-005")  # Logging fidelity
            result["matched_requirements"].append("REQ-HR-006")  # Transparency cues

        # Hash presence = record keeping
        if "hash" in entry:
            result["matched_requirements"].append("REQ-RK-001")  # Decision trace completeness
            result["matched_requirements"].append("REQ-CC-001")  # Model update gating (via hash)

    def validate_directory(self, log_dir: Path) -> Dict[str, Any]:
        """Validate all execution logs in a directory."""

        results = {
            "validation_timestamp": datetime.utcnow().isoformat() + "Z",
            "total_logs": 0,
            "compliant_logs": 0,
            "total_violations": 0,
            "requirements_exercised": set(),
            "log_results": []
        }

        # Find all execution.jsonl files
        log_files = list(log_dir.rglob("execution.jsonl"))
        results["total_logs"] = len(log_files)

        for log_file in log_files:
            log_result = self.validate_execution_log(log_file)
            results["log_results"].append(log_result)

            if log_result["decision_compliance"] and not log_result["violations"]:
                results["compliant_logs"] += 1

            results["total_violations"] += len(log_result["violations"])
            results["requirements_exercised"].update(log_result["matched_requirements"])

        # Convert set to sorted list for JSON serialization
        results["requirements_exercised"] = sorted(list(results["requirements_exercised"]))

        # Summary
        results["summary"] = {
            "compliance_rate": f"{results['compliant_logs']}/{results['total_logs']}",
            "requirements_covered": f"{len(results['requirements_exercised'])}/34",
            "violations_found": results["total_violations"],
            "status": "PASS" if results["total_violations"] == 0 else "FAIL"
        }

        return results

    def generate_compliance_report(self, validation_results: Dict[str, Any], output_path: Path):
        """Generate a human-readable compliance report."""

        with open(output_path, 'w') as f:
            f.write("# EU AI Act Compliance Validation Report\n\n")
            f.write(f"**Generated:** {validation_results['validation_timestamp']}\n\n")

            f.write("## Summary\n\n")
            summary = validation_results['summary']
            f.write(f"- **Status:** {summary['status']}\n")
            f.write(f"- **Compliance Rate:** {summary['compliance_rate']}\n")
            f.write(f"- **Requirements Covered:** {summary['requirements_covered']}\n")
            f.write(f"- **Violations Found:** {summary['violations_found']}\n\n")

            f.write("## Requirements Exercised\n\n")
            for req in validation_results['requirements_exercised']:
                f.write(f"- {req}\n")
            f.write("\n")

            f.write("## Log Analysis\n\n")
            for log_result in validation_results['log_results']:
                f.write(f"### {Path(log_result['log_path']).parent.name}\n\n")
                f.write(f"- **Decision Compliance:** {'✅ PASS' if log_result['decision_compliance'] else '❌ FAIL'}\n")
                f.write(f"- **Evidence Quality:** {log_result['evidence_quality']}\n")
                f.write(f"- **Requirements Matched:** {len(log_result['matched_requirements'])}\n")

                if log_result['violations']:
                    f.write("\n**Violations:**\n")
                    for violation in log_result['violations']:
                        f.write(f"- ❌ {violation}\n")

                if log_result['details']:
                    f.write("\n**Details:**\n")
                    for req_id, detail in log_result['details'].items():
                        f.write(f"- Request `{req_id}`: {detail['requirement']} → {detail['decision']} ({detail['reason']})\n")

                f.write("\n")

            f.write("## Coverage Gap Analysis\n\n")
            total_reqs = 34
            covered = len(validation_results['requirements_exercised'])
            uncovered = total_reqs - covered

            f.write(f"- **Total Requirements:** {total_reqs}\n")
            f.write(f"- **Exercised:** {covered}\n")
            f.write(f"- **Not Yet Tested:** {uncovered}\n\n")

            if uncovered > 0:
                f.write("**Note:** Some requirements may only be triggered by specific scenarios.\n")
                f.write("Run additional test cases to increase coverage.\n\n")

            f.write("---\n\n")
            f.write("*This report validates actual Echo execution logs against EU AI Act requirements.*\n")
            f.write("*See `proof/eu_ai_act_sim/` for full specification.*\n")


def main():
    """CLI entry point."""

    spec_dir = Path("proof/eu_ai_act_sim")
    log_dir = Path("echo-judgment-pipeline/examples")
    output_dir = Path("proof/eu_ai_act_sim")

    print("🔍 EU AI Act Compliance Validator")
    print(f"Spec directory: {spec_dir}")
    print(f"Log directory: {log_dir}")
    print()

    # Initialize validator
    try:
        validator = EUActComplianceValidator(spec_dir)
    except FileNotFoundError as e:
        print(f"❌ Error: {e}")
        print("Run: python tools/generate_eu_act_sim_spec.py --out proof/eu_ai_act_sim --validate")
        sys.exit(1)

    # Validate all logs
    print("Validating execution logs...")
    results = validator.validate_directory(log_dir)

    # Save JSON results
    json_output = output_dir / "EU_AI_ACT_VALIDATION_RESULTS.json"
    with open(json_output, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"✅ JSON results: {json_output}")

    # Generate report
    report_output = output_dir / "EU_AI_ACT_COMPLIANCE_REPORT.md"
    validator.generate_compliance_report(results, report_output)
    print(f"✅ Compliance report: {report_output}")

    # Print summary
    print()
    print("Summary:")
    print(f"  Status: {results['summary']['status']}")
    print(f"  Compliance: {results['summary']['compliance_rate']}")
    print(f"  Coverage: {results['summary']['requirements_covered']}")
    print(f"  Violations: {results['summary']['violations_found']}")

    # Exit code
    sys.exit(0 if results['summary']['status'] == 'PASS' else 1)


if __name__ == "__main__":
    main()

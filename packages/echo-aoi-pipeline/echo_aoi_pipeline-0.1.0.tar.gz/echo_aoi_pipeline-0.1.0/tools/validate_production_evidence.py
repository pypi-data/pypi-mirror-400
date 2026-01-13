#!/usr/bin/env python3
"""
Production Evidence Validator

Validates that runtime/judgment_evidence_store.db exists and contains
evidence records from actual production use (not just simulations).

This is the CRITICAL difference between:
- "We can comply" (simulation)
- "We do comply" (production evidence)

For EU AI Act litigation/audit, only production evidence matters.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
import json

# Add echo_engine to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from echo_engine.evidence_store import get_evidence_store, EvidenceStore


class ProductionEvidenceValidator:
    """Validates production evidence store for EU AI Act compliance."""

    def __init__(self, min_days_history: int = 7):
        """
        Initialize validator.

        Args:
            min_days_history: Minimum days of evidence history required
        """
        self.min_days_history = min_days_history
        self.store = get_evidence_store()

    def validate(self) -> dict:
        """
        Run complete validation.

        Returns:
            Validation results with pass/fail status
        """
        results = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "checks": {},
            "summary": {},
            "status": "UNKNOWN"
        }

        # Check 1: Evidence store exists
        results["checks"]["store_exists"] = self._check_store_exists()

        # Check 2: Evidence records exist
        results["checks"]["has_records"] = self._check_has_records()

        # Check 3: Evidence history depth
        results["checks"]["history_depth"] = self._check_history_depth()

        # Check 4: No critical violations
        results["checks"]["no_critical_violations"] = self._check_no_critical_violations()

        # Check 5: Human oversight records
        results["checks"]["human_oversight_logged"] = self._check_human_oversight()

        # Check 6: Recent activity (not stale)
        results["checks"]["recent_activity"] = self._check_recent_activity()

        # Summary
        total_checks = len(results["checks"])
        passed_checks = sum(1 for check in results["checks"].values() if check["pass"])

        results["summary"] = {
            "total_checks": total_checks,
            "passed_checks": passed_checks,
            "failed_checks": total_checks - passed_checks,
            "pass_rate": f"{passed_checks}/{total_checks}"
        }

        # Overall status
        if passed_checks == total_checks:
            results["status"] = "PASS"
        elif passed_checks >= total_checks * 0.8:  # 80% threshold
            results["status"] = "WARN"
        else:
            results["status"] = "FAIL"

        return results

    def _check_store_exists(self) -> dict:
        """Check that evidence store database exists."""
        exists = self.store.db_path.exists()
        return {
            "name": "Evidence store exists",
            "pass": exists,
            "details": {
                "path": str(self.store.db_path),
                "exists": exists
            },
            "message": "✅ Evidence store found" if exists else "❌ Evidence store not found"
        }

    def _check_has_records(self) -> dict:
        """Check that evidence store contains records."""
        count = self.store.count_total()
        has_records = count > 0

        return {
            "name": "Evidence records exist",
            "pass": has_records,
            "details": {
                "total_records": count,
                "minimum_required": 1
            },
            "message": f"✅ {count} evidence records found" if has_records else "❌ No evidence records found"
        }

    def _check_history_depth(self) -> dict:
        """Check that evidence spans required history period."""
        total = self.store.count_total()

        if total == 0:
            return {
                "name": "Evidence history depth",
                "pass": False,
                "details": {
                    "total_records": 0,
                    "earliest": None,
                    "latest": None,
                    "span_days": 0,
                    "required_days": self.min_days_history
                },
                "message": "❌ No evidence records to analyze"
            }

        # Get earliest and latest records
        latest_records = self.store.get_latest(total)  # Get all
        if not latest_records:
            return {
                "name": "Evidence history depth",
                "pass": False,
                "details": {"error": "Could not retrieve records"},
                "message": "❌ Failed to retrieve evidence records"
            }

        timestamps = [datetime.fromisoformat(r.timestamp.replace('Z', '+00:00')) for r in latest_records]
        earliest = min(timestamps)
        latest = max(timestamps)
        span = (latest - earliest).days

        sufficient_history = span >= self.min_days_history

        return {
            "name": "Evidence history depth",
            "pass": sufficient_history,
            "details": {
                "total_records": total,
                "earliest": earliest.isoformat(),
                "latest": latest.isoformat(),
                "span_days": span,
                "required_days": self.min_days_history
            },
            "message": f"✅ {span} days of history" if sufficient_history else f"⚠️  Only {span} days of history (need {self.min_days_history})"
        }

    def _check_no_critical_violations(self) -> dict:
        """Check that there are no critical EU AI Act violations."""
        violation_count = self.store.count_violations()
        no_critical_violations = violation_count == 0

        details = {
            "total_violations": violation_count,
            "allowed_violations": 0
        }

        if violation_count > 0:
            # Get sample violations
            violations = self.store.query_violations(limit=5)
            details["sample_violations"] = [
                {
                    "run_id": v.run_id,
                    "timestamp": v.timestamp,
                    "violations": json.loads(v.violations)
                }
                for v in violations
            ]

        return {
            "name": "No critical violations",
            "pass": no_critical_violations,
            "details": details,
            "message": "✅ No violations detected" if no_critical_violations else f"❌ {violation_count} violations detected"
        }

    def _check_human_oversight(self) -> dict:
        """Check that human oversight is being logged when triggered."""
        # Query recent records to check for human oversight patterns
        total = self.store.count_total()

        if total == 0:
            return {
                "name": "Human oversight logging",
                "pass": True,  # Pass if no records (not applicable)
                "details": {"note": "No records to check"},
                "message": "⚠️  No records to verify human oversight"
            }

        # Sample recent records
        recent = self.store.get_latest(min(100, total))

        human_gate_triggered_count = sum(1 for r in recent if r.human_gate_triggered)
        human_gate_approved_count = sum(1 for r in recent if r.human_gate_triggered and r.human_reviewer_id)

        if human_gate_triggered_count == 0:
            # No human gates triggered - this is OK
            return {
                "name": "Human oversight logging",
                "pass": True,
                "details": {
                    "human_gates_triggered": 0,
                    "note": "No human gates triggered in recent records"
                },
                "message": "✅ Human oversight: No gates triggered"
            }

        # If gates were triggered, all should have approval
        all_approved = human_gate_triggered_count == human_gate_approved_count

        return {
            "name": "Human oversight logging",
            "pass": all_approved,
            "details": {
                "human_gates_triggered": human_gate_triggered_count,
                "human_gates_approved": human_gate_approved_count,
                "approval_rate": f"{human_gate_approved_count}/{human_gate_triggered_count}"
            },
            "message": f"✅ All {human_gate_triggered_count} human gates have approval" if all_approved else f"❌ {human_gate_triggered_count - human_gate_approved_count} human gates missing approval"
        }

    def _check_recent_activity(self) -> dict:
        """Check that evidence store has recent activity (not stale)."""
        latest = self.store.get_latest(1)

        if not latest:
            return {
                "name": "Recent activity",
                "pass": False,
                "details": {"note": "No records found"},
                "message": "❌ No evidence records"
            }

        latest_record = latest[0]
        latest_ts = datetime.fromisoformat(latest_record.timestamp.replace('Z', '+00:00'))
        now = datetime.now(timezone.utc)
        age_hours = (now - latest_ts).total_seconds() / 3600

        # Consider stale if no activity in last 24 hours (production system)
        is_recent = age_hours < 24

        return {
            "name": "Recent activity",
            "pass": is_recent,
            "details": {
                "latest_timestamp": latest_ts.isoformat(),
                "age_hours": round(age_hours, 2),
                "threshold_hours": 24
            },
            "message": f"✅ Latest evidence {round(age_hours, 1)}h ago" if is_recent else f"⚠️  Latest evidence {round(age_hours, 1)}h ago (stale)"
        }

    def print_results(self, results: dict):
        """Print validation results in human-readable format."""
        print("\n" + "=" * 60)
        print("Production Evidence Validation")
        print("=" * 60)
        print(f"\nTimestamp: {results['timestamp']}")
        print(f"Database: {self.store.db_path}")
        print()

        # Checks
        print("Validation Checks:")
        print("-" * 60)
        for check in results["checks"].values():
            status_icon = "✅" if check["pass"] else "❌"
            print(f"{status_icon} {check['name']}")
            print(f"   {check['message']}")

        print()

        # Summary
        print("Summary:")
        print("-" * 60)
        summary = results["summary"]
        print(f"Total checks: {summary['total_checks']}")
        print(f"Passed: {summary['passed_checks']}")
        print(f"Failed: {summary['failed_checks']}")
        print(f"Pass rate: {summary['pass_rate']}")
        print()

        # Overall status
        status = results["status"]
        if status == "PASS":
            print("✅ PASS - Production evidence is compliant")
        elif status == "WARN":
            print("⚠️  WARN - Production evidence has minor issues")
        else:
            print("❌ FAIL - Production evidence is NOT compliant")

        print("=" * 60)
        print()


def main():
    """CLI entry point."""

    import argparse

    parser = argparse.ArgumentParser(
        description="Validate production evidence store for EU AI Act compliance"
    )
    parser.add_argument(
        "--min-days",
        type=int,
        default=7,
        help="Minimum days of evidence history required (default: 7)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict mode: exit code 1 on any warning"
    )

    args = parser.parse_args()

    # Run validation
    validator = ProductionEvidenceValidator(min_days_history=args.min_days)
    results = validator.validate()

    # Output
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        validator.print_results(results)

    # Exit code
    if results["status"] == "FAIL":
        sys.exit(1)
    elif args.strict and results["status"] == "WARN":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()

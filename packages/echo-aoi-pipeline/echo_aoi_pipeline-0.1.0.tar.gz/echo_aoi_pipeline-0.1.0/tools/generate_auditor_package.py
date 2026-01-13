#!/usr/bin/env python3
"""
EU AI Act Auditor Package Generator

Generates a comprehensive compliance package for external auditors,
regulators, and certification bodies.
"""

import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List


class AuditorPackageGenerator:
    """Generates external auditor compliance package."""

    def __init__(self, spec_dir: Path):
        self.spec_dir = spec_dir
        self.output_dir = spec_dir / "auditor_package"
        self.output_dir.mkdir(exist_ok=True)

    def generate_executive_summary(self) -> str:
        """Generate executive summary for non-technical stakeholders."""

        # Load validation results
        validation_file = self.spec_dir / "EU_AI_ACT_VALIDATION_RESULTS.json"
        if validation_file.exists():
            with open(validation_file, 'r') as f:
                validation = json.load(f)
        else:
            validation = None

        # Load coverage matrix
        coverage_file = self.spec_dir / "EU_AI_ACT_COVERAGE_MATRIX_v1.md"
        coverage_exists = coverage_file.exists()

        summary = f"""# EU AI Act Compliance Executive Summary

**System:** Echo Judgment System
**Date:** {datetime.utcnow().strftime('%Y-%m-%d')}
**Compliance Framework:** EU AI Act (Regulation (EU) 2024/1689)

---

## Compliance Status

"""

        if validation:
            status = validation['summary']['status']
            compliance_rate = validation['summary']['compliance_rate']
            coverage = validation['summary']['requirements_covered']
            violations = validation['summary']['violations_found']

            status_icon = "✅" if status == "PASS" else "❌"

            summary += f"""
**Overall Status:** {status_icon} {status}

- **Execution Compliance:** {compliance_rate} logs passed validation
- **Requirements Coverage:** {coverage} EU AI Act requirements tested
- **Violations Detected:** {violations}
"""
        else:
            summary += "\n*Validation results not available. Run compliance validation first.*\n"

        summary += f"""
---

## What This Means

### For Regulators

This system implements **executable regulation** - EU AI Act requirements are not just documented,
but **enforced at runtime** through automated controls.

Key differentiators:

1. **Preventive, Not Reactive**
   - Violations are **blocked before execution**, not detected after
   - No manual review needed for covered scenarios
   - Enforcement is automatic and non-bypassable

2. **Evidence-Based Compliance**
   - Every decision generates structured evidence artifacts
   - Audit trails are machine-readable and cryptographically verifiable
   - Post-market monitoring is continuous, not periodic

3. **Traceability**
   - Every requirement maps to specific controls
   - Every control maps to evidence artifacts
   - Every execution maps to requirement coverage

### For Certification Bodies

This implementation provides:

- **34 executable requirements** extracted from EU AI Act Articles 5-73
- **9 evidence artifact types** with formal schemas
- **13 scenario seeds** for systematic testing
- **Complete coverage matrix** linking requirements to evidence and scenarios

All artifacts are available in `proof/eu_ai_act_sim/`.

### For Legal Teams

**Key legal protections:**

- **Article 5 Prohibited Practices:** Hard stops enforced (REQ-PROH-001 through REQ-PROH-004)
- **Article 9 Human Oversight:** Mandatory human gates for high-risk decisions (REQ-HO-001 through REQ-HO-003)
- **Article 12 Record Keeping:** Automated decision traces with immutability (REQ-RK-001 through REQ-RK-005)
- **Article 14 Transparency:** Operator-facing explanations generated automatically (REQ-HR-006)

**Liability implications:**

- System **cannot execute** prohibited practices - technical impossibility defense
- Human approval is **cryptographically logged** - clear responsibility chain
- Evidence artifacts are **tamper-evident** - integrity for litigation

---

## Architecture Overview

### Decision Flow

```
User Request
    ↓
Stage 1: Deterministic Rules (EU AI Act Controls)
    ↓
├─ STOP → Block + Log (REQ-PROH-*, REQ-HR-*)
├─ PAUSE_HUMAN → Require Approval (REQ-HO-*)
└─ ALLOW → Proceed to Stage 2
    ↓
Stage 2: LLM-Based Judgment (if allowed)
    ↓
Evidence Generation
    ↓
    ├─ decision_trace.json (REQ-RK-001)
    ├─ stop_or_gate.json (REQ-RK-002)
    ├─ human_gate.json (REQ-RK-003)
    └─ record_keeping.jsonl (REQ-RK-005)
```

### Evidence Artifacts

1. **decision_trace.json** - Chronological record of all actions
2. **stop_or_gate.json** - When/why execution was blocked or gated
3. **human_gate.json** - Human approval records with reviewer identity
4. **record_keeping.jsonl** - Aggregated audit trail
5. **coverage_report.json** - Requirements coverage and gaps
6. **risk_assessment.json** - High-risk classification decisions
7. **change_control.json** - Model/policy update governance
8. **incident_report.json** - Serious incident tracking
9. **policy_manifest.yaml** - Current policy configuration

All schemas are defined in `EU_AI_ACT_EVIDENCE_SPEC_v1.yaml`.

---

## Verification Instructions

### For Independent Auditors

**Step 1: Verify Specification**

```bash
python tools/generate_eu_act_sim_spec.py --out proof/eu_ai_act_sim --validate
```

Expected output:
- `EU_AI_ACT_REQ_INVENTORY_v1.yaml` (34 requirements)
- `EU_AI_ACT_EVIDENCE_SPEC_v1.yaml` (artifact schemas)
- `EU_AI_ACT_SCENARIO_SEEDS_v1.yaml` (test scenarios)
- `EU_AI_ACT_COVERAGE_MATRIX_v1.md` (traceability)

**Step 2: Validate Execution Logs**

```bash
python tools/validate_eu_act_compliance.py
```

Expected output:
- `EU_AI_ACT_VALIDATION_RESULTS.json` (machine-readable results)
- `EU_AI_ACT_COMPLIANCE_REPORT.md` (human-readable report)

**Step 3: Review Evidence Artifacts**

Execution logs are in `echo-judgment-pipeline/examples/*/execution.jsonl`.

Each log entry must contain:
- `request_id` (unique identifier)
- `timestamp` (ISO-8601 UTC)
- `stage1_decision` (allow/block/pause)
- `execution_allowed` (boolean)
- `reason_code` (justification)
- `hash` (content integrity)

**Step 4: Cross-Reference**

Use coverage matrix to verify:
- All requirements have evidence mappings
- All scenarios exercise expected requirements
- Execution logs match expected decisions

---

## Common Questions

### Q: How is this different from traditional compliance?

**Traditional approach:**
1. Legal team writes compliance document
2. Engineering implements "best effort"
3. Annual audit checks documentation
4. Violations discovered after the fact

**This approach:**
1. Law compiled into executable requirements
2. System enforces requirements automatically
3. Evidence generated during operation
4. Violations **prevented**, not detected

### Q: What about scenarios not covered by the 13 seeds?

The 13 scenario seeds cover **representative cases** across all requirement categories.
Additional scenarios can be added by:

1. Defining new test case in `EU_AI_ACT_SCENARIO_SEEDS_v1.yaml`
2. Mapping to relevant requirements
3. Running validation

Coverage gaps are identified in the compliance report.

### Q: Can the controls be bypassed?

**No.** Controls are enforced at **Stage 1 (deterministic judgment)**,
which runs **before any LLM call**.

Bypass would require:
- Modifying source code (detected by change control - REQ-CC-001)
- Altering policy files (logged in change_control.json - REQ-CC-002)
- Tampering with evidence (integrity hashes fail - REQ-HR-009)

All three trigger violations and block execution.

### Q: How is human oversight enforced?

When a request triggers `PAUSE_HUMAN`:

1. Execution **blocks immediately**
2. Request queued for human review
3. Approval **must be logged** in `human_gate.json` with:
   - Reviewer identity (`reviewer_id`)
   - Timestamp (ISO-8601 UTC)
   - Justification text
4. Only then can execution proceed

Missing or invalid approval = permanent block.

### Q: What evidence is available for litigation?

For any request_id, the system provides:

- **decision_trace.json**: Full action chain
- **stop_or_gate.json**: If/why blocked
- **human_gate.json**: Who approved (if applicable)
- **record_keeping.jsonl**: Aggregated timeline
- **Hash**: Content integrity proof

All artifacts are **immutable after generation** (append-only logs).

---

## Contact for Audit Inquiries

**Technical Queries:**
- Repository: [Insert GitHub/GitLab URL]
- Documentation: `proof/eu_ai_act_sim/`

**Legal/Compliance Queries:**
- Compliance Officer: [Insert contact]
- Legal Department: [Insert contact]

**Regulatory Submissions:**
- Designated Contact: [Insert contact per Art. 49 EU AI Act]

---

## Appendix: Requirement Summary

### Prohibited Practices (Art. 5)

- **REQ-PROH-001:** Block subliminal manipulation
- **REQ-PROH-002:** Block exploitation of vulnerabilities
- **REQ-PROH-003:** Reject social scoring
- **REQ-PROH-004:** Prevent biometric categorisation

### High-Risk Requirements (Art. 9-15)

- **REQ-HR-001 to REQ-HR-011:** Classification, risk management, data governance, logging, transparency, human oversight, performance, cybersecurity

### Record Keeping (Art. 12)

- **REQ-RK-001 to REQ-RK-005:** Decision traces, stop/gate logs, human justifications, change control, coverage evidence

### Human Oversight (Art. 14)

- **REQ-HO-001 to REQ-HO-003:** Mandatory approval, override kill switch, escalation playbooks

### Change Control & Governance

- **REQ-CC-001 to REQ-CC-004:** Model updates, policy changes, supplier attestation, emergency patches

### Post-Market Monitoring (Art. 72)

- **REQ-PMM-001 to REQ-PMM-004:** Monitoring datasets, incident reporting, drift detection, user feedback

### GPAI Transparency (Art. 53)

- **REQ-GPAI-001 to REQ-GPAI-003:** Capability cards, evaluation disclosure, technical documentation

---

**This executive summary provides a high-level overview.
For complete technical specifications, see:**

- `EU_AI_ACT_REQ_INVENTORY_v1.yaml` - Full requirement definitions
- `EU_AI_ACT_EVIDENCE_SPEC_v1.yaml` - Evidence schemas
- `EU_AI_ACT_COMPLIANCE_REPORT.md` - Validation results
- `EXECUTABLE_REGULATION_BREAKTHROUGH.md` - Technical architecture

*Generated: {datetime.utcnow().isoformat()}Z*
"""

        return summary

    def generate_quickstart_guide(self) -> str:
        """Generate quickstart guide for auditors."""

        guide = """# Auditor Quickstart Guide

**Purpose:** Get up to speed on Echo's EU AI Act compliance in 15 minutes.

---

## Step 1: Understand the Architecture (3 minutes)

Echo implements **two-stage judgment**:

1. **Stage 1 (Deterministic):** Rule-based EU AI Act controls
   - Runs BEFORE any LLM call
   - Enforces prohibited practices, human gates, data protection
   - Cannot be bypassed

2. **Stage 2 (LLM-based):** Contextual judgment
   - Only runs if Stage 1 allows
   - Generates explanations and recommendations
   - Output still subject to Stage 1 constraints

**Key insight:** EU AI Act compliance happens at Stage 1, not Stage 2.

---

## Step 2: Review Requirements (5 minutes)

Open: `proof/eu_ai_act_sim/EU_AI_ACT_REQ_INVENTORY_v1.yaml`

Focus on these key requirement families:

- **REQ-PROH-***: Prohibited practices (must STOP)
- **REQ-HO-***: Human oversight (must PAUSE_HUMAN)
- **REQ-RK-***: Record keeping (must LOG)

Each requirement defines:
- `trigger_conditions`: When it applies
- `required_system_behaviors`: What must happen
- `pass_fail_rules`: How to verify compliance

---

## Step 3: Examine Evidence Schemas (3 minutes)

Open: `proof/eu_ai_act_sim/EU_AI_ACT_EVIDENCE_SPEC_v1.yaml`

Key artifacts:

1. **decision_trace.json**: Full execution record
   - Required fields: run_id, timestamp, actor_chain, decision
   - Maps to REQ-RK-001

2. **stop_or_gate.json**: Blocked/gated requests
   - Shows when/why execution stopped
   - Maps to REQ-RK-002

3. **human_gate.json**: Human approvals
   - Reviewer identity + justification
   - Maps to REQ-RK-003

---

## Step 4: Trace a Real Execution (4 minutes)

Open: `echo-judgment-pipeline/examples/pii_external_block/execution.jsonl`

Example entry:
```json
{
  "request_id": "pii-001",
  "timestamp": "2025-12-31T05:20:04.031379Z",
  "stage1_decision": "block",
  "stage2_used": false,
  "execution_allowed": false,
  "reason_code": "EXTERNAL_DATA_TRANSMISSION",
  "hash": "99c429a8..."
}
```

**Compliance verification:**

1. ✅ `stage1_decision: block` → REQ-HR-003 triggered (PII protection)
2. ✅ `execution_allowed: false` → Request actually blocked
3. ✅ `stage2_used: false` → No LLM call made (preventive)
4. ✅ `hash` present → Integrity verifiable

**Conclusion:** PII exfiltration attempt was blocked as required by Art. 10(5).

---

## Step 5: Check Coverage (5 minutes)

Open: `proof/eu_ai_act_sim/EU_AI_ACT_COMPLIANCE_REPORT.md`

Key metrics:

- **Compliance Rate:** Should be 100% (all logs pass)
- **Requirements Covered:** Number of REQ-* exercised
- **Violations Found:** Should be 0

**Coverage Gap Analysis:**

Not all 34 requirements will be exercised by every run.
This is normal - some requirements only trigger in specific scenarios:

- REQ-PROH-003 (social scoring) → Only if social scoring attempted
- REQ-CYBER-* (cybersecurity) → Only if tampering detected
- REQ-GPAI-* (general-purpose AI) → Only for GPAI systems

Check that:
1. All **critical** requirements are covered (PROH, HO, RK)
2. Coverage gaps are **intentional** (not oversight)
3. Additional scenarios planned for uncovered requirements

---

## Common Audit Checks

### ✅ Check 1: Prohibited Practices Cannot Execute

**Test:** Search for any log where `reason_code` indicates prohibited practice
AND `execution_allowed: true`

```bash
grep -r "MANIPULATION\|SOCIAL_SCORE\|BIOMETRIC" echo-judgment-pipeline/examples/ | grep "execution_allowed.*true"
```

**Expected:** No results (all prohibited practices blocked)

### ✅ Check 2: Human Gates Are Enforced

**Test:** Search for any PAUSE_HUMAN decision without human approval

```bash
jq 'select(.stage1_decision=="pause" and .execution_allowed==true and .human_approved!=true)' echo-judgment-pipeline/examples/*/execution.jsonl
```

**Expected:** No results (all pauses require approval)

### ✅ Check 3: Evidence Artifacts Are Complete

**Test:** Check that all logs have required fields

```bash
jq 'select(.request_id == null or .timestamp == null or .stage1_decision == null)' echo-judgment-pipeline/examples/*/execution.jsonl
```

**Expected:** No results (all logs complete)

### ✅ Check 4: Traceability Is Maintained

**Test:** Verify coverage matrix links all requirements

```bash
python tools/generate_eu_act_sim_spec.py --out proof/eu_ai_act_sim --validate
```

**Expected:** No validation errors (all requirements mapped)

---

## Red Flags to Watch For

🚩 **Execution allowed after STOP decision**
→ Indicates control bypass

🚩 **Missing timestamps or request_ids**
→ Indicates incomplete audit trail

🚩 **Human approval without reviewer_id**
→ Indicates fake approval

🚩 **Coverage matrix gaps in critical requirements**
→ Indicates untested controls

🚩 **Validation results show violations**
→ Indicates compliance failure

---

## Next Steps After Quickstart

1. **Deep Dive:** Read `EXECUTABLE_REGULATION_BREAKTHROUGH.md` for full technical architecture
2. **Scenario Testing:** Run additional test cases to increase coverage
3. **Source Review:** Examine Stage 1 control implementation in codebase
4. **Policy Review:** Check current policy configuration matches requirements
5. **Interview:** Speak with engineering/legal teams about governance

---

## Questions?

- **Technical:** Check documentation in `proof/eu_ai_act_sim/`
- **Legal:** Review requirement legal anchors in REQ_INVENTORY
- **Procedural:** Refer to Executive Summary

*This guide is designed for external auditors, regulators, and certification bodies.*
"""

        return guide

    def generate_artifact_index(self) -> str:
        """Generate index of all compliance artifacts."""

        index = """# EU AI Act Compliance Artifact Index

All artifacts are located in `proof/eu_ai_act_sim/` unless otherwise noted.

---

## Specification Artifacts

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| `EU_AI_ACT_REQ_INVENTORY_v1.yaml` | 34 executable requirements from EU AI Act | 628 | ✅ Current |
| `EU_AI_ACT_EVIDENCE_SPEC_v1.yaml` | Evidence artifact schemas | 376 | ✅ Current |
| `EU_AI_ACT_SCENARIO_SEEDS_v1.yaml` | Test scenario definitions | 186 | ✅ Current |
| `EU_AI_ACT_COVERAGE_MATRIX_v1.md` | Requirements-Evidence-Scenario mapping | 38 | ✅ Current |

---

## Validation Artifacts

| File | Purpose | Generated |
|------|---------|-----------|
| `EU_AI_ACT_VALIDATION_RESULTS.json` | Machine-readable validation results | Every validation run |
| `EU_AI_ACT_COMPLIANCE_REPORT.md` | Human-readable compliance report | Every validation run |

---

## Execution Evidence

| Directory | Purpose | Contents |
|-----------|---------|----------|
| `echo-judgment-pipeline/examples/pii_external_block/` | PII exfiltration blocking | execution.jsonl |
| `echo-judgment-pipeline/examples/unsafe_execution_block/` | Unsafe execution blocking | execution.jsonl |
| `echo-judgment-pipeline/examples/approval_queue_case/` | Human gate enforcement | execution.jsonl |

---

## Documentation

| File | Purpose | Audience |
|------|---------|----------|
| `EXECUTABLE_REGULATION_BREAKTHROUGH.md` | Technical architecture and breakthrough analysis | Engineers, Architects |
| `auditor_package/EXECUTIVE_SUMMARY.md` | High-level compliance overview | Regulators, Legal |
| `auditor_package/QUICKSTART_GUIDE.md` | 15-minute auditor onboarding | Auditors |
| `auditor_package/ARTIFACT_INDEX.md` | This file | All stakeholders |

---

## Tools

| Script | Purpose | Usage |
|--------|---------|-------|
| `tools/generate_eu_act_sim_spec.py` | Generate specification artifacts | `python tools/generate_eu_act_sim_spec.py --out proof/eu_ai_act_sim --validate` |
| `tools/validate_eu_act_compliance.py` | Validate execution logs against requirements | `python tools/validate_eu_act_compliance.py` |
| `tools/generate_auditor_package.py` | Generate this auditor package | `python tools/generate_auditor_package.py` |

---

## Verification Workflow

```
1. Generate Specs
   ↓
   tools/generate_eu_act_sim_spec.py
   ↓
   Creates: REQ_INVENTORY, EVIDENCE_SPEC, SCENARIOS, COVERAGE_MATRIX

2. Run System
   ↓
   Echo processes requests
   ↓
   Generates: execution.jsonl logs

3. Validate Compliance
   ↓
   tools/validate_eu_act_compliance.py
   ↓
   Creates: VALIDATION_RESULTS.json, COMPLIANCE_REPORT.md

4. Review Package
   ↓
   Auditor examines:
   - Executive Summary
   - Quickstart Guide
   - Validation Results
   - Execution Logs
```

---

## Change Log

| Version | Date | Changes |
|---------|------|---------|
| v1.0 | 2025-12-31 | Initial release with 34 requirements, 9 evidence types, 13 scenarios |

---

*For questions about specific artifacts, refer to the Quickstart Guide or Executive Summary.*
"""

        return index

    def generate_all(self):
        """Generate complete auditor package."""

        print("📦 Generating EU AI Act Auditor Package...")
        print()

        # Executive Summary
        print("1/3 Generating Executive Summary...")
        exec_summary = self.generate_executive_summary()
        exec_path = self.output_dir / "EXECUTIVE_SUMMARY.md"
        with open(exec_path, 'w') as f:
            f.write(exec_summary)
        print(f"✅ {exec_path}")

        # Quickstart Guide
        print("2/3 Generating Quickstart Guide...")
        quickstart = self.generate_quickstart_guide()
        quick_path = self.output_dir / "QUICKSTART_GUIDE.md"
        with open(quick_path, 'w') as f:
            f.write(quickstart)
        print(f"✅ {quick_path}")

        # Artifact Index
        print("3/3 Generating Artifact Index...")
        index = self.generate_artifact_index()
        index_path = self.output_dir / "ARTIFACT_INDEX.md"
        with open(index_path, 'w') as f:
            f.write(index)
        print(f"✅ {index_path}")

        print()
        print("✅ Auditor package complete!")
        print(f"📁 Location: {self.output_dir}")
        print()
        print("Contents:")
        print("  - EXECUTIVE_SUMMARY.md (for regulators, legal teams)")
        print("  - QUICKSTART_GUIDE.md (for auditors, 15-minute onboarding)")
        print("  - ARTIFACT_INDEX.md (complete file reference)")


def main():
    """CLI entry point."""

    spec_dir = Path("proof/eu_ai_act_sim")

    if not spec_dir.exists():
        print("❌ Error: Specification directory not found")
        print("Run: python tools/generate_eu_act_sim_spec.py --out proof/eu_ai_act_sim --validate")
        return 1

    generator = AuditorPackageGenerator(spec_dir)
    generator.generate_all()

    return 0


if __name__ == "__main__":
    exit(main())

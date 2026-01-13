#!/usr/bin/env python3
"""
Validate ARAL gate fields in PR body.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

VOID_TYPES = {
    "SESSION",
    "AUTOMATION",
    "ROLEINHERITANCE",
    "APPROVALBYIMPLICATION",
    "AI-MEDIATED",
    "ENVIRONMENTTRANSITION",
    "POSTHOCRESPONSIBILITY",
}

BANNED_EVIDENCE = [
    "약관 동의",
    "사용자 책임",
    "초기 설정",
    "ai 추천",
    "관례상",
]
REQUIRED_FIELDS = ["judgment_id", "timestamp", "actor", "scope", "decision", "evidence_link"]

# Session expiration requirements (for UAT permits in PASS evidence)
SESSION_REQUIRED_FIELDS = [
    "expires_at",
    "max_session_duration_seconds",
    "reconfirm_interval_seconds",
    "last_reconfirmed_at",
]

OUTPUT_FILE = Path("aral_gate_output.json")


def write_output(result: str, void_type: str, evidence: str) -> None:
    payload = {"result": result, "void_type": void_type, "evidence": evidence}
    OUTPUT_FILE.write_text(json.dumps(payload, ensure_ascii=False))


def fail(message: str, void_type: str = "", evidence: str = "") -> None:
    write_output("FAIL", void_type, evidence)
    print(f"ARAL_GATE_RESULT=FAIL:{message}")
    sys.exit(1)


def main() -> None:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        fail("Missing GITHUB_EVENT_PATH.")
    with open(event_path, "r", encoding="utf-8") as handle:
        event = json.load(handle)
    pr = event.get("pull_request") or {}
    body = pr.get("body") or ""

    def extract(label: str) -> str:
        pattern = re.compile(rf"^{label}:(.*)$", re.IGNORECASE | re.MULTILINE)
        match = pattern.search(body)
        return match.group(1).strip() if match else ""

    gate_value = extract("ARAL Gate")
    if not gate_value:
        fail("Missing 'ARAL Gate' field.")

    evidence = extract("Judgment Evidence")
    void_type_line = extract("VoidType (if FAIL)")

    gate_value_upper = gate_value.strip().upper()
    void_type_normalized = void_type_line.strip()
    result = ""

    if gate_value_upper.startswith("PASS"):
        if not evidence:
            fail("Judgment Evidence is required for PASS.")
        lower_evidence = evidence.lower()
        for keyword in BANNED_EVIDENCE:
            if keyword.lower() in lower_evidence:
                fail(f"Evidence contains prohibited phrase ({keyword}).", evidence=evidence)
        for field in REQUIRED_FIELDS:
            if f"{field}=" not in lower_evidence and f"\"{field}\"" not in lower_evidence:
                fail(f"Judgment Evidence missing required field '{field}'.", evidence=evidence)

        # Additional check: If evidence mentions UAT permit, require session control fields
        if "uat" in lower_evidence and "permit" in lower_evidence:
            if "permit_version" in lower_evidence and ("2.0" in evidence or "v2" in lower_evidence):
                # Check for session control fields in v2.0 permits
                for session_field in SESSION_REQUIRED_FIELDS:
                    if session_field not in lower_evidence:
                        fail(
                            f"UAT Permit v2.0 evidence missing session control field '{session_field}' (SESSION_VOID prevention required).",
                            void_type="SESSION",
                            evidence=evidence
                        )

        result = "PASS"
        write_output(result, "", evidence)
        print(f"ARAL_GATE_RESULT={result}")
        return

    if gate_value_upper.startswith("FAIL"):
        if not void_type_normalized:
            fail("VoidType must be specified when Gate is FAIL.", evidence=evidence)
        normalized_key = void_type_normalized.replace(" ", "").replace("_", "").upper()
        if normalized_key not in VOID_TYPES:
            fail(f"Unknown VoidType '{void_type_line}'.", evidence=evidence)
        result = f"FAIL:{void_type_normalized}"
        write_output("FAIL", void_type_normalized, evidence)
        print(f"ARAL_GATE_RESULT={result}")
        sys.exit(1)

    fail("ARAL Gate must be PASS or FAIL.", evidence=evidence)


if __name__ == "__main__":
    main()

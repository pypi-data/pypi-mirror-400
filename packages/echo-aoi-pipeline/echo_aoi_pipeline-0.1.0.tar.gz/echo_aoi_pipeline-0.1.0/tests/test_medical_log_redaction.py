"""
Test: Medical roles must NOT emit PHI or clinical interpretation
"""

import re

FORBIDDEN_KEYS = [
    "lab_value",
    "result_value",
    "diagnosis",
    "impression",
    "prescription",
    "recommendation",
    "questionnaire_answer",
    "consent_contents",
]

FORBIDDEN_PATTERNS = [
    r"\bdiagnos(e|is|tic)\b",
    r"\bprescrib(e|ed|ing)\b",
    r"\btreat(ment|ing)?\b",
    r"\brecommend(ation|ed|s)?\b",
]

def _flatten(obj):
    if obj is None:
        return ""
    if isinstance(obj, (str, int, float, bool)):
        return str(obj)
    if isinstance(obj, dict):
        return " ".join([_flatten(k) + " " + _flatten(v) for k, v in obj.items()])
    if isinstance(obj, list):
        return " ".join(_flatten(x) for x in obj)
    return str(obj)

def assert_no_phi_like_content(role_result_dict):
    flat = _flatten(role_result_dict).lower()

    for k in FORBIDDEN_KEYS:
        assert k.lower() not in flat, f"Forbidden key/content found: {k}"

    for pat in FORBIDDEN_PATTERNS:
        assert re.search(pat, flat) is None, f"Forbidden pattern found: {pat}"

def test_medical_roles_do_not_emit_phi_like_content():
    """
    This test is structural: ensure our role results never include forbidden content.
    Use representative example payloads similar to RoleResult.
    """
    examples = [
        {
            "success": True,
            "goal_achieved": True,
            "output_data": {"row_count": 12, "results_present": True},
            "config_snapshot": {"labs_url": "https://lab.local/results", "date_range_days": 90},
        },
        {
            "success": True,
            "goal_achieved": True,
            "output_data": {"review_required": True, "queue": "clinical-review", "reason_code": "LAB_RESULTS_READY"},
            "config_snapshot": {"queue": "clinical-review"},
        },
    ]

    for ex in examples:
        assert_no_phi_like_content(ex)

def test_medical_roles_metadata_only():
    """Ensure only metadata (counts, status) in output, never actual values"""
    allowed_example = {
        "row_count": 42,
        "results_present": True,
        "table_selector": ".results-table",
        "login_success": True,
        "review_required": True,
    }
    
    # Should NOT raise
    assert_no_phi_like_content({"output_data": allowed_example})

def test_forbidden_content_detected():
    """Verify test catches forbidden content"""
    forbidden_examples = [
        {"output_data": {"diagnosis": "hypertension"}},
        {"output_data": {"lab_value": "120"}},
        {"error": "treatment failed"},
    ]
    
    for example in forbidden_examples:
        try:
            assert_no_phi_like_content(example)
            assert False, f"Should have detected forbidden content in: {example}"
        except AssertionError as e:
            # Expected to fail
            assert "Forbidden" in str(e)

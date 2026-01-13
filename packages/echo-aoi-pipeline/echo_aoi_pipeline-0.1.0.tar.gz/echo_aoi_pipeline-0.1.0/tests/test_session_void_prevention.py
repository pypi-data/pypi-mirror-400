#!/usr/bin/env python3
"""
Test: Session-based Judgment Void Prevention (ARAL Taxonomy Item 1)

Scenario: Hotel TV Netflix
- User A grants permit at T0
- User A logs out at T0+1h
- User B logs in at T0+2h
- Expected: Permit invalid (reconfirmation missed)

This test verifies that the "hotel TV scenario" from ARAL_OVERVIEW.md
is now BLOCKED by UAT Permit v2.0 session control.
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
import tempfile
import yaml

# Add uat to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from uat.enforcement import permit_is_valid_with_reason


def test_hotel_tv_scenario_blocked():
    """
    Test that hotel TV scenario is blocked by session expiration.

    BEFORE v2.0: Permit would remain valid indefinitely
    AFTER v2.0: Permit expires when reconfirmation missed
    """

    # Create a v2.0 permit that expired 2 hours ago
    now = datetime.now(timezone.utc)
    issued_at = now - timedelta(hours=3)
    expires_at = now - timedelta(hours=2)  # Expired 2 hours ago
    last_reconfirmed = issued_at

    permit_data = {
        "uat_autonomy_permit": {
            "valid": True,
            "core_version": "1.0.0",
            "permit_version": "2.0",
            "issued_at": issued_at.isoformat(),
            "grantee": "system:echo-engine",
            "grantor": "human:user-a",
            "session_control": {
                "expires_at": expires_at.isoformat(),
                "max_session_duration_seconds": 21600,  # 6 hours
                "reconfirm_interval_seconds": 3600,     # 1 hour
                "last_reconfirmed_at": last_reconfirmed.isoformat(),
                "grace_period_seconds": 300,
            }
        }
    }

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(permit_data, f)
        temp_path = f.name

    try:
        # Monkey-patch _get_permit_path to use temp file
        import uat.enforcement.permit as permit_module
        original_get_permit_path = permit_module._get_permit_path
        permit_module._get_permit_path = lambda: Path(temp_path)

        # Test: Should be INVALID (expired)
        is_valid, reason = permit_is_valid_with_reason("1.0.0")

        assert not is_valid, "Permit should be invalid (expired)"
        assert "SESSION_VOID" in reason, f"Reason should mention SESSION_VOID, got: {reason}"
        assert "expired" in reason.lower(), f"Reason should mention expiration, got: {reason}"

        print("✅ Test PASSED: Hotel TV scenario is BLOCKED")
        print(f"   Reason: {reason}")

    finally:
        # Restore original function
        permit_module._get_permit_path = original_get_permit_path
        Path(temp_path).unlink()


def test_reconfirmation_missed():
    """
    Test that permit becomes invalid when reconfirmation is missed.

    Scenario:
    - Permit issued at T0
    - Reconfirm interval: 1 hour
    - Last reconfirmed: T0
    - Current time: T0+2h
    - Expected: INVALID (reconfirmation required at T0+1h)
    """

    now = datetime.now(timezone.utc)
    issued_at = now - timedelta(hours=2)
    expires_at = now + timedelta(hours=4)  # Still valid expiration
    last_reconfirmed = issued_at  # Never reconfirmed since issue

    permit_data = {
        "uat_autonomy_permit": {
            "valid": True,
            "core_version": "1.0.0",
            "permit_version": "2.0",
            "issued_at": issued_at.isoformat(),
            "grantee": "system:echo-engine",
            "grantor": "human:user-a",
            "session_control": {
                "expires_at": expires_at.isoformat(),
                "max_session_duration_seconds": 21600,
                "reconfirm_interval_seconds": 3600,  # 1 hour interval
                "last_reconfirmed_at": last_reconfirmed.isoformat(),
                "grace_period_seconds": 300,
            }
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(permit_data, f)
        temp_path = f.name

    try:
        import uat.enforcement.permit as permit_module
        original_get_permit_path = permit_module._get_permit_path
        permit_module._get_permit_path = lambda: Path(temp_path)

        is_valid, reason = permit_is_valid_with_reason("1.0.0")

        assert not is_valid, "Permit should be invalid (reconfirmation missed)"
        assert "SESSION_VOID" in reason, f"Reason should mention SESSION_VOID, got: {reason}"
        assert "Reconfirmation required" in reason, f"Reason should mention reconfirmation, got: {reason}"

        print("✅ Test PASSED: Reconfirmation enforcement works")
        print(f"   Reason: {reason}")

    finally:
        permit_module._get_permit_path = original_get_permit_path
        Path(temp_path).unlink()


def test_valid_permit_with_recent_reconfirmation():
    """
    Test that permit remains valid when properly reconfirmed.

    Scenario:
    - Permit issued at T0-2h
    - Reconfirm interval: 1 hour
    - Last reconfirmed: T0-30min (within interval)
    - Current time: T0
    - Expected: VALID
    """

    now = datetime.now(timezone.utc)
    issued_at = now - timedelta(hours=2)
    expires_at = now + timedelta(hours=4)
    last_reconfirmed = now - timedelta(minutes=30)  # Recent reconfirmation

    permit_data = {
        "uat_autonomy_permit": {
            "valid": True,
            "core_version": "1.0.0",
            "permit_version": "2.0",
            "issued_at": issued_at.isoformat(),
            "grantee": "system:echo-engine",
            "grantor": "human:user-a",
            "session_control": {
                "expires_at": expires_at.isoformat(),
                "max_session_duration_seconds": 21600,
                "reconfirm_interval_seconds": 3600,
                "last_reconfirmed_at": last_reconfirmed.isoformat(),
                "grace_period_seconds": 300,
            }
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(permit_data, f)
        temp_path = f.name

    try:
        import uat.enforcement.permit as permit_module
        original_get_permit_path = permit_module._get_permit_path
        permit_module._get_permit_path = lambda: Path(temp_path)

        is_valid, reason = permit_is_valid_with_reason("1.0.0")

        assert is_valid, f"Permit should be valid (properly reconfirmed), got: {reason}"
        assert reason == "", f"Reason should be empty for valid permit, got: {reason}"

        print("✅ Test PASSED: Valid permit with recent reconfirmation")

    finally:
        permit_module._get_permit_path = original_get_permit_path
        Path(temp_path).unlink()


def test_v1_permit_without_session_control():
    """
    Test that v1.0 permits still work (backward compatibility).

    v1.0 permits don't have session_control, should be allowed.
    """

    now = datetime.now(timezone.utc)
    issued_at = now - timedelta(hours=1)

    permit_data = {
        "uat_autonomy_permit": {
            "valid": True,
            "core_version": "1.0.0",
            "permit_version": "1.0",  # v1.0
            "issued_at": issued_at.isoformat(),
            "grantee": "system:echo-engine",
            "grantor": "human:user-a",
            # No session_control in v1.0
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(permit_data, f)
        temp_path = f.name

    try:
        import uat.enforcement.permit as permit_module
        original_get_permit_path = permit_module._get_permit_path
        permit_module._get_permit_path = lambda: Path(temp_path)

        is_valid, reason = permit_is_valid_with_reason("1.0.0")

        assert is_valid, f"v1.0 permit should be valid (backward compat), got: {reason}"

        print("✅ Test PASSED: v1.0 permit backward compatibility")

    finally:
        permit_module._get_permit_path = original_get_permit_path
        Path(temp_path).unlink()


if __name__ == "__main__":
    print("=" * 70)
    print("SESSION-BASED JUDGMENT VOID PREVENTION TEST")
    print("=" * 70)
    print()

    print("Test 1: Hotel TV Scenario (expired permit)")
    test_hotel_tv_scenario_blocked()
    print()

    print("Test 2: Reconfirmation Enforcement")
    test_reconfirmation_missed()
    print()

    print("Test 3: Valid Permit with Recent Reconfirmation")
    test_valid_permit_with_recent_reconfirmation()
    print()

    print("Test 4: v1.0 Permit Backward Compatibility")
    test_v1_permit_without_session_control()
    print()

    print("=" * 70)
    print("ALL TESTS PASSED: Session void prevention is ACTIVE")
    print("=" * 70)

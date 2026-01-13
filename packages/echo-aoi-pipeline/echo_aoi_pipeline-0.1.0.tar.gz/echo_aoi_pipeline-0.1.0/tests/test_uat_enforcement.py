"""
UAT Enforcement Tests

Fail-fast tests for UAT autonomy permit enforcement.
"""

import pytest
import tempfile
import yaml
from pathlib import Path

from uat.enforcement import (
    enforce_uat_autonomy,
    UATAutonomyDenied,
    permit_exists,
    permit_is_valid,
    UAT_CORE_VERSION,
    get_uat_enforcement_trace,
)


@pytest.fixture
def permit_path(monkeypatch):
    """Mock permit path to temp location"""
    temp_dir = Path(tempfile.mkdtemp())
    permit_file = temp_dir / "UAT_AUTONOMY_PERMIT.yaml"

    # Monkeypatch the permit path function
    def mock_get_permit_path():
        return permit_file

    import uat.enforcement.permit as permit_module
    monkeypatch.setattr(permit_module, "_get_permit_path", mock_get_permit_path)

    yield permit_file

    # Cleanup
    if permit_file.exists():
        permit_file.unlink()
    temp_dir.rmdir()


def test_permit_missing__enforcement_stops(permit_path):
    """Test: No permit → enforcement raises UATAutonomyDenied"""
    # Ensure permit doesn't exist
    assert not permit_path.exists()

    # Enforcement should raise
    with pytest.raises(UATAutonomyDenied) as exc_info:
        enforce_uat_autonomy(UAT_CORE_VERSION)

    assert "Permit not found" in str(exc_info.value)


def test_permit_invalid__enforcement_stops(permit_path):
    """Test: Invalid permit (valid=false) → enforcement raises"""
    # Create invalid permit
    permit_data = {
        "uat_autonomy_permit": {
            "system_name": "test_system",
            "core_version": UAT_CORE_VERSION,
            "valid": False,  # Invalid
            "reviewer": "test_reviewer",
        }
    }

    with open(permit_path, 'w') as f:
        yaml.dump(permit_data, f)

    # Enforcement should raise
    with pytest.raises(UATAutonomyDenied) as exc_info:
        enforce_uat_autonomy(UAT_CORE_VERSION)

    assert "invalid" in str(exc_info.value).lower()


def test_permit_version_mismatch__enforcement_stops(permit_path):
    """Test: Version mismatch → enforcement raises"""
    # Create permit with wrong version
    permit_data = {
        "uat_autonomy_permit": {
            "system_name": "test_system",
            "core_version": "999.999",  # Wrong version
            "valid": True,
            "reviewer": "test_reviewer",
        }
    }

    with open(permit_path, 'w') as f:
        yaml.dump(permit_data, f)

    # Enforcement should raise
    with pytest.raises(UATAutonomyDenied) as exc_info:
        enforce_uat_autonomy(UAT_CORE_VERSION)

    assert "invalid" in str(exc_info.value).lower()


def test_permit_valid__enforcement_passes(permit_path):
    """Test: Valid permit → enforcement passes"""
    # Create valid permit
    permit_data = {
        "uat_autonomy_permit": {
            "system_name": "test_system",
            "core_version": UAT_CORE_VERSION,
            "valid": True,
            "reviewer": "test_reviewer",
            "compliance_check": {
                "flow_order_preserved": True,
                "judgment_can_stop": True,
                "actions_traceable": True,
                "human_authority_explicit": True,
            }
        }
    }

    with open(permit_path, 'w') as f:
        yaml.dump(permit_data, f)

    # Enforcement should pass without exception
    enforce_uat_autonomy(UAT_CORE_VERSION)  # No exception = success


def test_permit_exists__detection(permit_path):
    """Test: permit_exists() correctly detects file presence"""
    assert not permit_exists()

    # Create permit
    permit_data = {"uat_autonomy_permit": {"valid": False}}
    with open(permit_path, 'w') as f:
        yaml.dump(permit_data, f)

    assert permit_exists()


def test_permit_is_valid__validation(permit_path):
    """Test: permit_is_valid() correctly validates permit"""
    # No permit
    assert not permit_is_valid(UAT_CORE_VERSION)

    # Invalid permit (valid=false)
    permit_data = {
        "uat_autonomy_permit": {
            "core_version": UAT_CORE_VERSION,
            "valid": False,
        }
    }
    with open(permit_path, 'w') as f:
        yaml.dump(permit_data, f)
    assert not permit_is_valid(UAT_CORE_VERSION)

    # Version mismatch
    permit_data["uat_autonomy_permit"]["valid"] = True
    permit_data["uat_autonomy_permit"]["core_version"] = "999.999"
    with open(permit_path, 'w') as f:
        yaml.dump(permit_data, f)
    assert not permit_is_valid(UAT_CORE_VERSION)

    # Valid permit
    permit_data["uat_autonomy_permit"]["core_version"] = UAT_CORE_VERSION
    with open(permit_path, 'w') as f:
        yaml.dump(permit_data, f)
    assert permit_is_valid(UAT_CORE_VERSION)


def test_enforcement_trace__permit_missing(permit_path):
    """Test: Trace correctly reports permit missing"""
    trace = get_uat_enforcement_trace("STOP")

    assert trace["uat_enforcement"]["permit_checked"] is True
    assert trace["uat_enforcement"]["permit_exists"] is False
    assert trace["uat_enforcement"]["permit_valid"] is False
    assert trace["uat_enforcement"]["enforcement_result"] == "STOP"
    assert trace["uat_enforcement"]["core_version"] == UAT_CORE_VERSION


def test_enforcement_trace__permit_valid(permit_path):
    """Test: Trace correctly reports valid permit"""
    # Create valid permit
    permit_data = {
        "uat_autonomy_permit": {
            "system_name": "test_system",
            "core_version": UAT_CORE_VERSION,
            "valid": True,
            "reviewer": "test_reviewer",
        }
    }
    with open(permit_path, 'w') as f:
        yaml.dump(permit_data, f)

    trace = get_uat_enforcement_trace("PASS")

    assert trace["uat_enforcement"]["permit_checked"] is True
    assert trace["uat_enforcement"]["permit_exists"] is True
    assert trace["uat_enforcement"]["permit_valid"] is True
    assert trace["uat_enforcement"]["enforcement_result"] == "PASS"
    assert trace["uat_enforcement"]["permit_version"] == UAT_CORE_VERSION


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

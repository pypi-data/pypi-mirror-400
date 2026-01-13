"""
Tests for EUE Offline Agent Role Library.

Tests:
- BaseRole abstraction
- RoleRegistry registration and discovery
- ExcelUploaderRole configuration
"""

from pathlib import Path
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops.eue.roles.base_role import BaseRole, RoleResult
from ops.eue.roles import RoleRegistry
from ops.eue.roles.excel import ExcelUploaderRole
from ops.eue.roles.erp import ERPLoginRole, ERPInventoryQueryRole, ERP2FARole
from ops.eue.roles.portal import PortalReportUploadRole
from ops.eue.offline_agent import Goal, Playbook


class TestRoleRegistry:
    """Test RoleRegistry functionality."""

    def setup_method(self):
        """Clear registry before each test."""
        RoleRegistry.clear()

    def test_register_role(self):
        """Test role registration."""
        RoleRegistry.register(ExcelUploaderRole)

        assert RoleRegistry.has_role("excel_uploader")
        assert len(RoleRegistry.list_roles()) == 1

    def test_get_role(self):
        """Test getting a registered role."""
        RoleRegistry.register(ExcelUploaderRole)

        role = RoleRegistry.get("excel_uploader")
        assert isinstance(role, ExcelUploaderRole)
        assert role.role_name == "excel_uploader"
        assert role.version == "1.0.0"

    def test_get_nonexistent_role(self):
        """Test getting a role that doesn't exist."""
        with pytest.raises(ValueError, match="not found"):
            RoleRegistry.get("nonexistent_role")

    def test_list_roles(self):
        """Test listing all registered roles."""
        RoleRegistry.register(ExcelUploaderRole)

        roles = RoleRegistry.list_roles()
        assert len(roles) == 1
        assert roles[0]["name"] == "excel_uploader"
        assert roles[0]["version"] == "1.0.0"

    def test_duplicate_registration(self):
        """Test that duplicate registration raises error."""
        RoleRegistry.register(ExcelUploaderRole)

        with pytest.raises(ValueError, match="already registered"):
            RoleRegistry.register(ExcelUploaderRole)

    def test_get_role_info(self):
        """Test getting role metadata."""
        RoleRegistry.register(ExcelUploaderRole)

        info = RoleRegistry.get_role_info("excel_uploader")
        assert info["name"] == "excel_uploader"
        assert info["version"] == "1.0.0"
        assert "description" in info


class TestExcelUploaderRole:
    """Test ExcelUploaderRole."""

    def test_role_metadata(self):
        """Test role has correct metadata."""
        role = ExcelUploaderRole()

        assert role.role_name == "excel_uploader"
        assert role.version == "1.0.0"
        assert role.description != ""

    def test_validate_config_missing_required(self):
        """Test validation fails with missing config."""
        role = ExcelUploaderRole()

        with pytest.raises(ValueError, match="Missing required config"):
            role.validate_config(target_url="http://test.com")  # Missing file_path

    def test_validate_config_success(self):
        """Test validation passes with complete config."""
        role = ExcelUploaderRole()

        # Should not raise
        role.validate_config(
            target_url="http://test.com",
            file_path="/path/to/file.xlsx"
        )

    def test_create_goal(self):
        """Test goal creation."""
        role = ExcelUploaderRole()

        goal = role.create_goal(
            target_url="http://test.com/excel",
            file_path="/data/test.xlsx"
        )

        assert isinstance(goal, Goal)
        assert goal.start_url == "http://test.com/excel"
        assert len(goal.targets) == 3
        assert "UploadFile" in goal.targets

    def test_create_playbook(self):
        """Test playbook creation."""
        role = ExcelUploaderRole()

        playbook = role.create_playbook(
            target_url="http://test.com/excel",
            file_path="/data/test.xlsx",
            analysis_type="quarterly"
        )

        assert isinstance(playbook, Playbook)
        assert playbook.form_data["analysis_type"] == "quarterly"
        assert "file_input" in playbook.selectors
        assert playbook.max_steps == 30

    def test_create_playbook_default_analysis(self):
        """Test playbook creation with default analysis type."""
        role = ExcelUploaderRole()

        playbook = role.create_playbook(
            target_url="http://test.com/excel",
            file_path="/data/test.xlsx"
        )

        assert playbook.form_data["analysis_type"] == "standard"

    def test_get_info(self):
        """Test getting role info."""
        role = ExcelUploaderRole()

        info = role.get_info()
        assert info["name"] == "excel_uploader"
        assert info["version"] == "1.0.0"
        assert "description" in info

    def test_str_representation(self):
        """Test string representation."""
        role = ExcelUploaderRole()

        assert str(role) == "excel_uploader v1.0.0"


class TestRoleResult:
    """Test RoleResult data class."""

    def test_role_result_success(self):
        """Test successful result."""
        result = RoleResult(
            role_name="test_role",
            version="1.0.0",
            success=True,
            goal_achieved=True,
            execution_time_ms=1234.5,
            step_count=10,
            output_data={"key": "value"}
        )

        assert result.success
        assert result.goal_achieved
        assert "SUCCESS" in str(result)
        assert "ACHIEVED" in str(result)

    def test_role_result_failure(self):
        """Test failed result."""
        result = RoleResult(
            role_name="test_role",
            version="1.0.0",
            success=False,
            goal_achieved=False,
            execution_time_ms=500.0,
            step_count=3,
            error="Test error"
        )

        assert not result.success
        assert not result.goal_achieved
        assert "FAILED" in str(result)
        assert result.error == "Test error"


class TestERPLoginRole:
    """Test ERPLoginRole behavior."""

    def test_validate_config_requires_credentials(self):
        role = ERPLoginRole()

        with pytest.raises(ValueError, match="Missing required config"):
            role.validate_config(target_url="https://erp.local")

    def test_create_goal_and_playbook(self):
        role = ERPLoginRole()
        config = {
            "target_url": "https://erp.local/login",
            "username": "demo",
            "password": "secret",
        }

        goal = role.create_goal(**config)
        playbook = role.create_playbook(**config)

        assert goal.start_url == config["target_url"]
        assert "SubmitCredentials" in goal.targets
        assert playbook.credentials["username"] == "demo"
        assert "username_input" in playbook.selectors


class TestERPInventoryQueryRole:
    """Test sealed inventory query role."""

    def test_requires_inventory_url(self):
        role = ERPInventoryQueryRole()
        with pytest.raises(ValueError, match="inventory_url"):
            role.validate_config()

    def test_playbook_uses_filters(self):
        role = ERPInventoryQueryRole()
        config = {
            "inventory_url": "https://erp.local/inventory",
            "query_params": {"warehouse": "A", "sku": "SKU-1"},
        }
        playbook = role.create_playbook(**config)

        assert playbook.form_data["warehouse"] == "A"
        assert playbook.max_steps == 40


class TestPortalReportUploadRole:
    """Test sealed portal report upload role."""

    def test_validate_file_path(self, tmp_path):
        role = PortalReportUploadRole()
        valid_file = tmp_path / "report.xlsx"
        valid_file.write_text("data")

        # Missing portal_url
        with pytest.raises(ValueError, match="portal_url"):
            role.validate_config(file_path=str(valid_file))

        # Valid config should not raise
        role.validate_config(portal_url="https://portal.local/upload", file_path=str(valid_file))


class TestERP2FARole:
    """Test ERP second-factor role."""

    def test_requires_value_or_provider(self):
        role = ERP2FARole()
        with pytest.raises(ValueError):
            role.validate_config(verification_url="https://erp.local/2fa", otp_method="totp")

    def test_goal_and_playbook(self):
        role = ERP2FARole()
        config = {
            "verification_url": "https://erp.local/2fa",
            "otp_method": "totp",
            "otp_value": "123456",
        }
        goal = role.create_goal(**config)
        playbook = role.create_playbook(**config)

        assert goal.name == "erp_2fa_step"
        assert "SubmitOTP" in goal.targets
        assert playbook.form_data["otp_value"] == "123456"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

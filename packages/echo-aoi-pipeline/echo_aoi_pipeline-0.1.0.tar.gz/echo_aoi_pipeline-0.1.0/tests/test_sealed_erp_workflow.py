"""Tests for the sealed ERP workflow runner."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ops.eue.workflows import (
    SealedERPWorkflowConfig,
    SealedERPWorkflow,
)


def _base_config(tmp_path: Path) -> SealedERPWorkflowConfig:
    report_path = tmp_path / "report.xlsx"
    report_path.write_text("data")
    return SealedERPWorkflowConfig(
        login={
            "target_url": "https://erp.local/login",
            "username": "demo",
            "password": "secret",
        },
        inventory_query={
            "inventory_url": "https://erp.local/inventory",
            "query_params": {"warehouse": "A"},
        },
        report_upload={
            "portal_url": "https://portal.local/upload",
            "file_path": str(tmp_path / "report.xlsx"),
        },
    )


def test_plan_without_second_factor(tmp_path: Path):
    cfg = _base_config(tmp_path)
    workflow = SealedERPWorkflow(cfg)
    plan = workflow.build_plan()
    assert [item.role_name for item in plan] == [
        "erp_login",
        "erp_inventory_query",
        "portal_report_upload",
    ]


def test_plan_with_second_factor(tmp_path: Path):
    cfg = _base_config(tmp_path)
    cfg = replace(
        cfg,
        second_factor={
            "verification_url": "https://erp.local/2fa",
            "otp_method": "totp",
            "otp_value": "123456",
        },
    )

    workflow = SealedERPWorkflow(cfg)
    plan = workflow.build_plan()
    assert [item.role_name for item in plan] == [
        "erp_login",
        "erp_2fa",
        "erp_inventory_query",
        "portal_report_upload",
    ]

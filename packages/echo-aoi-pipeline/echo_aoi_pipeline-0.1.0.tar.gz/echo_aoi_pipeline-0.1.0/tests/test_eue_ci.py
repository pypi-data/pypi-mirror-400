#!/usr/bin/env python3
"""
EUE v1.0 CI/CD Test Suite

Automated tests for continuous integration and deployment validation.
"""

import sys
import unittest
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


class TestEUEImports(unittest.TestCase):
    """Test EUE module imports."""

    def test_eue_import(self):
        """Test that EUE module can be imported."""
        try:
            from ops.eue import get_eue
            self.assertTrue(True, "EUE import successful")
        except ImportError as e:
            self.fail(f"EUE import failed: {e}")

    def test_eue_config_import(self):
        """Test that EUEConfig can be imported."""
        try:
            from ops.eue import EUEConfig
            self.assertTrue(True, "EUEConfig import successful")
        except ImportError as e:
            self.fail(f"EUEConfig import failed: {e}")

    def test_eue_mode_import(self):
        """Test that EUEMode can be imported."""
        try:
            from ops.eue import EUEMode
            self.assertTrue(True, "EUEMode import successful")
        except ImportError as e:
            self.fail(f"EUEMode import failed: {e}")

    def test_all_imports(self):
        """Test all EUE imports together."""
        try:
            from ops.eue import get_eue, EUEConfig, EUEMode, EUEResult, EUESubsystem
            self.assertTrue(True, "All EUE imports successful")
        except ImportError as e:
            self.fail(f"EUE imports failed: {e}")


class TestEUEConfiguration(unittest.TestCase):
    """Test EUE configuration."""

    def test_config_creation(self):
        """Test EUEConfig creation."""
        from ops.eue import EUEConfig, EUEMode

        config = EUEConfig(
            scenario="test",
            mode=EUEMode.DIRECT,
        )

        self.assertEqual(config.scenario, "test")
        self.assertEqual(config.mode, EUEMode.DIRECT)

    def test_all_modes(self):
        """Test all EUE modes."""
        from ops.eue import EUEConfig, EUEMode

        modes = [EUEMode.DIRECT, EUEMode.SELF_HEAL, EUEMode.RECORD, EUEMode.VERIFY]

        for mode in modes:
            config = EUEConfig(scenario="test", mode=mode)
            self.assertEqual(config.mode, mode)

    def test_config_with_options(self):
        """Test EUEConfig with all options."""
        from ops.eue import EUEConfig, EUEMode

        config = EUEConfig(
            scenario="test",
            mode=EUEMode.SELF_HEAL,
            max_attempts=5,
            enable_proof=True,
            enable_timecapsule=True,
            enable_cursor=True,
            enable_video=True,
        )

        self.assertEqual(config.max_attempts, 5)
        self.assertTrue(config.enable_proof)
        self.assertTrue(config.enable_timecapsule)
        self.assertTrue(config.enable_cursor)
        self.assertTrue(config.enable_video)


class TestMigratedFiles(unittest.TestCase):
    """Test that migrated files use EUE."""

    def test_codex_agent_migration(self):
        """Test that Codex Agent uses EUE."""
        codex_file = PROJECT_ROOT / "codex_cli_autodexa_patch.py"

        if not codex_file.exists():
            self.skipTest("Codex Agent file not found")

        content = codex_file.read_text()
        self.assertIn("from ops.eue import", content, "Codex Agent should use EUE")

    def test_self_heal_tests_migration(self):
        """Test that Self-Heal tests use EUE."""
        test_file = PROJECT_ROOT / "tests" / "test_self_heal_flow.py"

        if not test_file.exists():
            self.skipTest("Self-Heal test file not found")

        content = test_file.read_text()
        self.assertIn("from ops.eue import", content, "Self-Heal tests should use EUE")

    def test_auto_demo_migration(self):
        """Test that Auto Demo Orchestrator uses EUE."""
        auto_demo_file = PROJECT_ROOT / "ops" / "eui" / "backend" / "runtime" / "auto_demo" / "full_stack_orchestrator.py"

        if not auto_demo_file.exists():
            self.skipTest("Auto Demo file not found")

        content = auto_demo_file.read_text()
        self.assertIn("from ops.eue import", content, "Auto Demo should use EUE")


class TestDeprecationWarnings(unittest.TestCase):
    """Test that deprecated modules have warnings."""

    def test_timecapsule_deprecation(self):
        """Test timecapsule.py has deprecation warning."""
        file_path = PROJECT_ROOT / "ops" / "mcp" / "playwright" / "timecapsule.py"

        if not file_path.exists():
            self.skipTest("timecapsule.py not found")

        content = file_path.read_text()
        self.assertIn("DEPRECATION WARNING", content, "timecapsule.py should have deprecation warning")

    def test_self_heal_orchestrator_deprecation(self):
        """Test self_heal_orchestrator.py has deprecation warning."""
        file_path = PROJECT_ROOT / "ops" / "mcp" / "playwright" / "self_heal_orchestrator.py"

        if not file_path.exists():
            self.skipTest("self_heal_orchestrator.py not found")

        content = file_path.read_text()
        self.assertIn("DEPRECATION WARNING", content, "self_heal_orchestrator.py should have deprecation warning")

    def test_mcp_bridge_deprecation(self):
        """Test mcp_bridge.py has deprecation warning."""
        file_path = PROJECT_ROOT / "ops" / "mcp" / "playwright" / "mcp_bridge.py"

        if not file_path.exists():
            self.skipTest("mcp_bridge.py not found")

        content = file_path.read_text()
        self.assertIn("DEPRECATION WARNING", content, "mcp_bridge.py should have deprecation warning")


class TestDocumentation(unittest.TestCase):
    """Test that documentation exists."""

    def test_eue_complete_doc(self):
        """Test EUE_v1_COMPLETE.md exists."""
        doc = PROJECT_ROOT / "EUE_v1_COMPLETE.md"
        self.assertTrue(doc.exists(), "EUE_v1_COMPLETE.md should exist")

    def test_implementation_summary(self):
        """Test EUE_v1_IMPLEMENTATION_SUMMARY.md exists."""
        doc = PROJECT_ROOT / "EUE_v1_IMPLEMENTATION_SUMMARY.md"
        self.assertTrue(doc.exists(), "EUE_v1_IMPLEMENTATION_SUMMARY.md should exist")

    def test_phase1_doc(self):
        """Test EUE_PHASE1_COMPLETE.md exists."""
        doc = PROJECT_ROOT / "EUE_PHASE1_COMPLETE.md"
        self.assertTrue(doc.exists(), "EUE_PHASE1_COMPLETE.md should exist")

    def test_phase2_doc(self):
        """Test EUE_PHASE2_COMPLETE.md exists."""
        doc = PROJECT_ROOT / "EUE_PHASE2_COMPLETE.md"
        self.assertTrue(doc.exists(), "EUE_PHASE2_COMPLETE.md should exist")

    def test_migration_complete(self):
        """Test MIGRATION_COMPLETE.md exists."""
        doc = PROJECT_ROOT / "MIGRATION_COMPLETE.md"
        self.assertTrue(doc.exists(), "MIGRATION_COMPLETE.md should exist")

    def test_validation_report(self):
        """Test VALIDATION_REPORT.md exists."""
        doc = PROJECT_ROOT / "VALIDATION_REPORT.md"
        self.assertTrue(doc.exists(), "VALIDATION_REPORT.md should exist")

    def test_readme(self):
        """Test ops/eue/README.md exists."""
        doc = PROJECT_ROOT / "ops" / "eue" / "README.md"
        self.assertTrue(doc.exists(), "ops/eue/README.md should exist")

    def test_migration_guide(self):
        """Test ops/eue/MIGRATION_GUIDE.md exists."""
        doc = PROJECT_ROOT / "ops" / "eue" / "MIGRATION_GUIDE.md"
        self.assertTrue(doc.exists(), "ops/eue/MIGRATION_GUIDE.md should exist")


def run_tests():
    """Run all tests and return results."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(sys.modules[__name__])

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(run_tests())

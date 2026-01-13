"""
Constitution Pack Presence Tests

Minimal tests to verify constitutional documents exist.
Does NOT validate content - only presence for CI.
"""

import pytest
from pathlib import Path


@pytest.fixture
def constitution_dir():
    """Get constitution directory path"""
    repo_root = Path(__file__).parent.parent
    return repo_root / "constitution"


def test_constitution_main_exists(constitution_dir):
    """Test: ECHO_CONSTITUTION.md exists"""
    constitution_file = constitution_dir / "ECHO_CONSTITUTION.md"
    assert constitution_file.exists(), "ECHO_CONSTITUTION.md must exist"


def test_annex_exists(constitution_dir):
    """Test: ANNEX_BOUNDARY_INTENT.md exists"""
    annex_file = constitution_dir / "ANNEX_BOUNDARY_INTENT.md"
    assert annex_file.exists(), "ANNEX_BOUNDARY_INTENT.md must exist"


def test_readme_exists(constitution_dir):
    """Test: README.md exists"""
    readme_file = constitution_dir / "README.md"
    assert readme_file.exists(), "constitution/README.md must exist"


def test_changelog_exists(constitution_dir):
    """Test: CHANGELOG.md exists"""
    changelog_file = constitution_dir / "CHANGELOG.md"
    assert changelog_file.exists(), "CHANGELOG.md must exist"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

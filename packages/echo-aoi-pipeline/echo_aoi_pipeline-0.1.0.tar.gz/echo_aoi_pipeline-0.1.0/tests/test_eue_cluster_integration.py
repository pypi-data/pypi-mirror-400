"""
Integration tests for EUE Remote Cluster Mode v1.

Tests the integration of cluster routing with EUE Core.
"""

import asyncio
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from ops.eue.eue_core import EchoUnifiedEntrypoint, EUEConfig, EUEMode


@pytest.fixture
def cluster_spec_path(tmp_path):
    """Create a temporary cluster spec for testing."""
    yaml_content = """\
version: 1.0.0
cluster:
  mode: active_pool
  default_browser: chromium
  strategy:
    type: round_robin
nodes:
  - id: test-node-01
    endpoint: ws://localhost:9001
  - id: test-node-02
    endpoint: ws://localhost:9002
routing:
  intents:
    smoke:
      strategy_override: round_robin
      allowed_tags: [primary]
"""
    spec = tmp_path / "test_cluster.yaml"
    spec.write_text(yaml_content, encoding="utf-8")
    return str(spec)


def test_cluster_config_fields():
    """Test that EUEConfig has cluster-related fields."""
    config = EUEConfig(
        enable_cluster=True,
        cluster_spec_path="spec/test.yaml",
        cluster_intent="smoke"
    )

    assert config.enable_cluster is True
    assert config.cluster_spec_path == "spec/test.yaml"
    assert config.cluster_intent == "smoke"


def test_cluster_mode_sets_remote_location():
    """Test that cluster mode automatically sets location to remote."""
    config = EUEConfig(
        location="local",  # Start with local
        cluster_spec_path="spec/test.yaml"
    )

    # Should be changed to remote by __post_init__
    assert config.location == "remote"


@pytest.mark.asyncio
async def test_cluster_endpoint_resolution(cluster_spec_path):
    """Test that cluster endpoint is resolved when bridge is created."""
    config = EUEConfig(
        mode=EUEMode.DIRECT,
        location="remote",
        cluster_spec_path=cluster_spec_path,
    )

    eue = EchoUnifiedEntrypoint(config)

    # Before _get_bridge, endpoint should be None
    assert eue.config.endpoint is None

    # Mock the Dexa engine to avoid actual Playwright calls
    async def mock_get_bridge(*args, **kwargs):
        return MagicMock()

    with patch.object(eue._dexa_engine, 'get_bridge', side_effect=mock_get_bridge):
        # Call _get_bridge which should resolve cluster endpoint
        await eue._get_bridge()

        # After _get_bridge, endpoint should be resolved
        assert eue.config.endpoint is not None
        assert eue.config.endpoint.startswith("ws://localhost:")
        assert eue.config.enable_cluster is True


@pytest.mark.asyncio
async def test_cluster_intent_routing(cluster_spec_path, tmp_path):
    """Test that intent parameter is used for routing."""
    # Create a spec with intent-based routing
    yaml_content = """\
version: 1.0.0
cluster:
  mode: active_pool
  default_browser: chromium
  strategy:
    type: round_robin
nodes:
  - id: primary-node
    endpoint: ws://localhost:9001
    tags: [primary]
  - id: backup-node
    endpoint: ws://localhost:9002
    tags: [backup]
routing:
  intents:
    smoke:
      strategy_override: round_robin
      allowed_tags: [primary]
"""
    spec = tmp_path / "intent_cluster.yaml"
    spec.write_text(yaml_content, encoding="utf-8")

    config = EUEConfig(
        mode=EUEMode.DIRECT,
        location="remote",
        cluster_spec_path=str(spec),
        cluster_intent="smoke"  # Only primary nodes
    )

    eue = EchoUnifiedEntrypoint(config)

    # Mock the Dexa engine
    async def mock_get_bridge(*args, **kwargs):
        return MagicMock()

    with patch.object(eue._dexa_engine, 'get_bridge', side_effect=mock_get_bridge):
        # Resolve cluster endpoint with intent
        await eue._get_bridge()

        # Should select primary node (9001)
        assert eue.config.endpoint == "ws://localhost:9001"


@pytest.mark.asyncio
async def test_cluster_no_spec_fallback():
    """Test that EUE works without cluster spec (fallback to explicit endpoint)."""
    config = EUEConfig(
        mode=EUEMode.DIRECT,
        location="remote",
        endpoint="ws://localhost:9000",  # Explicit endpoint
    )

    eue = EchoUnifiedEntrypoint(config)

    # Mock the Dexa engine
    async def mock_get_bridge(*args, **kwargs):
        return MagicMock()

    with patch.object(eue._dexa_engine, 'get_bridge', side_effect=mock_get_bridge):
        await eue._get_bridge()

        # Should keep explicit endpoint
        assert eue.config.endpoint == "ws://localhost:9000"
        assert eue.config.enable_cluster is False


def test_cluster_validation_no_endpoint_no_spec():
    """Test that validation fails without endpoint or cluster spec."""
    with pytest.raises(ValueError, match="Remote execution requires an endpoint"):
        EUEConfig(
            location="remote",
            endpoint=None,
            cluster_spec_path=None
        )


@pytest.mark.asyncio
async def test_cluster_browser_override(cluster_spec_path, tmp_path):
    """Test that cluster can override browser type."""
    # Create a spec with firefox browser
    yaml_content = """\
version: 1.0.0
cluster:
  mode: active_pool
  default_browser: firefox
  strategy:
    type: round_robin
nodes:
  - id: firefox-node
    browser: firefox
    endpoint: ws://localhost:9001
routing:
  intents: {}
"""
    spec = tmp_path / "firefox_cluster.yaml"
    spec.write_text(yaml_content, encoding="utf-8")

    config = EUEConfig(
        mode=EUEMode.DIRECT,
        location="remote",
        browser="chromium",  # Start with chromium
        cluster_spec_path=str(spec),
    )

    eue = EchoUnifiedEntrypoint(config)

    # Mock the Dexa engine
    async def mock_get_bridge(*args, **kwargs):
        return MagicMock()

    with patch.object(eue._dexa_engine, 'get_bridge', side_effect=mock_get_bridge):
        await eue._get_bridge()

        # Browser should be changed to firefox
        assert eue.config.browser == "firefox"
        assert eue.config.endpoint == "ws://localhost:9001"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
